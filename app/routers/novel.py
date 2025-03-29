from fastapi import APIRouter
import myutils

router = APIRouter()

@router.get("/create_novel")
async def create_quiz(text: str, lang: str):
    return myutils.create_novel(
        text=text,
        lang=lang
    )