import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse  # Добавили эту строчку
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess
import chess.engine

app = FastAPI()

# Разрешаем доступ к серверу с любых сайтов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к движку
ENGINE_PATH = "./patricia"

class AnalysisRequest(BaseModel):
    fen: str
    time_limit: float = 1.0

# ИЗМЕНИЛИ ТУТ: Теперь при заходе на сайт будет открываться наша шахматная доска
@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "working", "engine": "Patricia 5.1", "info": "Файл index.html не найден"}

@app.post("/analyze")
async def analyze_position(data: AnalysisRequest):
    try:
        board = chess.Board(data.fen)
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный формат FEN")

    if not os.path.exists(ENGINE_PATH):
        raise HTTPException(status_code=500, detail="Движок Patricia еще не установлен на сервере")

    try:
        transport, engine = await chess.engine.popen_uci(ENGINE_PATH)
        result = await engine.analyse(board, chess.engine.Limit(time=data.time_limit))
        await engine.quit()

        best_move = result.get("pv")[0].uci() if result.get("pv") else "None"
        score = result.get("score").relative.score(mate_score=10000) / 100.0 if result.get("score") else 0.0

        return {
            "best_move": best_move,
            "score": score,
            "depth": result.get("depth", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      
