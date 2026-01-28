"""
会议纪要流式生成服务
支持 SSE 流式输出，确保流吐完再关闭连接，在关闭前完成文件保存

核心逻辑改进：
1. SSE 流式吐字
2. LLM 吐字完成后，不立即关闭连接
3. 在当前函数内同步执行 save_to_json()
4. 通过 SSE 发送完成信号
5. 最后再关闭连接
"""

import asyncio
import json
import os
from typing import AsyncGenerator, Dict, Optional
from datetime import datetime, timezone
from app.utils.logger import get_logger
from app.services.nlp_service import nlp_service
from app.services.document_generation_service import document_generation_service
from app.core.config import settings

logger = get_logger(__name__)


class MeetingStreamingService:
    """会议纪要流式生成服务"""
    
    def __init__(self):
        self.nlp = nlp_service
        self.doc_gen = document_generation_service
    
    async def generate_minutes_stream(
        self,
        meeting_id: str,
        meeting_data: Dict,
        llm_stream_generator: AsyncGenerator[str, None],
        save_callback=None
    ) -> AsyncGenerator[str, None]:
        """
        生成会议纪要的流式版本
        
        核心改进：保证流完全吐完才关闭连接，并在关闭前保存文件
        
        Args:
            meeting_id: 会议ID
            meeting_data: 会议数据
            llm_stream_generator: LLM 的流式生成器
            save_callback: 保存完成的回调函数
            
        Yields:
            SSE 格式的流式数据
        """
        full_content = ""
        
        try:
            # ============================================================
            # 第一步：SSE 正常吐字
            # ============================================================
            logger.info(f"[{meeting_id}] 开始流式生成会议纪要")
            
            async for chunk in llm_stream_generator:
                if not chunk:
                    continue
                
                full_content += chunk
                
                # 发送 SSE 数据块
                sse_data = {
                    "status": "streaming",
                    "meeting_id": meeting_id,
                    "chunk": chunk,
                    "content": full_content
                }
                yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"
            
            logger.info(f"[{meeting_id}] LLM 吐字完成，长度: {len(full_content)} 字符")
            
            # ============================================================
            # 第二步：LLM 吐字完成，但不关闭连接，开始处理和保存
            # ============================================================
            
            # 发送处理中的信号
            processing_signal = {
                "status": "processing",
                "message": "正在处理和保存纪要...",
                "meeting_id": meeting_id
            }
            yield f"data: {json.dumps(processing_signal, ensure_ascii=False)}\n\n"
            logger.info(f"[{meeting_id}] 发送处理中信号")
            
            # ============================================================
            # 第三步：立即在当前函数内执行 save_to_json()
            # ============================================================
            
            try:
                saved_data = await self._save_minutes_to_files(
                    meeting_id=meeting_id,
                    meeting_data=meeting_data,
                    full_content=full_content
                )
                logger.info(f"[{meeting_id}] 文件保存成功: {saved_data}")
            except Exception as e:
                logger.error(f"[{meeting_id}] 文件保存失败: {e}")
                error_signal = {
                    "status": "save_error",
                    "error": str(e),
                    "meeting_id": meeting_id
                }
                yield f"data: {json.dumps(error_signal, ensure_ascii=False)}\n\n"
                raise
            
            # ============================================================
            # 第四步：文件保存成功后，通过 SSE 发送完成信号包
            # ============================================================
            
            completion_signal = {
                "status": "completed",
                "meeting_id": meeting_id,
                "summary": self._extract_summary(full_content),
                "file_path": f"/uploads/meeting_{meeting_id}_minutes.json",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_length": len(full_content),
                "message": "会议纪要生成完成！"
            }
            yield f"data: {json.dumps(completion_signal, ensure_ascii=False)}\n\n"
            logger.info(f"[{meeting_id}] 发送完成信号，SSE 即将关闭")
            
            # 调用回调函数（如果提供）
            if save_callback:
                await save_callback(meeting_id, saved_data)
            
        except asyncio.CancelledError:
            logger.warning(f"[{meeting_id}] 流式生成被取消")
            error_signal = {
                "status": "cancelled",
                "meeting_id": meeting_id,
                "message": "流式生成被中止"
            }
            yield f"data: {json.dumps(error_signal, ensure_ascii=False)}\n\n"
            raise
        
        except Exception as e:
            logger.error(f"[{meeting_id}] 流式生成异常: {e}")
            error_signal = {
                "status": "error",
                "meeting_id": meeting_id,
                "error": str(e)
            }
            yield f"data: {json.dumps(error_signal, ensure_ascii=False)}\n\n"
            raise
    
    async def _save_minutes_to_files(
        self,
        meeting_id: str,
        meeting_data: Dict,
        full_content: str
    ) -> Dict:
        """
        保存会议纪要到文件
        
        Args:
            meeting_id: 会议ID
            meeting_data: 会议数据
            full_content: 完整的纪要内容
            
        Returns:
            保存的数据信息
        """
        logger.info(f"[{meeting_id}] 开始保存文件...")
        
        # 确保上传目录存在
        if not os.path.exists(settings.UPLOAD_DIR):
            os.makedirs(settings.UPLOAD_DIR)
        
        # ============================================================
        # 保存 JSON 文件
        # ============================================================
        
        json_filename = f"meeting_{meeting_id}_minutes.json"
        json_filepath = os.path.join(settings.UPLOAD_DIR, json_filename)
        
        json_data = {
            "meeting_id": meeting_id,
            "title": meeting_data.get("title", f"会议纪要 - {meeting_id}"),
            "date": meeting_data.get("date") or datetime.now().strftime("%Y-%m-%d"),
            "participants": meeting_data.get("participants", []),
            "agendas": meeting_data.get("agendas", []),
            "decisions": meeting_data.get("decisions", []),
            "action_items": meeting_data.get("action_items", []),
            "key_points": meeting_data.get("key_points", []),
            "content": full_content,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "original_data": meeting_data
        }
        
        try:
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            logger.info(f"[{meeting_id}] JSON 文件保存成功: {json_filepath}")
        except Exception as e:
            logger.error(f"[{meeting_id}] JSON 文件保存失败: {e}")
            raise
        
        # ============================================================
        # 保存 Markdown 文件
        # ============================================================
        
        md_filename = f"meeting_{meeting_id}_minutes.md"
        md_filepath = os.path.join(settings.UPLOAD_DIR, md_filename)
        
        md_content = self.doc_gen.generate_markdown(
            title=json_data["title"],
            meeting_data=json_data,
            include_toc=True
        )
        
        try:
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"[{meeting_id}] Markdown 文件保存成功: {md_filepath}")
        except Exception as e:
            logger.error(f"[{meeting_id}] Markdown 文件保存失败: {e}")
            raise
        
        # ============================================================
        # 生成 PDF（可选，耗时较长）
        # ============================================================
        
        pdf_filename = f"meeting_{meeting_id}_minutes.pdf"
        pdf_filepath = os.path.join(settings.UPLOAD_DIR, pdf_filename)
        
        try:
            success = self.doc_gen.generate_pdf(
                title=json_data["title"],
                meeting_data=json_data,
                output_path=pdf_filepath
            )
            if success:
                logger.info(f"[{meeting_id}] PDF 文件生成成功: {pdf_filepath}")
            else:
                logger.warning(f"[{meeting_id}] PDF 文件生成失败，可能缺少依赖")
        except Exception as e:
            logger.warning(f"[{meeting_id}] PDF 生成异常（非致命）: {e}")
        
        # ============================================================
        # 生成 DOCX（可选，耗时较长）
        # ============================================================
        
        docx_filename = f"meeting_{meeting_id}_minutes.docx"
        docx_filepath = os.path.join(settings.UPLOAD_DIR, docx_filename)
        
        try:
            success = self.doc_gen.generate_docx(
                title=json_data["title"],
                meeting_data=json_data,
                output_path=docx_filepath
            )
            if success:
                logger.info(f"[{meeting_id}] DOCX 文件生成成功: {docx_filepath}")
            else:
                logger.warning(f"[{meeting_id}] DOCX 文件生成失败，可能缺少依赖")
        except Exception as e:
            logger.warning(f"[{meeting_id}] DOCX 生成异常（非致命）: {e}")
        
        # 返回保存信息
        saved_data = {
            "json": f"/uploads/{json_filename}",
            "markdown": f"/uploads/{md_filename}",
            "pdf": f"/uploads/{pdf_filename}",
            "docx": f"/uploads/{docx_filename}",
            "saved_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"[{meeting_id}] 所有文件保存完成: {saved_data}")
        return saved_data
    
    def _extract_summary(self, content: str, max_length: int = 200) -> str:
        """
        从内容中提取摘要
        
        Args:
            content: 完整内容
            max_length: 最大长度
            
        Returns:
            摘要文本
        """
        if not content:
            return "无内容"
        
        # 简单处理：取前 max_length 个字符 + "..."
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content


# 全局实例
meeting_streaming_service = MeetingStreamingService()
