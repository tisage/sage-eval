"""
SAGE Framework Configuration Loader

配置驱动架构的核心：从YAML加载配置，Fail-fast原则
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic import BaseModel, ValidationError, Field


# ==================== Pydantic配置Schema ====================

class JudgeModelConfig(BaseModel):
    """单个评审模型配置"""
    provider: str
    model: str
    temperature: float = Field(default=0.5, ge=0.0, le=2.0)
    max_tokens: int = Field(default=32768, ge=1024)
    timeout: int = Field(default=120, ge=10)


class EnsembleConfig(BaseModel):
    """评审聚合配置"""
    method: str = "trimmed_mean"
    trim_ratio: float = Field(default=0.2, ge=0.0, le=0.5)
    min_judges: int = Field(default=2, ge=1)


class UncertaintyConfig(BaseModel):
    """不确定度配置"""
    high_threshold: float = Field(default=0.4, ge=0.0, le=1.0)
    flag_for_review: float = Field(default=0.6, ge=0.0, le=1.0)


class EvidenceConfig(BaseModel):
    """证据验证配置"""
    require_citation: bool = True
    min_quotes: int = Field(default=1, ge=0)
    max_quote_length: int = Field(default=100, ge=10)
    fuzzy_match_threshold: float = Field(default=0.85, ge=0.0, le=1.0)


class JudgeConfig(BaseModel):
    """评审配置总体"""
    version: str
    stage: str
    judge_models: Dict[str, list[JudgeModelConfig]]
    llm_layers: list[int]
    ensemble: EnsembleConfig
    uncertainty: UncertaintyConfig
    evidence: EvidenceConfig


class LayerMetricsConfig(BaseModel):
    """层级指标配置"""
    version: str
    layer1_language: Dict[str, Any]
    layer2_narrative: Dict[str, Any]
    layer3_thematic: Dict[str, Any]
    layer4_cultural: Dict[str, Any]
    layer5_emotional: Dict[str, Any]
    layer6_existential: Dict[str, Any]


class CatalogConfig(BaseModel):
    """Catalog索引配置"""
    yaml: Dict[str, Any]
    database: Dict[str, Any]


class CorpusConfig(BaseModel):
    """语料库配置"""
    version: str
    short_stories: Dict[str, Any]
    medium_stories: Dict[str, Any]
    long_stories: Dict[str, Any]
    preprocessing: Dict[str, Any]
    catalog: CatalogConfig
    output: Dict[str, Any]


# ==================== 配置加载器 ====================

class SAGEConfigLoader:
    """
    SAGE框架配置加载器

    核心原则：
    1. Fail-fast：缺失配置直接报错，不使用默认值
    2. 配置驱动：所有参数从YAML读取
    3. 类型验证：使用Pydantic确保配置正确性
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化配置加载器

        Args:
            config_dir: 配置文件目录，默认为 config/evaluation
        """
        if config_dir is None:
            # 从当前文件位置推导项目根目录
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent.parent
            config_dir = project_root / "config" / "evaluation"

        self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            raise FileNotFoundError(
                f"Config directory not found: {self.config_dir}. "
                f"Please create config/evaluation/ directory with required YAML files."
            )

    def load_judge_config(self, stage: str = "dev") -> JudgeConfig:
        """
        加载评审配置

        Args:
            stage: "dev" (开发/测试) 或 "prod" (生产/大规模实验)

        Returns:
            JudgeConfig对象

        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置格式错误
        """
        if stage not in ["dev", "prod"]:
            raise ValueError(f"Invalid stage: {stage}. Must be 'dev' or 'prod'.")

        config_file = self.config_dir / f"judge_config_{stage}.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"Judge config not found: {config_file}\n"
                f"Please create the config file with required parameters.\n"
                f"No default values will be used (Fail-fast principle)."
            )

        with open(config_file, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        try:
            return JudgeConfig(**config_dict)
        except ValidationError as e:
            raise ValueError(
                f"Invalid judge config format in {config_file}:\n{e}\n"
                f"Please check config file against schema."
            )

    def load_layer_metrics_config(self) -> LayerMetricsConfig:
        """
        加载层级指标配置

        Returns:
            LayerMetricsConfig对象

        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置格式错误
        """
        config_file = self.config_dir / "layer_metrics_config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"Layer metrics config not found: {config_file}\n"
                f"No default values will be used."
            )

        with open(config_file, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        try:
            return LayerMetricsConfig(**config_dict)
        except ValidationError as e:
            raise ValueError(
                f"Invalid layer metrics config: {e}"
            )

    def load_corpus_config(self) -> CorpusConfig:
        """
        加载语料库配置

        Returns:
            CorpusConfig对象

        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置格式错误
        """
        config_file = self.config_dir / "corpus_config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"Corpus config not found: {config_file}\n"
                f"No default values will be used."
            )

        with open(config_file, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        try:
            return CorpusConfig(**config_dict)
        except ValidationError as e:
            raise ValueError(
                f"Invalid corpus config: {e}"
            )

    def get_prompt_template(self, layer: int) -> str:
        """
        加载层级提示词模板

        Args:
            layer: 层级编号 (4-6使用LLM)

        Returns:
            提示词模板字符串

        Raises:
            ValueError: 层级不使用LLM
            FileNotFoundError: 提示词文件不存在
        """
        if layer not in [4, 5, 6]:
            raise ValueError(f"Layer {layer} does not use LLM evaluation")

        layer_names = {
            4: "layer4_cultural",
            5: "layer5_emotional",
            6: "layer6_existential"
        }

        prompt_file = self.config_dir / "prompts" / f"{layer_names[layer]}.yaml"

        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {prompt_file}\n"
                f"No default prompt will be used."
            )

        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_config = yaml.safe_load(f)

        return prompt_config.get('template', '')

    def get_layer_config(self, layer_num: int) -> Dict[str, Any]:
        """
        获取特定层级的配置

        Args:
            layer_num: 层级编号 (1-6)

        Returns:
            层级配置字典

        Raises:
            ValueError: 层级编号无效
        """
        if not 1 <= layer_num <= 6:
            raise ValueError(f"Invalid layer number: {layer_num}. Must be 1-6.")

        layer_metrics = self.load_layer_metrics_config()

        layer_attr_map = {
            1: "layer1_language",
            2: "layer2_narrative",
            3: "layer3_thematic",
            4: "layer4_cultural",
            5: "layer5_emotional",
            6: "layer6_existential"
        }

        return getattr(layer_metrics, layer_attr_map[layer_num])


# ==================== 全局单例 ====================

_config_loader_instance: Optional[SAGEConfigLoader] = None


def get_config_loader(config_dir: Optional[Path] = None) -> SAGEConfigLoader:
    """
    获取全局配置加载器实例（单例模式）

    Args:
        config_dir: 配置文件目录（仅首次调用时有效）

    Returns:
        SAGEConfigLoader实例
    """
    global _config_loader_instance

    if _config_loader_instance is None:
        _config_loader_instance = SAGEConfigLoader(config_dir)

    return _config_loader_instance
