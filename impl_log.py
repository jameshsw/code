
"""
Running CPython 3.10
123456
Scenario
You’re part of a team maintaining a Python-based web service with dozens of REST API endpoints (e.g. built on Flask/FastAPI/Django). Lately you’ve begun to see slowdown in some routes and sporadic spikes in latency.

Task
Design and implement a home-grown solution that you can apply to any endpoint to automatically log:

Incoming request metadata (URL, method, headers)
Request payload
Total execution time per call
Feel free to ask clarifying questions up front before jumping into code.

Sample API endpoints
@app.route("/status", methods=["GET"])
def status():
    # … process logic (omitted for brevity) …

@app.route("/create-account", methods=["POST"])
def create_account():
    payload = request.get_json()
    username = payload.get("username")
    password = payload.get("password")
    # … process logic (omitted for brevity) …

@app.route("/add-payment-info", methods=["POST"])
def add_payment_info():
    payload = request.get_json()
    credit_card_number = payload.get("credit_card_number")
    billing_address = payload.get("billing_address")
    # … process logic (omitted for brevity) …

@app.route("/run-simulation", methods=["POST"])
def run_simulation():
    payload = request.get_json()
    simulation_type = payload.get("simulation_type")
    
    # Customer proprietary chemical information would be provided
    chemical_structures = payload.get("chemical_structures")  
    # … process logic (omitted for brevity) …

"""
"""
Solution
"""

# logging_config.py
import logging

def setup_logging(log_file="requests.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),  # Also print to console
        ]
    )

logger = logging.getLogger("fastapi.request")

"""
use middleware 
"""

from fastapi import FastAPI, Request
import time
import json

app = FastAPI()

@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    start_time = time.time()

    body = await request.body()
    try:
        payload = json.loads(body.decode())
    except Exception:
        payload = None

    metadata = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    }

    response = await call_next(request)

    duration = (time.time() - start_time) * 1000

    log_data = {
        "request": metadata,
        "payload": payload,
        "duration_ms": round(duration, 2),
        "status_code": response.status_code
    }

    print("[Request Log]", json.dumps(log_data, indent=2))
    return response

"""
mask sensitive data 
"""
def mask_sensitive(data: dict) -> dict:
    SENSITIVE_FIELDS = {"password", "credit_card_number"}
    return {
        k: ("***" if k in SENSITIVE_FIELDS else v)
        for k, v in (data.items() if data else {})
    }


"""
log performance 
"""

@app.middleware("http")
async def log_performance(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000  # ms

    logger.info(f"{request.method} {request.url.path} took {duration:.2f} ms")
    return response



"""
using wrapper to log request
"""

import time
import json
from functools import wraps
from fastapi import Request
from starlette.responses import Response

def log_request(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        start_time = time.time()

        # Clone the body from the request stream
        body = await request.body()
        try:
            payload = json.loads(body.decode())
        except Exception:
            payload = None

        metadata = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
        }

        # Run the actual endpoint function
        response: Response = await func(request, *args, **kwargs)

        duration = (time.time() - start_time) * 1000  # ms

        log_data = {
            "request": metadata,
            "payload": payload,
            "duration_ms": round(duration, 2)
        }

        print("[Request Log]", json.dumps(log_data, indent=2))
        return response

    return wrapper


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/status")
@log_request
async def status(request: Request):
    return JSONResponse({"status": "ok"})

@app.post("/create-account")
@log_request
async def create_account(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    return JSONResponse({"message": f"Account created for {username}"}, status_code=201)

@app.post("/add-payment-info")
@log_request
async def add_payment_info(request: Request):
    data = await request.json()
    return JSONResponse({"message": "Payment info added"})

@app.post("/run-simulation")
@log_request
async def run_simulation(request: Request):
    data = await request.json()
    return JSONResponse({"message": "Simulation started"}, status_code=202)



"""

Middleware vs Wrapper (Decorator)
Definition	
Code that intercepts every HTTP request and response globally, before hitting any route handler and after it returns
Function that wraps around a single route handler to modify behavior or add features on that endpoint only

Scope	
Application-wide, applies to all routes unless filtered	
Applied on a per-route basis by decorating functions

Typical Use Cases	
Logging, authentication, CORS, compression, performance timing, request/response modification	
Input validation, authorization checks on specific endpoints, caching, response formatting

Implementation	
Registered once in app (e.g., @app.middleware("http"))	
Python function decorators wrapping handler functions (@log_execution_time)

Control	
Less granular, runs on all requests	
Very granular, per function

Order of Execution	
Executes early (before route), and after response	
Executes just around the wrapped route handler

Access to Request	
Middleware gets full Request and Response objects	
Wrapper typically gets the handler’s input arguments and return value

"""
