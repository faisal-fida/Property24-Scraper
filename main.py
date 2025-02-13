from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
import os

from utils.config import logging
from utils.search import SearchSuggestions

from web_scraper.main import scrape_properties

@asynccontextmanager
async def lifespan(app: FastAPI):
    global search_suggestions
    search_suggestions = SearchSuggestions()
    search_suggestions.load_suggestions()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(
    request: Request, search_text: str = Form(...)
):
    suggestions = search_suggestions.get_property_suggestions(search_text)
    return templates.TemplateResponse(
        "index.html", {"request": request, "suggestions": suggestions}
    )


@app.post("/download")
async def download(
    request: Request, 
    selected_suggestions: list[str] = Form(...),
    search_type: str = Form(...)
):
    logging.info(
        f"Starting download of properties for the following suggestions: {selected_suggestions}"
    )

    if os.path.exists("properties.csv"):
        os.remove("properties.csv")

    if not selected_suggestions:
        return {"error": "No properties selected"}
        
    df = await scrape_properties(selected_suggestions, search_type)
    df.to_csv("properties.csv", index=False)
    return FileResponse("properties.csv")



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
