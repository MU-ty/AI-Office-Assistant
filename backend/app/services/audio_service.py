
import os
import shutil
from typing import Optional, Dict
import imageio_ffmpeg
import subprocess

from app.utils.logger import get_logger

logger = get_logger(__name__)

class AudioService:
    """音频处理服务：负责音频格式转换、元数据提取等"""
    
    def __init__(self):
        self._setup_ffmpeg()

    def _setup_ffmpeg(self):
        """确保 FFmpeg 可用"""
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
        
        # 确保系统 PATH 中有 ffmpeg
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
            
        # 尝试查找 ffprobe
        self.ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe.exe")
        if not os.path.exists(self.ffprobe_path):
             self.ffprobe_path = None # 或者尝试从 path 查找

    def convert_to_wav(self, input_path: str, output_path: str = None) -> str:
        """
        将音频转换为 WAV 格式 (16kHz, 单声道 - 适合语音识别)
        使用 subprocess 直接调用 ffmpeg，避免 pydub 在 Python 3.13+ (缺少 audioop) 的问题
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选，默认同名.wav）
            
        Returns:
            输出文件路径
        """
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + ".wav"
            
        # 检查输入输出是否为同一文件
        final_output_path = output_path
        temp_output_path = None
        if os.path.abspath(input_path) == os.path.abspath(output_path):
            base, ext = os.path.splitext(output_path)
            temp_output_path = f"{base}_temp{ext}"
            output_path = temp_output_path
            
        try:
            logger.info(f"正在转换音频: {input_path} -> {output_path}")
            
            # 构造 ffmpeg 命令
            # -y: 覆盖输出文件
            # -ar 16000: 采样率 16kHz
            # -ac 1: 单声道
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", input_path,
                "-ar", "16000",
                "-ac", "1",
                output_path
            ]
            
            # 执行命令
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 如果使用了临时文件，替换原文件
            if temp_output_path:
                if os.path.exists(final_output_path):
                    os.remove(final_output_path)
                os.rename(temp_output_path, final_output_path)
                output_path = final_output_path
                logger.info(f"覆盖原文件: {final_output_path}")
            
            logger.info(f"音频转换成功: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"音频转换失败 (ffmpeg error): {e.stderr.decode('utf-8', errors='ignore')}")
            raise
        except Exception as e:
            logger.error(f"音频转换失败: {e}")
            raise

    def get_audio_duration(self, file_path: str) -> float:
        """获取音频时长（秒）"""
        try:
            # 如果有 ffprobe，优先使用 ffprobe
            if self.ffprobe_path:
                cmd = [
                    self.ffprobe_path,
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    file_path
                ]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                return float(result.stdout.strip())
            return 0.0
        except Exception as e:
            logger.error(f"获取音频时长失败: {e}")
            return 0.0

    def split_audio(self, file_path: str, chunk_duration_sec: int = 600) -> list[str]:
        """
        将音频按指定时长进行分块
        
        Args:
            file_path: 输入文件路径
            chunk_duration_sec: 每个块的时长（秒），默认 10 分钟
            
        Returns:
            分块后的文件路径列表
        """
        try:
            logger.info(f"开始音频分块: {file_path}, 块大小: {chunk_duration_sec}s")
            
            # 创建分块输出目录
            base_dir = os.path.dirname(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            chunks_dir = os.path.join(base_dir, f"{file_name}_chunks")
            os.makedirs(chunks_dir, exist_ok=True)
            
            # 输出文件模板
            output_pattern = os.path.join(chunks_dir, "chunk_%03d.wav")
            
            # 使用 ffmpeg segment muxer 进行分块
            # -f segment: 启用分块
            # -segment_time: 块时长
            # -c copy: 直接流复制，不重新编码（非常快），前提是源文件格式合适
            # 但为了保险起见（避免时间戳问题），这里我们还是用 wav 重新封装一下，
            # 也可以加上 -c:a pcm_s16le 确保格式正确，但之前已经转过 wav 了，copy 应该没问题。
            # 为了最大兼容性，我们显式指定编码器为 pcm_s16le
            
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", file_path,
                "-f", "segment",
                "-segment_time", str(chunk_duration_sec),
                "-c:a", "pcm_s16le", 
                output_pattern
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 获取生成的文件列表并排序
            chunks = []
            for f in os.listdir(chunks_dir):
                if f.startswith("chunk_") and f.endswith(".wav"):
                    chunks.append(os.path.join(chunks_dir, f))
            
            chunks.sort() # 确保顺序
            logger.info(f"音频分块完成，共生成 {len(chunks)} 个分块")
            return chunks
            
        except subprocess.CalledProcessError as e:
            logger.error(f"音频分块失败 (ffmpeg error): {e.stderr.decode('utf-8', errors='ignore')}")
            raise
        except Exception as e:
            logger.error(f"音频分块失败: {e}")
            raise

# 全局实例
audio_service = AudioService()
