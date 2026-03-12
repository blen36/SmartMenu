from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/onboarding/{step}")
def onboarding(request: Request, step: int):

    return templates.TemplateResponse(
        "onboarding.html",
        {
            "request": request,
            "step": step
        }
    )