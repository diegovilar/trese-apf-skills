#!/usr/bin/env python3
"""Calculadora e renderizador da skill nesma-apf-estimator.

Somente biblioteca padrão; Python >= 3.8.

Uso:
    python3 apf.py check  ESTIMATIVA.json
    python3 apf.py calc   ESTIMATIVA.json            # JSON com os valores calculados
    python3 apf.py render ESTIMATIVA.json --format md|txt [--out ARQUIVO] [--perfil chat|arquivo]
        (sem --out o padrão é 'chat': legenda só com os termos usados; com --out, 'arquivo': legenda completa)
    python3 apf.py render ESTIMATIVA.json --format xlsx --out ARQUIVO.xlsx

O agente monta o JSON canônico (ver references/05-saida-e-legenda.md). Este script
valida o JSON, calcula pesos, fatores e totais com aritmética decimal exata e gera
as saídas. A LLM não faz contas.

Códigos de saída: 0 = ok; 1 = JSON inválido (erros listados); 2 = erro de uso ou de E/S;
3 = arquivo de saída já existe (nunca é sobrescrito).
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from decimal import Decimal
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

VERSAO_ESQUEMA = 2

TIPOS_DADOS = ("ALI", "AIE")
TIPOS_TRANSACAO = ("EE", "SE", "CE")
TIPOS = TIPOS_DADOS + TIPOS_TRANSACAO

# NESMA, Early Function Point Analysis (2015): contagem estimada.
PESOS_ESTIMADA = {"ALI": 7, "AIE": 5, "EE": 4, "SE": 5, "CE": 4}
COMPLEXIDADE_ESTIMADA = {"ALI": "Baixa", "AIE": "Baixa", "EE": "Média", "SE": "Média", "CE": "Média"}
# NESMA, Early Function Point Analysis (2015): contagem indicativa.
PESOS_INDICATIVA = {"ALI": 35, "AIE": 15}

# NESMA, APF para Melhoria de Software 2.2.1.
FATOR_INCLUIDA = Decimal("1.00")
FATOR_EXCLUIDA = Decimal("0.40")
FATOR_MUDANCA_TIPO = Decimal("0.40")
FATOR_COSMETICA = Decimal("0.25")
# Tabela 1 (dados): % de TDs alterados.
TABELA_DADOS = [
    (Fraction(1, 3), Decimal("0.25")),
    (Fraction(2, 3), Decimal("0.50")),
    (Fraction(1, 1), Decimal("0.75")),
]
FATOR_DADOS_ACIMA = Decimal("1.00")
# Tabela 2 (transações): linhas = % de ARs, colunas = % de TDs.
LIMITES_AR = [Fraction(1, 3), Fraction(2, 3), Fraction(1, 1)]  # quarta linha: > 100%
LIMITES_TD = [Fraction(2, 3), Fraction(1, 1)]  # terceira coluna: > 100%
TABELA_TRANSACOES = [
    [Decimal("0.25"), Decimal("0.50"), Decimal("0.75")],
    [Decimal("0.50"), Decimal("0.75"), Decimal("1.00")],
    [Decimal("0.75"), Decimal("1.00"), Decimal("1.25")],
    [Decimal("1.00"), Decimal("1.25"), Decimal("1.50")],
]
FATORES_PERMITIDOS_DADOS = sorted({f for _, f in TABELA_DADOS} | {FATOR_DADOS_ACIMA, FATOR_MUDANCA_TIPO})
FATORES_PERMITIDOS_TRANSACOES = sorted({f for linha in TABELA_TRANSACOES for f in linha})

ROTULO_HIBRIDO = "estimativa híbrida: pesos NESMA estimada + fatores EFPA"
CATEGORIAS_NAO_CONTADOS = {
    "absorvido": "absorvido no processo elementar",
    "dado-de-codigo": "dado de código",
    "fora-do-escopo": "fora do escopo da APF",
    "sem-evidencia": "sem evidência no pedido",
}


class ErroValidacao(Exception):
    def __init__(self, erros: List[str]):
        super().__init__("\n".join(erros))
        self.erros = erros


# --------------------------------------------------------------------------- validação

def _e_texto(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _texto(obj: Dict[str, Any], chave: str, onde: str, erros: List[str], opcional: bool = False) -> None:
    valor = obj.get(chave)
    if valor is None and opcional:
        return
    if not _e_texto(valor):
        erros.append(f"{onde}: '{chave}' deve ser texto não vazio" + (" ou null" if opcional else ""))


def _e_inteiro(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _contagem(obj: Any, onde: str, erros: List[str]) -> Optional[Tuple[int, int]]:
    if obj is None:
        return None
    if not isinstance(obj, dict):
        erros.append(f"{onde}: deve ser objeto com 'afetados' e 'originais'")
        return None
    afetados, originais = obj.get("afetados"), obj.get("originais")
    ok = True
    if not _e_inteiro(afetados) or afetados < 0:
        erros.append(f"{onde}.afetados: inteiro >= 0")
        ok = False
    if not _e_inteiro(originais) or originais < 1:
        erros.append(f"{onde}.originais: inteiro >= 1")
        ok = False
    return (afetados, originais) if ok else None


def _fator(valor: Any, onde: str, permitidos: List[Decimal], erros: List[str]) -> Optional[Decimal]:
    if not isinstance(valor, str):
        erros.append(f"{onde}: fator deve ser texto decimal, ex.: \"0.50\"")
        return None
    try:
        d = Decimal(valor)
    except Exception:
        d = None
    if d is None or not d.is_finite():
        erros.append(f"{onde}: fator inválido '{valor}'")
        return None
    if d not in permitidos:
        lista = ", ".join(str(p) for p in permitidos)
        erros.append(f"{onde}: fator {valor} fora dos valores do EFPA para este tipo ({lista})")
        return None
    return d


def _just_nc(item: Dict[str, Any]) -> str:
    """Justificativa de um item não contado, com as pendências que o cobrem."""
    refs = item.get("pendencias") or []
    return item["justificativa"] + (f" (ver {', '.join(refs)})" if refs else "")


def _validar_estrutura(est: Any) -> List[str]:
    """Validação de tipos, valores e referências. Não calcula cenários."""
    if not isinstance(est, dict):
        return ["raiz: deve ser objeto JSON"]
    erros: List[str] = []

    if est.get("versao_esquema") != VERSAO_ESQUEMA:
        erros.append(f"versao_esquema: esperado {VERSAO_ESQUEMA}")
    metodo = est.get("metodo")
    if metodo not in ("estimada", "indicativa"):
        erros.append("metodo: 'estimada' ou 'indicativa'")
        metodo = None
    tipo_projeto = est.get("tipo_projeto")
    if tipo_projeto not in ("desenvolvimento", "melhoria"):
        erros.append("tipo_projeto: 'desenvolvimento' ou 'melhoria'")
        tipo_projeto = None
    regime = est.get("regime_melhoria")
    if tipo_projeto == "melhoria":
        if regime not in ("sem-fatores", "nesma"):
            erros.append("regime_melhoria: 'sem-fatores' ou 'nesma' em projeto de melhoria")
            regime = None
    elif regime is not None:
        erros.append("regime_melhoria: deve ser null fora de projeto de melhoria")
        regime = None
    if metodo == "indicativa" and tipo_projeto == "melhoria":
        erros.append("metodo 'indicativa' não se aplica a projeto de melhoria")

    projeto = est.get("projeto")
    if not isinstance(projeto, dict):
        erros.append("projeto: deve ser objeto")
    else:
        for chave in ("titulo", "fronteira", "origem_subsidio", "data"):
            _texto(projeto, chave, "projeto", erros)

    cobertura = est.get("cobertura")
    if not isinstance(cobertura, dict):
        erros.append("cobertura: objeto com 'status' ('completa' ou 'parcial') e 'motivo'")
    else:
        status = cobertura.get("status")
        if status not in ("completa", "parcial"):
            erros.append("cobertura.status: 'completa' ou 'parcial'")
        if status == "parcial":
            _texto(cobertura, "motivo", "cobertura", erros)
        else:
            _texto(cobertura, "motivo", "cobertura", erros, opcional=True)

    def lista(chave: str, obrigatoria: bool = False) -> List[Any]:
        if chave not in est:
            if obrigatoria:
                erros.append(f"{chave}: lista obrigatória (pode ser vazia)")
            return []
        valor = est[chave]
        if not isinstance(valor, list):
            erros.append(f"{chave}: deve ser lista")
            return []
        return valor

    for i, aviso in enumerate(lista("avisos")):
        if not _e_texto(aviso):
            erros.append(f"avisos[{i}]: texto não vazio")

    # Hipóteses
    hipoteses = lista("hipoteses", obrigatoria=True)
    ids_hip: List[str] = []
    for i, h in enumerate(hipoteses):
        onde = f"hipoteses[{i}]"
        if not isinstance(h, dict):
            erros.append(f"{onde}: deve ser objeto")
            continue
        hid = h.get("id")
        if not isinstance(hid, str) or not re.fullmatch(r"H\d+", hid):
            erros.append(f"{onde}.id: formato H1, H2…")
        elif hid in ids_hip:
            erros.append(f"{onde}.id: '{hid}' repetido")
        else:
            ids_hip.append(hid)
            onde = f"hipoteses[{hid}]"
        _texto(h, "descricao", onde, erros)
        _texto(h, "trecho", onde, erros, opcional=True)
        _texto(h, "grupo", onde, erros, opcional=True)
        requer = h.get("requer", [])
        if requer is None:
            requer = []
        if not isinstance(requer, list) or not all(isinstance(r, str) for r in requer):
            erros.append(f"{onde}.requer: lista de IDs de hipóteses")
    for h in hipoteses:
        if isinstance(h, dict) and isinstance(h.get("requer"), list):
            for r in h["requer"]:
                if isinstance(r, str) and r not in ids_hip:
                    erros.append(f"hipoteses[{h.get('id')}].requer: '{r}' não existe")
                if r == h.get("id"):
                    erros.append(f"hipoteses[{h.get('id')}].requer: não pode exigir a si mesma")

    ids_pend: List[str] = []
    for chave, prefixo in (("premissas", "PR"), ("pendencias", "P")):
        vistos: List[str] = ids_pend if chave == "pendencias" else []
        for i, item in enumerate(lista(chave, obrigatoria=True)):
            onde = f"{chave}[{i}]"
            if not isinstance(item, dict):
                erros.append(f"{onde}: deve ser objeto")
                continue
            iid = item.get("id")
            if not isinstance(iid, str) or not re.fullmatch(prefixo + r"\d+", iid):
                erros.append(f"{onde}.id: formato {prefixo}1, {prefixo}2…")
            elif iid in vistos:
                erros.append(f"{onde}.id: '{iid}' repetido")
            else:
                vistos.append(iid)
            _texto(item, "descricao", onde, erros)

    nao_contados = lista("nao_contados", obrigatoria=True)
    for i, item in enumerate(nao_contados):
        onde = f"nao_contados[{i}]"
        if not isinstance(item, dict):
            erros.append(f"{onde}: deve ser objeto")
            continue
        _texto(item, "item", onde, erros)
        _texto(item, "justificativa", onde, erros)
        if not isinstance(item.get("categoria"), str) or item["categoria"] not in CATEGORIAS_NAO_CONTADOS:
            erros.append(f"{onde}.categoria: uma de {', '.join(CATEGORIAS_NAO_CONTADOS)}")
        refs = item.get("pendencias")
        if item.get("categoria") == "sem-evidencia" and (refs is None or refs == []):
            erros.append(f"{onde}.pendencias: item sem evidência exige a lista das pendências que o cobrem (ex.: [\"P2\"])")
        elif refs is not None:
            if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
                erros.append(f"{onde}.pendencias: lista de IDs de pendências")
            else:
                if len(set(refs)) != len(refs):
                    erros.append(f"{onde}.pendencias: ID repetido")
                for r in refs:
                    if r not in ids_pend:
                        erros.append(f"{onde}.pendencias: '{r}' não existe em 'pendencias'")

    # Funções
    funcoes = lista("funcoes", obrigatoria=True)
    if "funcoes" in est and isinstance(est["funcoes"], list) and not funcoes and not nao_contados:
        erros.append("funcoes: ao menos uma função, ou 'nao_contados' explicando por que nada é contado")
    ids_fun: List[str] = []
    hip_usadas = set()
    for i, f in enumerate(funcoes):
        onde = f"funcoes[{i}]"
        if not isinstance(f, dict):
            erros.append(f"{onde}: deve ser objeto")
            continue
        fid = f.get("id")
        if not isinstance(fid, str) or not re.fullmatch(r"F\d+", fid):
            erros.append(f"{onde}.id: formato F1, F2… (ou F01…)")
        elif fid in ids_fun:
            erros.append(f"{onde}.id: '{fid}' repetido")
        else:
            ids_fun.append(fid)
            onde = f"funcoes[{fid}]"
        for chave in ("requisito", "nome", "justificativa"):
            _texto(f, chave, onde, erros)
        tipo = f.get("tipo")
        if not isinstance(tipo, str) or tipo not in TIPOS:
            erros.append(f"{onde}.tipo: um de {', '.join(TIPOS)}")
            tipo = None
        if metodo == "indicativa" and tipo in TIPOS_TRANSACAO:
            erros.append(f"{onde}: a contagem indicativa só tem funções de dados (ALI/AIE)")
        op = f.get("operacao")
        if tipo_projeto == "melhoria":
            if not isinstance(op, str) or op not in ("I", "A", "E"):
                erros.append(f"{onde}.operacao: 'I', 'A' ou 'E' em projeto de melhoria")
                op = None
        elif op is not None:
            erros.append(f"{onde}.operacao: deve ser null em projeto de desenvolvimento")
        hip = f.get("hipotese")
        if hip is not None:
            if not isinstance(hip, str) or hip not in ids_hip:
                erros.append(f"{onde}.hipotese: {hip!r} não é o ID de uma hipótese existente (use null para evidência)")
            else:
                hip_usadas.add(hip)

        efpa = f.get("efpa")
        usa_efpa = tipo_projeto == "melhoria" and regime == "nesma" and op == "A"
        if not usa_efpa:
            if efpa is not None:
                erros.append(f"{onde}.efpa: só existe em melhoria, regime 'nesma', operação 'A'")
            continue
        if not isinstance(efpa, dict):
            erros.append(f"{onde}.efpa: obrigatório (objeto) para função alterada no regime 'nesma'")
            continue
        if tipo is not None:
            _validar_efpa(efpa, tipo, f"{onde}.efpa", erros)

    grupos: Dict[str, List[str]] = {}
    for h in hipoteses:
        if isinstance(h, dict) and _e_texto(h.get("grupo")) and h.get("id") in ids_hip:
            grupos.setdefault(h["grupo"], []).append(h["id"])
    for g, membros in grupos.items():
        if len(membros) < 2:
            erros.append(f"hipoteses: o grupo '{g}' (alternativas excludentes) precisa de ao menos duas hipóteses")
    for h in hipoteses:
        if isinstance(h, dict) and h.get("id") in ids_hip and h["id"] not in hip_usadas and not _e_texto(h.get("grupo")):
            requeridas = any(isinstance(o, dict) and isinstance(o.get("requer"), list) and h["id"] in o["requer"] for o in hipoteses)
            if not requeridas:
                erros.append(f"hipoteses: '{h['id']}' não está ligada a nenhuma função; registre-a como premissa")
    return erros


def _validar_efpa(efpa: Dict[str, Any], tipo: str, onde: str, erros: List[str]) -> None:
    cosmetica = efpa.get("cosmetica", False)
    mudanca_tipo = efpa.get("mudanca_tipo", False)
    if not isinstance(cosmetica, bool) or not isinstance(mudanca_tipo, bool):
        erros.append(f"{onde}: 'cosmetica' e 'mudanca_tipo' são booleanos")
        return
    tem_td, tem_ar, faixa = efpa.get("td") is not None, efpa.get("ar") is not None, efpa.get("faixa")
    td = _contagem(efpa.get("td"), f"{onde}.td", erros)
    _contagem(efpa.get("ar"), f"{onde}.ar", erros)
    dados = tipo in TIPOS_DADOS
    if dados:
        if cosmetica:
            erros.append(f"{onde}: 'cosmetica' só se aplica a transações")
        if tem_ar:
            erros.append(f"{onde}: 'ar' só se aplica a transações")
        if tem_td and td is not None and td[0] == 0 and not mudanca_tipo:
            erros.append(f"{onde}: função de dados alterada sem TD afetado e sem mudança de tipo não é contada (exemplo 8 do EFPA)")
        if tem_td and faixa is not None:
            erros.append(f"{onde}: fator determinado por 'td'; não informe 'faixa'")
        determinado = tem_td or (mudanca_tipo and faixa is None)
    else:
        if mudanca_tipo:
            erros.append(f"{onde}: 'mudanca_tipo' só se aplica a funções de dados")
        if cosmetica and (tem_td or tem_ar or faixa is not None):
            erros.append(f"{onde}: alteração cosmética tem fator fixo 0,25; não informe 'td', 'ar' nem 'faixa'")
        if tem_td != tem_ar:
            erros.append(f"{onde}: informe 'td' e 'ar' juntos, ou use 'faixa'")
        if tem_td and tem_ar and faixa is not None:
            erros.append(f"{onde}: fator determinado por 'td' e 'ar'; não informe 'faixa'")
        determinado = cosmetica or (tem_td and tem_ar)
    if determinado:
        return
    if not isinstance(faixa, dict):
        erros.append(f"{onde}: sem dados para determinar o fator, informe 'faixa' com min, max e justificativa")
        return
    permitidos = FATORES_PERMITIDOS_DADOS if dados else FATORES_PERMITIDOS_TRANSACOES
    fmin = _fator(faixa.get("min"), f"{onde}.faixa.min", permitidos, erros)
    fmax = _fator(faixa.get("max"), f"{onde}.faixa.max", permitidos, erros)
    _texto(faixa, "justificativa", f"{onde}.faixa", erros)
    if fmin is not None and fmax is not None and fmin > fmax:
        erros.append(f"{onde}.faixa: min maior que max")
    if mudanca_tipo and fmin is not None and fmin < FATOR_MUDANCA_TIPO:
        erros.append(f"{onde}.faixa: com mudança de tipo o fator é o maior entre 0,40 e o da tabela 1, então min >= 0.40")


def validar(est: Any) -> List[str]:
    """Retorna a lista de erros (vazia se o JSON é válido e pode ser calculado)."""
    erros = _validar_estrutura(est)
    if erros:
        return erros
    _, erros_cenario = _calcular(est)
    return erros_cenario


# --------------------------------------------------------------------------- cálculo

def fator_dados(td: Optional[Tuple[int, int]], mudanca_tipo: bool) -> Decimal:
    candidatos = []
    if mudanca_tipo:
        candidatos.append(FATOR_MUDANCA_TIPO)
    if td is not None and td[0] > 0:
        pct = Fraction(td[0], td[1])
        fator = FATOR_DADOS_ACIMA
        for limite, valor in TABELA_DADOS:
            if pct <= limite:
                fator = valor
                break
        candidatos.append(fator)
    return max(candidatos)


def fator_transacao(td: Tuple[int, int], ar: Tuple[int, int]) -> Decimal:
    pct_ar = Fraction(ar[0], ar[1])
    pct_td = Fraction(td[0], td[1])
    linha = len(LIMITES_AR)
    for i, limite in enumerate(LIMITES_AR):
        if pct_ar <= limite:
            linha = i
            break
    coluna = len(LIMITES_TD)
    for j, limite in enumerate(LIMITES_TD):
        if pct_td <= limite:
            coluna = j
            break
    return TABELA_TRANSACOES[linha][coluna]


def _par(obj: Optional[Dict[str, Any]]) -> Optional[Tuple[int, int]]:
    if obj is None:
        return None
    return (obj["afetados"], obj["originais"])


MAX_COMBINACOES = 4096


def _fechamento(ativas: set, requer: Dict[str, List[str]]) -> set:
    resultado, pilha = set(ativas), list(ativas)
    while pilha:
        for r in requer.get(pilha.pop(), []):
            if r not in resultado:
                resultado.add(r)
                pilha.append(r)
    return resultado


def _calcular(est: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    metodo = est["metodo"]
    melhoria = est["tipo_projeto"] == "melhoria"
    regime = est.get("regime_melhoria")
    nesma = melhoria and regime == "nesma"
    pesos = PESOS_INDICATIVA if metodo == "indicativa" else PESOS_ESTIMADA

    linhas = []
    for f in est["funcoes"]:
        peso = Decimal(pesos[f["tipo"]])
        origem_fator = "—"
        fmin = fmax = Decimal("1.00")
        if nesma:
            op = f["operacao"]
            if op == "I":
                fmin = fmax = FATOR_INCLUIDA
                origem_fator = "incluída"
            elif op == "E":
                fmin = fmax = FATOR_EXCLUIDA
                origem_fator = "excluída"
            else:
                efpa = f["efpa"]
                if f["tipo"] in TIPOS_DADOS:
                    td = _par(efpa.get("td"))
                    if td is not None or (efpa.get("mudanca_tipo") and efpa.get("faixa") is None):
                        fmin = fmax = fator_dados(td, bool(efpa.get("mudanca_tipo")))
                        origem_fator = "tabela 1" if td is not None else "mudança de tipo"
                    else:
                        fmin, fmax = Decimal(efpa["faixa"]["min"]), Decimal(efpa["faixa"]["max"])
                        origem_fator = "faixa"
                else:
                    if efpa.get("cosmetica"):
                        fmin = fmax = FATOR_COSMETICA
                        origem_fator = "cosmética"
                    elif efpa.get("td") is not None:
                        fmin = fmax = fator_transacao(_par(efpa["td"]), _par(efpa["ar"]))
                        origem_fator = "tabela 2"
                    else:
                        fmin, fmax = Decimal(efpa["faixa"]["min"]), Decimal(efpa["faixa"]["max"])
                        origem_fator = "faixa"
        linhas.append({
            "id": f["id"],
            "tipo": f["tipo"],
            "operacao": f.get("operacao"),
            "complexidade": COMPLEXIDADE_ESTIMADA[f["tipo"]] if metodo == "estimada" else "—",
            "peso": peso,
            "fator_min": fmin,
            "fator_max": fmax,
            "origem_fator": origem_fator,
            "valor_min": peso * fmin,
            "valor_max": peso * fmax,
            "hipotese": f.get("hipotese"),
        })

    # Cenários. Hipótese sem grupo é opcional: fora do mínimo, dentro do máximo.
    # Em cada grupo vale exatamente uma alternativa. 'requer' puxa as hipóteses exigidas.
    # Combinações que ativam duas alternativas do mesmo grupo são inválidas.
    hipoteses = est.get("hipoteses", [])
    grupo_de = {h["id"]: h["grupo"] for h in hipoteses if _e_texto(h.get("grupo"))}
    requer = {h["id"]: list(h.get("requer") or []) for h in hipoteses}
    soltas = [h["id"] for h in hipoteses if h["id"] not in grupo_de]
    grupos: Dict[str, List[str]] = {}
    for hid, g in grupo_de.items():
        grupos.setdefault(g, []).append(hid)
    nomes_grupos = sorted(grupos)

    def total(ativas: set, chave: str) -> Decimal:
        return sum((ln[chave] for ln in linhas if ln["hipotese"] is None or ln["hipotese"] in ativas), Decimal(0))

    def valida(ativas: set) -> bool:
        for membros in grupos.values():
            if sum(1 for m in membros if m in ativas) != 1:
                return False
        return True

    def combinacoes():
        if not nomes_grupos:
            yield ()
            return
        idx = [0] * len(nomes_grupos)
        while True:
            yield tuple(grupos[g][i] for g, i in zip(nomes_grupos, idx))
            k = len(idx) - 1
            while k >= 0:
                idx[k] += 1
                if idx[k] < len(grupos[nomes_grupos[k]]):
                    break
                idx[k] = 0
                k -= 1
            if k < 0:
                return

    n_comb = 1
    for g in nomes_grupos:
        n_comb *= len(grupos[g])
    if n_comb > MAX_COMBINACOES:
        return None, [f"hipoteses: {n_comb} combinações de alternativas; simplifique os grupos (máximo {MAX_COMBINACOES})"]

    melhor_min: Optional[Tuple[Decimal, List[str], set]] = None
    melhor_max: Optional[Tuple[Decimal, List[str], set]] = None
    for escolha in combinacoes():
        a_min = _fechamento(set(escolha), requer)
        if valida(a_min):
            t = total(a_min, "valor_min")
            chave = (t, sorted(a_min))
            if melhor_min is None or chave < (melhor_min[0], melhor_min[1]):
                melhor_min = (t, sorted(a_min), a_min)
        a_max = _fechamento(set(escolha) | set(soltas), requer)
        if valida(a_max):
            t = total(a_max, "valor_max")
            chave = (-t, sorted(a_max))
            if melhor_max is None or chave < (-melhor_max[0], melhor_max[1]):
                melhor_max = (t, sorted(a_max), a_max)
    erros: List[str] = []
    if melhor_min is None or melhor_max is None:
        return None, ["hipoteses: nenhuma combinação coerente (uma exigência em 'requer' ativa duas alternativas do mesmo grupo)"]

    # Coerência estrutural: em desenvolvimento estimado, um cenário com arquivos e sem
    # nenhuma transação é impossível (todo ALI é mantido e todo AIE é lido por algum processo).
    if metodo == "estimada" and not melhoria:
        for nome, (_, _, ativas) in (("mínimo", melhor_min), ("máximo", melhor_max)):
            tipos = {ln["tipo"] for ln in linhas if ln["hipotese"] is None or ln["hipotese"] in ativas}
            if tipos & set(TIPOS_DADOS) and not tipos & set(TIPOS_TRANSACAO):
                erros.append(f"cenário {nome}: tem funções de dados e nenhuma transação que as mantenha ou leia; "
                             "use 'requer' para ligar as hipóteses dos arquivos às das transações")
    if erros:
        return None, erros

    ativas_min, ativas_max = melhor_min[2], melhor_max[2]
    for ln in linhas:
        h = ln["hipotese"]
        ln["entra_min"] = h is None or h in ativas_min
        ln["entra_max"] = h is None or h in ativas_max
    efeito = {}
    for h in hipoteses:
        efeito[h["id"]] = {
            "min": sum((ln["valor_min"] for ln in linhas if ln["hipotese"] == h["id"]), Decimal(0)),
            "max": sum((ln["valor_max"] for ln in linhas if ln["hipotese"] == h["id"]), Decimal(0)),
        }

    if nesma:
        unidade = "PFM"
    elif melhoria:
        unidade = "PF de melhoria"
    else:
        unidade = "PF"
    cobertura = est["cobertura"]
    avisos = list(est.get("avisos", []))
    if melhor_max[0] == 0:
        avisos.insert(0, "O total é zero. Zero pontos de função não significa ausência de trabalho: "
                         "veja os itens não contados e as pendências antes de concluir a análise de viabilidade.")
    return {
        "unidade": unidade,
        "metodo": metodo,
        "tipo_projeto": est["tipo_projeto"],
        "regime_melhoria": regime,
        "rotulo": ROTULO_HIBRIDO if nesma else None,
        "linhas": linhas,
        "total_min": melhor_min[0],
        "total_max": melhor_max[0],
        "total": melhor_min[0] if melhor_min[0] == melhor_max[0] else None,
        "tem_faixa_de_fator": any(ln["origem_fator"] == "faixa" for ln in linhas),
        "cobertura": cobertura.get("status"),
        "motivo_cobertura": cobertura.get("motivo"),
        "avisos": avisos,
        "efeito_hipoteses": efeito,
        "hipoteses_cenario_min": melhor_min[1],
        "hipoteses_cenario_max": melhor_max[1],
    }, []


def calcular(est: Dict[str, Any]) -> Dict[str, Any]:
    erros = _validar_estrutura(est)
    if erros:
        raise ErroValidacao(erros)
    calc, erros = _calcular(est)
    if erros:
        raise ErroValidacao(erros)
    return calc


# --------------------------------------------------------------------------- formatação

def num(d: Decimal, casas: Optional[int] = None) -> str:
    """Número em formato brasileiro. Sem 'casas', inteiros saem sem decimais."""
    if casas is None:
        casas = 0 if d == d.to_integral_value() else 2
    q = Decimal(1).scaleb(-casas)
    texto = f"{d.quantize(q):,.{casas}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def _casas(calc: Dict[str, Any]) -> Optional[int]:
    return 2 if calc["unidade"] == "PFM" else None


def texto_total(calc: Dict[str, Any]) -> str:
    casas = _casas(calc)
    u = calc["unidade"]
    if calc["total"] is not None:
        texto = f"{num(calc['total'], casas)} {u}"
    else:
        texto = f"de {num(calc['total_min'], casas)} a {num(calc['total_max'], casas)} {u} (cenários mínimo e máximo; sem valor central)"
    if calc["cobertura"] == "parcial":
        texto += " — PARCIAL: condicionado às funções identificadas"
    return texto


def linhas_resumo_extra(est: Dict[str, Any], calc: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Pares (rótulo, texto) que todo resumo executivo mostra depois do total."""
    pares: List[Tuple[str, str]] = []
    if calc["cobertura"] == "parcial":
        pares.append(("Cobertura", "parcial. " + str(calc["motivo_cobertura"])))
    else:
        pares.append(("Cobertura", "completa em relação ao pedido analisado"))
    if calc["rotulo"]:
        pares.append(("Natureza", calc["rotulo"]))
    if est["metodo"] == "indicativa":
        pares.append(("Atenção", AVISO_INDICATIVA))
    for aviso in calc["avisos"]:
        pares.append(("Aviso", aviso))
    return pares


AVISO_INDICATIVA = ("na pesquisa da NESMA (cerca de 100 aplicações), a contagem indicativa desviou até cerca de 50% "
                    "da contagem detalhada em alguns casos. É uma observação da pesquisa, não um limite garantido de erro.")


def _faixa(a: Decimal, b: Decimal, casas: Optional[int]) -> str:
    return num(a, casas) if a == b else f"{num(a, casas)}–{num(b, casas)}"


def _md(texto: Any) -> str:
    s = "" if texto is None else str(texto)
    return re.sub(r"\s*\n\s*", " ", s).replace("|", "\\|").strip()


LEGENDA = [
    ("ALI", "Arquivo Lógico Interno: grupo de dados reconhecido pelo usuário e mantido pela aplicação."),
    ("AIE", "Arquivo de Interface Externa: grupo de dados reconhecido pelo usuário, só lido pela aplicação e mantido por outra."),
    ("EE", "Entrada Externa: processo que recebe dados de fora e mantém ALI ou altera o comportamento do sistema."),
    ("SE", "Saída Externa: processo que envia dados para fora com cálculo, dado derivado, atualização de ALI ou mudança de comportamento."),
    ("CE", "Consulta Externa: processo que recupera e apresenta dados sem cálculo, sem dado derivado e sem atualizar ALI."),
    ("Op. (I/A/E)", "Em melhoria: função incluída, alterada ou excluída. Em desenvolvimento: não se aplica (—)."),
    ("Complexidade", "Na contagem estimada da NESMA, é fixa: Baixa para ALI/AIE e Média para EE/SE/CE. Na indicativa, não se aplica."),
    ("Pesos (estimada)", "ALI 7, AIE 5, EE 4, SE 5, CE 4 PF."),
    ("Pesos (indicativa)", "35 PF por ALI e 15 PF por AIE; só funções de dados são identificadas."),
    ("Base", "'evidência': sustentada pelo texto do pedido. 'H1', 'H2'…: depende da hipótese indicada."),
    ("Cenário mínimo / máximo", "Mínimo: só evidências, a alternativa menor de cada grupo e as hipóteses que ela exige. Máximo: todas as hipóteses independentes, a alternativa maior de cada grupo e as exigidas. Não há valor central."),
    ("Cobertura", "'completa': as funções identificadas cobrem o pedido analisado. 'parcial': há funções afetadas que o subsídio não permite identificar; o total vale só para as funções listadas."),
    ("PF de melhoria", "Regime 'sem-fatores': soma simples dos PF das funções incluídas, alteradas e excluídas."),
    ("PFM", "Regime 'nesma': pontos de função de melhoria (EFPA 2.2.1), unidade distinta de PF. Fatores: incluída 1,00; excluída 0,40; alterada pela tabela 1 (dados) ou 2 (transações); só cosmética 0,25; só mudança de tipo AIE↔ALI 0,40."),
    ("Fator", "Multiplicador do PF base. Fora do regime 'nesma' é sempre 1,00."),
    ("Faixa de fator", "Fator de função alterada sem dados suficientes (TDs/ARs) no pedido: apresentado como intervalo, sem valor central."),
]


def legenda(est: Dict[str, Any], calc: Dict[str, Any], perfil: str = "arquivo") -> List[Tuple[str, str]]:
    """Perfil 'arquivo': legenda completa (exigida na planilha e nos arquivos exportados).
    Perfil 'chat': só os termos que aparecem neste resultado, para reduzir o texto que o agente
    precisa copiar para a resposta. A seleção é determinística, feita aqui, nunca pelo agente."""
    if perfil == "arquivo":
        return list(LEGENDA)
    tipos = {ln["tipo"] for ln in calc["linhas"]}
    melhoria = est["tipo_projeto"] == "melhoria"
    nesma = calc["unidade"] == "PFM"
    usar = set(tipos) | {"Base"}
    if melhoria:
        usar.add("Op. (I/A/E)")
    if est["metodo"] == "estimada":
        usar |= {"Complexidade", "Pesos (estimada)"}
    else:
        usar.add("Pesos (indicativa)")
    if est.get("hipoteses"):
        usar.add("Cenário mínimo / máximo")
    if calc["cobertura"] == "parcial":
        usar.add("Cobertura")
    if melhoria and not nesma:
        usar.add("PF de melhoria")
    if nesma:
        usar |= {"PFM", "Fator"}
        if calc["tem_faixa_de_fator"]:
            usar.add("Faixa de fator")
    return [(t, d) for t, d in LEGENDA if t in usar]


# --------------------------------------------------------------------------- markdown

def render_md(est: Dict[str, Any], calc: Dict[str, Any], perfil: str = "arquivo") -> str:
    p = est["projeto"]
    casas = _casas(calc)
    nesma = calc["unidade"] == "PFM"
    melhoria = est["tipo_projeto"] == "melhoria"
    out: List[str] = []
    out.append(f"# Estimativa de tamanho funcional: {_md(p['titulo'])}")
    out.append("")
    out.append("## Resumo executivo")
    out.append("")
    metodo = "NESMA estimada" if est["metodo"] == "estimada" else "NESMA indicativa"
    out.append(f"- **Tipo de projeto:** {est['tipo_projeto']}")
    if melhoria:
        out.append(f"- **Regime de melhoria:** {est['regime_melhoria']}")
    out.append(f"- **Método:** {metodo}")
    out.append(f"- **Fronteira da aplicação:** {_md(p['fronteira'])}")
    out.append(f"- **Origem do subsídio:** {_md(p['origem_subsidio'])}")
    out.append(f"- **Data:** {_md(p['data'])}")
    out.append(f"- **Total:** {texto_total(calc)}")
    for rotulo, texto in linhas_resumo_extra(est, calc):
        out.append(f"- **{rotulo}:** {_md(texto)}")
    out.append("")
    out.append("## Memória de cálculo")
    out.append("")
    if nesma:
        cab = ["ID", "Requisito / História", "Função identificada", "Tipo", "Operação (I/A/E)", "Complexidade", "PF base", "Fator", "PFM", "Base", "Justificativa técnica"]
    else:
        cab = ["ID", "Requisito / História", "Função identificada", "Tipo", "Operação (I/A/E)", "Complexidade", "PF", "Base", "Justificativa técnica"]
    out.append("| " + " | ".join(cab) + " |")
    out.append("|" + "|".join("---:" if c in ("PF", "PF base", "Fator", "PFM") else "---" for c in cab) + "|")
    funcoes = {f["id"]: f for f in est["funcoes"]}
    for ln in calc["linhas"]:
        f = funcoes[ln["id"]]
        base = ln["hipotese"] or "evidência"
        linha = [ln["id"], _md(f["requisito"]), _md(f["nome"]), ln["tipo"], ln["operacao"] or "—", ln["complexidade"]]
        if nesma:
            linha += [num(ln["peso"]), _faixa(ln["fator_min"], ln["fator_max"], 2), _faixa(ln["valor_min"], ln["valor_max"], 2)]
        else:
            linha += [num(ln["peso"])]
        just = _md(f["justificativa"])
        if nesma and ln["origem_fator"] == "faixa":
            just += " Faixa de fator: " + _md(f["efpa"]["faixa"]["justificativa"])
        linha += [base, just]
        out.append("| " + " | ".join(linha) + " |")
    vazio = [""] * (len(cab) - 2)
    total_col = cab.index("PFM") if nesma else cab.index("PF")
    linha_total = ["", "**Total**"] + vazio
    linha_total[total_col] = "**" + _faixa(calc["total_min"], calc["total_max"], casas) + "**"
    out.append("| " + " | ".join(linha_total) + " |")
    out.append("")

    hipoteses = est.get("hipoteses", [])
    if hipoteses:
        out.append("## Hipóteses e cenários")
        out.append("")
        out.append("| ID | Hipótese | Trecho do pedido | Alternativas (grupo) | Exige | Efeito |")
        out.append("|---|---|---|---|---|---:|")
        for h in hipoteses:
            ef = calc["efeito_hipoteses"][h["id"]]
            exige = ", ".join(h.get("requer") or []) or "—"
            out.append(f"| {h['id']} | {_md(h['descricao'])} | {_md(h.get('trecho')) or '—'} | {_md(h.get('grupo')) or '—'} | {exige} | +{_faixa(ef['min'], ef['max'], casas)} {calc['unidade']} |")
        out.append("")
        ativ_min = ", ".join(calc["hipoteses_cenario_min"]) or "nenhuma"
        ativ_max = ", ".join(calc["hipoteses_cenario_max"]) or "nenhuma"
        out.append(f"- **Cenário mínimo:** {num(calc['total_min'], casas)} {calc['unidade']} (hipóteses: {ativ_min})")
        out.append(f"- **Cenário máximo:** {num(calc['total_max'], casas)} {calc['unidade']} (hipóteses: {ativ_max})")
        out.append("")

    def secao(titulo: str, itens: List[Dict[str, Any]]) -> None:
        out.append(f"## {titulo}")
        out.append("")
        if not itens:
            out.append("Nenhuma.")
        for item in itens:
            out.append(f"- **{item['id']}.** {_md(item['descricao'])}")
        out.append("")

    secao("Premissas assumidas", est.get("premissas", []))
    out.append("## Itens não contados")
    out.append("")
    nao = est.get("nao_contados", [])
    if not nao:
        out.append("Nenhum.")
    else:
        out.append("| Item | Categoria | Justificativa |")
        out.append("|---|---|---|")
        for item in nao:
            out.append(f"| {_md(item['item'])} | {CATEGORIAS_NAO_CONTADOS[item['categoria']]} | {_md(_just_nc(item))} |")
    out.append("")
    secao("Dúvidas de requisito e pendências", est.get("pendencias", []))
    out.append("## Legenda")
    out.append("")
    for termo, desc in legenda(est, calc, perfil):
        out.append(f"- **{termo}:** {desc}")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------- texto puro

def _tabela_txt(cab: List[str], linhas: List[List[str]], direita: Tuple[int, ...] = ()) -> List[str]:
    larg = [len(c) for c in cab]
    for ln in linhas:
        for i, c in enumerate(ln):
            larg[i] = max(larg[i], len(c))

    def fmt(ln: List[str]) -> str:
        return "  ".join(c.rjust(larg[i]) if i in direita else c.ljust(larg[i]) for i, c in enumerate(ln)).rstrip()

    sep = "  ".join("-" * w for w in larg)
    return [fmt(cab), sep] + [fmt(ln) for ln in linhas]


def _quebrar(texto: str, largura: int = 96, recuo: str = "    ") -> List[str]:
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        if atual and len(atual) + 1 + len(p) > largura - len(recuo):
            linhas.append(recuo + atual)
            atual = p
        else:
            atual = f"{atual} {p}" if atual else p
    if atual:
        linhas.append(recuo + atual)
    return linhas


def render_txt(est: Dict[str, Any], calc: Dict[str, Any], perfil: str = "arquivo") -> str:
    p = est["projeto"]
    casas = _casas(calc)
    nesma = calc["unidade"] == "PFM"
    melhoria = est["tipo_projeto"] == "melhoria"
    out: List[str] = []
    titulo = f"ESTIMATIVA DE TAMANHO FUNCIONAL: {_md(p['titulo'])}"
    out += [titulo, "=" * len(titulo), ""]
    out += ["RESUMO EXECUTIVO", ""]
    metodo = "NESMA estimada" if est["metodo"] == "estimada" else "NESMA indicativa"
    pares = [("Tipo de projeto", est["tipo_projeto"])]
    if melhoria:
        pares.append(("Regime de melhoria", est["regime_melhoria"]))
    pares += [("Método", metodo), ("Fronteira da aplicação", _md(p["fronteira"])),
              ("Origem do subsídio", _md(p["origem_subsidio"])), ("Data", _md(p["data"])),
              ("Total", texto_total(calc))]
    pares += linhas_resumo_extra(est, calc)
    for k, v in pares:
        out += _quebrar(f"{k}: {_md(v)}", recuo="  ")
    out += ["", "MEMÓRIA DE CÁLCULO", ""]
    funcoes = {f["id"]: f for f in est["funcoes"]}
    if nesma:
        cab = ["ID", "Função identificada", "Tipo", "Op.", "Complex.", "PF base", "Fator", "PFM", "Base"]
        direita = (5, 6, 7)
    else:
        cab = ["ID", "Função identificada", "Tipo", "Op.", "Complex.", "PF", "Base"]
        direita = (5,)
    linhas = []
    for ln in calc["linhas"]:
        f = funcoes[ln["id"]]
        nome = _md(f["nome"])
        nome = nome if len(nome) <= 48 else nome[:47] + "…"
        linha = [ln["id"], nome, ln["tipo"], ln["operacao"] or "—", ln["complexidade"], num(ln["peso"])]
        if nesma:
            linha += [_faixa(ln["fator_min"], ln["fator_max"], 2), _faixa(ln["valor_min"], ln["valor_max"], 2)]
        linha += [ln["hipotese"] or "evidência"]
        linhas.append(linha)
    total = ["", "TOTAL"] + [""] * (len(cab) - 2)
    total[7 if nesma else 5] = _faixa(calc["total_min"], calc["total_max"], casas)
    linhas.append(total)
    out += _tabela_txt(cab, linhas, direita)
    out += ["", "DETALHAMENTO POR FUNÇÃO", ""]
    for ln in calc["linhas"]:
        f = funcoes[ln["id"]]
        out.append(f"{ln['id']}  {_md(f['nome'])}")
        out += _quebrar("Requisito / história: " + _md(f["requisito"]))
        just = _md(f["justificativa"])
        if nesma and ln["origem_fator"] == "faixa":
            just += " Faixa de fator: " + _md(f["efpa"]["faixa"]["justificativa"])
        out += _quebrar("Justificativa técnica: " + just)
    hipoteses = est.get("hipoteses", [])
    if hipoteses:
        out += ["", "HIPÓTESES E CENÁRIOS", ""]
        for h in hipoteses:
            ef = calc["efeito_hipoteses"][h["id"]]
            grupo = f" [alternativas: {_md(h['grupo'])}]" if h.get("grupo") else ""
            if h.get("requer"):
                grupo += f" [exige: {', '.join(h['requer'])}]"
            out += _quebrar(f"{h['id']}{grupo} (+{_faixa(ef['min'], ef['max'], casas)} {calc['unidade']}): {_md(h['descricao'])}", recuo="  ")
            if h.get("trecho"):
                out += _quebrar(f"Trecho: {_md(h['trecho'])}", recuo="      ")
        out.append("")
        out.append(f"  Cenário mínimo: {num(calc['total_min'], casas)} {calc['unidade']} (hipóteses: {', '.join(calc['hipoteses_cenario_min']) or 'nenhuma'})")
        out.append(f"  Cenário máximo: {num(calc['total_max'], casas)} {calc['unidade']} (hipóteses: {', '.join(calc['hipoteses_cenario_max']) or 'nenhuma'})")

    def secao(titulo: str, itens: List[Dict[str, Any]]) -> None:
        out.extend(["", titulo, ""])
        if not itens:
            out.append("  Nenhuma.")
        for item in itens:
            out.extend(_quebrar(f"{item['id']}. {_md(item['descricao'])}", recuo="  "))

    secao("PREMISSAS ASSUMIDAS", est.get("premissas", []))
    out += ["", "ITENS NÃO CONTADOS", ""]
    nao = est.get("nao_contados", [])
    if not nao:
        out.append("  Nenhum.")
    for item in nao:
        out += _quebrar(f"- {_md(item['item'])} ({CATEGORIAS_NAO_CONTADOS[item['categoria']]}): {_md(_just_nc(item))}", recuo="  ")
    secao("DÚVIDAS DE REQUISITO E PENDÊNCIAS", est.get("pendencias", []))
    out += ["", "LEGENDA", ""]
    for termo, desc in legenda(est, calc, perfil):
        out += _quebrar(f"{termo}: {desc}", recuo="  ")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------- xlsx (SpreadsheetML mínimo)

_XML_INVALIDO = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _esc(s: str) -> str:
    s = _XML_INVALIDO.sub("", s)[:32767]
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _col(n: int) -> str:
    letras = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        letras = chr(65 + r) + letras
    return letras


# Estilos: 0 padrão; 1 cabeçalho; 2 texto com quebra; 3 número 0,00; 4 negrito; 5 negrito 0,00; 6 número inteiro
_STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="1"><numFmt numFmtId="164" formatCode="0.00"/></numFmts>
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFD9E1F2"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="7">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top"/></xf>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment vertical="top"/></xf>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="164" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1" applyNumberFormat="1" applyAlignment="1"><alignment vertical="top"/></xf>
<xf numFmtId="1" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment vertical="top"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


class _Planilha:
    def __init__(self, nome: str, larguras: List[float], congelar: bool = True):
        self.nome = nome[:31]
        self.larguras = larguras
        self.congelar = congelar
        self.linhas: List[List[Optional[Tuple[str, Any, int]]]] = []

    def add(self, celulas: List[Optional[Tuple[str, Any, int]]]) -> int:
        self.linhas.append(celulas)
        return len(self.linhas)  # número da linha (1-based)

    def xml(self) -> str:
        partes = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                  '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
        if self.congelar:
            partes.append('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')
        else:
            partes.append('<sheetViews><sheetView workbookViewId="0"/></sheetViews>')
        partes.append("<cols>" + "".join(
            f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(self.larguras)) + "</cols>")
        partes.append("<sheetData>")
        for r, celulas in enumerate(self.linhas, start=1):
            partes.append(f'<row r="{r}">')
            for c, cel in enumerate(celulas):
                if cel is None:
                    continue
                tipo, valor, estilo = cel
                ref = f"{_col(c)}{r}"
                if tipo == "s":
                    partes.append(f'<c r="{ref}" t="inlineStr" s="{estilo}"><is><t xml:space="preserve">{_esc(str(valor))}</t></is></c>')
                elif tipo == "n":
                    partes.append(f'<c r="{ref}" s="{estilo}"><v>{valor}</v></c>')
                elif tipo == "f":
                    formula, cache = valor
                    partes.append(f'<c r="{ref}" s="{estilo}"><f>{_esc(formula)}</f><v>{cache}</v></c>')
            partes.append("</row>")
        partes.append("</sheetData></worksheet>")
        return "".join(partes)


def _s(v: Any, estilo: int = 2) -> Tuple[str, Any, int]:
    return ("s", "" if v is None else str(v), estilo)


def _n(v: Decimal, estilo: int = 3) -> Tuple[str, Any, int]:
    return ("n", format(v, "f"), estilo)


def _f(formula: str, cache: Decimal, estilo: int = 5) -> Tuple[str, Any, int]:
    return ("f", (formula, format(cache, "f")), estilo)


def gerar_xlsx(est: Dict[str, Any], calc: Dict[str, Any]) -> bytes:
    p = est["projeto"]
    nesma = calc["unidade"] == "PFM"
    melhoria = est["tipo_projeto"] == "melhoria"
    u = calc["unidade"]
    funcoes = {f["id"]: f for f in est["funcoes"]}

    # --- Memória de cálculo
    mem = _Planilha("Memória de cálculo", [7, 40, 32, 7, 10, 13, 9, 10, 10, 12, 12, 11, 10, 10, 60])
    cab = ["ID", "Requisito / História", "Função identificada", "Tipo", "Operação (I/A/E)", "Complexidade",
           "PF base", "Fator mín.", "Fator máx.", f"{u} mín.", f"{u} máx.", "Base", "Entra no mínimo (1/0)",
           "Entra no máximo (1/0)", "Justificativa técnica"]
    mem.add([_s(c, 1) for c in cab])
    primeira = 2
    for ln in calc["linhas"]:
        f = funcoes[ln["id"]]
        just = f["justificativa"]
        if nesma and ln["origem_fator"] == "faixa":
            just += " Faixa de fator: " + f["efpa"]["faixa"]["justificativa"]
        mem.add([_s(ln["id"], 0), _s(f["requisito"]), _s(f["nome"]), _s(ln["tipo"], 0), _s(ln["operacao"] or "—", 0),
                 _s(ln["complexidade"], 0), _n(ln["peso"], 6), _n(ln["fator_min"]), _n(ln["fator_max"]),
                 _n(ln["valor_min"]), _n(ln["valor_max"]), _s(ln["hipotese"] or "evidência", 0),
                 _n(Decimal(int(ln["entra_min"])), 6), _n(Decimal(int(ln["entra_max"])), 6), _s(just)])
    ultima = primeira + len(calc["linhas"]) - 1
    faixa_min, faixa_max = f"J{primeira}:J{ultima}", f"K{primeira}:K{ultima}"
    ent_min, ent_max = f"M{primeira}:M{ultima}", f"N{primeira}:N{ultima}"
    mem.add([])
    vazio = not calc["linhas"]
    r_min = mem.add([None, _s("Total — cenário mínimo" if calc["total"] is None else "Total", 4)] + [None] * 7 +
                    [_f("0" if vazio else f"SUMPRODUCT({faixa_min},{ent_min})", calc["total_min"])])
    r_max = r_min
    if calc["total"] is None:
        r_max = mem.add([None, _s("Total — cenário máximo", 4)] + [None] * 8 +
                        [_f("0" if vazio else f"SUMPRODUCT({faixa_max},{ent_max})", calc["total_max"])])

    ref_mem = "'Memória de cálculo'!"
    # --- Resumo
    res = _Planilha("Resumo", [28, 90], congelar=False)
    res.add([_s("Estimativa de tamanho funcional", 4), _s(p["titulo"], 4)])
    res.add([])
    metodo = "NESMA estimada" if est["metodo"] == "estimada" else "NESMA indicativa"
    pares = [("Tipo de projeto", est["tipo_projeto"])]
    if melhoria:
        pares.append(("Regime de melhoria", est["regime_melhoria"]))
    pares += [("Método", metodo), ("Fronteira da aplicação", p["fronteira"]), ("Origem do subsídio", p["origem_subsidio"]),
              ("Data", p["data"]), ("Unidade", u)]
    for k, v in pares:
        res.add([_s(k, 4), _s(v)])
    if calc["total"] is not None:
        res.add([_s("Total", 4), _f(f"{ref_mem}J{r_min}", calc["total"])])
    else:
        res.add([_s("Total — cenário mínimo", 4), _f(f"{ref_mem}J{r_min}", calc["total_min"])])
        res.add([_s("Total — cenário máximo", 4), _f(f"{ref_mem}K{r_max}", calc["total_max"])])
        res.add([_s("Observação", 4), _s("Cenários mínimo e máximo; sem valor central.")])
    for k, v in linhas_resumo_extra(est, calc):
        res.add([_s(k, 4), _s(v)])

    planilhas = [res, mem]

    # --- Hipóteses e cenários
    hipoteses = est.get("hipoteses", [])
    if hipoteses:
        hp = _Planilha("Hipóteses e cenários", [7, 60, 40, 18, 12, 12, 12])
        hp.add([_s(c, 1) for c in ("ID", "Hipótese", "Trecho do pedido", "Alternativas (grupo)", "Exige", f"Efeito mín. ({u})", f"Efeito máx. ({u})")])
        for h in hipoteses:
            ef = calc["efeito_hipoteses"][h["id"]]
            hp.add([_s(h["id"], 0), _s(h["descricao"]), _s(h.get("trecho") or "—"), _s(h.get("grupo") or "—"),
                    _s(", ".join(h.get("requer") or []) or "—", 0), _n(ef["min"]), _n(ef["max"])])
        hp.add([])
        hp.add([_s("Cenário mínimo", 4), _s("Hipóteses: " + (", ".join(calc["hipoteses_cenario_min"]) or "nenhuma"))])
        hp.add([_s("Cenário máximo", 4), _s("Hipóteses: " + (", ".join(calc["hipoteses_cenario_max"]) or "nenhuma"))])
        planilhas.append(hp)

    # --- Premissas, pendências e itens não contados
    pp = _Planilha("Premissas e pendências", [10, 30, 90])
    pp.add([_s(c, 1) for c in ("ID", "Seção", "Descrição")])
    for item in est.get("premissas", []):
        pp.add([_s(item["id"], 0), _s("Premissa assumida"), _s(item["descricao"])])
    for item in est.get("pendencias", []):
        pp.add([_s(item["id"], 0), _s("Dúvida / pendência"), _s(item["descricao"])])
    for item in est.get("nao_contados", []):
        pp.add([_s("—", 0), _s("Não contado: " + CATEGORIAS_NAO_CONTADOS[item["categoria"]]),
                _s(f"{item['item']}: {_just_nc(item)}")])
    planilhas.append(pp)

    # --- Legenda
    lg = _Planilha("Legenda", [24, 110])
    lg.add([_s("Termo", 1), _s("Significado", 1)])
    for termo, desc in LEGENDA:
        lg.add([_s(termo, 4), _s(desc)])
    planilhas.append(lg)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        tipos = "".join(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for i in range(1, len(planilhas) + 1))
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   + tipos + "</Types>")
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                   "</Relationships>")
        folhas = "".join(f'<sheet name="{_esc(pl.nome)}" sheetId="{i}" r:id="rId{i}"/>' for i, pl in enumerate(planilhas, start=1))
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                   f"<sheets>{folhas}</sheets><calcPr calcId=\"0\" fullCalcOnLoad=\"1\"/></workbook>")
        rels = "".join(
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
            for i in range(1, len(planilhas) + 1))
        n = len(planilhas) + 1
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + rels +
                   f'<Relationship Id="rId{n}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                   "</Relationships>")
        z.writestr("xl/styles.xml", _STYLES)
        for i, pl in enumerate(planilhas, start=1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", pl.xml())
    return buf.getvalue()


# --------------------------------------------------------------------------- CLI

def _para_json(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return format(obj, "f")
    if isinstance(obj, dict):
        return {k: _para_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_para_json(v) for v in obj]
    return obj


def _carregar(caminho: str) -> Any:
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="apf.py", description="Calculadora da skill nesma-apf-estimator")
    sub = ap.add_subparsers(dest="cmd")
    for nome in ("check", "calc"):
        sp = sub.add_parser(nome)
        sp.add_argument("json")
    sp = sub.add_parser("render")
    sp.add_argument("json")
    sp.add_argument("--format", required=True, choices=("md", "txt", "xlsx"))
    sp.add_argument("--out")
    sp.add_argument("--perfil", choices=("chat", "arquivo"),
                    help="padrão: 'chat' (legenda só com os termos usados) ao imprimir; 'arquivo' (legenda completa) com --out")
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help(sys.stderr)
        return 2
    try:
        est = _carregar(args.json)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERRO: não foi possível ler o JSON: {e}", file=sys.stderr)
        return 2
    erros = validar(est)
    if erros:
        print("JSON INVÁLIDO:", file=sys.stderr)
        for e in erros:
            print(f"- {e}", file=sys.stderr)
        return 1
    if args.cmd == "check":
        print("OK")
        return 0
    calc = calcular(est)
    if args.cmd == "calc":
        print(json.dumps(_para_json(calc), ensure_ascii=False, indent=2))
        return 0
    if args.format == "xlsx":
        if not args.out:
            print("ERRO: --out é obrigatório para xlsx", file=sys.stderr)
            return 2
        dados = gerar_xlsx(est, calc)
    else:
        perfil = args.perfil or ("arquivo" if args.out else "chat")
        texto = render_md(est, calc, perfil) if args.format == "md" else render_txt(est, calc, perfil)
        if not args.out:
            sys.stdout.write(texto)
            return 0
        dados = texto.encode("utf-8")
    # Criação exclusiva: nunca sobrescreve um arquivo existente.
    try:
        with open(args.out, "xb") as fh:
            fh.write(dados)
    except FileExistsError:
        print(f"ERRO: o arquivo já existe e não foi alterado: {args.out}. Escolha outro nome.", file=sys.stderr)
        return 3
    except OSError as e:
        print(f"ERRO: não foi possível gravar {args.out}: {e}", file=sys.stderr)
        return 2
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
