import random
from typing import Generator
from transformers import pipeline

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

RESPONSES = {
    "POSITIVE": [
        "Rất vui khi nghe điều đó! Bạn muốn nói thêm không?",
        "Tuyệt vời! Có gì thú vị đang xảy ra không?",
        "Cảm ơn bạn đã chia sẻ, nghe hay đấy!",
    ],
    "NEGATIVE": [
        "Tôi tiếc khi nghe điều đó. Có gì tôi giúp được không?",
        "Ồ, có vẻ không vui lắm. Bạn ổn chứ?",
        "Đừng lo, mọi chuyện rồi sẽ ổn thôi!",
    ],
    "NEUTRAL": [
        "Ừm, thú vị đấy. Bạn muốn nói gì tiếp không?",
        "Tôi hiểu rồi. Có gì đặc biệt không?",
        "Cứ tự nhiên hỏi tôi bất cứ điều gì nhé!",
    ],
}


def distilbert_chatbot(user_input: str) -> str:
    result = sentiment_analyzer(user_input)

    if result is None:
        return "Không có kết quả phân tích cảm xúc."

    elif isinstance(result, Generator):
        result_list = list(result)
        if result_list:
            return random.choice(RESPONSES[result_list[0]["label"]])
        else:
            return "Không có cảm xúc được xác định."

    elif isinstance(result, list) or isinstance(result, tuple):
        if result:
            return random.choice(RESPONSES[result[0]["label"]])
        else:
            return "Không có cảm xúc được xác định."
    else:
        return "Đã xảy ra lỗi khi phân tích cảm xúc."
