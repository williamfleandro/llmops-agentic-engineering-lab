import type { FormEvent } from "react";
import { useMemo, useState } from "react";
import "./App.css";

type MathSolution = {
  original_expression: string;
  topic: string;
  rule_name: string;
  rule_formula: string;
  identified_terms: Record<string, string>;
  steps: string[];
  development_line: string;
  result: string;
};

type ApiError = {
  detail?: string;
};

const examples = ["(x+5)^2", "(5x+6)(5x-2)", "(x+y)^3", "(x-y)^3"];

function formatDevelopmentLine(developmentLine: string): string[] {
  const parts = developmentLine.split(" = ");

  if (parts.length <= 1) {
    return [developmentLine];
  }

  return [`${parts[0]} =`, ...parts.slice(1).map((part) => `= ${part}`)];
}

function App() {
  const [expression, setExpression] = useState("(x+5)^2");
  const [solution, setSolution] = useState<MathSolution | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const identifiedTerms = useMemo(() => {
    if (!solution) {
      return [];
    }

    return Object.entries(solution.identified_terms);
  }, [solution]);

  const developmentLines = useMemo(() => {
    if (!solution) {
      return [];
    }

    return formatDevelopmentLine(solution.development_line);
  }, [solution]);

  async function solveExpression(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();

    const normalizedExpression = expression.trim();

    if (!normalizedExpression) {
      setError("Digite uma expressão matemática antes de resolver.");
      setSolution(null);
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/api/v1/math/solve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          expression: normalizedExpression,
        }),
      });

      const payload = (await response.json()) as MathSolution | ApiError;

      if (!response.ok) {
        const detail =
          "detail" in payload && payload.detail
            ? payload.detail
            : "Não foi possível resolver a expressão.";
        throw new Error(detail);
      }

      setSolution(payload as MathSolution);
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "Erro inesperado ao chamar a API.";
      setError(message);
      setSolution(null);
    } finally {
      setIsLoading(false);
    }
  }

  function selectExample(example: string) {
    setExpression(example);
    setError("");
  }

  return (
    <main className="page-shell">
      <section className="hero-panel">
        <div className="project-label">
          <span />
          LLMOps Agentic Engineering Lab
          <span />
        </div>

        <h1>Resolvedor de Produtos Notáveis</h1>

        <p className="hero-subtitle">
          Digite uma expressão algébrica e veja a regra, o desenvolvimento e o
          resultado explicados passo a passo.
        </p>

        <form className="solver-form" onSubmit={solveExpression}>
          <label htmlFor="expression">Expressão matemática</label>

          <div className="input-action-row">
            <input
              id="expression"
              value={expression}
              onChange={(event) => setExpression(event.target.value)}
              placeholder="Exemplo: (x+5)^2"
              autoComplete="off"
            />

            <button type="submit" disabled={isLoading}>
              {isLoading ? "Resolvendo..." : "Resolver"}
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </form>

        <div className="examples-row">
          <strong>Exemplos:</strong>

          {examples.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => selectExample(example)}
            >
              {example}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <section className="result-panel error-panel">
          <div className="section-title-row">
            <div className="section-icon">!</div>
            <h2>Não foi possível resolver</h2>
          </div>
          <p>{error}</p>
        </section>
      )}

      {solution && (
        <section className="result-panel">
          <div className="result-topline">
            <div className="section-title-row">
              <div className="section-icon">↗</div>
              <p>Resultado</p>
            </div>

            <span className="topic-pill">{solution.topic}</span>
          </div>

          <h2 className="result-expression">{solution.result}</h2>

          <div className="info-grid">
            <article className="info-card">
              <div className="info-icon">□</div>
              <div>
                <h3>Regra utilizada</h3>
                <p>{solution.rule_name}</p>
                <code>{solution.rule_formula}</code>
              </div>
            </article>

            <article className="info-card">
              <div className="info-icon">⌕</div>
              <div>
                <h3>Termos identificados</h3>
                <ul className="terms-list">
                  {identifiedTerms.map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}:</strong> {value}
                    </li>
                  ))}
                </ul>
              </div>
            </article>
          </div>

          <article className="wide-card development-card">
            <div className="info-icon">▦</div>
            <div className="development-content">
              <h3>Desenvolvimento</h3>
              <div className="development-line">
                {developmentLines.map((line) => (
                  <p key={line}>{line}</p>
                ))}
              </div>
            </div>
          </article>

          <article className="wide-card">
            <div className="info-icon">≡</div>
            <div>
              <h3>Passo a passo</h3>
              <ol className="steps-list">
                {solution.steps.map((step, index) => (
                  <li key={step}>
                    <span>{index + 1}</span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          </article>
        </section>
      )}
    </main>
  );
}

export default App;
