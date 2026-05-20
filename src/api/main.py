from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.math_solver.notable_products import solve_notable_product


class MathSolveRequest(BaseModel):
    expression: str = Field(
        ...,
        examples=["(x+5)^2"],
        description="Algebraic expression to solve.",
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="LLMOps Agentic Engineering Math API",
        description="Educational API for solving algebra expressions step by step.",
        version="0.1.0",
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/math/solve")
    def solve_math_problem(request: MathSolveRequest) -> dict[str, object]:
        try:
            solution = solve_notable_product(request.expression)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return solution.to_dict()

    return app


app = create_app()