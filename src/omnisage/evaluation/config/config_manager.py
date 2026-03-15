"""
Configuration Manager for Evaluation Framework

Loads and validates YAML configuration files, provides unified access interface.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from functools import lru_cache


class ConfigManager:
    """
    Centralized configuration management for evaluation framework.

    Loads configuration from YAML files and provides validated access.
    Supports configuration caching and hierarchical access.
    """

    _instance = None  # Singleton instance
    _config_cache: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure one config manager instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_dir: Path to configuration directory
                       (default: config/evaluation/)
        """
        if hasattr(self, '_initialized'):
            return

        self.config_dir = self._resolve_config_dir(config_dir)
        self._load_all_configs()
        self._initialized = True

    def _resolve_config_dir(self, config_dir: Optional[str]) -> Path:
        """Resolve configuration directory path."""
        if config_dir:
            return Path(config_dir)

        # Try to find config directory relative to project root
        current = Path(__file__).resolve()

        # Go up from src/omnisage/evaluation/config/ to project root
        project_root = current.parent.parent.parent.parent.parent

        config_path = project_root / "config" / "evaluation"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration directory not found: {config_path}\n"
                f"Please create config/evaluation/ in project root or specify config_dir"
            )

        return config_path

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load and parse YAML configuration file.

        Args:
            filename: Name of YAML file (e.g., 'layer1_metrics.yaml')

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If file is not valid YAML
        """
        filepath = self.config_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    config = {}
                return config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filename}: {e}")

    def _load_all_configs(self):
        """Load all configuration files into cache."""
        config_files = {
            'layer1_metrics': 'layer1_metrics.yaml',
            'layer2_metrics': 'layer2_metrics.yaml',
            'layer3_metrics': 'layer3_metrics.yaml',
            'llm_models': 'llm_models.yaml',
            'experiment_design': 'experiment_design.yaml',
            'story_catalog': 'story_catalog.yaml',
        }

        for key, filename in config_files.items():
            try:
                self._config_cache[key] = self._load_yaml(filename)
            except FileNotFoundError as e:
                # Layer 2/3 might not exist yet
                if key in ['layer2_metrics', 'layer3_metrics']:
                    self._config_cache[key] = {'status': 'not_found'}
                else:
                    raise e

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., 'layer1_metrics.lexical_diversity.mtld.threshold')
            default: Default value if key not found

        Returns:
            Configuration value

        Examples:
            >>> config = ConfigManager()
            >>> threshold = config.get('layer1_metrics.lexical_diversity.mtld.threshold')
            >>> models = config.get('experiment_design.generation.models')
        """
        parts = key.split('.')
        value = self._config_cache

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def get_layer1_config(self) -> Dict[str, Any]:
        """Get Layer 1 metrics configuration."""
        return self._config_cache.get('layer1_metrics', {})

    def get_layer2_config(self) -> Dict[str, Any]:
        """Get Layer 2 metrics configuration."""
        return self._config_cache.get('layer2_metrics', {})

    def get_layer3_config(self) -> Dict[str, Any]:
        """Get Layer 3 metrics configuration."""
        return self._config_cache.get('layer3_metrics', {})

    def get_llm_models_config(self) -> Dict[str, Any]:
        """Get LLM models configuration."""
        return self._config_cache.get('llm_models', {})

    def get_experiment_design_config(self) -> Dict[str, Any]:
        """Get experiment design configuration."""
        return self._config_cache.get('experiment_design', {})

    def get_story_catalog_config(self) -> Dict[str, Any]:
        """Get story catalog configuration."""
        return self._config_cache.get('story_catalog', {})

    def get_story_metadata(self, story_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for specific story.

        Args:
            story_id: Story identifier (e.g., 'gift_of_magi')

        Returns:
            Story metadata dictionary or None if not found
        """
        catalog = self.get_story_catalog_config()
        stories = catalog.get('stories', {})
        return stories.get(story_id)

    def get_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for specific LLM model.

        Args:
            model_id: Model identifier (e.g., 'gemini-flash')

        Returns:
            Model configuration dictionary or None if not found
        """
        models_config = self.get_llm_models_config()
        models = models_config.get('models', {})
        return models.get(model_id)

    def get_generation_params(self) -> Dict[str, Any]:
        """Get generation parameters from experiment design."""
        return self.get('experiment_design.generation', {})

    def get_evaluation_params(self) -> Dict[str, Any]:
        """Get evaluation parameters from experiment design."""
        return self.get('experiment_design.evaluation', {})

    def get_statistics_config(self) -> Dict[str, Any]:
        """Get statistical analysis configuration."""
        return self.get('experiment_design.statistics', {})

    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration (file naming, directories)."""
        return self.get('experiment_design.output', {})

    def get_naming_convention(self, result_type: str = 'raw_result') -> str:
        """
        Get file naming convention pattern.

        Args:
            result_type: Type of result file
                        ('raw_result', 'aggregated', 'comparison', 'statistical_summary')

        Returns:
            Naming convention pattern with placeholders

        Example:
            >>> config.get_naming_convention('raw_result')
            "{story_id}_{model}_t{temperature}_r{run}_layer{layer}.json"
        """
        output_config = self.get_output_config()
        naming = output_config.get('naming_convention', {})
        return naming.get(result_type, '')

    def format_filename(
        self,
        result_type: str,
        story_id: str,
        model: str = None,
        temperature: float = None,
        run: int = None,
        layer: str = None
    ) -> str:
        """
        Format filename using naming convention.

        Args:
            result_type: Type of result file
            story_id: Story identifier
            model: Model identifier (optional)
            temperature: Temperature value (optional)
            run: Run number (optional)
            layer: Layer identifier (optional)

        Returns:
            Formatted filename

        Example:
            >>> config.format_filename(
            ...     'raw_result', 'gift_of_magi',
            ...     model='gemini-flash', temperature=0.3, run=1, layer='layer1'
            ... )
            "gift_of_magi_gemini-flash_t0.3_r1_layer1.json"
        """
        pattern = self.get_naming_convention(result_type)

        # Format temperature with one decimal place
        if temperature is not None:
            temperature = f"{temperature:.1f}"

        replacements = {
            'story_id': story_id,
            'model': model or '',
            'temperature': temperature or '',
            'run': str(run) if run is not None else '',
            'layer': layer or '',
        }

        filename = pattern
        for key, value in replacements.items():
            filename = filename.replace(f"{{{key}}}", value)

        return filename

    def get_spacy_model(self, language: str) -> str:
        """
        Get spaCy model name for specified language.

        Args:
            language: Language code ('en' or 'zh')

        Returns:
            spaCy model name
        """
        return self.get(f'layer1_metrics.syntactic_complexity.spacy_models.{language}', 'en_core_web_sm')

    def validate(self) -> bool:
        """
        Validate all loaded configurations.

        Returns:
            True if all configurations are valid

        Raises:
            ValueError: If any configuration is invalid
        """
        # Basic validation: check required sections exist
        required_sections = {
            'layer1_metrics': ['lexical_diversity', 'syntactic_complexity', 'punctuation_patterns'],
            'experiment_design': ['generation', 'evaluation', 'statistics', 'output'],
            'llm_models': ['models', 'providers'],
            'story_catalog': ['stories'],
        }

        for config_key, sections in required_sections.items():
            config = self._config_cache.get(config_key, {})
            for section in sections:
                if section not in config:
                    raise ValueError(f"Missing required section '{section}' in {config_key}")

        return True

    def reload(self):
        """Reload all configuration files from disk."""
        self._config_cache.clear()
        self._load_all_configs()

    def __repr__(self) -> str:
        return f"ConfigManager(config_dir={self.config_dir})"


# Global singleton instance
_global_config: Optional[ConfigManager] = None


def load_config(config_dir: Optional[str] = None) -> ConfigManager:
    """
    Load configuration manager (singleton).

    Args:
        config_dir: Optional path to configuration directory

    Returns:
        ConfigManager instance
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager(config_dir=config_dir)
    return _global_config


def get_config() -> ConfigManager:
    """
    Get existing configuration manager instance.

    Returns:
        ConfigManager instance

    Raises:
        RuntimeError: If config not loaded yet
    """
    if _global_config is None:
        raise RuntimeError("Configuration not loaded. Call load_config() first.")
    return _global_config
