from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the smallest backend!"}

@app.get("/status")
def read_status():
    return {
        "status": "online",
        "description": "The backend server is running smoothly."
    }
