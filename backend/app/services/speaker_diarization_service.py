
import os
import numpy as np
import librosa
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)

class SpeakerDiarizationService:
    """
    基于 MFCC 特征聚类的轻量级声纹识别/角色分离服务
    不依赖重型深度学习模型 (如 pyannote.audio)，适合快速部署和低资源环境
    """
    
    def __init__(self):
        pass

    def diarize(self, audio_path: str, segments: List[Dict], num_speakers: int = None) -> List[Dict]:
        """
        对 Whisper 转录生成的片段进行说话人分离
        
        Args:
            audio_path: 音频文件路径
            segments: Whisper 生成的 segments 列表，每个元素需包含 'start', 'end', 'text'
            num_speakers: 预期的说话人数（可选）。如果未指定，将尝试自动推断（默认2-5人）
            
        Returns:
            添加了 'speaker' 字段的 segments 列表
        """
        if not segments:
            return []
            
        try:
            logger.info(f"开始声纹识别: {audio_path}, 片段数: {len(segments)}")
            
            # 1. 提取特征
            features = self._extract_features(audio_path, segments)
            
            if not features:
                logger.warning("未能提取有效音频特征，跳过聚类")
                return self._assign_default_speakers(segments)
                
            # 2. 特征标准化
            scaler = StandardScaler()
            X = scaler.fit_transform(features)
            
            # 3. 聚类
            # 如果没有指定说话人数，使用 AgglomerativeClustering 的 distance_threshold
            # 如果指定了，则使用 n_clusters
            if num_speakers:
                clustering = AgglomerativeClustering(n_clusters=num_speakers)
            else:
                # 距离阈值调整：
                # 原始值 10.0 可能过小，导致同一个人的不同语气被聚类为不同的人
                # 调大阈值可以减少聚类簇的数量（即减少识别出的说话人数）
                # 建议尝试 30.0 - 50.0 范围
                clustering = AgglomerativeClustering(
                    n_clusters=None, 
                    distance_threshold=30.0, 
                    metric='euclidean',
                    linkage='ward'
                )
                
            labels = clustering.fit_predict(X)
            
            # 4. 回填结果
            diarized_segments = []
            for i, segment in enumerate(segments):
                # 复制 segment 避免修改原数据
                new_seg = segment.copy()
                new_seg['speaker'] = f"Speaker {labels[i]}"
                diarized_segments.append(new_seg)
            
            # 5. 合并同说话人的连续片段
            merged_segments = self._merge_consecutive_segments(diarized_segments)
            
            logger.info(f"声纹识别完成，识别出 {len(set(labels))} 个说话人")
            return merged_segments
            
        except Exception as e:
            logger.error(f"声纹识别失败: {e}")
            # 出错时返回默认结果，不阻断流程
            return self._assign_default_speakers(segments)

    def _extract_features(self, audio_path: str, segments: List[Dict]) -> List[np.ndarray]:
        """
        提取每个片段的音频特征 (MFCC)
        """
        features = []
        
        # 加载音频 (sr=16000 适合语音)
        y, sr = librosa.load(audio_path, sr=16000)
        duration = librosa.get_duration(y=y, sr=sr)
        
        for segment in segments:
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            
            # 边界检查
            if start_time >= duration:
                continue
            if end_time > duration:
                end_time = duration
                
            # 转换为采样点索引
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            
            # 提取片段音频
            y_seg = y[start_sample:end_sample]
            
            if len(y_seg) < 512: # 太短的片段忽略或补零，这里忽略
                # 使用一个零向量代替，避免对齐问题
                features.append(np.zeros(20)) 
                continue
                
            # 计算 MFCC
            # n_mfcc=20 是语音识别常用值
            mfcc = librosa.feature.mfcc(y=y_seg, sr=sr, n_mfcc=20)
            
            # 对时间轴求平均，得到该片段的定长特征向量 (shape: 20)
            mfcc_mean = np.mean(mfcc.T, axis=0)
            features.append(mfcc_mean)
            
        return features

    def _assign_default_speakers(self, segments: List[Dict]) -> List[Dict]:
        """如果失败，给所有片段分配默认说话人"""
        result = []
        for seg in segments:
            s = seg.copy()
            s['speaker'] = "Unknown Speaker"
            result.append(s)
        return result

    def _merge_consecutive_segments(self, segments: List[Dict]) -> List[Dict]:
        """合并连续且属于同一说话人的片段"""
        if not segments:
            return []
            
        merged = []
        current = segments[0]
        
        for next_seg in segments[1:]:
            # 如果说话人相同，且时间间隔很短（例如小于1秒），则合并
            # 这里简化逻辑：只要说话人相同就合并
            if current['speaker'] == next_seg['speaker']:
                current['end'] = next_seg['end']
                current['text'] += " " + next_seg['text']
            else:
                merged.append(current)
                current = next_seg
                
        merged.append(current)
        return merged

speaker_diarization_service = SpeakerDiarizationService()
