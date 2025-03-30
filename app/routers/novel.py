from fastapi import APIRouter
import app.myutils

router = APIRouter()

@router.get("/create_novel")
async def create_quiz(text: str, lang: str):
    return app.myutils.create_novel(
        text=text,
        lang=lang
    )