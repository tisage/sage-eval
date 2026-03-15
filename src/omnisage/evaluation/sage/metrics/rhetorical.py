"""
Rhetorical Density Metrics for SAGE Framework Layer 1

修辞密度指标实现
"""

from typing import Dict, Tuple, List, Optional
import re


class RhetoricalDensityCalculator:
    """
    修辞密度计算器

    实现指标：
    - 形容词比率 (Adjective Ratio)
    - 副词比率 (Adverb Ratio)
    - 比喻性语言频率 (Figurative Language Frequency) - 基于模式匹配

    注意：完整的修辞分析需要spaCy等NLP工具。
    这里实现基础版本（基于词性标注和模式匹配）
    """

    def __init__(self, use_spacy: bool = False, spacy_model: str = "en_core_web_sm"):
        """
        初始化修辞分析器

        Args:
            use_spacy: 是否使用spaCy（更精确的词性标注）
            spacy_model: spaCy模型名称
        """
        self.use_spacy = use_spacy
        self.nlp = None

        if use_spacy:
            try:
                import spacy
                self.nlp = spacy.load(spacy_model)
            except (ImportError, OSError):
                print("Warning: spaCy not available. Using pattern-based analysis.")
                self.use_spacy = False

        # 常见形容词和副词后缀
        self.adjective_suffixes = [
            'able', 'ible', 'al', 'ful', 'ic', 'ical', 'ish', 'less', 'ous', 'ious',
            'uous', 'ive', 'ative', 'itive', 'ant', 'ent', 'ary', 'ory', 'esque'
        ]

        self.adverb_suffixes = ['ly', 'wise', 'ward', 'wards']

        # 比喻性语言模式
        self.figurative_patterns = [
            # "as X as Y" 明喻
            r'\bas\s+\w+\s+as\s+',
            # "like X" 明喻
            r'\blike\s+a\s+',
            r'\blike\s+the\s+',
            # "seemed to" / "appeared to" 暗喻
            r'\bseemed\s+to\s+',
            r'\bappeared\s+to\s+',
            # 拟人化动词
            r'\b(whispered|danced|laughed|cried|sang|breathed)\b',
        ]

    def tokenize(self, text: str) -> List[str]:
        """简单分词"""
        return re.findall(r'\b[\w\'-]+\b', text.lower())

    def calculate_adjective_ratio(self, text: str) -> Tuple[float, int, int]:
        """
        计算形容词比率

        Args:
            text: 输入文本

        Returns:
            (形容词比率, 形容词数量, 总词数)
        """
        if self.use_spacy and self.nlp is not None:
            # 使用spaCy精确识别
            doc = self.nlp(text)
            total_tokens = len([token for token in doc if token.is_alpha])
            adjectives = len([token for token in doc if token.pos_ == "ADJ"])
            ratio = adjectives / total_tokens if total_tokens > 0 else 0.0
            return ratio, adjectives, total_tokens
        else:
            # 基于后缀的启发式方法
            tokens = self.tokenize(text)
            total_tokens = len(tokens)

            adjectives = 0
            for token in tokens:
                # 检查常见形容词后缀
                for suffix in self.adjective_suffixes:
                    if token.endswith(suffix) and len(token) > len(suffix) + 2:
                        adjectives += 1
                        break

            ratio = adjectives / total_tokens if total_tokens > 0 else 0.0
            return ratio, adjectives, total_tokens

    def calculate_adverb_ratio(self, text: str) -> Tuple[float, int, int]:
        """
        计算副词比率

        Args:
            text: 输入文本

        Returns:
            (副词比率, 副词数量, 总词数)
        """
        if self.use_spacy and self.nlp is not None:
            # 使用spaCy精确识别
            doc = self.nlp(text)
            total_tokens = len([token for token in doc if token.is_alpha])
            adverbs = len([token for token in doc if token.pos_ == "ADV"])
            ratio = adverbs / total_tokens if total_tokens > 0 else 0.0
            return ratio, adverbs, total_tokens
        else:
            # 基于后缀的启发式方法（主要是-ly）
            tokens = self.tokenize(text)
            total_tokens = len(tokens)

            adverbs = 0
            for token in tokens:
                # 检查常见副词后缀
                for suffix in self.adverb_suffixes:
                    if token.endswith(suffix) and len(token) > len(suffix) + 2:
                        adverbs += 1
                        break

            ratio = adverbs / total_tokens if total_tokens > 0 else 0.0
            return ratio, adverbs, total_tokens

    def calculate_figurative_language_density(self, text: str) -> Tuple[float, int]:
        """
        计算比喻性语言密度

        基于模式匹配识别明喻、暗喻、拟人等修辞手法

        Args:
            text: 输入文本

        Returns:
            (比喻性语言密度, 匹配次数)
        """
        text_lower = text.lower()
        word_count = len(text.split())

        figurative_count = 0
        for pattern in self.figurative_patterns:
            matches = re.findall(pattern, text_lower)
            figurative_count += len(matches)

        # 计算密度：每1000词中的比喻性表达数量
        density = (figurative_count / word_count * 1000) if word_count > 0 else 0.0

        return density, figurative_count

    def calculate_descriptive_density(self, text: str) -> float:
        """
        计算描述性语言密度（形容词+副词）

        Args:
            text: 输入文本

        Returns:
            描述性词汇比率
        """
        adj_ratio, _, _ = self.calculate_adjective_ratio(text)
        adv_ratio, _, _ = self.calculate_adverb_ratio(text)

        return adj_ratio + adv_ratio

    def calculate_all(self, text: str) -> Dict[str, any]:
        """
        计算所有修辞密度指标

        Args:
            text: 输入文本

        Returns:
            {
                "adjective_ratio": float,
                "adjective_count": int,
                "adverb_ratio": float,
                "adverb_count": int,
                "figurative_density": float,  # 每1000词
                "figurative_count": int,
                "descriptive_density": float,
                "total_tokens": int
            }
        """
        adj_ratio, adj_count, total_tokens = self.calculate_adjective_ratio(text)
        adv_ratio, adv_count, _ = self.calculate_adverb_ratio(text)
        fig_density, fig_count = self.calculate_figurative_language_density(text)
        desc_density = self.calculate_descriptive_density(text)

        return {
            "adjective_ratio": adj_ratio,
            "adjective_count": adj_count,
            "adverb_ratio": adv_ratio,
            "adverb_count": adv_count,
            "figurative_density": fig_density,
            "figurative_count": fig_count,
            "descriptive_density": desc_density,
            "total_tokens": total_tokens
        }

    def score_rhetorical_density(
        self,
        adjective_ratio: float,
        adverb_ratio: float,
        figurative_density: float,
        adj_weight: float = 0.4,
        adv_weight: float = 0.2,
        fig_weight: float = 0.4
    ) -> Tuple[float, Dict[str, float]]:
        """
        将修辞密度指标映射到1-5分制

        映射规则（基于经验值）：
        - 形容词比率: 0.05→1分, 0.15→5分
        - 副词比率:   0.02→1分, 0.08→5分
        - 比喻密度:   0→1分, 20/1000词→5分

        Args:
            adjective_ratio: 形容词比率
            adverb_ratio: 副词比率
            figurative_density: 比喻密度（每1000词）
            adj_weight: 形容词权重
            adv_weight: 副词权重
            fig_weight: 比喻语言权重

        Returns:
            (综合分数, {adj_score, adv_score, fig_score})
        """
        # 形容词比率映射
        if adjective_ratio < 0.05:
            adj_score = 1.0
        elif adjective_ratio > 0.15:
            adj_score = 5.0
        else:
            adj_score = 1.0 + (adjective_ratio - 0.05) / 0.10 * 4.0

        # 副词比率映射
        if adverb_ratio < 0.02:
            adv_score = 1.0
        elif adverb_ratio > 0.08:
            adv_score = 5.0
        else:
            adv_score = 1.0 + (adverb_ratio - 0.02) / 0.06 * 4.0

        # 比喻密度映射
        if figurative_density < 0:
            fig_score = 1.0
        elif figurative_density > 20:
            fig_score = 5.0
        else:
            fig_score = 1.0 + figurative_density / 20 * 4.0

        # 加权平均
        final_score = (
            adj_weight * adj_score +
            adv_weight * adv_score +
            fig_weight * fig_score
        )

        return final_score, {
            "adjective_score": adj_score,
            "adverb_score": adv_score,
            "figurative_score": fig_score
        }


# ==================== 辅助函数 ====================

def calculate_rhetorical_density(text: str, use_spacy: bool = False) -> Dict[str, any]:
    """
    便捷函数：计算修辞密度指标

    Args:
        text: 输入文本
        use_spacy: 是否使用spaCy

    Returns:
        包含所有指标的字典
    """
    calculator = RhetoricalDensityCalculator(use_spacy=use_spacy)
    return calculator.calculate_all(text)
