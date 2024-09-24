from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api.config import allowed_origins
from .api.routes import api_router, auth_router

tags_metadata = [
    {"name": "Auth"},
    {"name": "Users"},
    {"name": "Products"},
    {"name": "Orders"},
]

app = FastAPI(title="Final Project API", openapi_tags=tags_metadata)

# Include our API routes
app.include_router(api_router)
# Let's include our auth routes aside from the API routes
app.include_router(auth_router)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="bootcamp_ecommerce/static"), name="static")
templates = Jinja2Templates(directory="bootcamp_ecommerce/templates")


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context=dict(
            title="Final Project API",
            description='Go to "/docs" for API documentation',
        ),
    )
