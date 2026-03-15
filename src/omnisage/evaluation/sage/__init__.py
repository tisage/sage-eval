"""
SAGE Framework: Stratified Assessment of Generated & Established narratives

六层文学评价框架的核心实现模块
"""

__version__ = "0.1.0"
__framework__ = "SAGE"

# 只导入不依赖外部库的核心组件
from .layers.base_layer import BaseLayer, LayerResult

# SAGEConfigLoader依赖yaml，延迟导入
def get_config_loader():
    """延迟导入配置加载器（需要yaml库）"""
    from .config.sage_config_loader import SAGEConfigLoader
    return SAGEConfigLoader

__all__ = [
    "BaseLayer",
    "LayerResult",
    "get_config_loader",
]
