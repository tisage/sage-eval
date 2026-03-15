"""
Base Layer Abstract Class for SAGE Framework

所有六层评估器的抽象基类，定义统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class LayerType(Enum):
    """层级类型枚举"""
    LANGUAGE = (1, "语言层", "Language")
    NARRATIVE = (2, "叙事层", "Narrative")
    THEMATIC = (3, "思想层", "Thematic")
    CULTURAL = (4, "文化层", "Cultural")
    EMOTIONAL = (5, "情感层", "Emotional")
    EXISTENTIAL_CARE = (6, "人生关怀层", "Existential Care")

    def __init__(self, layer_num: int, cn_name: str, en_name: str):
        self.layer_num = layer_num
        self.cn_name = cn_name
        self.en_name = en_name


@dataclass
class LayerResult:
    """
    层级评估结果的标准化数据结构

    所有层级的evaluate()方法必须返回此数据结构
    """
    # 基本信息
    layer_num: int
    layer_name: str
    score: float  # 1-5分制，或0分表示不涉及

    # 详细指标
    metrics: Dict[str, Any] = field(default_factory=dict)
    sub_scores: Dict[str, float] = field(default_factory=dict)

    # 元数据
    uncertainty: Optional[float] = None  # 不确定度 (0-1)，仅LLM评审层使用
    evidence: Optional[list] = None      # 证据引用，仅LLM评审层使用
    rationale: Optional[str] = None      # 评分理由，仅LLM评审层使用

    # 计算信息
    computation_time: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "layer_num": self.layer_num,
            "layer_name": self.layer_name,
            "score": self.score,
            "metrics": self.metrics,
            "sub_scores": self.sub_scores,
        }

        # 可选字段
        if self.uncertainty is not None:
            result["uncertainty"] = self.uncertainty
        if self.evidence is not None:
            result["evidence"] = self.evidence
        if self.rationale is not None:
            result["rationale"] = self.rationale
        if self.computation_time is not None:
            result["computation_time"] = self.computation_time
        if self.error is not None:
            result["error"] = self.error

        return result


class BaseLayer(ABC):
    """
    SAGE框架的基础层抽象类

    所有六层评估器必须继承此类并实现required方法
    """

    def __init__(self, layer_type: LayerType, config: Dict[str, Any]):
        """
        初始化层级评估器

        Args:
            layer_type: 层级类型（LayerType枚举）
            config: 层级配置（从YAML加载）
        """
        self.layer_type = layer_type
        self.layer_num = layer_type.layer_num
        self.layer_name = f"{layer_type.cn_name} ({layer_type.en_name})"
        self.config = config

        # 验证配置
        self._validate_config()

    @abstractmethod
    def evaluate(self, text: str, context: Optional[Dict[str, Any]] = None) -> LayerResult:
        """
        评估文本

        Args:
            text: 待评估的故事文本
            context: 额外上下文（如其他层级的结果）

        Returns:
            LayerResult对象

        Raises:
            ValueError: 文本为空或无效
            RuntimeError: 评估过程中出现错误
        """
        pass

    @abstractmethod
    def _validate_config(self) -> None:
        """
        验证配置的有效性

        Raises:
            ValueError: 配置缺失必需字段或格式错误
        """
        pass

    def _check_text_validity(self, text: str) -> None:
        """
        检查文本有效性（所有层级共用）

        Args:
            text: 待检查的文本

        Raises:
            ValueError: 文本为空或过短
        """
        if not text or not text.strip():
            raise ValueError(f"Layer {self.layer_num}: Text is empty")

        word_count = len(text.split())
        if word_count < 50:
            raise ValueError(
                f"Layer {self.layer_num}: Text too short ({word_count} words). "
                f"Minimum 50 words required."
            )

    def get_layer_info(self) -> Dict[str, Any]:
        """获取层级基本信息"""
        return {
            "layer_num": self.layer_num,
            "layer_name": self.layer_name,
            "layer_type": self.layer_type.name,
            "config_enabled": self.config.get("enabled", False),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} - Layer {self.layer_num}: {self.layer_name}>"
