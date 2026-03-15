# PROJECT_FOLDER/src/omnisage/utils/prompt_loader.py
"""
简化的提示词加载工具。
支持合并的prompt文件格式，包含system_prompt和user_prompt。
"""

import yaml
from pathlib import Path
from typing import Dict, Any

from omnisage.utils.logger import get_logger

logger = get_logger(__name__)

class PromptLoader:
    """加载和格式化流水线阶段的提示词。"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._prompt_cache = {}
    
    def _load_prompt_file(self, file_path: Path) -> Dict[str, Any]:
        """加载提示词文件并缓存。"""
        cache_key = str(file_path)
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_data = yaml.safe_load(f)
            
            self._prompt_cache[cache_key] = prompt_data
            logger.debug(f"Loaded prompt file: {file_path}")
            return prompt_data
        
        except Exception as e:
            logger.error(f"Failed to load prompt file {file_path}: {str(e)}")
            raise
    
    def _get_prompt_file_path(self, stage: str) -> Path:
        """获取流水线阶段的提示词文件路径。"""
        filename = f"{stage}_prompt.yaml"
        prompt_path = self.prompts_dir / "novel" / filename
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        return prompt_path
    
    def _get_merged_prompt_data(self, stage: str) -> Dict[str, Any]:
        """获取合并的提示词数据。"""
        file_path = self._get_prompt_file_path(stage)
        return self._load_prompt_file(file_path)
    
    def load_system_prompt(self, stage: str, variables: Dict[str, Any] = None) -> str:
        """加载并格式化系统提示词。"""
        if variables is None:
            variables = {}
        
        prompt_data = self._get_merged_prompt_data(stage)
        system_prompt = prompt_data.get("system_prompt", "")
        
        if variables:
            try:
                system_prompt = system_prompt.format(**variables)
            except KeyError as e:
                logger.warning(f"Missing variable in system prompt for {stage}: {e}")
        
        return system_prompt
    
    def load_user_prompt(self, stage: str, variables: Dict[str, Any] = None) -> str:
        """加载并格式化用户提示词。"""
        if variables is None:
            variables = {}
        
        prompt_data = self._get_merged_prompt_data(stage)
        user_prompt = prompt_data.get("user_prompt", "")
        
        if variables:
            try:
                user_prompt = user_prompt.format(**variables)
            except KeyError as e:
                logger.warning(f"Missing variable in user prompt for {stage}: {e}")
        
        return user_prompt
    
    def get_temperature(self, stage: str) -> float:
        """获取流水线阶段的温度设置。"""
        try:
            prompt_data = self._get_merged_prompt_data(stage)
            return prompt_data.get("temperature", 0.7)
        except:
            return 0.7
    
    def get_variables_schema(self, stage: str) -> Dict[str, str]:
        """获取提示词的变量模式。"""
        try:
            prompt_data = self._get_merged_prompt_data(stage)
            return prompt_data.get("variables", {})
        except:
            return {}