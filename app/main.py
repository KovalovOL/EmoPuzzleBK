from fastapi import FastAPI
from app.routers import video_emotion, quiz, novel


app = FastAPI()


app.include_router(video_emotion.router)
app.include_router(quiz.router, prefix="/quiz")
app.include_router(novel.router, prefix="/novel")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)