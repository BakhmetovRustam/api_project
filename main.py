from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import time

app = FastAPI()


global_list = []

class Element(BaseModel):
    element: str

class Expression(BaseModel):
    expr: str


http_requests_total = Counter(
    "http_requests_total", 
    "Number of HTTP requests received",
    ["method", "endpoint"]
)

http_requests_duration = Histogram(
    "http_requests_milliseconds",
    "Duration of HTTP requests in milliseconds",
    ["method", "endpoint"]
)

last_sum1n = Gauge(
    "last_sum1n",
    "Value stores last result of sum1n"
)

last_fibo = Gauge(
    "last_fibo",
    "Value stores last result of fibo"
)

list_size = Gauge(
    "list_size",
    "Value stores current list size"
)

last_calculator = Gauge(
    "last_calculator",
    "Value stores last result of calculator"
)

errors_calculator_total = Counter(
    "errors_calculator_total",
    "Number of errors in calculator"
)


metrics_app = prometheus_client.make_asgi_app()
app.mount("/metrics", metrics_app)


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    http_requests_total.labels(method=method, endpoint=endpoint).inc() 

    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000  
    http_requests_duration.labels(method=method, endpoint=endpoint).observe(duration)

    return response


@app.get("/sum1n/{n}")
async def sum1_to_n(n: int):
    if n < 1:
        raise HTTPException(status_code=400, detail="n must be greater than or equal to 1")
    result = sum(range(1, n + 1))
    last_sum1n.set(result)  
    return {"result": result}

@app.get("/fibo")
async def fibonacci(n: Optional[int] = None):
    if n is None or n < 0:
        raise HTTPException(status_code=400, detail="n must be a positive integer")
    
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    last_fibo.set(a)  
    return {"result": a}

@app.post("/reverse")
async def reverse_string(string: Optional[str] = Header(None)):
    if not string:
        raise HTTPException(status_code=400, detail="Header 'string' is missing")
    return {"result": string[::-1]}

@app.put("/list")
async def add_element_to_list(item: Element):
    global_list.append(item.element)
    list_size.set(len(global_list))  
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
        errors_calculator_total.inc()  
        raise HTTPException(status_code=400, detail="invalid")

    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    elif operator == '/':
        if num2 == 0:
            errors_calculator_total.inc() 
            raise HTTPException(status_code=403, detail="zerodiv")
        result = num1 / num2
    else:
        errors_calculator_total.inc()  
        raise HTTPException(status_code=400, detail="invalid operator")
    
    last_calculator.set(result)  
    return {"result": result}
