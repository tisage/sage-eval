"""
Theme Extraction Metrics for SAGE Framework Layer 3

主题提取分析
"""

from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
import re
import math


class ThemeExtractor:
    """
    主题提取器

    基于TF-IDF和词频分析提取主题关键词

    实现指标：
    - 主题关键词提取 (Theme Keywords)
    - 主题一致性 (Theme Consistency)
    - 主题多样性 (Theme Diversity)
    """

    def __init__(self, top_k: int = 10):
        """
        初始化主题提取器

        Args:
            top_k: 提取的主题关键词数量
        """
        self.top_k = top_k

        # 停用词列表（基础英文停用词）
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'she', 'her', 'his', 'they', 'them',
            'i', 'you', 'we', 'or', 'but', 'if', 'not', 'this', 'have', 'had',
            'were', 'been', 'being', 'do', 'does', 'did', 'can', 'could',
            'would', 'should', 'may', 'might', 'must', 'shall', 'so', 'than',
            'such', 'no', 'nor', 'too', 'very', 'just', 'where', 'when',
            'what', 'which', 'who', 'how', 'all', 'each', 'every', 'both',
            'few', 'more', 'most', 'other', 'some', 'any', 'many', 'much'
        }

    def tokenize(self, text: str) -> List[str]:
        """
        分词并清理

        Returns:
            词语列表（已去除停用词和标点）
        """
        # 转小写，提取单词
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())

        # 去除停用词
        words = [w for w in words if w not in self.stopwords]

        return words

    def calculate_tf(self, words: List[str]) -> Dict[str, float]:
        """
        计算词频 (Term Frequency)

        TF(t) = count(t) / total_words
        """
        total = len(words)
        if total == 0:
            return {}

        word_counts = Counter(words)

        tf = {word: count / total for word, count in word_counts.items()}

        return tf

    def calculate_tfidf(
        self,
        text: str,
        segment_size: int = 200
    ) -> Dict[str, float]:
        """
        计算TF-IDF分数

        将文本分段作为"文档集合"，计算每个词的TF-IDF

        Args:
            text: 输入文本
            segment_size: 分段大小（词数）

        Returns:
            {word: tfidf_score}
        """
        words = self.tokenize(text)

        if not words:
            return {}

        # 分段
        segments = []
        for i in range(0, len(words), segment_size):
            segment = words[i:i+segment_size]
            if segment:
                segments.append(segment)

        if not segments:
            return {}

        # 计算IDF
        num_segments = len(segments)
        doc_freq = defaultdict(int)  # 包含该词的段落数

        for segment in segments:
            unique_words = set(segment)
            for word in unique_words:
                doc_freq[word] += 1

        idf = {
            word: math.log(num_segments / df)
            for word, df in doc_freq.items()
        }

        # 计算全局TF
        tf = self.calculate_tf(words)

        # TF-IDF
        tfidf = {
            word: tf[word] * idf.get(word, 0)
            for word in tf
        }

        return tfidf

    def extract_keywords(
        self,
        text: str,
        segment_size: int = 200
    ) -> List[Tuple[str, float]]:
        """
        提取主题关键词

        使用TF-IDF提取top_k个关键词

        Returns:
            [(word, tfidf_score), ...]
        """
        tfidf = self.calculate_tfidf(text, segment_size)

        # 按分数排序
        sorted_words = sorted(
            tfidf.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_words[:self.top_k]

    def calculate_theme_consistency(
        self,
        keywords: List[Tuple[str, float]],
        text: str,
        window_size: int = 100
    ) -> float:
        """
        计算主题一致性

        通过滑动窗口检查关键词在文本中的分布均匀性

        高一致性 = 关键词在全文均匀分布
        低一致性 = 关键词集中在某些区域

        Returns:
            一致性分数 [0, 1]
        """
        if not keywords:
            return 0.0

        words = self.tokenize(text)
        if len(words) < window_size:
            return 1.0  # 文本太短，默认一致

        keyword_set = {kw[0] for kw in keywords}

        # 滑动窗口统计关键词密度
        densities = []
        for i in range(0, len(words) - window_size + 1, window_size // 2):
            window = words[i:i+window_size]
            keyword_count = sum(1 for w in window if w in keyword_set)
            density = keyword_count / window_size
            densities.append(density)

        if len(densities) < 2:
            return 1.0

        # 计算密度的变异系数（CV）
        # CV = std / mean，越小越一致
        mean_density = sum(densities) / len(densities)

        if mean_density == 0:
            return 0.0

        variance = sum((d - mean_density) ** 2 for d in densities) / len(densities)
        std = math.sqrt(variance)

        cv = std / mean_density

        # 转换为一致性分数：CV越小，一致性越高
        # CV=0 → consistency=1.0
        # CV=1 → consistency=0.5
        # CV>2 → consistency≈0
        consistency = 1.0 / (1.0 + cv)

        return consistency

    def calculate_theme_diversity(
        self,
        keywords: List[Tuple[str, float]]
    ) -> float:
        """
        计算主题多样性

        基于关键词的TF-IDF分数分布

        高多样性 = 多个关键词分数接近（多主题）
        低多样性 = 少数关键词分数很高（单一主题）

        Returns:
            多样性分数 [0, 1]
        """
        if len(keywords) < 2:
            return 0.0

        scores = [kw[1] for kw in keywords]
        total_score = sum(scores)

        if total_score == 0:
            return 0.0

        # 计算归一化分数的熵
        probs = [s / total_score for s in scores]

        entropy = -sum(p * math.log2(p) for p in probs if p > 0)

        # 最大熵 = log2(n)
        max_entropy = math.log2(len(keywords))

        # 归一化到[0,1]
        diversity = entropy / max_entropy if max_entropy > 0 else 0.0

        return diversity

    def calculate_all(
        self,
        text: str,
        segment_size: int = 200
    ) -> Dict[str, any]:
        """
        计算所有主题提取指标

        Args:
            text: 输入文本
            segment_size: TF-IDF分段大小

        Returns:
            {
                "keywords": [(word, score), ...],
                "theme_consistency": float,
                "theme_diversity": float,
                "keyword_count": int
            }
        """
        keywords = self.extract_keywords(text, segment_size)
        consistency = self.calculate_theme_consistency(keywords, text)
        diversity = self.calculate_theme_diversity(keywords)

        return {
            "keywords": keywords,
            "theme_consistency": consistency,
            "theme_diversity": diversity,
            "keyword_count": len(keywords)
        }

    def score_theme_extraction(
        self,
        theme_consistency: float,
        theme_diversity: float,
        consistency_weight: float = 0.5,
        diversity_weight: float = 0.5
    ) -> Tuple[float, Dict[str, float]]:
        """
        将主题提取指标映射到1-5分制

        映射规则：
        - 一致性: 0.3→1分, 0.7→5分
        - 多样性: 0.4→1分, 0.8→5分

        Args:
            theme_consistency: 主题一致性
            theme_diversity: 主题多样性
            consistency_weight: 一致性权重
            diversity_weight: 多样性权重

        Returns:
            (综合分数, {consistency_score, diversity_score})
        """
        # 一致性映射
        if theme_consistency < 0.3:
            consistency_score = 1.0
        elif theme_consistency > 0.7:
            consistency_score = 5.0
        else:
            consistency_score = 1.0 + (theme_consistency - 0.3) / 0.4 * 4.0

        # 多样性映射
        if theme_diversity < 0.4:
            diversity_score = 1.0
        elif theme_diversity > 0.8:
            diversity_score = 5.0
        else:
            diversity_score = 1.0 + (theme_diversity - 0.4) / 0.4 * 4.0

        # 加权平均（归一化）
        total_weight = consistency_weight + diversity_weight
        if total_weight > 0:
            final_score = (
                consistency_weight * consistency_score +
                diversity_weight * diversity_score
            ) / total_weight
        else:
            final_score = 0.0

        return final_score, {
            "consistency_score": consistency_score,
            "diversity_score": diversity_score
        }


# ==================== 辅助函数 ====================

def extract_themes(text: str, top_k: int = 10) -> Dict[str, any]:
    """
    便捷函数：提取主题

    Args:
        text: 输入文本
        top_k: 关键词数量

    Returns:
        包含所有指标的字典
    """
    extractor = ThemeExtractor(top_k=top_k)
    return extractor.calculate_all(text)
