import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.create_sample_data import create_data_in_bulk
from app.database import SessionLocal, create_db_tables
from app.langchain_helper import process_question
from app.models import Discount


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and load initial data
    create_db_tables()
    db = SessionLocal()
    try:
        print("Checking for existing data...")
        if db.query(Discount).count() == 0:
            print("Creating sample data...")
            create_data_in_bulk()
            print("Sample data created.")
    finally:
        db.close()
    yield


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

# Get the absolute path to the static directory
static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/ask", response_class=HTMLResponse)
async def ask_question(request: Request, question: str = Form(...)):
    """Process the question and return the response"""

    try:
        # Call your processing function
        answer = process_question(question)
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        print("Error processing question:", str(e))
        return JSONResponse(
            content={"error": "Sorry, there was an error processing your request."},
            status_code=500,
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
