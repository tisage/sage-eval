# PROJECT_FOLDER/src/omnisage/utils/content_cleaner.py
"""
Content cleaner for LLM outputs.

关键特性
--------
1. 去除模型回答中的元信息 / 标注行
2. **保留缩进**，保证 YAML 字面量块 (| / >) 不被破坏
3. 自动剥离 ```yaml / ```json 代码围栏
"""

import re
import json
from typing import Optional

from omnisage.utils.logger import get_logger

logger = get_logger(__name__)


class ContentCleaner:
    """Content cleaner for LLM outputs."""

    # 常见「提示语 / 元信息」正则
    META_PATTERNS = [
        r'^以下是.*?分析.*?结果.*?$',
        r'^分析.*?如下.*?：.*?$',
        r'^根据.*?要求.*?分析.*?$',
        r'^.*?JSON.*?格式.*?如下.*?$',
        r'^\*\*.*?分析.*?\*\*.*?$',
        r'^```json.*$',
        r'^```ya?ml.*$',
        r'^```.*$',  # 其它 fenced-code 起始
    ]

    @classmethod
    def clean_content(cls, content: str, role: str = "") -> Optional[str]:
        """
        清理 meta 行并提取正文，保留缩进。

        Parameters
        ----------
        content : str
            原始模型输出
        role : str, optional
            日志用角色标签
        Returns
        -------
        Optional[str]
            清洗后的文本；若结果为空返回 None
        """
        if not content or not content.strip():
            return None

        original_content = content.strip("\n")
        lines = original_content.splitlines()

        cleaned_lines = []
        removed_meta = 0

        for raw_line in lines:
            stripped = raw_line.lstrip()          # 仅用于匹配
            if not stripped:
                cleaned_lines.append("")          # 保留空行
                continue

            if any(re.match(p, stripped, re.IGNORECASE) for p in cls.META_PATTERNS):
                removed_meta += 1
                logger.debug(f"Removed meta line from {role}: {stripped[:60]}...")
                continue

            cleaned_lines.append(raw_line)        # 保留原缩进

        cleaned_content = "\n".join(cleaned_lines).strip()

        # 若包在代码围栏里，直接截取栏内部分
        fenced = re.search(r'```(?:ya?ml|json)?\s*\n(.*?)\n```',
                           cleaned_content, re.DOTALL)
        if fenced:
            cleaned_content = fenced.group(1).strip()

        # 折叠 3 行以上的连续空行
        cleaned_content = re.sub(r'\n\s*\n\s*\n+', "\n\n", cleaned_content).strip()

        if removed_meta:
            logger.info(f"Cleaned {role} content: removed {removed_meta} meta lines")

        return cleaned_content or None

    # ------------------------------------------------------------------ #
    #  JSON 专用工具
    # ------------------------------------------------------------------ #
    @classmethod
    def extract_json(cls, content: str) -> Optional[dict]:
        """尝试从文本中提取并解析 JSON。"""
        cleaned = cls.clean_content(content)
        if not cleaned:
            return None
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return None
