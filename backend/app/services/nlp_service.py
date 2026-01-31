"""
NLP文本处理服务 - 可复用的文本分析工具
处理文本的各种NLP任务：分句、关键词提取、命名实体识别等

表格中标黄部分 - 优先级p1/p2的通用文本处理能力
"""

from typing import List, Dict, Tuple, Optional
try:
    import jieba
    from jieba import analyse
    import jieba.posseg as pseg
except Exception:
    # jieba is optional; provide fallbacks so the module can be analyzed/run without jieba installed
    jieba = None
    class _DummyAnalyse:
        @staticmethod
        def extract_tags(text, topK=20, withWeight=False, allowPOS=None):
            return []
    analyse = _DummyAnalyse()
    pseg = None
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NLPService:
    """通用NLP处理服务"""
    
    def __init__(self):
        """初始化NLP工具"""
        # 加载自定义词典（可选）
        self.keywords_extractor = analyse.extract_tags
        
    def add_entity(self, word: str, entity_type: str = 'n'):
        """
        添加自定义实体/词汇到词典
        
        Args:
            word: 词汇
            entity_type: 实体类型 ('nr' 人名, 'ns' 地名, 'nt' 机构名, 'n' 普通名词)
        """
        if jieba:
            jieba.add_word(word, tag=entity_type)

    def load_user_dict(self, file_path: str):
        """
        加载用户自定义词典
        
        Args:
            file_path: 词典文件路径
        """
        if jieba:
            try:
                jieba.load_userdict(file_path)
            except Exception as e:
                logger.error(f"加载自定义词典失败: {e}")
        
    # ============================================================
    # 话题划分 (Topic Segmentation)
    # ============================================================
    
    def segment_topics(self, text: str, window_size: int = 3) -> List[Dict]:
        """
        基于文本相似度的话题划分 (TextTiling-like approach)
        
        Args:
            text: 输入文本
            window_size: 窗口大小（句子数），用于计算局部相似度
            
        Returns:
            话题列表，每个话题包含：
            - id: 话题序号
            - content: 话题内容
            - keywords: 话题关键词
            - sentences: 句子列表
        """
        if not text or not isinstance(text, str):
            return []
            
        sentences = self.split_sentences(text)
        if len(sentences) <= window_size:
            # 文本太短，视为一个话题
            return [{
                "id": 1,
                "content": text,
                "keywords": self.extract_keywords(text, top_k=5),
                "sentences": sentences
            }]
            
        try:
            # 1. 预处理：分词并去除停用词
            tokenized_sentences = []
            for sent in sentences:
                # 仅保留名词和动词，过滤单字
                words = [w for w, f in self.tokenize_with_pos(sent) 
                         if len(w) > 1 and f.startswith(('n', 'v'))]
                tokenized_sentences.append(set(words))
                
            # 2. 计算相邻窗口的相似度 (Block Similarity)
            # 使用Jaccard相似度: |A ∩ B| / |A ∪ B|
            scores = []
            for i in range(len(sentences) - 2 * window_size + 1):
                block1 = set()
                block2 = set()
                
                # 构建左窗口
                for j in range(window_size):
                    block1.update(tokenized_sentences[i + j])
                
                # 构建右窗口
                for j in range(window_size):
                    block2.update(tokenized_sentences[i + window_size + j])
                
                # 计算相似度
                union_len = len(block1.union(block2))
                if union_len == 0:
                    score = 0.0
                else:
                    score = len(block1.intersection(block2)) / union_len
                scores.append(score)
                
            # 3. 寻找分割点 (Valley Detection)
            # 简单的波谷检测：如果某个点比平均值低很多，且是局部最小值
            if not scores:
                boundaries = []
            else:
                avg_score = sum(scores) / len(scores)
                std_dev = (sum((s - avg_score) ** 2 for s in scores) / len(scores)) ** 0.5
                threshold = avg_score - 0.5 * std_dev # 阈值可调
                
                boundaries = []
                for i in range(1, len(scores) - 1):
                    # 局部最小值且低于阈值
                    if scores[i] < scores[i-1] and scores[i] < scores[i+1] and scores[i] < threshold:
                        # 记录分割点索引 (对应原句子的索引需要偏移 window_size)
                        boundaries.append(i + window_size)
            
            # 4. 构建话题结果
            topics = []
            start_idx = 0
            topic_id = 1
            
            # 添加结尾边界
            boundaries.append(len(sentences))
            
            for end_idx in boundaries:
                # 过滤过短的片段 (例如少于2句，除非是最后一段)
                if end_idx - start_idx < 2 and end_idx != len(sentences) and start_idx != 0:
                    continue
                    
                segment_sentences = sentences[start_idx:end_idx]
                if not segment_sentences:
                    continue
                    
                segment_text = " ".join(segment_sentences)
                topics.append({
                    "id": topic_id,
                    "content": segment_text,
                    "keywords": self.extract_keywords(segment_text, top_k=5),
                    "sentences": segment_sentences
                })
                topic_id += 1
                start_idx = end_idx
                
            return topics
            
        except Exception as e:
            logger.error(f"话题划分失败: {e}")
            # 降级处理：返回单个话题
            return [{
                "id": 1,
                "content": text,
                "keywords": self.extract_keywords(text, top_k=5),
                "sentences": sentences
            }]

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
            entities['dates'] = list(set(re.findall(date_pattern, text)))
            
            # 时间识别（简单正则）
            time_pattern = r'\d{1,2}:\d{2}(?::\d{2})?'
            entities['times'] = list(set(re.findall(time_pattern, text)))
            
            # 使用jieba进行命名实体识别
            if jieba and pseg:
                words = pseg.cut(text)
                for word, flag in words:
                    if flag == 'nr':
                        # 简单的姓氏过滤，排除一些单字或非人名
                        if len(word) > 1:
                            entities['persons'].append(word)
                    elif flag == 'ns':
                        entities['locations'].append(word)
                    elif flag == 'nt':
                        entities['organizations'].append(word)
                    elif flag == 'nz': # 其他专名
                        if "公司" in word or "部" in word:
                             entities['organizations'].append(word)

            
            # 简单的发言者模式匹配 (例如 "张三：大家好" 或 "李四说：")
            speaker_pattern = r'([^\s：:]{2,5})[：:说]'
            potential_speakers = re.findall(speaker_pattern, text)
            for speaker in potential_speakers:
                # 再次验证是否为人名（或者是已知的发言者）
                if jieba and pseg:
                    words = list(pseg.cut(speaker))
                    # 如果被jieba认为是人名，或者包含在已有的人名列表中
                    if (len(words) == 1 and words[0].flag == 'nr') or speaker in entities['persons']:
                        entities['persons'].append(speaker)
                elif not jieba:
                     # Fallback: 如果没有jieba，只要不包含数字和特殊符号，长度2-4，就认为是人名
                     if re.match(r'^[\u4e00-\u9fa5]{2,4}$', speaker):
                         entities['persons'].append(speaker)

            # 增强规则：基于职务和称呼
            title_pattern = r'(?:总经理|经理|总监|主管|组长|工程师|秘书|助理)([\u4e00-\u9fa5]{2,4})'
            potential_persons = re.findall(title_pattern, text)
            entities['persons'].extend(potential_persons)

            # 去重
            entities['persons'] = list(set(entities['persons']))
            entities['locations'] = list(set(entities['locations']))
            entities['organizations'] = list(set(entities['organizations']))
            
        except Exception as e:
            logger.error(f"实体识别失败: {e}")
        
        return entities

    # ============================================================
    # 议程与关键信息提取
    # ============================================================
    
    def extract_agendas(self, text: str, topics: List[Dict] = None) -> List[str]:
        """
        提取会议议程
        """
        agendas = []
        if not text:
            return []
            
        try:
            # 策略1: 显式议程关键词匹配
            agenda_patterns = [
                r'(?:议程|议题|讨论|主题)(?:包括|是|包含|为)?[:：\s]([^。！？\n]+)',
                r'(?:首先|其次|然后|最后|接着)(?:我们)?(?:要|来)?(?:讨论|看|关注|汇报|介绍)([^。！？\n,，]+)',
                r'(?:关于)([^。！？\n,，]+)',
                r'第[一二三四五12345]项(?:议程|议题|内容)?(?:是|为|：)([^。！？\n]+)',
                r'关于([^。！？\n,，]+)的(?:议题|讨论|事项|计划|方案)'
            ]
            
            for pattern in agenda_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    content = match.strip()
                    if len(content) > 4: 
                        agendas.append(content)
            
            # 策略2: 如果没有显式匹配到，或者有topics输入，利用topics
            if topics:
                for topic in topics:
                    # 优先使用 content 字段
                    content = topic.get('content')
                    if content and len(content) < 50: # 如果 content 比较短，直接作为议题
                         agendas.append(content)
                    else:
                        # 否则使用关键词
                        keywords = topic.get('keywords', [])
                        if keywords:
                            kw_str = "、".join([k[0] if isinstance(k, tuple) else k for k in keywords[:3]])
                            agendas.append(f"关于 {kw_str} 的讨论")
            
            # 策略3：如果以上都没有，尝试分析第一句话（通常包含会议主题）
            if not agendas:
                 first_sentence = text.split('。')[0]
                 if "会议" in first_sentence or "讨论" in first_sentence:
                      agendas.append(first_sentence)

            # 去重并限制数量
            unique_agendas = []
            seen = set()
            for agenda in agendas:
                if agenda not in seen:
                    unique_agendas.append(agenda)
                    seen.add(agenda)
            
            return unique_agendas
            
        except Exception as e:
            logger.error(f"议程提取失败: {e}")
            return []

    def extract_decisions(self, text: str) -> List[str]:
        """
        提取会议决议
        """
        decisions = []
        if not text:
            return []
            
        try:
            # 增强匹配模式
            decision_patterns = [
                r'(?:决议|决定|结论|共识)(?:如下|包括|是|为)?[:：\s]([^。！？\n]+)',
                r'(?:一致|原则|最终|大家)?(?:同意|批准|通过|确认|确定)(?:了)?([^。！？\n]+)',
                r'会议(?:认为|指出|强调|要求|还指出)(?:，|:)?([^。！？\n]+)',
                r'(?:将|会)(?:在|于)([^。！？\n]+)(?:上线|发布|完成)',
                r'(?:预算|资金)(?:定为|为|是)([^。！？\n]+)'
            ]
            
            for pattern in decision_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    content = match.strip()
                    if len(content) > 4:
                        decisions.append(content)
            
            # 简单的启发式补充：包含"同意"、"确定"的关键句
            if not decisions:
                sentences = self.split_sentences(text)
                for sent in sentences:
                    if any(k in sent for k in ["同意", "批准", "确定", "通过", "预算"]):
                         if len(sent) < 100: # 避免提取过长的句子
                            decisions.append(sent)

            unique_decisions = []
            seen = set()
            for d in decisions:
                if d not in seen:
                    unique_decisions.append(d)
                    seen.add(d)
                    
            return unique_decisions
            
        except Exception as e:
            logger.error(f"决议提取失败: {e}")
            return []

    def extract_action_items(self, text: str) -> List[Dict[str, str]]:
        """
        提取Action Items (待办事项)
        
        Args:
            text: 全文内容
            
        Returns:
            待办事项列表，每项包含:
            - content: 内容
            - owner: 负责人
            - due_date: 截止日期
        """
        action_items = []
        
        if not text:
            return []
            
        try:
            # 1. 识别待办事项句子
            # 模式: "请xxx完成..."、"xxx负责..."、"需要xxx..."
            sentences = self.split_sentences(text)
            
            action_keywords = ['请', '需要', '负责', '任务', '待办', '下一步', '行动']
            
            for sent in sentences:
                is_action = False
                
                # 简单关键词过滤
                if any(kw in sent for kw in action_keywords):
                    is_action = True
                
                if is_action:
                    # 尝试提取负责人 (Owner)
                    # 策略: 寻找句子中的人名 (nr)
                    owner = "待定"
                    if jieba and pseg:
                        words = pseg.cut(sent)
                        for w, f in words:
                            if f == 'nr' and len(w) > 1:
                                owner = w
                                break # 取第一个提到的人名作为负责人
                    
                    # 尝试提取截止日期 (Due Date)
                    # 策略: 寻找日期时间模式
                    due_date = "待定"
                    date_pattern = r'(\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|下周[一二三四五六日]|本周[一二三四五六日]|明天|后天|月底|年底)'
                    date_match = re.search(date_pattern, sent)
                    if date_match:
                        due_date = date_match.group(1)
                    
                    # 清洗内容 (移除 "请"、"负责" 等起始词，但这比较复杂，暂时保留原句)
                    # 简单的清洗：移除 "Action Item:" 前缀等
                    content = re.sub(r'^(?:Action Items?|待办事项)[:：\s]*', '', sent, flags=re.IGNORECASE)
                    
                    # 只有当包含明确的指派或动作时才认为是Action Item
                    # 这里为了演示，只要含有关键词就算
                    if len(content) > 5:
                        action_items.append({
                            "content": content,
                            "owner": owner,
                            "due_date": due_date
                        })
            
            return action_items
            
        except Exception as e:
            logger.error(f"待办事项提取失败: {e}")
            return []
    
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
