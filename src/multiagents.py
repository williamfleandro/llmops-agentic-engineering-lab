import asyncio
import sys

from agents import Agent, Runner

from documentation_harness import save_documentation_report
from main import (
    list_project_files,
    read_text_file,
    run_pytest,
    run_quality_checks,
    write_text_file,
)

architecture_agent = Agent(
    name="Architecture Agent",
    instructions="""
Você é um agente arquiteto de software.

Sua função é analisar a estrutura do projeto e propor uma estratégia técnica
antes de qualquer alteração.

Regras:
1. Leia AGENTS.md antes de qualquer análise.
2. Use list_project_files antes de ler arquivos específicos.
3. Não modifique arquivos.
4. Foque em arquitetura, impacto, riscos e plano de implementação.
5. Responda de forma objetiva e verificável.
""",
    tools=[
        list_project_files,
        read_text_file,
    ],
)


code_agent = Agent(
    name="Code Implementation Agent",
    instructions="""
Você é um agente implementador de código.

Sua função é alterar arquivos quando a tarefa solicitar implementação.

Regras:
1. Leia AGENTS.md antes de modificar qualquer coisa.
2. Use list_project_files antes de ler arquivos específicos.
3. Leia o arquivo atual antes de modificá-lo.
4. Escreva somente em src/, tests/ e frontend/.
5. Nunca altere .env, apikeys, .venv, arquivos .bak ou backups/.
6. Depois de qualquer alteração relevante, execute run_quality_checks.
7. Informe exatamente quais arquivos foram modificados.
8. Quando write_text_file retornar diff, resuma claramente a alteração.
""",
    tools=[
        list_project_files,
        read_text_file,
        write_text_file,
        run_pytest,
        run_quality_checks,
    ],
)


test_agent = Agent(
    name="Test Validation Agent",
    instructions="""
Você é um agente especializado em testes e quality gates.

Sua função é validar se o projeto está estável.

Regras:
1. Execute run_quality_checks para validação completa.
2. Não diga que os testes passaram sem executar a ferramenta.
3. Se houver falha, explique qual gate falhou.
4. Não modifique arquivos.
5. Retorne resultado objetivo: pytest, compileall e ruff.
""",
    tools=[
        list_project_files,
        read_text_file,
        run_pytest,
        run_quality_checks,
    ],
)


review_agent = Agent(
    name="Code Review Agent",
    instructions="""
Você é um agente revisor de código.

Sua função é revisar mudanças no projeto com foco em qualidade, segurança,
manutenibilidade, clareza e aderência ao AGENTS.md.

Regras:
1. Leia AGENTS.md.
2. Liste os arquivos do projeto.
3. Leia os arquivos relevantes.
4. Não modifique arquivos.
5. Execute run_quality_checks quando a tarefa envolver validação.
6. Aponte riscos reais, não sugestões genéricas.
7. Classifique a revisão como aprovado, aprovado com ressalvas ou reprovado.
""",
    tools=[
        list_project_files,
        read_text_file,
        run_quality_checks,
    ],
)


documentation_agent = Agent(
    name="Documentation Agent",
    instructions="""
Você é um agente de documentação técnica.

Sua função é transformar a execução recebida em uma síntese técnica clara.

Regras:
1. Não escreva arquivos diretamente.
2. Não invente resultados.
3. Documente somente fatos recebidos na tarefa.
4. Organize a saída em diagnóstico, evidências, riscos e próximo passo.
5. O Documentation Harness externo fará a persistência incremental.
""",
)


orchestrator_agent = Agent(
    name="Multi-Agent Engineering Orchestrator",
    instructions="""
Você é o agente orquestrador de engenharia.

Use este agente apenas para tarefas pequenas. Para tarefas grandes,
prefira executar uma etapa por vez usando os modos:
architecture, code, test, review e docs.

Regras obrigatórias:
1. Nunca diga que código foi alterado se o Code Agent não foi chamado.
2. Nunca diga que testes passaram se o Test Agent não foi chamado.
3. A persistência documental é responsabilidade do Documentation Harness.
4. Responda com diagnóstico, agentes acionados, alterações, quality gates,
   revisão, documentação gerada e próximo passo recomendado.
""",
    tools=[
        architecture_agent.as_tool(
            tool_name="architecture_agent",
            tool_description="Analisa arquitetura, impacto e plano técnico.",
        ),
        code_agent.as_tool(
            tool_name="code_implementation_agent",
            tool_description="Implementa alterações controladas.",
        ),
        test_agent.as_tool(
            tool_name="test_validation_agent",
            tool_description="Executa pytest, compileall e ruff.",
        ),
        review_agent.as_tool(
            tool_name="code_review_agent",
            tool_description="Revisa qualidade, riscos e aderência ao AGENTS.md.",
        ),
        documentation_agent.as_tool(
            tool_name="documentation_agent",
            tool_description="Produz síntese técnica para documentação.",
        ),
    ],
)


AGENTS_BY_STAGE: dict[str, Agent] = {
    "architecture": architecture_agent,
    "code": code_agent,
    "test": test_agent,
    "review": review_agent,
    "docs": documentation_agent,
    "orchestrator": orchestrator_agent,
}


def parse_stage_and_task(argv: list[str]) -> tuple[str, str]:
    if not argv:
        task = input("Digite a tarefa para o sistema multiagent: ")
        return "orchestrator", task

    first_argument = argv[0].strip().lower()

    if first_argument in AGENTS_BY_STAGE:
        stage = first_argument
        task = " ".join(argv[1:]).strip()
    else:
        stage = "orchestrator"
        task = " ".join(argv).strip()

    if not task:
        task = input(f"Digite a tarefa para o agente {stage}: ")

    return stage, task


async def run_single_stage(stage: str, task: str) -> str:
    agent = AGENTS_BY_STAGE[stage]
    result = await Runner.run(agent, task)

    return result.final_output


async def main() -> None:
    stage, task = parse_stage_and_task(sys.argv[1:])

    try:
        final_output = await run_single_stage(stage=stage, task=task)
    except Exception as error:
        final_output = f"Execution failed with error: {error}"

    print(f"\n=== RESPOSTA DO AGENTE: {stage.upper()} ===\n")
    print(final_output)

    documentation_result = save_documentation_report(
        stage=stage,
        task=task,
        content=final_output,
    )

    print(f"\n{documentation_result}")


if __name__ == "__main__":
    asyncio.run(main())
