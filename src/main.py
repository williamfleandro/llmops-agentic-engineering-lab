import asyncio
import subprocess
import sys
from pathlib import Path
import difflib
from datetime import datetime
from agents import Agent, Runner, function_tool


PROJECT_ROOT = Path(__file__).resolve().parents[1]

IGNORED_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
}

ALLOWED_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
}


def safe_project_path(relative_path: str) -> Path:
    target = (PROJECT_ROOT / relative_path).resolve()

    try:
        target.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError("Access outside the project directory is not allowed.")

    return target


@function_tool
def list_project_files() -> str:
    """List files available in the current project."""

    files: list[str] = []

    for path in PROJECT_ROOT.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        if path.is_file():
            files.append(str(path.relative_to(PROJECT_ROOT)))

    if not files:
        return "No files found."

    return "\n".join(sorted(files))


@function_tool
def read_text_file(relative_path: str) -> str:
    """Read a text file from the project using a relative path."""

    path = safe_project_path(relative_path)

    if not path.exists():
        return f"File not found: {relative_path}"

    if not path.is_file():
        return f"Path is not a file: {relative_path}"

    if path.suffix not in ALLOWED_SUFFIXES:
        return f"File type not allowed: {path.suffix}"

    return path.read_text(encoding="utf-8")


@function_tool
def run_pytest() -> str:
    """Run pytest in the project and return stdout, stderr and exit code."""

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )

    return (
        f"exit_code: {completed.returncode}\n\n"
        f"stdout:\n{completed.stdout}\n\n"
        f"stderr:\n{completed.stderr}"
    )

@function_tool
def write_text_file(relative_path: str, content: str) -> str:
    """Write text content to a safe project file under src/ or tests/ only and return a unified diff."""

    path = safe_project_path(relative_path)

    allowed_roots = [
        (PROJECT_ROOT / "src").resolve(),
        (PROJECT_ROOT / "tests").resolve(),
    ]

    if not any(path.is_relative_to(root) for root in allowed_roots):
        return "Write denied. Only files under src/ and tests/ can be modified."

    if path.suffix not in ALLOWED_SUFFIXES:
        return f"Write denied. File type not allowed: {path.suffix}"

    old_content = ""

    if path.exists():
        old_content = path.read_text(encoding="utf-8")

        backup_dir = PROJECT_ROOT / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = relative_path.replace("/", "_").replace("\\", "_")
        backup_path = backup_dir / f"{safe_name}.{timestamp}.bak"

        backup_path.write_text(old_content, encoding="utf-8")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    diff = difflib.unified_diff(
        old_content.splitlines(),
        content.splitlines(),
        fromfile=f"{relative_path} before",
        tofile=f"{relative_path} after",
        lineterm="",
    )

    diff_text = "\n".join(diff)

    if not diff_text:
        diff_text = "No textual differences detected."

    return (
        f"File written successfully: {relative_path}\n\n"
        f"Backup directory: backups/\n\n"
        f"Unified diff:\n{diff_text}"
    )

agent = Agent(
    name="Agentic Engineering Lab Assistant",
    instructions="""
Você é um assistente técnico especializado em Agentic Engineering.

Sua missão é analisar e evoluir este projeto Python usando ferramentas controladas.

Regras obrigatórias:
1. Sempre leia AGENTS.md antes de analisar o projeto.
2. Use list_project_files antes de ler arquivos específicos.
3. Nunca invente conteúdo de arquivos.
4. Não diga que executou testes sem chamar run_pytest.
5. Você pode escrever arquivos apenas em src/ e tests/.
6. Depois de qualquer escrita, execute run_pytest.
7. Nunca altere AGENTS.md, requirements.txt, .env, apikeys ou arquivos fora de src/ e tests/.
8. Antes de modificar um arquivo, leia o conteúdo atual dele.
9. Produza uma resposta objetiva e verificável.
10. Quando write_text_file retornar um Unified diff, incluir o diff na resposta ou resumir claramente as linhas alteradas.
11. Nunca sugerir refatorar arquivos .bak; eles são apenas backups.

Formato obrigatório da resposta:
- Diagnóstico
- Evidências encontradas
- Alterações realizadas
- Resultado dos testes
- Riscos
- Próximo passo recomendado
""",
    tools=[
        list_project_files,
        read_text_file,
        run_pytest,
        write_text_file
    ],
)

async def main() -> None:
    task = " ".join(sys.argv[1:]).strip()

    if not task:
        task = input("Digite a tarefa para o agente: ")

    result = await Runner.run(agent, task)

    print("\n=== RESPOSTA DO AGENTE ===\n")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())