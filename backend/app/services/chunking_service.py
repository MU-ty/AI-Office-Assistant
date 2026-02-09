
from typing import List, Dict, Any
import re

class ChunkingService:
    """
    文档切片服务
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        将文本切分为片段
        简单实现：基于字符数的滑动窗口，尽量在句号或换行符处切分
        """
        if not text:
            return []

        # 预处理：统一换行符
        text = text.replace("\r\n", "\n")
        
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            
            # 如果不是最后一段，尝试找到合适的切分点
            if end < text_len:
                # 在窗口末尾附近寻找换行符或句号
                # 搜索范围：end - overlap 到 end + overlap (但不超过 text_len)
                search_start = max(start, end - self.chunk_overlap // 2)
                search_end = min(text_len, end + self.chunk_overlap // 2)
                
                # 优先找段落换行
                split_point = -1
                
                # 1. 查找双换行 (段落)
                idx = text.rfind("\n\n", search_start, search_end)
                if idx != -1:
                    split_point = idx + 2
                
                # 2. 查找单换行
                if split_point == -1:
                    idx = text.rfind("\n", search_start, search_end)
                    if idx != -1:
                        split_point = idx + 1
                
                # 3. 查找句号
                if split_point == -1:
                    for punct in ["。", "！", "？", ".", "!", "?"]:
                        idx = text.rfind(punct, search_start, search_end)
                        if idx != -1:
                            split_point = idx + 1
                            break
                
                # 4. 如果都没找到，强制切分
                if split_point == -1:
                    split_point = end
                
                chunks.append(text[start:split_point].strip())
                # 下一段的起始位置 = 当前结束位置 - 重叠部分 (如果是非自然切分)
                # 如果是自然切分（找到句号/换行），通常不需要重叠太多，但为了上下文连贯，还是保留一点重叠比较好
                # 这里简化处理：直接从 split_point 开始，因为我们是按语义边界切的，
                # 但为了防止切分点正好切断了某些上下文，我们可以让 start 回退一点点，
                # 或者更简单的：如果 split_point 是强制切分的，回退 overlap；如果是自然切分，不回退。
                
                # 修正策略：LangChain 的 RecursiveCharacterTextSplitter 逻辑更复杂但更好。
                # 这里采用简单策略：
                # 如果找到了自然分隔符，split_point 就是分隔符后。
                # 下一次 start 应该是 split_point。
                # 为了保证上下文，我们可以在构建 chunk 时，向前包含一些 context，但这里简单起见，不重叠或者少重叠。
                
                # 重新调整策略：使用固定重叠
                # 下一个 chunk 从 end - overlap 开始？不对，这样会乱。
                
                # 采用标准滑动窗口：
                # 强制 end = start + chunk_size
                # 找到最近的分隔符作为实际 end
                # next_start = 实际 end - overlap (但这会导致重复内容过多)
                
                # 简化版：
                start = split_point
            else:
                # 最后一段
                chunks.append(text[start:].strip())
                break
        
        # 过滤空片段
        return [c for c in chunks if c]

    def split_text_recursive(self, text: str) -> List[str]:
        """
        递归切分 (类似 LangChain RecursiveCharacterTextSplitter)
        """
        separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        return self._split_text_with_separators(text, separators)

    def _split_text_with_separators(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []
        
        # 找到第一个匹配的分隔符
        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break
                
        # 使用分隔符切分
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # 逐字符
            
        # 合并小片段
        good_splits = []
        current_chunk = ""
        
        for split in splits:
            if separator:
                split_with_sep = split + separator if separator else split # 简单的恢复分隔符，不完全准确但够用
            else:
                split_with_sep = split

            if len(current_chunk) + len(split_with_sep) < self.chunk_size:
                current_chunk += split_with_sep
            else:
                if current_chunk:
                    good_splits.append(current_chunk)
                
                if len(split_with_sep) > self.chunk_size and new_separators:
                    # 递归切分过长的片段
                    good_splits.extend(self._split_text_with_separators(split_with_sep, new_separators))
                    current_chunk = ""
                else:
                    current_chunk = split_with_sep
        
        if current_chunk:
            good_splits.append(current_chunk)
            
        return [s.strip() for s in good_splits if s.strip()]

chunking_service = ChunkingService()
