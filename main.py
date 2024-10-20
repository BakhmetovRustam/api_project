from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

global_list = []

class Element(BaseModel):
    element: str


class Expression(BaseModel):
    expr: str


@app.get("/sum1n/{n}")
async def sum1_to_n(n: int):
    if n < 1:
        raise HTTPException(status_code=400, detail="n must be greater than or equal to 1")
    result = sum(range(1, n + 1))
    return {"result": result}


@app.get("/fibo")
async def fibonacci(n: Optional[int] = None):
    if n is None or n < 0:
        raise HTTPException(status_code=400, detail="n must be a positive integer")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return {"result": a}


@app.post("/reverse")
async def reverse_string(string: Optional[str] = Header(None)):
    if not string:
        raise HTTPException(status_code=400, detail="Header 'string' is missing")
    return {"result": string[::-1]}


@app.put("/list")
async def add_element_to_list(item: Element):
    global_list.append(item.element)
    return {"result": global_list}


@app.get("/list")
async def get_list():
    return {"result": global_list}


@app.post("/calculator")
async def calculator(expression: Expression):
    try:
        num1_str, operator, num2_str = expression.expr.split(',')
        num1 = float(num1_str)
        num2 = float(num2_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid")

    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    elif operator == '/':
        if num2 == 0:
            raise HTTPException(status_code=403, detail="zerodiv")
        result = num1 / num2
    else:
        raise HTTPException(status_code=400, detail="invalid operator")

    return {"result": result}
