import pytest
from src.api.v1.train import train_model
from fastapi import UploadFile
from io import BytesIO


@pytest.mark.asyncio
async def test_train_model():
    result = await train_model(text="Hãy dạy tôi về Python")
    assert result["status"] == "ok"
    assert "train_id" in result

    file_content = b"Python la mot ngon ngu lap trinh"
    file = UploadFile(filename="test.txt", file=BytesIO(file_content))
    result = await train_model(file=file)
    assert result["status"] == "ok"
    assert "fine-tune" in result["message"]
