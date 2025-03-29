from fastapi import APIRouter
import myutils

router = APIRouter()

@router.get("/create_quiz")
async def create_quiz(text: str, lang: str):
    return myutils.create_quiz(
        text=text,
        lang=lang
    )