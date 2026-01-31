
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
import dashscope
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/asr", tags=["语音识别"])

class WSRecognitionCallback(RecognitionCallback):
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    def on_open(self) -> None:
        logger.info("Aliyun ASR WebSocket RecognitionCallback open.")

    def on_close(self) -> None:
        logger.info("Aliyun ASR WebSocket RecognitionCallback close.")

    def on_complete(self) -> None:
        logger.info("Aliyun ASR WebSocket RecognitionCallback completed.")

    def on_error(self, message) -> None:
        logger.error(f"Aliyun ASR WebSocket error: {message.message}")
        asyncio.run_coroutine_threadsafe(
            self.websocket.send_json({"type": "error", "message": message.message}),
            asyncio.get_event_loop()
        )

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.get_sentence()
        if 'text' in sentence:
            is_final = RecognitionResult.is_sentence_end(sentence)
            response = {
                "type": "result",
                "text": sentence['text'],
                "is_final": is_final,
                "begin_time": sentence.get('begin_time'),
                "end_time": sentence.get('end_time'),
                "request_id": result.get_request_id()
            }
            # 使用 loop.call_soon_threadsafe 因为 callback 可能在不同线程
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(
                self.websocket.send_json(response),
                loop
            )

@router.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("ASR WebSocket connection accepted")

    if not settings.QWEN_API_KEY:
        await websocket.send_json({"type": "error", "message": "Aliyun API Key not configured"})
        await websocket.close()
        return

    dashscope.api_key = settings.QWEN_API_KEY
    callback = WSRecognitionCallback(websocket)
    recognition = Recognition(
        model='fun-asr-realtime',
        format='pcm',
        sample_rate=16000,
        semantic_punctuation_enabled=True,
        callback=callback
    )

    try:
        recognition.start()
        
        while True:
            # 接收前端发来的二进制音频数据
            data = await websocket.receive_bytes()
            recognition.send_audio_frame(data)
            
    except WebSocketDisconnect:
        logger.info("ASR WebSocket disconnected")
    except Exception as e:
        logger.error(f"ASR WebSocket error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        try:
            recognition.stop()
        except:
            pass
        logger.info("ASR Recognition stopped")
