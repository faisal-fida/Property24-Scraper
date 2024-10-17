from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
import zipfile
import os
from scraper.config import logging

from scraper.search import SearchSuggestions


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
    request: Request, search_text: str = Form(...), search_type: str = Form(...)
):
    suggestions = search_suggestions.get_property_suggestions(search_text, search_type)
    return templates.TemplateResponse(
        "index.html", {"request": request, "suggestions": suggestions}
    )


@app.post("/download")
async def download(request: Request, selected_suggestions: list[str] = Form(...)):
    # scraped_data = []
    # for url in selected_suggestions:
    #     data = scrape_properties(url)
    #     scraped_data.append(data)

    # zip_filename = "scraped_properties.zip"
    # with zipfile.ZipFile(zip_filename, "w") as zipf:
    #     for i, data in enumerate(scraped_data):
    #         file_name = f"property_{i+1}.txt"
    #         with open(file_name, "w") as f:
    #             f.write(data)
    #         zipf.write(file_name)
    #         os.remove(file_name)

    logging.info(
        f"Downloading properies: {selected_suggestions} {type(selected_suggestions)}"
    )

    sample_data = [
        "Property 1",
        "Property 2",
        "Property 3",
        "Property 4",
        "Property 5",
    ]

    zip_filename = "sample_properties.zip"

    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for i, data in enumerate(sample_data):
            file_name = f"property_{i+1}.txt"
            with open(file_name, "w") as f:
                f.write(data)
            zipf.write(file_name)
            os.remove(file_name)

    return FileResponse(
        zip_filename, media_type="application/zip", filename=zip_filename
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
