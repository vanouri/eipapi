from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from srcs.ApiCallHandler import APIHandler
from datetime import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/prediction")
def prediction():
    api_handler = APIHandler()
    
    return {"prediction": api_handler.getPrediction()}

@app.get("/ref")
def reference():
    ref = {
        "-1": "Short Position",
        "0": "No Position",
        "1": "Long Position"
    }
    return {"status": "API is running", "reference": ref}

@app.get("/")
def root():
    routes = [route.path for route in app.routes]
    return {"available_routes": routes}
