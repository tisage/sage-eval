"""
Lexical Diversity Metrics for SAGE Framework Layer 1

词汇多样性指标实现
"""

from typing import List, Dict, Tuple
import re


class LexicalDiversityCalculator:
    """
    词汇多样性计算器

    实现指标：
    - TTR (Type-Token Ratio)
    - MTLD (Measure of Textual Lexical Diversity)
    """

    def __init__(self):
        pass

    def tokenize(self, text: str) -> List[str]:
        """
        简单的分词器（基于空格和标点）

        Args:
            text: 输入文本

        Returns:
            token列表
        """
        # 转换为小写
        text = text.lower()

        # 使用正则分词（保留单词和连字符）
        tokens = re.findall(r'\b[\w\'-]+\b', text)

        return tokens

    def calculate_ttr(self, tokens: List[str]) -> float:
        """
        计算Type-Token Ratio (TTR)

        TTR = unique_words / total_words

        Args:
            tokens: token列表

        Returns:
            TTR值 (0-1之间)
        """
        if len(tokens) == 0:
            return 0.0

        unique_tokens = len(set(tokens))
        total_tokens = len(tokens)

        return unique_tokens / total_tokens

    def calculate_mtld(
        self,
        tokens: List[str],
        threshold: float = 0.72
    ) -> float:
        """
        计算Measure of Textual Lexical Diversity (MTLD)

        MTLD是更稳健的词汇多样性指标，不受文本长度影响

        算法：
        1. 从文本开头开始，逐词增加，计算累积TTR
        2. 当TTR降到阈值以下时，记录factor长度
        3. 重复直到文本结束
        4. MTLD = 总词数 / factor数量

        Args:
            tokens: token列表
            threshold: TTR阈值（默认0.72）

        Returns:
            MTLD值（越高越好，典型值50-100）
        """
        total_tokens = len(tokens)

        if total_tokens < 50:  # MTLD需要最小词数
            return 0.0

        def forward_mtld(token_list: List[str]) -> float:
            """正向计算MTLD"""
            factors = 0
            current_types = set()
            current_tokens = 0
            current_ttr = 1.0

            for token in token_list:
                current_types.add(token)
                current_tokens += 1
                current_ttr = len(current_types) / current_tokens

                if current_ttr <= threshold:
                    factors += 1
                    current_types = set()
                    current_tokens = 0
                    current_ttr = 1.0

            # 处理最后不完整的factor
            if current_tokens > 0:
                factors += (1 - current_ttr) / (1 - threshold)

            return total_tokens / factors if factors > 0 else total_tokens

        # 双向计算并取平均（更稳健）
        forward = forward_mtld(tokens)
        backward = forward_mtld(tokens[::-1])

        return (forward + backward) / 2

    def calculate_all(self, text: str) -> Dict[str, float]:
        """
        计算所有词汇多样性指标

        Args:
            text: 输入文本

        Returns:
            {
                "ttr": float,
                "mtld": float,
                "token_count": int,
                "type_count": int
            }
        """
        tokens = self.tokenize(text)

        ttr = self.calculate_ttr(tokens)
        mtld = self.calculate_mtld(tokens)

        return {
            "ttr": ttr,
            "mtld": mtld,
            "token_count": len(tokens),
            "type_count": len(set(tokens))
        }

    def score_lexical_diversity(
        self,
        ttr: float,
        mtld: float,
        ttr_weight: float = 0.4,
        mtld_weight: float = 0.6
    ) -> Tuple[float, Dict[str, float]]:
        """
        将指标映射到1-5分制

        映射规则（基于经验值）：
        - TTR: 0.55→1分, 0.70→5分
        - MTLD: 40→1分, 100→5分

        Args:
            ttr: TTR值
            mtld: MTLD值
            ttr_weight: TTR权重（从配置读取）
            mtld_weight: MTLD权重（从配置读取）

        Returns:
            (综合分数, {ttr_score, mtld_score})
        """
        # TTR映射到1-5分
        if ttr < 0.55:
            ttr_score = 1.0
        elif ttr > 0.70:
            ttr_score = 5.0
        else:
            # 线性插值
            ttr_score = 1.0 + (ttr - 0.55) / 0.15 * 4.0

        # MTLD映射到1-5分
        if mtld < 40:
            mtld_score = 1.0
        elif mtld > 100:
            mtld_score = 5.0
        else:
            # 线性插值
            mtld_score = 1.0 + (mtld - 40) / 60 * 4.0

        # 加权平均
        final_score = ttr_weight * ttr_score + mtld_weight * mtld_score

        return final_score, {
            "ttr_score": ttr_score,
            "mtld_score": mtld_score
        }


# ==================== 辅助函数 ====================

def calculate_lexical_diversity(text: str) -> Dict[str, float]:
    """
    便捷函数：计算词汇多样性指标

    Args:
        text: 输入文本

    Returns:
        包含所有指标的字典
    """
    calculator = LexicalDiversityCalculator()
    return calculator.calculate_all(text)
