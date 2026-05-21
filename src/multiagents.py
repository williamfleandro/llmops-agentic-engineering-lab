import asyncio
import sys
from datetime import datetime
from pathlib import Path

from agents import Agent, Runner, function_tool

try:
    from src.main import (
        list_project_files,
        read_text_file,
        run_pytest,
        run_quality_checks,
        write_text_file,
    )
except ModuleNotFoundError:
    from main import (
        list_project_files,
        read_text_file,
        run_pytest,
        run_quality_checks,
        write_text_file,
    )


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
RESULTS_FILE = DOCS_DIR / "results.md"


def save_results_file(task: str, content: str) -> str:
    """Save multiagent execution results into docs/results.md."""

    DOCS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    markdown = f"""# Multiagent Execution Results

## Timestamp

{timestamp}

## Task

```text
{task}
```

## Result

{content}
"""

    RESULTS_FILE.write_text(markdown, encoding="utf-8")

    return "Execution results saved in docs/results.md."


@function_tool
def save_execution_results(task: str, content: str) -> str:
    """Save multiagent execution results into docs/results.md."""

    return save_results_file(task=task, content=content)


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
4. Escreva somente em src/ e tests/.
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

Sua função é registrar a execução do sistema multiagent em Markdown.

Regras:
1. Documente a tarefa executada.
2. Documente o resultado recebido.
3. Salve o resultado em docs/results.md usando save_execution_results.
4. Não modifique arquivos de código.
5. Não invente resultados.
6. Documente apenas o conteúdo recebido.
""",
    tools=[
        save_execution_results,
    ],
)


orchestrator_agent = Agent(
    name="Multi-Agent Engineering Orchestrator",
    instructions="""
Você é o agente orquestrador de engenharia.

Sua função é coordenar agentes especializados para executar tarefas de
Agentic Engineering neste projeto Python.

Fluxo recomendado:
1. Para análise ou planejamento, chame o Architecture Agent.
2. Para implementação, chame o Code Implementation Agent.
3. Para validação, chame o Test Validation Agent.
4. Para revisão final, chame o Code Review Agent.
5. Para documentação final, chame o Documentation Agent.

Regras obrigatórias:
1. Nunca diga que código foi alterado se o Code Agent não foi chamado.
2. Nunca diga que testes passaram se o Test Agent não foi chamado.
3. Para tarefas de código, use a sequência:
   Architecture Agent → Code Implementation Agent → Test Validation Agent
   → Code Review Agent → Documentation Agent.
4. Se a tarefa for apenas revisão, use Code Review Agent e Documentation Agent.
5. Se a tarefa for apenas validação, use Test Validation Agent e Documentation Agent.
6. Sempre gere documentação final da execução em docs/results.md.
7. Responda sempre com:
   - Diagnóstico
   - Agentes acionados
   - Alterações realizadas
   - Resultado dos quality gates
   - Revisão
   - Documentação gerada
   - Próximo passo recomendado
""",
    tools=[
        architecture_agent.as_tool(
            tool_name="architecture_agent",
            tool_description="Analisa arquitetura, impacto e plano técnico.",
        ),
        code_agent.as_tool(
            tool_name="code_implementation_agent",
            tool_description="Implementa alterações controladas em src/ e tests/.",
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
            tool_description="Documenta a execução em docs/results.md.",
        ),
    ],
)


async def main() -> None:
    task = " ".join(sys.argv[1:]).strip()

    if not task:
        task = input("Digite a tarefa para o sistema multiagent: ")

    try:
        result = await Runner.run(orchestrator_agent, task)
        final_output = result.final_output
    except Exception as error:
        final_output = f"Execution failed with error: {error}"

    print("\n=== RESPOSTA DO SISTEMA MULTIAGENT ===\n")
    print(final_output)

    save_results_file(
        task=task,
        content=final_output,
    )

    print("\nResultado salvo em docs/results.md")


if __name__ == "__main__":
    asyncio.run(main())
