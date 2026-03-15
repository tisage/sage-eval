"""
Concept Density Metrics for SAGE Framework Layer 3

概念密度分析
"""

from typing import Dict, List, Tuple, Optional
import re
from collections import Counter


class ConceptDensityAnalyzer:
    """
    概念密度分析器

    识别抽象概念和具体概念，分析思想深度

    实现指标：
    - 抽象概念密度 (Abstract Concept Density)
    - 具体概念密度 (Concrete Concept Density)
    - 抽象/具体比率 (Abstract/Concrete Ratio)
    """

    def __init__(self):
        """初始化概念密度分析器"""

        # 抽象概念词汇（哲学、情感、价值观等）
        self.abstract_concepts = {
            # 哲学概念
            'truth', 'beauty', 'justice', 'freedom', 'equality', 'democracy',
            'liberty', 'morality', 'ethics', 'virtue', 'wisdom', 'knowledge',
            'existence', 'reality', 'consciousness', 'soul', 'spirit', 'faith',

            # 情感与心理
            'love', 'hate', 'fear', 'hope', 'despair', 'joy', 'sorrow',
            'happiness', 'sadness', 'anger', 'pride', 'shame', 'guilt',
            'jealousy', 'envy', 'compassion', 'empathy', 'sympathy',

            # 社会与价值
            'power', 'authority', 'responsibility', 'duty', 'honor', 'dignity',
            'respect', 'trust', 'loyalty', 'betrayal', 'courage', 'cowardice',
            'sacrifice', 'redemption', 'forgiveness', 'revenge', 'fate',
            'destiny', 'fortune', 'luck', 'chance',

            # 时间与变化
            'eternity', 'infinity', 'mortality', 'immortality', 'memory',
            'nostalgia', 'progress', 'decline', 'evolution', 'revolution',

            # 关系与联系
            'friendship', 'kinship', 'community', 'society', 'culture',
            'tradition', 'identity', 'belonging', 'alienation', 'isolation',

            # 认知与理解
            'understanding', 'ignorance', 'perception', 'illusion', 'delusion',
            'reason', 'logic', 'intuition', 'imagination', 'creativity',

            # 其他抽象概念
            'meaning', 'purpose', 'significance', 'value', 'worth', 'essence',
            'nature', 'quality', 'quantity', 'form', 'substance', 'principle',
            'concept', 'idea', 'thought', 'belief', 'opinion', 'theory'
        }

        # 具体概念词汇（物体、动作、感官等）
        self.concrete_indicators = {
            # 感官动词
            'see', 'saw', 'seen', 'look', 'watch', 'observe',
            'hear', 'heard', 'listen', 'sound',
            'touch', 'feel', 'felt', 'hold', 'grasp',
            'smell', 'taste',

            # 物理动作
            'walk', 'run', 'jump', 'sit', 'stand', 'lie',
            'open', 'close', 'push', 'pull', 'carry', 'drop',
            'eat', 'drink', 'sleep', 'wake',

            # 颜色
            'red', 'blue', 'green', 'yellow', 'black', 'white',
            'brown', 'gray', 'purple', 'orange', 'pink',

            # 尺寸与形状
            'big', 'small', 'large', 'tiny', 'huge', 'little',
            'round', 'square', 'long', 'short', 'tall', 'wide',

            # 材质
            'wood', 'stone', 'metal', 'glass', 'paper', 'cloth',
            'gold', 'silver', 'iron', 'steel',

            # 自然物
            'tree', 'flower', 'grass', 'leaf', 'root', 'branch',
            'sun', 'moon', 'star', 'sky', 'cloud', 'rain',
            'mountain', 'river', 'ocean', 'lake', 'forest',

            # 人造物
            'house', 'door', 'window', 'wall', 'floor', 'roof',
            'table', 'chair', 'bed', 'book', 'pen', 'paper',
            'car', 'road', 'bridge', 'building', 'street'
        }

    def tokenize(self, text: str) -> List[str]:
        """分词"""
        words = re.findall(r'\b[a-z]+\b', text.lower())
        return words

    def count_abstract_concepts(self, text: str) -> int:
        """统计抽象概念词数量"""
        words = self.tokenize(text)
        count = sum(1 for w in words if w in self.abstract_concepts)
        return count

    def count_concrete_concepts(self, text: str) -> int:
        """统计具体概念词数量"""
        words = self.tokenize(text)
        count = sum(1 for w in words if w in self.concrete_indicators)
        return count

    def calculate_abstract_density(
        self,
        abstract_count: int,
        total_words: int
    ) -> float:
        """
        计算抽象概念密度

        抽象密度 = 抽象词数 / 总词数
        """
        if total_words == 0:
            return 0.0

        return abstract_count / total_words

    def calculate_concrete_density(
        self,
        concrete_count: int,
        total_words: int
    ) -> float:
        """
        计算具体概念密度

        具体密度 = 具体词数 / 总词数
        """
        if total_words == 0:
            return 0.0

        return concrete_count / total_words

    def calculate_abstraction_ratio(
        self,
        abstract_count: int,
        concrete_count: int
    ) -> float:
        """
        计算抽象/具体比率

        比率 = 抽象词数 / 具体词数

        高比率 = 偏向抽象思考
        低比率 = 偏向具体描述
        """
        if concrete_count == 0:
            return float('inf') if abstract_count > 0 else 0.0

        return abstract_count / concrete_count

    def identify_key_concepts(
        self,
        text: str,
        top_k: int = 5
    ) -> Tuple[List[str], List[str]]:
        """
        识别关键抽象和具体概念

        Returns:
            (top_abstract, top_concrete)
        """
        words = self.tokenize(text)

        # 统计出现次数
        abstract_counts = Counter(
            w for w in words if w in self.abstract_concepts
        )

        concrete_counts = Counter(
            w for w in words if w in self.concrete_indicators
        )

        top_abstract = [w for w, _ in abstract_counts.most_common(top_k)]
        top_concrete = [w for w, _ in concrete_counts.most_common(top_k)]

        return top_abstract, top_concrete

    def calculate_all(self, text: str) -> Dict[str, any]:
        """
        计算所有概念密度指标

        Args:
            text: 输入文本

        Returns:
            {
                "abstract_density": float,
                "concrete_density": float,
                "abstraction_ratio": float,
                "abstract_count": int,
                "concrete_count": int,
                "total_words": int,
                "key_abstract_concepts": List[str],
                "key_concrete_concepts": List[str]
            }
        """
        words = self.tokenize(text)
        total_words = len(words)

        abstract_count = self.count_abstract_concepts(text)
        concrete_count = self.count_concrete_concepts(text)

        abstract_density = self.calculate_abstract_density(
            abstract_count, total_words
        )
        concrete_density = self.calculate_concrete_density(
            concrete_count, total_words
        )
        abstraction_ratio = self.calculate_abstraction_ratio(
            abstract_count, concrete_count
        )

        key_abstract, key_concrete = self.identify_key_concepts(text)

        return {
            "abstract_density": abstract_density,
            "concrete_density": concrete_density,
            "abstraction_ratio": abstraction_ratio,
            "abstract_count": abstract_count,
            "concrete_count": concrete_count,
            "total_words": total_words,
            "key_abstract_concepts": key_abstract,
            "key_concrete_concepts": key_concrete
        }

    def score_concept_density(
        self,
        abstract_density: float,
        abstraction_ratio: float,
        density_weight: float = 0.6,
        ratio_weight: float = 0.4
    ) -> Tuple[float, Dict[str, float]]:
        """
        将概念密度指标映射到1-5分制

        映射规则：
        - 抽象密度: 0.01→1分, 0.05→5分
        - 抽象/具体比率: 0.2→1分, 1.0→5分

        高思想深度 = 高抽象密度 + 适中比率

        Args:
            abstract_density: 抽象概念密度
            abstraction_ratio: 抽象/具体比率
            density_weight: 密度权重
            ratio_weight: 比率权重

        Returns:
            (综合分数, {density_score, ratio_score})
        """
        # 抽象密度映射
        if abstract_density < 0.01:
            density_score = 1.0
        elif abstract_density > 0.05:
            density_score = 5.0
        else:
            density_score = 1.0 + (abstract_density - 0.01) / 0.04 * 4.0

        # 比率映射
        # 注意：过高的比率（>2.0）可能意味着缺乏具体支撑
        if abstraction_ratio < 0.2:
            ratio_score = 1.0
        elif abstraction_ratio > 2.0:
            # 过度抽象，扣分
            ratio_score = 3.0
        elif abstraction_ratio > 1.0:
            ratio_score = 5.0
        else:
            ratio_score = 1.0 + (abstraction_ratio - 0.2) / 0.8 * 4.0

        # 加权平均
        final_score = (
            density_weight * density_score +
            ratio_weight * ratio_score
        )

        return final_score, {
            "density_score": density_score,
            "ratio_score": ratio_score
        }


# ==================== 辅助函数 ====================

def analyze_concept_density(text: str) -> Dict[str, any]:
    """
    便捷函数：分析概念密度

    Args:
        text: 输入文本

    Returns:
        包含所有指标的字典
    """
    analyzer = ConceptDensityAnalyzer()
    return analyzer.calculate_all(text)
