from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from scraper.search import Property24Client


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = Property24Client()
    yield
    await client.close()


app = FastAPI(lifespan=lifespan)

client = None

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(
    request: Request, search_text: str = Form(...), search_type: str = Form(...)
):
    suggestions = client.get_property_suggestions(search_text)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "suggestions": suggestions, "search_text": search_text},
    )


@app.post("/select", response_class=HTMLResponse)
async def select(
    request: Request, suggestion_index: int = Form(...), search_text: str = Form(...)
):
    suggestions = client.get_property_suggestions(search_text)
    if 0 < suggestion_index <= len(suggestions):
        selected_suggestion = suggestions[suggestion_index - 1]
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "selected_suggestion": selected_suggestion},
        )
    else:
        return templates.TemplateResponse(
            "suggestions.html",
            {
                "request": request,
                "suggestions": suggestions,
                "error": "Invalid selection.",
                "search_text": search_text,
            },
        )


@app.post("/download")
async def download(suggestion: str = Form(...)):
    file_path = "path/to/properties.csv"
    return FileResponse(
        file_path, media_type="application/octet-stream", filename="properties.csv"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
