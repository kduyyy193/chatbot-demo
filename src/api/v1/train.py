import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from src.db import save_training_data, get_all_training_data, save_fine_tuned_model_to_db
from openai import OpenAI
from src.config.settings import settings
import json
import asyncio
from typing import Optional, List, Dict

from src.logger_config import setup_logging

logger = setup_logging()

router = APIRouter()
client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger.info(f"Key {settings.OPENAI_API_KEY}")

current_model: str = settings.MODEL_NAME
MIN_RECORDS_FOR_FINETUNE: int = 2  # Fine-tune when there are at least 2 records


def generate_dynamic_prompts(content: str) -> list:
    if "Giám đốc" in content or "giám đốc" in content:
        prompt = "Ai là giám đốc?"
    elif "Trưởng phòng" in content or "trưởng phòng" in content:
        prompt = "Ai là trưởng phòng?"
    elif "Công ty" in content or "công ty" in content:
        prompt = "Công ty làm gì?"
    else:
        prompt = "Nói gì vậy?"
    return [{
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": content}
        ]
    }]


async def wait_for_finetune(fine_tune_id: str) -> str:
    while True:
        status = await asyncio.to_thread(client.fine_tuning.jobs.retrieve, fine_tune_id)
        if status.status == "succeeded" and status.fine_tuned_model:
            return status.fine_tuned_model
        elif status.status in ["failed", "cancelled"]:
            raise HTTPException(status_code=500, detail=f"Fine-tune failed: {status.status}")
        logger.info(f"Fine-tune {fine_tune_id} status: {status.status}")
        await asyncio.sleep(10)


async def prepare_finetune_data() -> str:
    training_data = get_all_training_data()
    if not training_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu để fine-tune")
    file_path = "fine_tune_data.jsonl"
    logger.debug(f"Preparing to write to {file_path}")
    with open(file_path, "w", encoding="utf-8") as f:
        for item in training_data:
            content = item["content"]
            entries = generate_dynamic_prompts(content)
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    if os.path.exists(file_path):
        logger.info(f"Successfully created fine-tune data in {file_path}")
    else:
        logger.error(f"Failed to create {file_path}")
    return file_path


async def upload_file_to_openai(file_path: str) -> str:
    with open(file_path, "rb") as f:
        response = await asyncio.to_thread(client.files.create, file=f, purpose="fine-tune")
    return response.id


async def start_finetune(file_id: str) -> str:
    fine_tune_response = await asyncio.to_thread(
        client.fine_tuning.jobs.create,
        training_file=file_id,
        model=settings.MODEL_NAME
    )
    return fine_tune_response.id


@router.post("/train")
async def train_model(file: Optional[UploadFile] = File(None), text: str = Form(None)):
    global current_model
    logger.debug(f"Received request - file: {file}, text: {text}")
    try:
        if not file and not text:
            raise HTTPException(status_code=400, detail="Vui lòng cung cấp file hoặc text!")
        if file and file.filename:
            if not file.filename.endswith(".txt"):
                raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file .txt!")
            content = (await file.read()).decode("utf-8")
            logger.info(f"Received training file: {file.filename}, length: {len(content)}")
        elif text:
            content = text
            logger.info(f"Received training text, length: {len(content)}")
        else:
            raise HTTPException(status_code=400, detail="Dữ liệu file không hợp lệ!")

        train_id = save_training_data(content)
        all_data = get_all_training_data()
        if len(all_data) >= MIN_RECORDS_FOR_FINETUNE:
            file_path = await prepare_finetune_data()
            file_id = await upload_file_to_openai(file_path)
            fine_tune_id = await start_finetune(file_id)
            new_model = await wait_for_finetune(fine_tune_id)
            logger.info(f"Fine-tuned model: {new_model}")
            current_model = new_model
            save_fine_tuned_model_to_db(new_model)

            return {
                "status": "ok",
                "message": f"Đã train và fine-tune. Model mới: {current_model}",
                "train_id": train_id
            }
        return {
            "status": "ok",
            "message": f"Đã lưu dữ liệu, cần {MIN_RECORDS_FOR_FINETUNE - len(all_data) + 1} bản ghi nữa để fine-tune",
            "train_id": train_id
        }
    except Exception as e:
        logger.error(f"Train error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi train: {str(e)}")


@router.get("/context")
async def get_context() -> Dict[str, List[Dict[str, str]]]:
    return {"context": get_all_training_data()}


@router.get("/current-model")
async def get_current_model() -> Dict[str, str]:
    return {"current_model": current_model}
