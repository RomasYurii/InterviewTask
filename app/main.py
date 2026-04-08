from fastapi import FastAPI

app = FastAPI(
    title="Travel Planner API",
    description="API for managing travel projects and places.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Travel Planner API is running!"}

