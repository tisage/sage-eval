"""
Event Sequence Metrics for SAGE Framework Layer 2

事件序列分析
"""

from typing import Dict, List, Tuple, Optional
import re
from collections import Counter


class EventSequenceAnalyzer:
    """
    事件序列分析器

    基于动词提取和时态分析评估叙事结构

    实现指标：
    - 事件数量和分布 (Event Count & Distribution)
    - 时间线一致性 (Temporal Consistency)
    - 动作密度 (Action Density)
    """

    def __init__(self, use_spacy: bool = False, spacy_model: str = "en_core_web_sm"):
        """
        初始化事件分析器

        Args:
            use_spacy: 是否使用spaCy（精确的词性标注）
            spacy_model: spaCy模型名称
        """
        self.use_spacy = use_spacy
        self.nlp = None

        if use_spacy:
            try:
                import spacy
                self.nlp = spacy.load(spacy_model)
            except (ImportError, OSError):
                print("Warning: spaCy not available. Using basic verb detection.")
                self.use_spacy = False

        # 常见动词词尾（用于基础版本）
        self.verb_patterns = [
            r'\b\w+ed\b',      # 过去式 -ed
            r'\b\w+ing\b',     # 进行时 -ing
            r'\b\w+s\b',       # 第三人称单数 -s
        ]

        # 常见动作动词
        self.action_verbs = {
            'go', 'come', 'walk', 'run', 'move', 'take', 'give', 'make',
            'see', 'look', 'watch', 'hear', 'listen', 'say', 'tell', 'speak',
            'think', 'know', 'feel', 'want', 'get', 'put', 'hold', 'turn',
            'find', 'bring', 'leave', 'sit', 'stand', 'open', 'close', 'write',
            'read', 'ask', 'answer', 'call', 'show', 'try', 'use', 'work'
        }

    def extract_verbs(self, text: str) -> List[Dict[str, str]]:
        """
        提取动词及其时态

        Returns:
            [
                {"verb": "walked", "lemma": "walk", "tense": "past"},
                ...
            ]
        """
        verbs = []

        if self.use_spacy and self.nlp is not None:
            # 使用spaCy精确识别
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ == "VERB":
                    # 判断时态
                    if "Past" in token.morph.get("Tense", []):
                        tense = "past"
                    elif "Pres" in token.morph.get("Tense", []):
                        tense = "present"
                    else:
                        tense = "other"

                    verbs.append({
                        "verb": token.text.lower(),
                        "lemma": token.lemma_.lower(),
                        "tense": tense
                    })
        else:
            # 基础版本：模式匹配
            words = re.findall(r'\b[\w\'-]+\b', text.lower())

            for word in words:
                # 判断是否可能是动词
                is_verb = False
                tense = "unknown"

                if word.endswith('ed'):
                    is_verb = True
                    tense = "past"
                elif word.endswith('ing'):
                    is_verb = True
                    tense = "present"
                elif word in self.action_verbs:
                    is_verb = True
                    tense = "present"

                if is_verb:
                    verbs.append({
                        "verb": word,
                        "lemma": word.rstrip('ed').rstrip('ing').rstrip('s'),
                        "tense": tense
                    })

        return verbs

    def calculate_event_count(self, verbs: List[Dict[str, str]]) -> int:
        """计算事件数量（动词数量）"""
        return len(verbs)

    def calculate_action_density(
        self,
        verbs: List[Dict[str, str]],
        total_words: int
    ) -> float:
        """
        计算动作密度

        动作密度 = 动词数 / 总词数
        """
        if total_words == 0:
            return 0.0

        return len(verbs) / total_words

    def calculate_tense_distribution(
        self,
        verbs: List[Dict[str, str]]
    ) -> Dict[str, float]:
        """
        计算时态分布

        Returns:
            {"past": 0.6, "present": 0.3, "other": 0.1}
        """
        if not verbs:
            return {"past": 0.0, "present": 0.0, "other": 0.0}

        tense_counts = Counter(v["tense"] for v in verbs)
        total = len(verbs)

        return {
            tense: count / total
            for tense, count in tense_counts.items()
        }

    def calculate_tense_shifts(self, verbs: List[Dict[str, str]]) -> int:
        """
        计算时态转换次数

        过多的时态转换可能表示叙事不一致
        """
        if len(verbs) < 2:
            return 0

        shifts = 0
        prev_tense = verbs[0]["tense"]

        for verb in verbs[1:]:
            if verb["tense"] != prev_tense and verb["tense"] != "unknown":
                shifts += 1
                prev_tense = verb["tense"]

        return shifts

    def calculate_verb_diversity(self, verbs: List[Dict[str, str]]) -> float:
        """
        计算动词多样性

        TTR for verbs
        """
        if not verbs:
            return 0.0

        lemmas = [v["lemma"] for v in verbs]
        unique_verbs = len(set(lemmas))
        total_verbs = len(lemmas)

        return unique_verbs / total_verbs if total_verbs > 0 else 0.0

    def calculate_all(self, text: str) -> Dict[str, any]:
        """
        计算所有事件序列指标

        Args:
            text: 输入文本

        Returns:
            {
                "event_count": int,
                "action_density": float,
                "tense_distribution": Dict[str, float],
                "tense_shifts": int,
                "verb_diversity": float,
                "total_words": int
            }
        """
        verbs = self.extract_verbs(text)
        total_words = len(text.split())

        event_count = self.calculate_event_count(verbs)
        action_density = self.calculate_action_density(verbs, total_words)
        tense_dist = self.calculate_tense_distribution(verbs)
        tense_shifts = self.calculate_tense_shifts(verbs)
        verb_diversity = self.calculate_verb_diversity(verbs)

        return {
            "event_count": event_count,
            "action_density": action_density,
            "tense_distribution": tense_dist,
            "tense_shifts": tense_shifts,
            "verb_diversity": verb_diversity,
            "total_words": total_words
        }

    def score_event_sequence(
        self,
        action_density: float,
        verb_diversity: float,
        tense_shifts: int,
        total_words: int,
        density_weight: float = 0.4,
        diversity_weight: float = 0.3,
        consistency_weight: float = 0.3
    ) -> Tuple[float, Dict[str, float]]:
        """
        将事件序列指标映射到1-5分制

        映射规则：
        - 动作密度: 0.10→1分, 0.25→5分
        - 动词多样性: 0.40→1分, 0.70→5分
        - 时态一致性: 过多转换→低分

        Args:
            action_density: 动作密度
            verb_diversity: 动词多样性
            tense_shifts: 时态转换次数
            total_words: 总词数
            density_weight: 密度权重
            diversity_weight: 多样性权重
            consistency_weight: 一致性权重

        Returns:
            (综合分数, {density_score, diversity_score, consistency_score})
        """
        # 动作密度映射
        if action_density < 0.10:
            density_score = 1.0
        elif action_density > 0.25:
            density_score = 5.0
        else:
            density_score = 1.0 + (action_density - 0.10) / 0.15 * 4.0

        # 动词多样性映射
        if verb_diversity < 0.40:
            diversity_score = 1.0
        elif verb_diversity > 0.70:
            diversity_score = 5.0
        else:
            diversity_score = 1.0 + (verb_diversity - 0.40) / 0.30 * 4.0

        # 时态一致性映射（每100词允许1-2次转换）
        expected_shifts = max(1, total_words / 100)
        shift_ratio = tense_shifts / expected_shifts if expected_shifts > 0 else 1.0

        if shift_ratio < 0.5:
            consistency_score = 5.0  # 很少转换=高一致性
        elif shift_ratio > 3.0:
            consistency_score = 1.0  # 过多转换=低一致性
        else:
            consistency_score = 5.0 - (shift_ratio - 0.5) / 2.5 * 4.0

        # 加权平均（归一化）
        total_weight = density_weight + diversity_weight + consistency_weight
        if total_weight > 0:
            final_score = (
                density_weight * density_score +
                diversity_weight * diversity_score +
                consistency_weight * consistency_score
            ) / total_weight
        else:
            final_score = 0.0

        return final_score, {
            "density_score": density_score,
            "diversity_score": diversity_score,
            "consistency_score": consistency_score
        }


# ==================== 辅助函数 ====================

def calculate_event_sequence(text: str, use_spacy: bool = False) -> Dict[str, any]:
    """
    便捷函数：计算事件序列指标

    Args:
        text: 输入文本
        use_spacy: 是否使用spaCy

    Returns:
        包含所有指标的字典
    """
    analyzer = EventSequenceAnalyzer(use_spacy=use_spacy)
    return analyzer.calculate_all(text)
