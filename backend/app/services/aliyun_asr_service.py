
import os
import dashscope
import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AliyunRecognitionCallback(RecognitionCallback):
    def __init__(self):
        self.full_text = ""
        self.segments = []
        self.is_complete = False
        self.error_message = None

    def on_open(self) -> None:
        logger.info("Aliyun ASR RecognitionCallback open.")

    def on_close(self) -> None:
        logger.info("Aliyun ASR RecognitionCallback close.")
        self.is_complete = True

    def on_complete(self) -> None:
        logger.info("Aliyun ASR RecognitionCallback completed.")
        self.is_complete = True

    def on_error(self, message) -> None:
        logger.error(f"Aliyun ASR RecognitionCallback error: {message.message}")
        self.error_message = message.message
        self.is_complete = True

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.get_sentence()
        if 'text' in sentence:
            # logger.debug(f"Aliyun ASR text: {sentence['text']}")
            if RecognitionResult.is_sentence_end(sentence):
                text = sentence['text']
                self.full_text += text
                self.segments.append({
                    "text": text,
                    "start": sentence.get('begin_time', 0) / 1000.0, # ms to s
                    "end": sentence.get('end_time', 0) / 1000.0,
                    "request_id": result.get_request_id()
                })

class AliyunASRService:
    """
    阿里云语音识别服务 (Fun-ASR/Gummy/Paraformer)
    """
    
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        if not self.api_key:
            logger.warning("QWEN_API_KEY is not set. Aliyun ASR will not work.")
        dashscope.api_key = self.api_key

    async def transcribe_file(self, file_path: str, model: str = 'fun-asr-realtime') -> Dict[str, Any]:
        """使用阿里云实时语音识别 API 转录本地文件 (非阻塞封装)"""
        return await asyncio.to_thread(self._transcribe_file_blocking, file_path, model)

    def _transcribe_file_blocking(self, file_path: str, model: str) -> Dict[str, Any]:
        """阻塞式转录实现，供线程池调用"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        callback = AliyunRecognitionCallback()
        recognition = Recognition(
            model=model,
            format='pcm',
            sample_rate=16000,
            semantic_punctuation_enabled=True,
            callback=callback
        )

        try:
            recognition.start()

            chunk_size = 3200
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    recognition.send_audio_frame(data)

            recognition.stop()

            timeout = 30
            start_time = time.time()
            while not callback.is_complete and time.time() - start_time < timeout:
                time.sleep(0.1)

            if callback.error_message:
                raise Exception(f"Aliyun ASR error: {callback.error_message}")

            return {
                "text": callback.full_text,
                "segments": callback.segments
            }

        except Exception as e:
            logger.error(f"Aliyun ASR transcription failed: {e}")
            try:
                recognition.stop()
            except Exception:
                pass
            raise

# 全局单例
aliyun_asr_service = AliyunASRService()
