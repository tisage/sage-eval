"""
Entity Coherence Metrics for SAGE Framework Layer 2

实体连贯性分析（Entity Grid Model, Barzilay & Lapata 2008）
"""

from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import re
import statistics


class EntityCoherenceAnalyzer:
    """
    实体连贯性分析器

    基于Entity Grid模型（Barzilay & Lapata, 2008）
    核心思想：连贯的文本中，实体在句子间的语法角色转换有规律

    实现指标：
    - 实体密度 (Entity Density)
    - 显著实体数 (Salient Entities)
    - 角色转换熵 (Transition Entropy)
    """

    def __init__(self, use_spacy: bool = False, spacy_model: str = "en_core_web_sm"):
        """
        初始化实体分析器

        Args:
            use_spacy: 是否使用spaCy（精确的依存分析）
            spacy_model: spaCy模型名称
        """
        self.use_spacy = use_spacy
        self.nlp = None

        if use_spacy:
            try:
                import spacy
                self.nlp = spacy.load(spacy_model)
            except (ImportError, OSError):
                print("Warning: spaCy not available. Using basic entity tracking.")
                self.use_spacy = False

    def split_sentences(self, text: str) -> List[str]:
        """分句"""
        if self.use_spacy and self.nlp is not None:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # 简单分句
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]

    def extract_entity_grid(self, text: str) -> Dict[str, List[str]]:
        """
        提取实体网格

        Returns:
            {
                "entity_name": ["S", "O", "-", "S", ...],  # 每句中的角色
                ...
            }

        角色标记:
        - "S": Subject (主语)
        - "O": Object (宾语)
        - "X": Other (其他成分)
        - "-": Absent (未出现)
        """
        sentences = self.split_sentences(text)
        entity_grid = defaultdict(lambda: ["-"] * len(sentences))

        if self.use_spacy and self.nlp is not None:
            # 使用spaCy精确识别
            for sent_idx, sent in enumerate(sentences):
                doc = self.nlp(sent)
                for token in doc:
                    if token.pos_ in ["NOUN", "PROPN", "PRON"]:
                        entity = token.lemma_.lower()

                        # 判断语法角色
                        if token.dep_ in ["nsubj", "nsubjpass"]:
                            role = "S"
                        elif token.dep_ in ["dobj", "iobj", "pobj"]:
                            role = "O"
                        else:
                            role = "X"

                        # 如果已有更重要的角色，不覆盖
                        current = entity_grid[entity][sent_idx]
                        if current == "-" or (current == "X" and role in ["S", "O"]):
                            entity_grid[entity][sent_idx] = role

        else:
            # 基础版本：使用简单的名词识别
            for sent_idx, sent in enumerate(sentences):
                words = sent.lower().split()

                # 简单识别名词（大写开头或常见名词后缀）
                nouns = []
                for word in words:
                    # 移除标点
                    word_clean = re.sub(r'[^\w]', '', word)
                    if word_clean:
                        # 简单启发式：首字母大写或以常见名词后缀结尾
                        if (word[0].isupper() or
                            any(word_clean.endswith(suffix) for suffix in
                                ['tion', 'ness', 'ment', 'er', 'or', 'ist'])):
                            nouns.append(word_clean.lower())

                # 假设句子开头的名词是主语，后面的是宾语
                for i, noun in enumerate(nouns):
                    if i == 0:
                        role = "S"
                    elif i == 1:
                        role = "O"
                    else:
                        role = "X"

                    current = entity_grid[noun][sent_idx]
                    if current == "-":
                        entity_grid[noun][sent_idx] = role

        return dict(entity_grid)

    def calculate_transition_probabilities(
        self,
        entity_grid: Dict[str, List[str]]
    ) -> Dict[Tuple[str, str], float]:
        """
        计算角色转换概率

        连贯文本的转换模式：
        - S→S（主题延续）
        - S→O（主题转换）
        更常见

        不连贯文本：
        - -→-（实体突然消失又出现）
        更随机
        """
        transitions = defaultdict(int)
        total = 0

        for entity, roles in entity_grid.items():
            for i in range(len(roles) - 1):
                transition = (roles[i], roles[i+1])
                transitions[transition] += 1
                total += 1

        # 归一化为概率
        if total == 0:
            return {}

        probs = {k: v / total for k, v in transitions.items()}
        return probs

    def calculate_entity_density(
        self,
        entity_grid: Dict[str, List[str]]
    ) -> float:
        """
        计算实体密度

        实体密度 = 总实体提及次数 / 句子数
        """
        if not entity_grid:
            return 0.0

        total_mentions = sum(
            len([r for r in roles if r != "-"])
            for roles in entity_grid.values()
        )

        sentence_count = len(next(iter(entity_grid.values())))

        return total_mentions / sentence_count if sentence_count > 0 else 0.0

    def calculate_salient_entities(
        self,
        entity_grid: Dict[str, List[str]],
        threshold: int = 2
    ) -> int:
        """
        计算显著实体数

        显著实体：在文本中出现>=threshold次的实体
        反映主线清晰度
        """
        salient_count = 0

        for roles in entity_grid.values():
            mentions = sum(1 for r in roles if r != "-")
            if mentions >= threshold:
                salient_count += 1

        return salient_count

    def calculate_transition_entropy(
        self,
        transition_probs: Dict[Tuple[str, str], float]
    ) -> float:
        """
        计算转换熵

        低熵 = 高规律 = 高连贯
        高熵 = 高随机 = 低连贯
        """
        if not transition_probs:
            return 0.0

        import math
        entropy = -sum(
            p * math.log2(p)
            for p in transition_probs.values()
            if p > 0
        )

        return entropy

    def calculate_all(self, text: str) -> Dict[str, any]:
        """
        计算所有实体连贯性指标

        Args:
            text: 输入文本

        Returns:
            {
                "entity_density": float,
                "salient_entities": int,
                "transition_entropy": float,
                "total_entities": int,
                "sentence_count": int,
                "entity_grid": dict  # 调试用
            }
        """
        entity_grid = self.extract_entity_grid(text)

        if not entity_grid:
            return {
                "entity_density": 0.0,
                "salient_entities": 0,
                "transition_entropy": 0.0,
                "total_entities": 0,
                "sentence_count": 0,
                "entity_grid": {}
            }

        density = self.calculate_entity_density(entity_grid)
        salient = self.calculate_salient_entities(entity_grid)
        trans_probs = self.calculate_transition_probabilities(entity_grid)
        entropy = self.calculate_transition_entropy(trans_probs)

        sentences = self.split_sentences(text)

        return {
            "entity_density": density,
            "salient_entities": salient,
            "transition_entropy": entropy,
            "total_entities": len(entity_grid),
            "sentence_count": len(sentences),
            "entity_grid": entity_grid  # 保留用于调试
        }

    def score_entity_coherence(
        self,
        entity_density: float,
        salient_entities: int,
        transition_entropy: float,
        density_weight: float = 0.4,
        salient_weight: float = 0.3,
        entropy_weight: float = 0.3
    ) -> Tuple[float, Dict[str, float]]:
        """
        将实体连贯性指标映射到1-5分制

        映射规则（基于经验值）：
        - 密度: 2→1分, 5→5分
        - 显著实体: 3→1分, 10→5分
        - 熵: 4→5分（低熵=高连贯）, 2→1分

        Args:
            entity_density: 实体密度
            salient_entities: 显著实体数
            transition_entropy: 转换熵
            density_weight: 密度权重
            salient_weight: 显著实体权重
            entropy_weight: 熵权重

        Returns:
            (综合分数, {density_score, salient_score, entropy_score})
        """
        # 密度映射
        if entity_density < 2:
            density_score = 1.0
        elif entity_density > 5:
            density_score = 5.0
        else:
            density_score = 1.0 + (entity_density - 2) / 3 * 4.0

        # 显著实体映射
        if salient_entities < 3:
            salient_score = 1.0
        elif salient_entities > 10:
            salient_score = 5.0
        else:
            salient_score = 1.0 + (salient_entities - 3) / 7 * 4.0

        # 熵映射（注意：低熵=高分）
        if entropy_weight > 0 and transition_entropy > 0:
            if transition_entropy > 4:
                entropy_score = 1.0
            elif transition_entropy < 2:
                entropy_score = 5.0
            else:
                entropy_score = 5.0 - (transition_entropy - 2) / 2 * 4.0
        else:
            entropy_score = 3.0  # 默认中等分

        # 加权平均（归一化）
        total_weight = density_weight + salient_weight + entropy_weight
        if total_weight > 0:
            final_score = (
                density_weight * density_score +
                salient_weight * salient_score +
                entropy_weight * entropy_score
            ) / total_weight
        else:
            final_score = 0.0

        return final_score, {
            "density_score": density_score,
            "salient_score": salient_score,
            "entropy_score": entropy_score
        }


# ==================== 辅助函数 ====================

def calculate_entity_coherence(text: str, use_spacy: bool = False) -> Dict[str, any]:
    """
    便捷函数：计算实体连贯性指标

    Args:
        text: 输入文本
        use_spacy: 是否使用spaCy

    Returns:
        包含所有指标的字典
    """
    analyzer = EntityCoherenceAnalyzer(use_spacy=use_spacy)
    return analyzer.calculate_all(text)
