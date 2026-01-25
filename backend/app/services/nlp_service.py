"""
NLP文本处理服务 - 可复用的文本分析工具
处理文本的各种NLP任务：分句、关键词提取、命名实体识别等

表格中标黄部分 - 优先级p1/p2的通用文本处理能力
"""

from typing import List, Dict, Tuple, Optional
try:
    import jieba
    from jieba import analyse
except Exception:
    # jieba is optional; provide fallbacks so the module can be analyzed/run without jieba installed
    jieba = None
    class _DummyAnalyse:
        @staticmethod
        def extract_tags(text, topK=20, withWeight=False, allowPOS=None):
            return []
    analyse = _DummyAnalyse()
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NLPService:
    """通用NLP处理服务"""
    
    def __init__(self):
        """初始化NLP工具"""
        # 加载自定义词典（可选）
        self.keywords_extractor = analyse.extract_tags
        
    # ============================================================
    # 分句与分段处理
    # ============================================================
    
    def split_sentences(self, text: str) -> List[str]:
        """
        分句处理
        
        按标点符号将文本分成句子
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        if not text or not isinstance(text, str):
            return []
            
        # 常见中文断句符号
        sentence_delimiters = r'[。！？；\n]'
        sentences = re.split(sentence_delimiters, text.strip())
        
        # 清除空白句子并保留至少2个字符的句子
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) >= 2]
    
    def split_paragraphs(self, text: str, delimiter: str = '\n\n') -> List[str]:
        """
        分段处理
        
        按段落分隔符将文本分成段落
        Args:
            text: 输入文本
            delimiter: 段落分隔符，默认为两个换行符
            
        Returns:
            段落列表
        """
        if not text or not isinstance(text, str):
            return []
            
        paragraphs = text.split(delimiter)
        return [p.strip() for p in paragraphs if p.strip()]
    
    # ============================================================
    # 关键词提取（TF-IDF）
    # ============================================================
    
    def extract_keywords(
        self, 
        text: str, 
        top_k: int = 10,
        withWeight: bool = False,
        allowPOS: Optional[List[str]] = None
    ) -> List[Tuple[str, float] | str]:
        """
        提取文本关键词 - TF-IDF算法
        
        Args:
            text: 输入文本
            top_k: 返回关键词个数
            withWeight: 是否返回权重
            allowPOS: 允许的词性列表，如['n', 'nr', 'nz']（名词）
            
        Returns:
            关键词列表，可选包含权重
            
        Example:
            >>> nlp = NLPService()
            >>> keywords = nlp.extract_keywords("这是一个测试文本", top_k=5)
            >>> keywords_with_weight = nlp.extract_keywords(
            ...     "这是一个测试文本", 
            ...     top_k=5, 
            ...     withWeight=True
            ... )
        """
        try:
            if not text or not isinstance(text, str):
                return []
            
            # 使用jieba.analyse的TF-IDF提取
            results = self.keywords_extractor(
                text,
                topK=top_k,
                withWeight=withWeight,
                allowPOS=allowPOS
            )
            return results
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []
    
    def extract_key_sentences(
        self, 
        text: str, 
        top_k: int = 5
    ) -> List[str]:
        """
        提取关键句 - 基于关键词在句子中的频率
        
        Args:
            text: 输入文本
            top_k: 返回关键句个数
            
        Returns:
            关键句列表
        """
        try:
            # 先提取关键词
            keywords = self.extract_keywords(text, top_k=20)
            keyword_set = set([kw[0] if isinstance(kw, tuple) else kw for kw in keywords])
            
            # 分句
            sentences = self.split_sentences(text)
            
            # 计算每个句子的关键词频率
            sentence_scores = []
            for sentence in sentences:
                score = sum(1 for kw in keyword_set if kw in sentence)
                sentence_scores.append((sentence, score))
            
            # 按分数排序并返回top_k
            sorted_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)
            return [s[0] for s in sorted_sentences[:top_k]]
            
        except Exception as e:
            logger.error(f"关键句提取失败: {e}")
            return []
    
    # ============================================================
    # 中文分词和词性标注
    # ============================================================
    
    def tokenize(self, text: str) -> List[str]:
        """
        中文分词
        
        Args:
            text: 输入文本
            
        Returns:
            词列表
        """
        if not text or not isinstance(text, str):
            return []
            
        if jieba is None:
            # fallback simple tokenizer when jieba is not available
            # split into words or single non-space characters
            return re.findall(r'\w+|[^\s]', text)
        return list(jieba.cut(text))
    
    def tokenize_with_pos(self, text: str) -> List[Tuple[str, str]]:
        """
        分词并标注词性
        
        Args:
            text: 输入文本
            
        Returns:
            (词, 词性) 元组列表
            
        Note:
            需要额外依赖: pip install jieba-fast
        """
        try:
            import jieba.posseg as pseg
            return [(w, p) for w, p in pseg.cut(text)]
        except ImportError:
            logger.warning("jieba.posseg 未安装，使用基础分词")
            return [(w, 'unknown') for w in self.tokenize(text)]
    
    # ============================================================
    # 命名实体识别基础
    # ============================================================
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        提取命名实体（基于词典和规则）
        
        Args:
            text: 输入文本
            
        Returns:
            实体字典，包含人物、机构、地点等
        """
        entities = {
            'persons': [],      # 人名
            'organizations': [], # 机构名
            'locations': [],     # 地点名
            'dates': [],        # 日期
            'times': [],        # 时间
        }
        
        try:
            # 日期识别（简单正则）
            date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}'
            entities['dates'] = re.findall(date_pattern, text)
            
            # 时间识别（简单正则）
            time_pattern = r'\d{1,2}:\d{2}(?::\d{2})?'
            entities['times'] = re.findall(time_pattern, text)
            
            # 如果有更好的NER模型，可在此集成
            # 例如使用spacy或transformers的NER模型
            
        except Exception as e:
            logger.error(f"实体识别失败: {e}")
        
        return entities
    
    # ============================================================
    # 文本统计
    # ============================================================
    
    def get_text_stats(self, text: str) -> Dict:
        """
        获取文本统计信息
        
        Args:
            text: 输入文本
            
        Returns:
            包含字符数、词数、句数等的统计字典
        """
        if not text or not isinstance(text, str):
            return {
                'char_count': 0,
                'word_count': 0,
                'sentence_count': 0,
                'paragraph_count': 0,
            }
        
        sentences = self.split_sentences(text)
        paragraphs = self.split_paragraphs(text)
        tokens = self.tokenize(text)
        
        return {
            'char_count': len(text),
            'word_count': len(tokens),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'avg_sentence_length': len(text) / len(sentences) if sentences else 0,
        }
    
    # ============================================================
    # 文本清洗
    # ============================================================
    
    def clean_text(self, text: str, remove_punctuation: bool = False) -> str:
        """
        清洗文本
        
        Args:
            text: 输入文本
            remove_punctuation: 是否移除标点符号
            
        Returns:
            清洗后的文本
        """
        if not text or not isinstance(text, str):
            return ""
        
        # 移除额外空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        if remove_punctuation:
            # 移除中英文标点
            text = re.sub(r'[。，！？；：""''（）【】《》、—~·•]', '', text)
            text = re.sub(r'[.,!?;:"\'-()[\]{}<>]', '', text)
        
        return text


# 全局实例
nlp_service = NLPService()
