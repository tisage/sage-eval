"""
数据迁移管理器

协调和管理整个数据迁移过程。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from omnisage.models.database import get_database_manager, get_session_context
from omnisage.dao import (
    UserDAO, ProjectDAO, ProjectConfigDAO, 
    WorkflowDAO, StageDAO, ContentDAO
)
from .json_migrator import JSONMigrator
from .data_validator import DataValidator

logger = logging.getLogger(__name__)

class MigrationManager:
    """数据迁移管理器"""
    
    def __init__(self, source_dir: str = "data", backup_dir: str = "migration_backup"):
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # 初始化组件
        self.json_migrator = JSONMigrator()
        self.data_validator = DataValidator()
        
        # 初始化DAO
        self.user_dao = UserDAO()
        self.project_dao = ProjectDAO()
        self.project_config_dao = ProjectConfigDAO()
        self.workflow_dao = WorkflowDAO()
        self.stage_dao = StageDAO()
        self.content_dao = ContentDAO()
        
        # 迁移统计
        self.migration_stats = {
            'start_time': None,
            'end_time': None,
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'created_users': 0,
            'created_projects': 0,
            'created_contents': 0,
            'errors': []
        }
    
    def run_migration(self, create_demo_user: bool = True) -> Dict[str, Any]:
        """运行完整的数据迁移"""
        logger.info("Starting data migration from JSON to database...")
        self.migration_stats['start_time'] = datetime.utcnow()
        
        try:
            # 1. 验证源数据
            logger.info("Step 1: Validating source data...")
            if not self._validate_source_data():
                raise ValueError("Source data validation failed")
            
            # 2. 创建备份
            logger.info("Step 2: Creating backup...")
            self._create_backup()
            
            # 3. 初始化数据库
            logger.info("Step 3: Initializing database...")
            self._initialize_database()
            
            # 4. 创建演示用户 (如果需要)
            if create_demo_user:
                logger.info("Step 4: Creating demo user...")
                demo_user = self._create_demo_user()
            else:
                demo_user = None
            
            # 5. 迁移数据
            logger.info("Step 5: Migrating data...")
            self._migrate_json_data(demo_user)
            
            # 6. 验证迁移结果
            logger.info("Step 6: Validating migration results...")
            self._validate_migration_results()
            
            self.migration_stats['end_time'] = datetime.utcnow()
            duration = (self.migration_stats['end_time'] - self.migration_stats['start_time']).total_seconds()
            
            logger.info(f"Migration completed successfully in {duration:.2f} seconds")
            logger.info(f"Migration stats: {self.migration_stats}")
            
            return {
                'success': True,
                'stats': self.migration_stats,
                'duration_seconds': duration
            }
            
        except Exception as e:
            self.migration_stats['end_time'] = datetime.utcnow()
            self.migration_stats['errors'].append(str(e))
            logger.error(f"Migration failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'stats': self.migration_stats
            }
    
    def _validate_source_data(self) -> bool:
        """验证源数据"""
        try:
            if not self.source_dir.exists():
                logger.error(f"Source directory {self.source_dir} does not exist")
                return False
            
            # 检查必要的JSON文件
            required_files = ['outline.json', 'objects_timeline.json', 'context_plan.json']
            existing_files = []
            
            for file_name in required_files:
                file_path = self.source_dir / file_name
                if file_path.exists():
                    existing_files.append(file_name)
                    # 验证JSON格式
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                        logger.debug(f"Validated JSON file: {file_name}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in {file_name}: {e}")
                        return False
            
            self.migration_stats['total_files'] = len(existing_files)
            logger.info(f"Found {len(existing_files)} valid JSON files to migrate")
            
            return len(existing_files) > 0
            
        except Exception as e:
            logger.error(f"Error validating source data: {e}")
            return False
    
    def _create_backup(self) -> None:
        """创建备份"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_subdir = self.backup_dir / f"backup_{timestamp}"
            backup_subdir.mkdir(exist_ok=True)
            
            # 备份JSON文件
            for json_file in self.source_dir.glob('*.json'):
                if json_file.is_file():
                    backup_file = backup_subdir / json_file.name
                    backup_file.write_text(json_file.read_text(encoding='utf-8'), encoding='utf-8')
                    logger.debug(f"Backed up {json_file.name}")
            
            logger.info(f"Created backup in {backup_subdir}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def _initialize_database(self) -> None:
        """初始化数据库"""
        try:
            db_manager = get_database_manager()
            
            # 测试连接
            if not db_manager.test_connection():
                raise ConnectionError("Failed to connect to database")
            
            # 创建表 (如果不存在)
            db_manager.create_all_tables()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _create_demo_user(self) -> Dict[str, Any]:
        """创建演示用户"""
        try:
            with get_session_context() as session:
                # 检查是否已存在演示用户
                existing_user = self.user_dao.get_by_username(session, 'demo_user')
                if existing_user:
                    logger.info("Demo user already exists")
                    return {
                        'id': existing_user.id,
                        'username': existing_user.username,
                        'email': existing_user.email
                    }
                
                # 创建新的演示用户
                demo_user = self.user_dao.create(
                    session,
                    username='demo_user',
                    email='demo@sage-framework.com',
                    password_hash='demo_password_hash',  # 在实际应用中应该是加密的
                    display_name='Demo User',
                    is_active=True,
                    is_verified=True
                )
                
                self.migration_stats['created_users'] += 1
                logger.info(f"Created demo user with ID: {demo_user.id}")
                
                return {
                    'id': demo_user.id,
                    'username': demo_user.username,
                    'email': demo_user.email
                }
                
        except Exception as e:
            logger.error(f"Error creating demo user: {e}")
            raise
    
    def _migrate_json_data(self, demo_user: Optional[Dict[str, Any]]) -> None:
        """迁移JSON数据"""
        try:
            # 获取所有JSON文件
            json_files = list(self.source_dir.glob('*.json'))
            
            for json_file in json_files:
                try:
                    logger.info(f"Processing {json_file.name}...")
                    
                    # 读取JSON数据
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 根据文件类型进行迁移
                    if json_file.name == 'outline.json':\n                        self._migrate_outline_data(data, demo_user)\n                    elif json_file.name == 'objects_timeline.json':\n                        self._migrate_objects_timeline_data(data, demo_user)\n                    elif json_file.name == 'context_plan.json':\n                        self._migrate_context_plan_data(data, demo_user)\n                    else:\n                        logger.info(f"Skipping unknown file: {json_file.name}")\n                        continue\n                    \n                    self.migration_stats['processed_files'] += 1\n                    \n                except Exception as e:\n                    logger.error(f"Error processing {json_file.name}: {e}")\n                    self.migration_stats['failed_files'] += 1\n                    self.migration_stats['errors'].append(f"{json_file.name}: {str(e)}")\n            \n        except Exception as e:\n            logger.error(f"Error migrating JSON data: {e}")\n            raise\n    \n    def _migrate_outline_data(self, data: Dict[str, Any], demo_user: Optional[Dict[str, Any]]) -> None:\n        """迁移大纲数据"""\n        try:\n            if not demo_user:\n                logger.warning("No demo user available, skipping outline migration")\n                return\n            \n            with get_session_context() as session:\n                # 创建项目\n                project = self.project_dao.create(\n                    session,\n                    name=data.get('title', 'Migrated Project'),\n                    description='Project migrated from JSON data',\n                    genre=data.get('genre', 'novel'),\n                    template_type=data.get('template_type', 'default'),\n                    owner_id=demo_user['id'],\n                    total_chapters=len(data.get('chapters', []))\n                )\n                \n                # 创建项目配置\n                config_data = {\n                    'project_id': project.id,\n                    'llm_provider': 'openai',\n                    'llm_model': 'gpt-3.5-turbo',\n                    'scheme_config': data\n                }\n                \n                project_config = self.project_config_dao.create(session, **config_data)\n                \n                # 创建内容记录\n                content = self.content_dao.create(\n                    session,\n                    project_id=project.id,\n                    title=f"{project.name} - Outline",\n                    content_type='outline',\n                    content_text=json.dumps(data, ensure_ascii=False, indent=2),\n                    content_data=data,\n                    word_count=len(str(data)),\n                    generated_by_stage='outline_planning',\n                    agent_name='OutlinePlannerAgent'\n                )\n                \n                self.migration_stats['created_projects'] += 1\n                self.migration_stats['created_contents'] += 1\n                \n                logger.info(f"Migrated outline data to project {project.id}")\n                \n        except Exception as e:\n            logger.error(f"Error migrating outline data: {e}")\n            raise\n    \n    def _migrate_objects_timeline_data(self, data: Dict[str, Any], demo_user: Optional[Dict[str, Any]]) -> None:\n        """迁移物品时间线数据"""\n        try:\n            # 这里可以根据需要实现物品时间线的迁移逻辑\n            # 暂时创建为独立的内容记录\n            logger.info("Objects timeline migration not fully implemented yet")\n            \n        except Exception as e:\n            logger.error(f"Error migrating objects timeline data: {e}")\n            raise\n    \n    def _migrate_context_plan_data(self, data: Dict[str, Any], demo_user: Optional[Dict[str, Any]]) -> None:\n        """迁移上下文计划数据"""\n        try:\n            # 这里可以根据需要实现上下文计划的迁移逻辑\n            # 暂时创建为独立的内容记录\n            logger.info("Context plan migration not fully implemented yet")\n            \n        except Exception as e:\n            logger.error(f"Error migrating context plan data: {e}")\n            raise\n    \n    def _validate_migration_results(self) -> None:\n        """验证迁移结果"""\n        try:\n            with get_session_context() as session:\n                # 统计迁移的数据\n                user_count = self.user_dao.count(session)\n                project_count = self.project_dao.count(session)\n                content_count = self.content_dao.count(session)\n                \n                logger.info(f"Migration results - Users: {user_count}, Projects: {project_count}, Contents: {content_count}")\n                \n                # 验证数据完整性\n                if project_count == 0:\n                    logger.warning("No projects were migrated")\n                \n                if content_count == 0:\n                    logger.warning("No contents were migrated")\n                \n        except Exception as e:\n            logger.error(f"Error validating migration results: {e}")\n            raise