from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path

ALLOWED_STAGES = {
    "architecture",
    "code",
    "test",
    "review",
    "docs",
    "orchestrator",
}

MAX_FIELD_LENGTH = 20000


@dataclass(frozen=True)
class DocumentationRecord:
    stage: str
    task: str
    content: str


def save_documentation_report(stage: str, task: str, content: str) -> str:
    """Persist an agent execution report using a deterministic documentation harness."""

    safe_record = DocumentationRecord(
        stage=_normalize_stage(stage),
        task=_normalize_text(task),
        content=_normalize_text(content),
    )

    docs_dir = Path("docs")
    executions_dir = docs_dir / "executions"

    docs_dir.mkdir(exist_ok=True)
    executions_dir.mkdir(exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    filename_timestamp = now.strftime("%Y-%m-%d_%H-%M-%S_%f")

    execution_id = _build_execution_id(
        timestamp=timestamp,
        stage=safe_record.stage,
        task=safe_record.task,
        content=safe_record.content,
    )

    execution_file = executions_dir / (
        f"{filename_timestamp}_{safe_record.stage}_{execution_id}.md"
    )

    latest_file = docs_dir / "results.md"
    index_file = docs_dir / "execution-log.md"

    markdown = _build_report_markdown(
        record=safe_record,
        timestamp=timestamp,
        execution_id=execution_id,
    )

    execution_file.write_text(markdown, encoding="utf-8")
    latest_file.write_text(markdown, encoding="utf-8")
    _append_execution_index(
        index_file=index_file,
        timestamp=timestamp,
        stage=safe_record.stage,
        execution_id=execution_id,
        execution_file=execution_file,
    )

    return (
        "Documentation harness saved the execution report in "
        f"{execution_file.as_posix()}, updated docs/execution-log.md, "
        "and refreshed docs/results.md."
    )


def _normalize_stage(stage: str) -> str:
    normalized = stage.strip().lower().replace(" ", "-")

    if normalized in ALLOWED_STAGES:
        return normalized

    return "orchestrator"


def _normalize_text(value: str) -> str:
    text = value.strip()

    if len(text) <= MAX_FIELD_LENGTH:
        return text

    return (
        text[:MAX_FIELD_LENGTH]
        + "\n\n...[truncated by documentation harness due to size limit]"
    )


def _build_execution_id(
    timestamp: str,
    stage: str,
    task: str,
    content: str,
) -> str:
    raw_value = f"{timestamp}|{stage}|{task}|{content}"
    return sha256(raw_value.encode("utf-8")).hexdigest()[:12]


def _build_report_markdown(
    record: DocumentationRecord,
    timestamp: str,
    execution_id: str,
) -> str:
    return f"""# Multiagent Execution Report

## Metadata

- Timestamp: `{timestamp}`
- Stage: `{record.stage}`
- Execution ID: `{execution_id}`

## Task

```text
{record.task}
```

## Result

{record.content}
"""


def _append_execution_index(
    index_file: Path,
    timestamp: str,
    stage: str,
    execution_id: str,
    execution_file: Path,
) -> None:
    if not index_file.exists():
        index_file.write_text(
            "# Multiagent Execution Log\n\n"
            "Histórico incremental das execuções do sistema multiagent.\n\n",
            encoding="utf-8",
        )

    relative_path = execution_file.relative_to(index_file.parent).as_posix()
    index_entry = (
        f"- `{timestamp}` | `{stage}` | `{execution_id}` | "
        f"[execution report]({relative_path})\n"
    )

    with index_file.open("a", encoding="utf-8") as file:
        file.write(index_entry)
