"""
Mock LLM Client for Testing

用于测试的模拟LLM客户端
"""

import json
import random
from typing import Dict, Any


class MockLLMClient:
    """
    模拟LLM客户端

    返回预定义的JSON响应，用于测试评审器而不消耗API费用
    """

    def __init__(self, deterministic: bool = True):
        """
        初始化Mock客户端

        Args:
            deterministic: 是否返回确定性结果（True）或随机结果（False）
        """
        self.deterministic = deterministic
        self.call_count = 0

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        生成模拟响应

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度（未使用）

        Returns:
            JSON格式的模拟响应
        """
        self.call_count += 1

        # 根据提示词判断评估类型
        if "CULTURAL DIMENSION" in system_prompt:
            return self._generate_cultural_response()
        elif "EMOTIONAL DIMENSION" in system_prompt or "EMOTIONAL RESONANCE" in system_prompt:
            return self._generate_emotional_response()
        elif "EXISTENTIAL" in system_prompt or "LIFE CONCERN" in system_prompt:
            return self._generate_existential_response()
        else:
            return self._generate_generic_response()

    def _generate_cultural_response(self) -> str:
        """生成文化维度的模拟响应"""
        if self.deterministic:
            response = {
                "overall_score": 4.2,
                "dimensions": {
                    "cultural_authenticity": 4.0,
                    "historical_accuracy": 4.5,
                    "social_context": 4.0,
                    "universal_vs_specific": 4.5
                },
                "rationale": "The narrative demonstrates strong cultural authenticity through its depiction of early 20th century American urban life. Historical details are accurate and well-researched. Social context effectively captures the period's economic hardships and value systems."
            }
        else:
            response = {
                "overall_score": round(random.uniform(3.0, 5.0), 1),
                "dimensions": {
                    "cultural_authenticity": round(random.uniform(3.0, 5.0), 1),
                    "historical_accuracy": round(random.uniform(3.0, 5.0), 1),
                    "social_context": round(random.uniform(3.0, 5.0), 1),
                    "universal_vs_specific": round(random.uniform(3.0, 5.0), 1)
                },
                "rationale": "Mock evaluation with randomized scores for testing purposes."
            }

        return json.dumps(response, indent=2)

    def _generate_emotional_response(self) -> str:
        """生成情感共鸣的模拟响应"""
        if self.deterministic:
            response = {
                "overall_score": 4.5,
                "dimensions": {
                    "emotional_depth": 4.5,
                    "character_empathy": 4.8,
                    "emotional_authenticity": 4.2,
                    "reader_impact": 4.5
                },
                "rationale": "The work achieves profound emotional resonance through authentic character portrayal and genuine emotional depth."
            }
        else:
            response = {
                "overall_score": round(random.uniform(3.0, 5.0), 1),
                "dimensions": {
                    "emotional_depth": round(random.uniform(3.0, 5.0), 1),
                    "character_empathy": round(random.uniform(3.0, 5.0), 1),
                    "emotional_authenticity": round(random.uniform(3.0, 5.0), 1),
                    "reader_impact": round(random.uniform(3.0, 5.0), 1)
                },
                "rationale": "Mock emotional evaluation."
            }

        return json.dumps(response, indent=2)

    def _generate_existential_response(self) -> str:
        """生成人生关怀的模拟响应"""
        if self.deterministic:
            response = {
                "overall_score": 4.0,
                "dimensions": {
                    "life_philosophy": 4.0,
                    "moral_reflection": 4.5,
                    "human_condition": 3.8,
                    "meaning_exploration": 3.5
                },
                "rationale": "The narrative explores meaningful questions about sacrifice, love, and human values with philosophical depth."
            }
        else:
            response = {
                "overall_score": round(random.uniform(3.0, 5.0), 1),
                "dimensions": {
                    "life_philosophy": round(random.uniform(3.0, 5.0), 1),
                    "moral_reflection": round(random.uniform(3.0, 5.0), 1),
                    "human_condition": round(random.uniform(3.0, 5.0), 1),
                    "meaning_exploration": round(random.uniform(3.0, 5.0), 1)
                },
                "rationale": "Mock existential evaluation."
            }

        return json.dumps(response, indent=2)

    def _generate_generic_response(self) -> str:
        """生成通用的模拟响应"""
        response = {
            "overall_score": 3.5,
            "dimensions": {},
            "rationale": "Generic mock response for unrecognized evaluation type."
        }
        return json.dumps(response, indent=2)

    async def generate_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """异步版本（直接调用同步版本）"""
        return self.generate(system_prompt, user_prompt, temperature)
