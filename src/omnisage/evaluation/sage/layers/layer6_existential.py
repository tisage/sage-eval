"""
Layer 6: Existential Care Layer (人生关怀层)

Implements existential/philosophical dimension evaluation using LLM-based judging.

Dimensions:
- Life Philosophy (人生哲学)
- Moral Reflection (道德反思)
- Human Condition (人性状况)
- Meaning Exploration (意义探索)
"""

from typing import Dict, Any, Optional
import time

from .base_layer import BaseLayer, LayerResult, LayerType
from ..llm.existential_judge import ExistentialJudge


class Layer6Existential(BaseLayer):
    """
    Layer 6: Existential Care Evaluator

    Uses LLM-based judging to assess philosophical depth, moral reflection,
    and existential inquiry in narratives.

    Configuration requirements:
    - llm_client: LLM客户端实例
    - temperature: 生成温度（默认0.0用于一致性研究）
    - prompt_version: Prompt版本 ("v1"-"v5", 默认"v1")
    - dimensions: 各维度权重配置
    """

    def __init__(self, config: Dict[str, Any], llm_client: Any):
        """
        Initialize Layer 6 with configuration and LLM client

        Args:
            config: Layer 6 configuration from YAML
                {
                    "enabled": True,
                    "temperature": 0.0,  # 0.0 for deterministic (consistency study)
                    "prompt_version": "v1",  # "v1" to "v5" for multi-prompt study
                    "dimensions": {
                        "life_philosophy": {"enabled": True, "weight": 0.30},
                        "moral_reflection": {"enabled": True, "weight": 0.25},
                        "human_condition": {"enabled": True, "weight": 0.25},
                        "meaning_exploration": {"enabled": True, "weight": 0.20}
                    }
                }
            llm_client: LLM客户端实例
        """
        # 提取配置参数（在super().__init__之前）
        self.temperature = config.get("temperature", 0.0)  # 改为默认0.0 (确定性)
        self.prompt_version = config.get("prompt_version", "v1")  # 新增prompt版本支持
        self.dimensions_config = config.get("dimensions", {})

        # 存储LLM客户端
        self.llm_client = llm_client

        # 调用父类初始化
        super().__init__(LayerType.EXISTENTIAL_CARE, config)

        # 初始化Judge
        self.judge = ExistentialJudge(
            llm_client=llm_client,
            temperature=self.temperature,
            prompt_version=self.prompt_version  # 传递prompt版本
        )

    def _validate_config(self) -> None:
        """Validate configuration"""
        if "enabled" not in self.config:
            raise ValueError("Layer 6 config must have 'enabled' field")

        if "dimensions" not in self.config:
            raise ValueError("Layer 6 config missing 'dimensions' section")

        # 检查至少有一个维度启用
        has_enabled = any(
            dim_config.get("enabled", False)
            for dim_config in self.dimensions_config.values()
        )

        if not has_enabled:
            raise ValueError("Layer 6 must have at least one dimension enabled")

    def evaluate(self, text: str, context: Optional[Dict[str, Any]] = None) -> LayerResult:
        """
        Evaluate existential dimension of text using LLM judge

        Args:
            text: Input text to evaluate
            context: Optional context (title, author, etc.)

        Returns:
            LayerResult with existential scores and LLM rationale
        """
        start_time = time.time()

        try:
            # 调用LLM Judge进行评审
            judge_result = self.judge.evaluate(text, context)

            # 检查是否有错误
            if judge_result.get("error"):
                return LayerResult(
                    layer_num=6,
                    layer_name="Existential Care Layer (人生关怀层)",
                    score=0.0,
                    error=judge_result["error"],
                    computation_time=time.time() - start_time
                )

            # 提取维度分数
            dimensions = judge_result.get("dimensions", {})

            # 计算加权总分
            total_weight = 0.0
            weighted_sum = 0.0

            for dim_name, dim_score in dimensions.items():
                weight = self._get_weight(dim_name)
                if weight > 0:
                    total_weight += weight
                    weighted_sum += weight * dim_score

            if total_weight == 0:
                # 使用overall_score作为fallback
                final_score = judge_result.get("score", 0.0)
            else:
                final_score = weighted_sum / total_weight

            # 准备子分数
            sub_scores = {
                f"{dim_name}_score": round(score, 2)
                for dim_name, score in dimensions.items()
            }
            sub_scores["llm_overall_score"] = round(judge_result.get("score", 0.0), 2)

            # 准备evidence (优先使用evidence_citations,回退到raw_response)
            evidence_list = judge_result.get("evidence_citations", [])
            if not evidence_list:
                evidence_list = [judge_result.get("raw_response", "")]

            # 返回结果
            return LayerResult(
                layer_num=6,
                layer_name="Existential Care Layer (人生关怀层)",
                score=round(final_score, 2),
                metrics={
                    "dimensions": dimensions,
                    "llm_score": judge_result.get("score", 0.0),
                    "evidence_citations": judge_result.get("evidence_citations", [])  # 新增
                },
                sub_scores=sub_scores,
                rationale=judge_result.get("rationale", ""),
                evidence=evidence_list,  # 使用evidence_citations或raw_response
                computation_time=judge_result.get("evaluation_time", 0.0)
            )

        except Exception as e:
            return LayerResult(
                layer_num=6,
                layer_name="Existential Care Layer (人生关怀层)",
                score=0.0,
                error=f"Layer 6 evaluation failed: {str(e)}",
                computation_time=time.time() - start_time
            )

    def _get_weight(self, dimension_name: str) -> float:
        """
        Extract weight for a dimension from config

        Args:
            dimension_name: Name of dimension

        Returns:
            Weight value (0.0 if disabled)
        """
        dim_config = self.dimensions_config.get(dimension_name, {})

        if not isinstance(dim_config, dict):
            return 0.0

        if not dim_config.get("enabled", False):
            return 0.0

        weight = dim_config.get("weight", 0.0)

        if weight is None:
            raise ValueError(
                f"Weight for '{dimension_name}' is enabled but weight value is missing. "
                f"Fail-fast principle: no defaults provided."
            )

        return float(weight)
