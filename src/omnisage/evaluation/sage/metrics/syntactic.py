"""
Syntactic Complexity Metrics for SAGE Framework Layer 1

句法复杂度指标实现
"""

from typing import List, Dict, Tuple, Optional
import re
import statistics


class SyntacticComplexityCalculator:
    """
    句法复杂度计算器

    实现指标：
    - 平均句长 (Mean Sentence Length)
    - 句长方差 (Sentence Length Variance)
    - 依存树深度 (Dependency Tree Depth) - 需要spaCy

    注意：完整功能需要spaCy。基础版本使用简化方法。
    """

    def __init__(self, use_spacy: bool = False, spacy_model: str = "en_core_web_sm"):
        """
        初始化句法分析器

        Args:
            use_spacy: 是否使用spaCy（需要安装）
            spacy_model: spaCy模型名称
        """
        self.use_spacy = use_spacy
        self.nlp = None

        if use_spacy:
            try:
                import spacy
                self.nlp = spacy.load(spacy_model)
            except ImportError:
                print("Warning: spaCy not installed. Using basic sentence splitting.")
                self.use_spacy = False
            except OSError:
                print(f"Warning: spaCy model '{spacy_model}' not found. Using basic sentence splitting.")
                self.use_spacy = False

    def split_sentences(self, text: str) -> List[str]:
        """
        分句

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        if self.use_spacy and self.nlp is not None:
            # 使用spaCy分句
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # 简单的正则分句（基于句号、问号、感叹号）
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            return sentences

    def calculate_mean_sentence_length(self, text: str) -> float:
        """
        计算平均句长（以单词数计）

        Args:
            text: 输入文本

        Returns:
            平均句长
        """
        sentences = self.split_sentences(text)

        if len(sentences) == 0:
            return 0.0

        sentence_lengths = [len(sent.split()) for sent in sentences]
        return statistics.mean(sentence_lengths)

    def calculate_sentence_length_variance(self, text: str) -> float:
        """
        计算句长方差（反映节奏变化）

        Args:
            text: 输入文本

        Returns:
            句长方差
        """
        sentences = self.split_sentences(text)

        if len(sentences) < 2:
            return 0.0

        sentence_lengths = [len(sent.split()) for sent in sentences]

        try:
            return statistics.variance(sentence_lengths)
        except statistics.StatisticsError:
            return 0.0

    def calculate_dependency_tree_depth(self, text: str) -> float:
        """
        计算依存句法树平均深度

        需要spaCy。深度反映句法嵌套复杂度。

        Args:
            text: 输入文本

        Returns:
            平均树深度（如果没有spaCy，返回0）
        """
        if not self.use_spacy or self.nlp is None:
            return 0.0

        doc = self.nlp(text)

        def get_tree_depth(token) -> int:
            """递归计算子树深度"""
            if not list(token.children):
                return 1
            return 1 + max(get_tree_depth(child) for child in token.children)

        depths = []
        for sent in doc.sents:
            # 找到句子的根节点
            root = [token for token in sent if token.dep_ == "ROOT"]
            if root:
                depths.append(get_tree_depth(root[0]))

        return statistics.mean(depths) if depths else 0.0

    def calculate_all(self, text: str) -> Dict[str, float]:
        """
        计算所有句法复杂度指标

        Args:
            text: 输入文本

        Returns:
            {
                "mean_sentence_length": float,
                "sentence_length_variance": float,
                "dependency_tree_depth": float,  # 如果没有spaCy则为0
                "sentence_count": int
            }
        """
        sentences = self.split_sentences(text)

        mean_length = self.calculate_mean_sentence_length(text)
        variance = self.calculate_sentence_length_variance(text)
        tree_depth = self.calculate_dependency_tree_depth(text)

        return {
            "mean_sentence_length": mean_length,
            "sentence_length_variance": variance,
            "dependency_tree_depth": tree_depth,
            "sentence_count": len(sentences)
        }

    def score_syntactic_complexity(
        self,
        mean_length: float,
        variance: float,
        tree_depth: float,
        length_weight: float = 0.3,
        variance_weight: float = 0.2,
        depth_weight: float = 0.5
    ) -> Tuple[float, Dict[str, float]]:
        """
        将指标映射到1-5分制

        映射规则（基于经验值）：
        - 句长: 10→1分, 25→5分
        - 方差: 0→1分, 100→5分
        - 树深度: 2→1分, 6→5分

        Args:
            mean_length: 平均句长
            variance: 句长方差
            tree_depth: 树深度
            length_weight: 句长权重
            variance_weight: 方差权重
            depth_weight: 树深度权重

        Returns:
            (综合分数, {length_score, variance_score, depth_score})
        """
        # 句长映射
        if mean_length < 10:
            length_score = 1.0
        elif mean_length > 25:
            length_score = 5.0
        else:
            length_score = 1.0 + (mean_length - 10) / 15 * 4.0

        # 方差映射
        if variance < 0:
            variance_score = 1.0
        elif variance > 100:
            variance_score = 5.0
        else:
            variance_score = 1.0 + variance / 100 * 4.0

        # 树深度映射
        if tree_depth == 0:
            # 如果没有spaCy，不计入深度得分
            depth_score = 0.0
            # 重新调整权重
            total_weight = length_weight + variance_weight
            if total_weight > 0:
                length_weight /= total_weight
                variance_weight /= total_weight
            depth_weight = 0.0
        elif tree_depth < 2:
            depth_score = 1.0
        elif tree_depth > 6:
            depth_score = 5.0
        else:
            depth_score = 1.0 + (tree_depth - 2) / 4 * 4.0

        # 加权平均
        final_score = (
            length_weight * length_score +
            variance_weight * variance_score +
            depth_weight * depth_score
        )

        return final_score, {
            "length_score": length_score,
            "variance_score": variance_score,
            "depth_score": depth_score
        }


# ==================== 辅助函数 ====================

def calculate_syntactic_complexity(text: str, use_spacy: bool = False) -> Dict[str, float]:
    """
    便捷函数：计算句法复杂度指标

    Args:
        text: 输入文本
        use_spacy: 是否使用spaCy

    Returns:
        包含所有指标的字典
    """
    calculator = SyntacticComplexityCalculator(use_spacy=use_spacy)
    return calculator.calculate_all(text)
