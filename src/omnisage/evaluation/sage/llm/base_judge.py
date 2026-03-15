"""
Base LLM Judge for SAGE Framework Layers 4-6

LLM评审基础类
"""

from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod
import json
import re
import time


class BaseJudge(ABC):
    """
    LLM评审器基类

    所有LLM评审器（Layer 4-6）必须继承此类

    核心功能：
    - 构造提示词
    - 调用LLM
    - 解析输出
    - 错误处理
    """

    def __init__(self, llm_client: Any, temperature: float = 0.5):
        """
        初始化评审器

        Args:
            llm_client: LLM客户端实例
            temperature: 生成温度（0.5推荐用于评审任务）
        """
        self.llm_client = llm_client
        self.temperature = temperature

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        获取系统提示词

        Returns:
            系统提示词字符串
        """
        pass

    @abstractmethod
    def get_user_prompt(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        获取用户提示词

        Args:
            text: 待评估的文本
            context: 可选上下文信息

        Returns:
            用户提示词字符串
        """
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应

        Args:
            response: LLM返回的原始文本

        Returns:
            解析后的结构化数据
        """
        pass

    def evaluate(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行评审

        Args:
            text: 待评估的文本
            context: 可选上下文信息

        Returns:
            {
                "score": float,  # 1-5分制
                "dimensions": Dict[str, float],  # 各维度分数
                "rationale": str,  # 评审理由
                "raw_response": str,  # 原始响应
                "error": Optional[str]
            }
        """
        try:
            start_time = time.time()

            # 构造提示词
            system_prompt = self.get_system_prompt()
            user_prompt = self.get_user_prompt(text, context)

            # 调用LLM
            response = self.llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=self.temperature
            )

            # 解析响应
            parsed = self.parse_response(response)

            # 添加元数据
            parsed["raw_response"] = response
            parsed["evaluation_time"] = time.time() - start_time

            return parsed

        except Exception as e:
            return {
                "score": 0.0,
                "dimensions": {},
                "rationale": "",
                "raw_response": "",
                "error": f"Evaluation failed: {str(e)}",
                "evaluation_time": time.time() - start_time if 'start_time' in locals() else 0.0
            }


class JSONOutputParser:
    """
    JSON输出解析器

    用于解析LLM返回的JSON格式响应
    """

    @staticmethod
    def extract_json(response: str) -> Optional[Dict[str, Any]]:
        """
        从LLM响应中提取JSON

        支持格式：
        1. 纯JSON
        2. Markdown代码块中的JSON
        3. 包含其他文本的JSON

        Args:
            response: LLM响应文本

        Returns:
            解析后的字典，失败返回None
        """
        # 尝试1: 直接解析
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        # 尝试2: 提取markdown代码块中的JSON
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass

        # 尝试3: 查找任何{...}结构
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(brace_pattern, response, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue

        return None

    @staticmethod
    def validate_score_range(
        data: Dict[str, Any],
        score_key: str = "score",
        min_score: float = 1.0,
        max_score: float = 5.0
    ) -> float:
        """
        验证并修正分数范围

        Args:
            data: 解析的数据
            score_key: 分数字段名
            min_score: 最小分数
            max_score: 最大分数

        Returns:
            修正后的分数
        """
        score = data.get(score_key, 0.0)

        # 转换为浮点数
        try:
            score = float(score)
        except (ValueError, TypeError):
            return min_score

        # 限制在有效范围
        return max(min_score, min(max_score, score))


# ==================== 辅助函数 ====================

def create_rubric_prompt(
    dimensions: List[Tuple[str, str]],
    scale_description: str = "1=Poor, 2=Fair, 3=Good, 4=Very Good, 5=Excellent"
) -> str:
    """
    创建评分标准提示词

    Args:
        dimensions: [(维度名, 维度描述), ...]
        scale_description: 分数等级描述

    Returns:
        格式化的评分标准文本
    """
    rubric = f"Scoring Scale: {scale_description}\n\n"
    rubric += "Evaluation Dimensions:\n"

    for i, (name, description) in enumerate(dimensions, 1):
        rubric += f"{i}. {name}: {description}\n"

    return rubric


def format_output_template(
    dimensions: List[str],
    include_rationale: bool = True,
    include_evidence: bool = False
) -> str:
    """
    创建输出格式模板

    Args:
        dimensions: 维度名称列表
        include_rationale: 是否包含理由
        include_evidence: 是否包含证据引用 (text citations)

    Returns:
        JSON格式模板说明
    """
    template = "{\n"
    template += "  \"overall_score\": <float between 1.0 and 5.0>,\n"
    template += "  \"dimensions\": {\n"

    for i, dim in enumerate(dimensions):
        comma = "," if i < len(dimensions) - 1 else ""
        template += f"    \"{dim}\": <float between 1.0 and 5.0>{comma}\n"

    template += "  }"

    if include_rationale:
        template += ",\n  \"rationale\": \"<brief explanation of the overall score>\""

    if include_evidence:
        template += ',\n  "evidence_citations": ["<1-3 specific sentences from text, ≤20 words each>", "..."]'

    template += "\n}"

    return template
