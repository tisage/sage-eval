"""
数据验证器

验证迁移前后的数据完整性和正确性。
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from omnisage.models.database import get_session_context
from omnisage.dao import UserDAO, ProjectDAO, ContentDAO

logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.validation_results = {
            'source_validation': {},
            'migration_validation': {},
            'integrity_checks': {}
        }
    
    def validate_source_files(self, source_dir: Path) -> Dict[str, Any]:
        """验证源文件"""
        logger.info("Validating source files...")
        
        results = {
            'valid_files': [],
            'invalid_files': [],
            'missing_files': [],
            'total_size': 0,
            'errors': []
        }
        
        try:
            # 检查目录是否存在
            if not source_dir.exists():
                results['errors'].append(f"Source directory {source_dir} does not exist")
                return results
            
            # 定义期望的文件
            expected_files = [
                'outline.json',
                'objects_timeline.json', 
                'context_plan.json'
            ]
            
            # 检查每个文件
            for filename in expected_files:
                file_path = source_dir / filename
                
                if not file_path.exists():
                    results['missing_files'].append(filename)
                    continue
                
                # 验证JSON格式
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 验证文件内容
                    validation_result = self._validate_json_content(filename, data)
                    
                    if validation_result['valid']:
                        results['valid_files'].append({
                            'filename': filename,
                            'size': file_path.stat().st_size,
                            'structure': validation_result['structure']
                        })
                        results['total_size'] += file_path.stat().st_size
                    else:
                        results['invalid_files'].append({
                            'filename': filename,
                            'errors': validation_result['errors']
                        })
                        
                except json.JSONDecodeError as e:
                    results['invalid_files'].append({
                        'filename': filename,
                        'errors': [f"Invalid JSON format: {str(e)}"]
                    })
                except Exception as e:
                    results['invalid_files'].append({
                        'filename': filename,
                        'errors': [f"File read error: {str(e)}"]
                    })
            
            # 检查其他JSON文件
            for json_file in source_dir.glob('*.json'):
                if json_file.name not in expected_files:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                        results['valid_files'].append({
                            'filename': json_file.name,
                            'size': json_file.stat().st_size,
                            'structure': {'type': 'additional_file'}
                        })
                        results['total_size'] += json_file.stat().st_size
                    except:
                        results['invalid_files'].append({
                            'filename': json_file.name,
                            'errors': ['Invalid JSON format']
                        })
            
            self.validation_results['source_validation'] = results
            logger.info(f"Source validation completed: {len(results['valid_files'])} valid, {len(results['invalid_files'])} invalid, {len(results['missing_files'])} missing")
            
            return results
            
        except Exception as e:
            logger.error(f"Error validating source files: {e}")
            results['errors'].append(str(e))
            return results
    
    def _validate_json_content(self, filename: str, data: Any) -> Dict[str, Any]:
        """验证JSON内容"""
        result = {
            'valid': True,
            'errors': [],
            'structure': {}
        }
        
        try:
            if not isinstance(data, dict):
                result['valid'] = False
                result['errors'].append("Root data must be an object")
                return result
            
            # 根据文件类型进行特定验证
            if filename == 'outline.json':
                result.update(self._validate_outline_structure(data))
            elif filename == 'objects_timeline.json':
                result.update(self._validate_objects_timeline_structure(data))
            elif filename == 'context_plan.json':
                result.update(self._validate_context_plan_structure(data))
            else:
                result['structure'] = {'type': 'unknown', 'keys': list(data.keys())}
            
            return result
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Content validation error: {str(e)}")
            return result
    
    def _validate_outline_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证大纲结构"""
        result = {'structure': {'type': 'outline'}}
        errors = []
        
        # 检查必需字段
        required_fields = ['title']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # 检查章节
        if 'chapters' in data:
            if isinstance(data['chapters'], list):
                result['structure']['chapters_count'] = len(data['chapters'])
            else:
                errors.append("'chapters' field must be an array")
        
        # 检查其他字段
        expected_fields = ['genre', 'template_type', 'theme', 'story_context']
        present_fields = [field for field in expected_fields if field in data]
        result['structure']['present_fields'] = present_fields
        
        if errors:
            result['valid'] = False
            result['errors'] = errors
        
        return result
    
    def _validate_objects_timeline_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证物品时间线结构"""
        result = {'structure': {'type': 'objects_timeline'}}
        errors = []
        
        # 检查是否有对象或时间线数据
        if 'objects' not in data and 'timeline' not in data:
            errors.append("Missing both 'objects' and 'timeline' fields")
        
        if 'objects' in data:
            if isinstance(data['objects'], (list, dict)):
                result['structure']['has_objects'] = True
            else:
                errors.append("'objects' field must be an array or object")
        
        if errors:
            result['valid'] = False
            result['errors'] = errors
        
        return result
    
    def _validate_context_plan_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证上下文计划结构"""
        result = {'structure': {'type': 'context_plan'}}
        errors = []
        
        # 检查基本结构
        if 'metadata' in data:
            result['structure']['has_metadata'] = True
        
        if 'story_context' in data:
            result['structure']['has_story_context'] = True
        
        if 'chapters' in data:
            if isinstance(data['chapters'], (list, dict)):
                result['structure']['has_chapters'] = True
            else:
                errors.append("'chapters' field must be an array or object")
        
        if errors:
            result['valid'] = False
            result['errors'] = errors
        
        return result
    
    def validate_migration_results(self) -> Dict[str, Any]:
        """验证迁移结果"""
        logger.info("Validating migration results...")
        
        results = {
            'database_connectivity': False,
            'data_counts': {},
            'data_integrity': {},
            'errors': []
        }
        
        try:
            with get_session_context() as session:
                results['database_connectivity'] = True
                
                # 统计数据量
                user_dao = UserDAO()
                project_dao = ProjectDAO()
                content_dao = ContentDAO()
                
                results['data_counts'] = {
                    'users': user_dao.count(session),
                    'projects': project_dao.count(session),
                    'contents': content_dao.count(session)
                }
                
                # 数据完整性检查
                integrity_results = self._check_data_integrity(session)
                results['data_integrity'] = integrity_results
                
                self.validation_results['migration_validation'] = results
                logger.info(f"Migration validation completed: {results['data_counts']}")
                
        except Exception as e:
            logger.error(f"Error validating migration results: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _check_data_integrity(self, session) -> Dict[str, Any]:
        """检查数据完整性"""
        integrity_results = {
            'orphaned_records': {},
            'missing_relations': {},
            'data_consistency': {}
        }
        
        try:
            # 检查孤立记录
            # 这里可以添加更多的完整性检查
            
            # 检查项目是否有对应的配置
            from omnisage.dao import ProjectConfigDAO
            project_dao = ProjectDAO()
            config_dao = ProjectConfigDAO()
            
            all_projects = project_dao.get_all(session)
            projects_without_config = []
            
            for project in all_projects:
                config = config_dao.get_by_project_id(session, project.id)
                if not config:
                    projects_without_config.append(project.id)
            
            if projects_without_config:
                integrity_results['missing_relations']['projects_without_config'] = projects_without_config
            
            return integrity_results
            
        except Exception as e:
            logger.error(f"Error checking data integrity: {e}")
            integrity_results['errors'] = [str(e)]
            return integrity_results
    
    def generate_validation_report(self) -> str:
        """生成验证报告"""
        report_lines = [
            "=== Sage Framework Data Migration Validation Report ===",
            "",
            "1. Source File Validation:",
        ]
        
        source_results = self.validation_results.get('source_validation', {})
        if source_results:
            report_lines.extend([
                f"   Valid files: {len(source_results.get('valid_files', []))}",
                f"   Invalid files: {len(source_results.get('invalid_files', []))}",
                f"   Missing files: {len(source_results.get('missing_files', []))}",
                f"   Total size: {source_results.get('total_size', 0)} bytes",
            ])
            
            if source_results.get('invalid_files'):
                report_lines.append("   Invalid files details:")
                for invalid_file in source_results['invalid_files']:
                    report_lines.append(f"     - {invalid_file['filename']}: {', '.join(invalid_file['errors'])}")
            
            if source_results.get('missing_files'):
                report_lines.append(f"   Missing files: {', '.join(source_results['missing_files'])}")
        
        report_lines.extend([
            "",
            "2. Migration Results Validation:",
        ])
        
        migration_results = self.validation_results.get('migration_validation', {})
        if migration_results:
            report_lines.extend([
                f"   Database connectivity: {'✓' if migration_results.get('database_connectivity') else '✗'}",
                "   Data counts:",
            ])
            
            data_counts = migration_results.get('data_counts', {})
            for data_type, count in data_counts.items():
                report_lines.append(f"     - {data_type}: {count}")
            
            integrity_results = migration_results.get('data_integrity', {})
            if integrity_results.get('missing_relations'):
                report_lines.append("   Data integrity issues:")
                for issue_type, details in integrity_results['missing_relations'].items():
                    report_lines.append(f"     - {issue_type}: {details}")
        
        report_lines.extend([
            "",
            "=== End of Report ===",
        ])
        
        return "\n".join(report_lines)