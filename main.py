from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from parser import parse_text
from exporter import export_to_excel

app = FastAPI(title="Car Info Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ParseRequest(BaseModel):
    text: str


class ExportRequest(BaseModel):
    records: list[dict]


@app.post("/api/parse")
async def parse(req: ParseRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    try:
        records = parse_text(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败：{e}")
    return {"records": records, "count": len(records)}


@app.post("/api/export")
async def export(req: ExportRequest):
    if not req.records:
        raise HTTPException(status_code=400, detail="无数据可导出")
    buf = export_to_excel(req.records)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=car_prices.xlsx"},
    )


app.mount("/", StaticFiles(directory=".", html=True), name="static")
