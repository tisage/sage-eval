"""
Layer 1: Language Layer (语言层)

核心问题：语言是否精炼、优美、有节奏？
Core Question: Is the language refined, elegant, and rhythmic?

评估方法：纯计算指标为主
"""

import time
from typing import Dict, Any, Optional

from .base_layer import BaseLayer, LayerResult, LayerType
from ..metrics.lexical import LexicalDiversityCalculator
from ..metrics.syntactic import SyntacticComplexityCalculator
from ..metrics.rhetorical import RhetoricalDensityCalculator


class Layer1Language(BaseLayer):
    """
    Layer 1: 语言层评估器

    评估维度：
    1. 词汇多样性 (Lexical Diversity)
       - TTR (Type-Token Ratio)
       - MTLD (Measure of Textual Lexical Diversity)

    2. 句法复杂度 (Syntactic Complexity)
       - 平均句长
       - 句长方差
       - 依存树深度（可选，需要spaCy）

    配置参数（从layer_metrics_config.yaml读取）：
    - lexical_diversity.ttr.weight
    - lexical_diversity.mtld.weight
    - syntactic_complexity.mean_sentence_length.weight
    - syntactic_complexity.sentence_length_variance.weight
    - syntactic_complexity.dependency_tree_depth.weight
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化Layer 1评估器

        Args:
            config: 层级配置（从YAML加载）
        """
        super().__init__(LayerType.LANGUAGE, config)

        # 初始化计算器
        self.lexical_calculator = LexicalDiversityCalculator()

        # 检查是否启用spaCy
        use_spacy = self._get_spacy_setting()
        spacy_model = self._get_spacy_model()
        self.syntactic_calculator = SyntacticComplexityCalculator(
            use_spacy=use_spacy,
            spacy_model=spacy_model
        )
        self.rhetorical_calculator = RhetoricalDensityCalculator(
            use_spacy=use_spacy,
            spacy_model=spacy_model
        )

    def _validate_config(self) -> None:
        """验证配置有效性"""
        if "enabled" not in self.config:
            raise ValueError("Layer 1 config must have 'enabled' field")

        # 检查必需的配置项
        required_sections = ["lexical_diversity", "syntactic_complexity"]
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Layer 1 config missing '{section}' section")

    def _get_spacy_setting(self) -> bool:
        """从配置获取spaCy设置"""
        try:
            syntax_config = self.config.get("syntactic_complexity", {})
            tree_depth_config = syntax_config.get("dependency_tree_depth", {})
            return tree_depth_config.get("enabled", False)
        except Exception:
            return False

    def _get_spacy_model(self) -> str:
        """从配置获取spaCy模型名称"""
        try:
            syntax_config = self.config.get("syntactic_complexity", {})
            tree_depth_config = syntax_config.get("dependency_tree_depth", {})
            return tree_depth_config.get("model", "en_core_web_sm")
        except Exception:
            return "en_core_web_sm"

    def _get_weights(self) -> Dict[str, float]:
        """从配置获取各指标权重"""
        weights = {}

        # 词汇多样性权重
        lex_config = self.config.get("lexical_diversity", {})
        weights["ttr"] = lex_config.get("ttr", {}).get("weight", 0.15)
        weights["mtld"] = lex_config.get("mtld", {}).get("weight", 0.20)

        # 句法复杂度权重
        syn_config = self.config.get("syntactic_complexity", {})
        weights["mean_length"] = syn_config.get("mean_sentence_length", {}).get("weight", 0.10)
        weights["variance"] = syn_config.get("sentence_length_variance", {}).get("weight", 0.10)
        weights["tree_depth"] = syn_config.get("dependency_tree_depth", {}).get("weight", 0.15)

        # 修辞密度权重
        rhet_config = self.config.get("rhetorical_density", {})
        weights["adjective"] = rhet_config.get("adjective_ratio", {}).get("weight", 0.05)
        weights["adverb"] = rhet_config.get("adverb_ratio", {}).get("weight", 0.05)
        weights["figurative"] = rhet_config.get("figurative_density", {}).get("weight", 0.20)

        return weights

    def evaluate(self, text: str, context: Optional[Dict[str, Any]] = None) -> LayerResult:
        """
        评估文本的语言质量

        Args:
            text: 待评估的故事文本
            context: 额外上下文（本层不使用）

        Returns:
            LayerResult对象

        Raises:
            ValueError: 文本为空或无效
        """
        start_time = time.time()

        # 验证文本
        self._check_text_validity(text)

        try:
            # 1. 计算词汇多样性指标
            lexical_metrics = self.lexical_calculator.calculate_all(text)

            # 2. 计算句法复杂度指标
            syntactic_metrics = self.syntactic_calculator.calculate_all(text)

            # 3. 计算修辞密度指标
            rhetorical_metrics = self.rhetorical_calculator.calculate_all(text)

            # 4. 获取权重
            weights = self._get_weights()

            # 5. 计算词汇多样性得分
            lex_score, lex_subscores = self.lexical_calculator.score_lexical_diversity(
                ttr=lexical_metrics["ttr"],
                mtld=lexical_metrics["mtld"],
                ttr_weight=weights["ttr"] / (weights["ttr"] + weights["mtld"]),
                mtld_weight=weights["mtld"] / (weights["ttr"] + weights["mtld"])
            )

            # 6. 计算句法复杂度得分
            syn_score, syn_subscores = self.syntactic_calculator.score_syntactic_complexity(
                mean_length=syntactic_metrics["mean_sentence_length"],
                variance=syntactic_metrics["sentence_length_variance"],
                tree_depth=syntactic_metrics["dependency_tree_depth"],
                length_weight=weights["mean_length"],
                variance_weight=weights["variance"],
                depth_weight=weights["tree_depth"]
            )

            # 7. 计算修辞密度得分
            rhet_score, rhet_subscores = self.rhetorical_calculator.score_rhetorical_density(
                adjective_ratio=rhetorical_metrics["adjective_ratio"],
                adverb_ratio=rhetorical_metrics["adverb_ratio"],
                figurative_density=rhetorical_metrics["figurative_density"],
                adj_weight=weights["adjective"],
                adv_weight=weights["adverb"],
                fig_weight=weights["figurative"]
            )

            # 8. 计算最终得分（词汇 + 句法 + 修辞）
            # 总权重归一化
            total_lex_weight = weights["ttr"] + weights["mtld"]
            total_syn_weight = weights["mean_length"] + weights["variance"] + weights["tree_depth"]
            total_rhet_weight = weights["adjective"] + weights["adverb"] + weights["figurative"]

            total_weight = total_lex_weight + total_syn_weight + total_rhet_weight

            final_score = (
                (total_lex_weight / total_weight) * lex_score +
                (total_syn_weight / total_weight) * syn_score +
                (total_rhet_weight / total_weight) * rhet_score
            )

            # 确保分数在1-5范围内
            final_score = max(1.0, min(5.0, final_score))

            # 9. 构建结果
            computation_time = time.time() - start_time

            return LayerResult(
                layer_num=self.layer_num,
                layer_name=self.layer_name,
                score=round(final_score, 2),
                metrics={
                    "lexical": lexical_metrics,
                    "syntactic": syntactic_metrics,
                    "rhetorical": rhetorical_metrics
                },
                sub_scores={
                    "lexical_diversity": round(lex_score, 2),
                    "syntactic_complexity": round(syn_score, 2),
                    "rhetorical_density": round(rhet_score, 2),
                    **lex_subscores,
                    **syn_subscores,
                    **rhet_subscores
                },
                computation_time=round(computation_time, 3)
            )

        except Exception as e:
            # 如果评估失败，返回错误结果
            return LayerResult(
                layer_num=self.layer_num,
                layer_name=self.layer_name,
                score=0.0,
                metrics={},
                sub_scores={},
                error=str(e),
                computation_time=time.time() - start_time
            )
