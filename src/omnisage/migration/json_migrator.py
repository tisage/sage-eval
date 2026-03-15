"""
JSON数据迁移器

专门处理JSON文件到数据库模型的转换。
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class JSONMigrator:
    """JSON数据迁移器"""
    
    def __init__(self):
        self.processed_files = []
        self.errors = []
    
    def load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded JSON file: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            self.errors.append(f"Load error in {file_path}: {str(e)}")
            return None
    
    def transform_outline_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换大纲数据格式"""
        try:
            transformed = {
                'title': data.get('title', 'Untitled'),
                'genre': data.get('genre', 'novel'),
                'template_type': data.get('template_type', 'default'),
                'theme': data.get('theme', ''),
                'total_chapters': len(data.get('chapters', [])),
                'chapters': data.get('chapters', []),
                'metadata': {
                    'original_file': 'outline.json',
                    'migration_timestamp': datetime.utcnow().isoformat(),
                    'source_format': 'sage_json_v1'
                }
            }
            
            # 提取更多元数据
            if 'story_context' in data:
                transformed['story_context'] = data['story_context']
            
            if 'characters' in data:
                transformed['characters'] = data['characters']
            
            logger.debug("Transformed outline data")
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming outline data: {e}")
            raise
    
    def transform_objects_timeline_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换物品时间线数据格式"""
        try:
            transformed = {
                'timeline_data': data,
                'metadata': {
                    'original_file': 'objects_timeline.json',
                    'migration_timestamp': datetime.utcnow().isoformat(),
                    'source_format': 'sage_json_v1'
                }
            }
            
            # 提取关键信息
            if 'objects' in data:
                transformed['objects_count'] = len(data['objects'])
                transformed['objects'] = data['objects']
            
            if 'timeline' in data:
                transformed['timeline'] = data['timeline']
            
            logger.debug("Transformed objects timeline data")
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming objects timeline data: {e}")
            raise
    
    def transform_context_plan_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换上下文计划数据格式"""
        try:
            transformed = {
                'context_data': data,
                'metadata': {
                    'original_file': 'context_plan.json',
                    'migration_timestamp': datetime.utcnow().isoformat(),
                    'source_format': 'sage_json_v1'
                }
            }
            
            # 提取关键信息
            if 'story_context' in data:
                transformed['story_context'] = data['story_context']
            
            if 'chapters' in data:
                transformed['chapters_count'] = len(data['chapters'])
                transformed['chapters'] = data['chapters']
            
            if 'metadata' in data:
                transformed['original_metadata'] = data['metadata']
            
            logger.debug("Transformed context plan data")
            return transformed
            
        except Exception as e:
            logger.error(f"Error transforming context plan data: {e}")
            raise
    
    def extract_content_metadata(self, data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """提取内容元数据"""
        try:
            metadata = {
                'file_type': file_type,
                'extraction_timestamp': datetime.utcnow().isoformat(),
                'word_count': self._count_words_in_data(data),
                'character_count': len(str(data)),
                'structure_info': self._analyze_structure(data)
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting content metadata: {e}")
            return {}
    
    def _count_words_in_data(self, data: Any) -> int:
        """统计数据中的单词数"""
        try:
            if isinstance(data, str):
                return len(data.split())
            elif isinstance(data, dict):
                total = 0
                for value in data.values():
                    total += self._count_words_in_data(value)
                return total
            elif isinstance(data, list):
                total = 0
                for item in data:
                    total += self._count_words_in_data(item)
                return total
            else:
                return len(str(data).split())
        except Exception:
            return 0
    
    def _analyze_structure(self, data: Any) -> Dict[str, Any]:
        """分析数据结构"""
        try:
            if isinstance(data, dict):
                return {
                    'type': 'object',
                    'keys': list(data.keys()),
                    'key_count': len(data),
                    'nested_objects': sum(1 for v in data.values() if isinstance(v, dict)),
                    'nested_arrays': sum(1 for v in data.values() if isinstance(v, list))
                }
            elif isinstance(data, list):
                return {
                    'type': 'array',
                    'length': len(data),
                    'item_types': list(set(type(item).__name__ for item in data))
                }
            else:
                return {
                    'type': type(data).__name__,
                    'length': len(str(data))
                }
        except Exception:
            return {'type': 'unknown'}
    
    def validate_transformed_data(self, data: Dict[str, Any], data_type: str) -> bool:
        """验证转换后的数据"""
        try:
            # 基础验证
            if not isinstance(data, dict):
                logger.error(f"Transformed {data_type} data is not a dictionary")
                return False
            
            if 'metadata' not in data:
                logger.warning(f"Transformed {data_type} data missing metadata")
            
            # 根据数据类型进行特定验证
            if data_type == 'outline':
                return self._validate_outline_data(data)
            elif data_type == 'objects_timeline':
                return self._validate_objects_timeline_data(data)
            elif data_type == 'context_plan':
                return self._validate_context_plan_data(data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating transformed {data_type} data: {e}")
            return False
    
    def _validate_outline_data(self, data: Dict[str, Any]) -> bool:
        """验证大纲数据"""
        required_fields = ['title', 'genre']
        for field in required_fields:
            if field not in data:
                logger.error(f"Outline data missing required field: {field}")
                return False
        return True
    
    def _validate_objects_timeline_data(self, data: Dict[str, Any]) -> bool:
        """验证物品时间线数据"""
        if 'timeline_data' not in data:
            logger.error("Objects timeline data missing timeline_data field")
            return False
        return True
    
    def _validate_context_plan_data(self, data: Dict[str, Any]) -> bool:
        """验证上下文计划数据"""
        if 'context_data' not in data:
            logger.error("Context plan data missing context_data field")
            return False
        return True