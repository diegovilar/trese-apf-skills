"""Tudo o que determina o que o JUIZ recebe: instruções, dossiê, CLI e modelo.
Entra no hash do juiz (com calibração, schema e gabaritos); cada julgamento registra também o hash do dossiê."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import casos as C

AQUI = Path(__file__).resolve().parent
GABARITOS = AQUI.parent / "gabaritos-iniciais.md"
BASE_WS = Path("/tmp/apf-evals")

CONFIG = {
    "cmd": "codex",
    "modelo": "gpt-6.1-sol",
    "esforco": "high",
    "timeout_s": 900,
}

PROMPT_SONDA = "Responda apenas com a palavra OK. Não use ferramentas."


INSTRUCOES_JUIZ = """Você é o juiz de uma avaliação. Um agente executou a skill `trese-apf-aproximacao` (estimativa de pontos de função NESMA) sobre o subsídio abaixo. Avalie o resultado dele contra o gabarito aprovado e as convenções. Não use ferramentas, não leia arquivos e não execute comandos: tudo o que você precisa está neste texto.

Critérios (responda um booleano para cada, com justificativa curta e uma citação literal do JSON ou da resposta que sustente o veredito; se não houver o que citar, use ""):
- K3: nenhuma função listada como PROIBIDA no gabarito foi contada (em `funcoes`), nem com outro nome.
- S1: as funções obrigatórias do gabarito estão presentes com o tipo correto (e, em melhoria, a operação correta), correspondendo NOME A NOME e PELO SIGNIFICADO, não só pela contagem de tipos. Uma função trocada por outra do mesmo tipo reprova. Nos casos avaliados por rubrica, aplique a rubrica do gabarito.
- S3: hipóteses e cenários coerentes: toda hipótese que muda o total está registrada com o efeito; alternativas que se excluem estão no mesmo grupo; nenhum cenário (mínimo ou máximo) descreve uma aplicação impossível, como contar a mesma entidade como ALI e AIE ao mesmo tempo, ou um arquivo sem processo que o mantenha ou leia. Se não houver hipóteses e o gabarito não exigir, aprove.
- S4: todas as pendências obrigatórias do gabarito aparecem (com estas ou outras palavras) em `pendencias`. Avalie pelo significado no contexto, sem exigir palavras específicas. Menção genérica ou ambígua que não estabeleça o aspecto exigido não basta. Todas as pendências obrigatórias devem aparecer, e nenhuma pendência proibida pelo gabarito (contraste) deve aparecer; na justificativa, separe ausências de perguntas indevidas. Sem obrigatórias nem proibidas no gabarito, aprove.
- S5: rastreabilidade: o campo `requisito` de cada função cita ou parafraseia fielmente um trecho que EXISTE no subsídio, ou a função está ligada a uma hipótese cujo trecho existe. Compare com o subsídio original; trecho inventado ou distorcido reprova.
Em `observacoes`, registre qualquer outro problema relevante que você notar (não afeta os critérios).
"""


INSTRUCOES_JUIZ_PREVIA = """Você é o juiz de uma avaliação. Um agente executou a skill `trese-apf-aproximacao` (estimativa de pontos de função NESMA) no modo interativo sobre o subsídio abaixo. Nesse modo, a execução termina numa PRÉVIA: a lista de funcionalidades detectadas, sem pontos de função, e as lacunas registradas como pendências, algumas com pergunta ao analista (campo `pergunta`), apresentadas em lotes. Avalie o JSON da prévia e a resposta contra o gabarito aprovado e as convenções. Não use ferramentas, não leia arquivos e não execute comandos: tudo o que você precisa está neste texto.

Critérios (responda um booleano para cada, com justificativa curta e uma citação literal do JSON ou da resposta que sustente o veredito; se não houver o que citar, use ""):
- K3: nenhuma função listada como PROIBIDA no gabarito foi contada (em `funcoes`), nem com outro nome.
- S1: as funções obrigatórias do gabarito estão presentes com o tipo correto, correspondendo NOME A NOME e PELO SIGNIFICADO, não só pela contagem de tipos. Aplique a rubrica do gabarito, inclusive as decomposições alternativas que ela aceita.
- S3: o modelo por trás da prévia é coerente: toda hipótese que mudaria o total está registrada e ligada às funções; alternativas que se excluem estão no mesmo grupo; nenhuma combinação descreve uma aplicação impossível (a mesma entidade como ALI e AIE ao mesmo tempo, um arquivo sem processo que o mantenha ou leia). A prévia NÃO mostra PF nem cenários: não exija efeitos numéricos nem totais na resposta. Agrupamentos ou separações que o gabarito diz não serem obrigatórios não reprovam se ausentes. Avalie equivalência semântica, não identidade de representação. Quando uma alternativa apenas incorpora uma atividade numa função já obrigatória, sem função adicional nem restrições próprias, é aceitável representar somente a alternativa adicional por hipótese opcional sem grupo. Isso satisfaz a exigência de alternativas do gabarito se preservar os mesmos cenários válidos e dependências. Não aceite omitir a atividade obrigatória nem eliminar restrições.
- S4 (só ausências): toda pendência obrigatória do gabarito aparece em `pendencias` COM `pergunta`, em qualquer situação (`aberta`, `perguntada`, `sem-resposta`) e em qualquer lote. A pergunta precisa de fato pedir o esclarecimento exigido; "pode esclarecer?" sem identificar a lacuna não basta. Avalie pelo significado, sem exigir palavras específicas; uma pergunta aberta que identifique a lacuna basta. Obrigatória só numa justificativa, em `nao_contados` ou numa pendência sem `pergunta` reprova. As pendências de diagnóstico do gabarito não reprovam se ausentes. Perguntas indevidas não são avaliadas aqui (são do critério R).
- S4_antigo: só quando a nota da variante pedir; senão, responda null. Quando pedida, aplique a lista de pendências obrigatórias do gabarito original indicada na nota, pela regra da iteração 1: cada uma presente em `pendencias`, com ou sem `pergunta`, avaliada pelo significado. Não afeta a aprovação.
- S5: rastreabilidade: o campo `requisito` de cada função cita ou parafraseia fielmente um trecho que EXISTE no subsídio, ou a função está ligada a uma hipótese cujo trecho existe. Trecho inventado ou distorcido reprova.
- R (perguntas e pendências indevidas): reprova se houver ao menos uma pendência (com ou sem `pergunta`) REDUNDANTE ou PROIBIDA pelo gabarito. Redundante é a que pede ao analista que confirme ou repita algo que o subsídio afirma, ou que escolha entre alternativas das quais o texto já escolheu uma. NÃO é redundante: citar o que o texto afirma como contexto para perguntar um aspecto não respondido; perguntar um detalhe não descrito de uma etapa descrita, quando ele muda a contagem; duas perguntas complementares (que pedem informações diferentes, ex.: como a pessoa é identificada e de onde vêm os dados dela). Duas pendências são redundantes entre si só se pedem a mesma informação. Numa pergunta mista, avalie só o trecho que efetivamente pede resposta: se a parte já respondida pelo texto é só contexto, não reprova; se o analista teria de responder de novo o que o texto já diz, reprova. Na justificativa, dê os IDs e os trechos de cada ocorrência.

Em `medidas` (relatadas, não reprovam): `n_perguntas` = número de pendências com `pergunta`; `genericas` = IDs das perguntas sem ligação com o processo descrito (ex.: "há outras integrações?", "há relatórios?" sem âncora no texto; uma pergunta aberta sobre uma etapa relevante NÃO é genérica); `nao_mudam_contagem` = IDs das perguntas cuja resposta não mudaria funções, tipos, hipóteses, cenários ou cobertura (campos, telas, layout); `redundantes` = IDs das redundantes ou proibidas (as mesmas do R); `diagnostico_presentes` = quais pendências de diagnóstico do gabarito apareceram, com o ID correspondente. Use listas vazias quando não houver.
Em `observacoes`, registre qualquer outro problema relevante que você notar (não afeta os critérios).
"""

INSTRUCOES_DIALOGO = """Esta execução é um DIÁLOGO do modo interativo (camada 2): o agente mostrou uma prévia, o analista respondeu com as mensagens transcritas abaixo e o agente calculou. Avalie o resultado final pelos critérios acima, com estas regras:
- A fonte da verdade é o subsídio original MAIS as mensagens do analista. O gabarito indicado já descreve esse conjunto. Para S5, um trecho que exista no subsídio ou numa mensagem do analista é válido; os esclarecimentos (`esclarecimentos`) devem refletir fielmente o que o analista escreveu.
- Pendências com `situacao: "resolvida"` são histórico do diálogo (o que foi perguntado e respondido), não dúvidas abertas: não as conte como pendências proibidas do gabarito.
- Qualquer outra pendência (sem situação, `aberta`, `perguntada` ou `sem-resposta`) que peça de novo, no todo ou em parte, o que o analista respondeu é pendência proibida e reprova S4. Uma pendência `sem-resposta` sobre algo que o analista disse não saber é legítima.
- Em S4, as pendências obrigatórias são as do gabarito indicado (depois das respostas); as que o analista respondeu não são exigidas.
"""

CRITERIOS = ("K3", "S1", "S3", "S4", "S5")
CRITERIOS_PREVIA = CRITERIOS + ("R",)


def e_previa(caso_id: str) -> bool:
    return bool(C.CASOS[caso_id].get("previa"))


def secao_gabarito(nome: str) -> str:
    texto = GABARITOS.read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(nome)} ·.*?(?=^## |\Z)", texto, re.S | re.M)
    return m.group(0).strip() if m else ""


def secao_convencoes() -> str:
    texto = GABARITOS.read_text(encoding="utf-8")
    m = re.search(r"^## Convenções usadas nos gabaritos.*?(?=^## )", texto, re.S | re.M)
    return m.group(0).strip() if m else ""


def montar_dossie(caso_id: str, invocacao: str, subsidio: str, est: Dict[str, Any], resposta: str, nota: str = "") -> str:
    c = C.CASOS[caso_id]
    previa = e_previa(caso_id)
    partes = [INSTRUCOES_JUIZ_PREVIA if previa else INSTRUCOES_JUIZ,
              "## Invocação exata\n\n" + invocacao,
              "## Subsídio completo (fonte da verdade para S5)\n\n" + subsidio,
              "## Gabarito do caso\n\n" + secao_gabarito(c.get("secao", caso_id))]
    if nota:
        partes.append("## Nota sobre esta variante\n\n" + nota)
    rotulo_json = "JSON da prévia produzido pelo agente" if previa else "JSON canônico produzido pelo agente"
    rotulo_resp = "Resposta do agente (a prévia mostrada ao analista)" if previa else "Resposta final do agente"
    partes += ["## Convenções\n\n" + secao_convencoes(),
               f"## {rotulo_json}\n\n```json\n" + json.dumps(est, ensure_ascii=False, indent=2) + "\n```",
               f"## {rotulo_resp}\n\n" + resposta]
    return "\n\n".join(partes)


def montar_dossie_dialogo(invocacao: str, subsidio: str, mensagens: list, secao: str, est: Dict[str, Any],
                          resposta: str, nota: str = "") -> str:
    """Dossiê do juiz final para um turno de diálogo (camada 2): fonte = subsídio + mensagens reais do analista."""
    conversa = "\n\n".join(f"**Mensagem {i} do analista:**\n\n> {m}" for i, m in enumerate(mensagens, start=1))
    partes = [INSTRUCOES_JUIZ, INSTRUCOES_DIALOGO,
              "## Invocação exata (primeiro turno)\n\n" + invocacao,
              "## Subsídio original (fonte da verdade para S5, com as mensagens do analista)\n\n" + subsidio,
              "## Mensagens do analista depois da prévia, na ordem\n\n" + conversa,
              "## Gabarito aplicável ao resultado final\n\n" + secao_gabarito(secao)]
    if nota:
        partes.append("## Nota sobre este diálogo\n\n" + nota)
    partes += ["## Convenções\n\n" + secao_convencoes(),
               "## JSON canônico produzido pelo agente no último turno\n\n```json\n" + json.dumps(est, ensure_ascii=False, indent=2) + "\n```",
               "## Resposta do agente no último turno\n\n" + resposta]
    return "\n\n".join(partes)


def schema_de(caso_id: Optional[str]) -> Path:
    if caso_id and e_previa(caso_id):
        return AQUI / "veredito-previa.schema.json"
    return AQUI / "veredito.schema.json"


def rodar_codex(prompt: str, saida: Path, com_schema: bool = True, schema: Optional[Path] = None) -> Dict[str, Any]:
    cfg = CONFIG
    vazio = Path(tempfile.mkdtemp(prefix="juiz-", dir=BASE_WS if BASE_WS.exists() else None))
    ultimo = saida / "veredito_bruto.txt"
    cmd = [cfg["cmd"], "exec", "-m", cfg["modelo"], "-c", f'model_reasoning_effort="{cfg["esforco"]}"',
           "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "--json",
           "-C", str(vazio), "-o", str(ultimo)]
    if com_schema:
        cmd += ["--output-schema", str(schema or AQUI / "veredito.schema.json")]
    cmd.append("-")
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=cfg["timeout_s"])
        codigo, stdout, stderr = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        codigo, stdout, stderr = "timeout", "", "timeout"
    (saida / "juiz_trace.jsonl").write_text(stdout or "", encoding="utf-8")
    (saida / "juiz_stderr.txt").write_text(stderr or "", encoding="utf-8")
    (saida / "juiz_dossie.md").write_text(prompt, encoding="utf-8")
    acoes = []
    for linha in (stdout or "").splitlines():
        try:
            ev = json.loads(linha)
        except json.JSONDecodeError:
            continue
        item = ev.get("item") or {}
        if item.get("type") in ("command_execution", "file_change", "mcp_tool_call", "web_search"):
            acoes.append(item.get("type"))
    texto = ultimo.read_text(encoding="utf-8") if ultimo.exists() else ""
    return {"codigo": codigo, "texto": texto, "acoes": acoes, "stderr": (stderr or "")[-2000:]}


def interpretar_veredito(texto: str, previa: bool = False) -> Optional[Dict[str, Any]]:
    """Veredito legível ou None. Na camada 1 (prévia), R e medidas são obrigatórios: sem eles, o julgamento é inválido."""
    v = _interpretar(texto)
    if v is None or not previa:
        return v
    if not (isinstance(v.get("R"), dict) and isinstance(v["R"].get("ok"), bool) and isinstance(v.get("medidas"), dict)):
        return None
    s4a = v.get("S4_antigo")
    if s4a is not None and not (isinstance(s4a, dict) and isinstance(s4a.get("ok"), bool)):
        return None
    return v


def _interpretar(texto: str) -> Optional[Dict[str, Any]]:
    try:
        v = json.loads(texto)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", texto, re.S)
        if not m:
            return None
        try:
            v = json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    if not all(isinstance(v.get(k), dict) and isinstance(v[k].get("ok"), bool) for k in ("K3", "S1", "S3", "S4", "S5")):
        return None
    return v
