"""
Emotional Arc Metrics for SAGE Framework Layer 2

情感弧线分析
"""

from typing import Dict, List, Tuple, Optional
import re
import statistics


class EmotionalArcAnalyzer:
    """
    情感弧线分析器

    基于情感词典分析文本的情感时间线

    实现指标：
    - 情感极性时间线 (Sentiment Timeline)
    - 张力曲线 (Tension Curve)
    - 情感强度方差 (Emotional Intensity Variance)
    """

    def __init__(self, lexicon: str = "basic"):
        """
        初始化情感分析器

        Args:
            lexicon: 情感词典类型 ("basic", "extended")
        """
        self.lexicon = lexicon
        self._init_sentiment_lexicon()

    def _init_sentiment_lexicon(self):
        """初始化基础情感词典"""
        # 基础正面词汇
        self.positive_words = {
            'happy', 'joy', 'love', 'wonderful', 'excellent', 'good', 'great',
            'beautiful', 'amazing', 'fantastic', 'delightful', 'pleasant',
            'cheerful', 'bright', 'smile', 'laugh', 'hope', 'peace', 'sweet',
            'warm', 'comfort', 'tender', 'gentle', 'kind', 'lovely', 'glory',
            'triumph', 'success', 'victory', 'win', 'perfect', 'brilliant'
        }

        # 基础负面词汇
        self.negative_words = {
            'sad', 'pain', 'hate', 'terrible', 'awful', 'bad', 'poor',
            'ugly', 'horrible', 'dreadful', 'miserable', 'gloomy', 'dark',
            'cry', 'weep', 'despair', 'fear', 'anger', 'cruel', 'harsh',
            'bitter', 'cold', 'suffer', 'agony', 'grief', 'sorrow', 'doom',
            'defeat', 'fail', 'loss', 'tragedy', 'disaster', 'death', 'die'
        }

        # 高强度情感词（用于张力分析）
        self.high_intensity_words = {
            'scream', 'shout', 'rage', 'terror', 'panic', 'ecstasy',
            'devastate', 'shock', 'astonish', 'amaze', 'horrify', 'thrill',
            'passion', 'fury', 'anguish', 'rapture', 'explode', 'collapse'
        }

    def split_segments(self, text: str, segment_size: int = 100) -> List[str]:
        """
        将文本分成固定大小的片段用于时间线分析

        Args:
            text: 输入文本
            segment_size: 每个片段的词数

        Returns:
            片段列表
        """
        words = text.split()
        segments = []

        for i in range(0, len(words), segment_size):
            segment = ' '.join(words[i:i+segment_size])
            if segment.strip():
                segments.append(segment)

        return segments

    def calculate_sentiment_polarity(self, text: str) -> float:
        """
        计算文本片段的情感极性

        Returns:
            极性值 [-1, 1]
            -1 = 完全负面
             0 = 中性
            +1 = 完全正面
        """
        words = re.findall(r'\b[\w\'-]+\b', text.lower())

        positive_count = sum(1 for w in words if w in self.positive_words)
        negative_count = sum(1 for w in words if w in self.negative_words)

        total_sentiment = positive_count + negative_count

        if total_sentiment == 0:
            return 0.0

        polarity = (positive_count - negative_count) / total_sentiment
        return polarity

    def calculate_emotional_intensity(self, text: str) -> float:
        """
        计算情感强度（绝对值，不考虑极性）

        Returns:
            强度值 [0, 1]
        """
        words = re.findall(r'\b[\w\'-]+\b', text.lower())

        sentiment_count = sum(
            1 for w in words
            if w in self.positive_words or w in self.negative_words
        )

        high_intensity_count = sum(
            1 for w in words
            if w in self.high_intensity_words
        )

        # 强度 = (情感词 + 2*高强度词) / 总词数
        total_words = len(words)
        if total_words == 0:
            return 0.0

        intensity = (sentiment_count + 2 * high_intensity_count) / total_words
        return min(1.0, intensity)  # 限制在[0,1]

    def calculate_sentiment_timeline(
        self,
        text: str,
        segment_size: int = 100
    ) -> List[Dict[str, float]]:
        """
        计算情感时间线

        Args:
            text: 输入文本
            segment_size: 每个片段的词数

        Returns:
            [
                {"position": 0.1, "polarity": 0.3, "intensity": 0.5},
                ...
            ]
        """
        segments = self.split_segments(text, segment_size)

        timeline = []
        total_segments = len(segments)

        for i, segment in enumerate(segments):
            polarity = self.calculate_sentiment_polarity(segment)
            intensity = self.calculate_emotional_intensity(segment)

            timeline.append({
                "position": i / total_segments if total_segments > 1 else 0.5,
                "polarity": polarity,
                "intensity": intensity
            })

        return timeline

    def calculate_tension_curve(self, timeline: List[Dict[str, float]]) -> float:
        """
        计算张力曲线的方差

        高方差 = 情感起伏大 = 戏剧张力强
        """
        if len(timeline) < 2:
            return 0.0

        intensities = [point["intensity"] for point in timeline]

        try:
            return statistics.variance(intensities)
        except statistics.StatisticsError:
            return 0.0

    def calculate_emotional_arc_shape(
        self,
        timeline: List[Dict[str, float]]
    ) -> str:
        """
        识别情感弧线形状

        常见形状：
        - "rising": 上升（喜剧）
        - "falling": 下降（悲剧）
        - "rise-fall": 上升后下降
        - "fall-rise": 下降后上升（希望）
        - "flat": 平坦（无戏剧性）
        """
        if len(timeline) < 3:
            return "unknown"

        # 分三段：开头、中间、结尾
        third = len(timeline) // 3

        start_polarity = statistics.mean([p["polarity"] for p in timeline[:third]])
        middle_polarity = statistics.mean([p["polarity"] for p in timeline[third:2*third]])
        end_polarity = statistics.mean([p["polarity"] for p in timeline[2*third:]])

        # 判断趋势
        if end_polarity > start_polarity + 0.2:
            return "rising"
        elif end_polarity < start_polarity - 0.2:
            return "falling"
        elif middle_polarity > start_polarity and middle_polarity > end_polarity:
            return "rise-fall"
        elif middle_polarity < start_polarity and middle_polarity < end_polarity:
            return "fall-rise"
        else:
            return "flat"

    def calculate_all(
        self,
        text: str,
        segment_size: int = 100
    ) -> Dict[str, any]:
        """
        计算所有情感弧线指标

        Args:
            text: 输入文本
            segment_size: 时间线片段大小

        Returns:
            {
                "timeline": List[Dict],
                "average_polarity": float,
                "average_intensity": float,
                "tension_variance": float,
                "arc_shape": str,
                "segment_count": int
            }
        """
        timeline = self.calculate_sentiment_timeline(text, segment_size)

        if not timeline:
            return {
                "timeline": [],
                "average_polarity": 0.0,
                "average_intensity": 0.0,
                "tension_variance": 0.0,
                "arc_shape": "unknown",
                "segment_count": 0
            }

        avg_polarity = statistics.mean([p["polarity"] for p in timeline])
        avg_intensity = statistics.mean([p["intensity"] for p in timeline])
        tension = self.calculate_tension_curve(timeline)
        arc_shape = self.calculate_emotional_arc_shape(timeline)

        return {
            "timeline": timeline,  # 保留完整时间线用于可视化
            "average_polarity": avg_polarity,
            "average_intensity": avg_intensity,
            "tension_variance": tension,
            "arc_shape": arc_shape,
            "segment_count": len(timeline)
        }

    def score_emotional_arc(
        self,
        average_intensity: float,
        tension_variance: float,
        intensity_weight: float = 0.5,
        tension_weight: float = 0.5
    ) -> Tuple[float, Dict[str, float]]:
        """
        将情感弧线指标映射到1-5分制

        映射规则：
        - 平均强度: 0.05→1分, 0.20→5分
        - 张力方差: 0.001→1分, 0.05→5分

        Args:
            average_intensity: 平均情感强度
            tension_variance: 张力方差
            intensity_weight: 强度权重
            tension_weight: 张力权重

        Returns:
            (综合分数, {intensity_score, tension_score})
        """
        # 强度映射
        if average_intensity < 0.05:
            intensity_score = 1.0
        elif average_intensity > 0.20:
            intensity_score = 5.0
        else:
            intensity_score = 1.0 + (average_intensity - 0.05) / 0.15 * 4.0

        # 张力映射
        if tension_variance < 0.001:
            tension_score = 1.0
        elif tension_variance > 0.05:
            tension_score = 5.0
        else:
            tension_score = 1.0 + (tension_variance - 0.001) / 0.049 * 4.0

        # 加权平均（归一化）
        total_weight = intensity_weight + tension_weight
        if total_weight > 0:
            final_score = (
                intensity_weight * intensity_score +
                tension_weight * tension_score
            ) / total_weight
        else:
            final_score = 0.0

        return final_score, {
            "intensity_score": intensity_score,
            "tension_score": tension_score
        }


# ==================== 辅助函数 ====================

def calculate_emotional_arc(text: str, segment_size: int = 100) -> Dict[str, any]:
    """
    便捷函数：计算情感弧线指标

    Args:
        text: 输入文本
        segment_size: 时间线片段大小

    Returns:
        包含所有指标的字典
    """
    analyzer = EmotionalArcAnalyzer()
    return analyzer.calculate_all(text, segment_size)
