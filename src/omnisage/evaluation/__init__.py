"""
SAGE Framework: Stratified Assessment of Generated & Established narratives

六层文学评价框架

Architecture:
    - Layer 1: 语言层 (Language) - Lexical, syntactic, rhetorical metrics
    - Layer 2: 叙事层 (Narrative) - Coherence, emotional arc, event sequence
    - Layer 3: 思想层 (Thematic) - Theme extraction, semantic networks, concepts
    - Layer 4: 文化层 (Cultural) - Cultural authenticity, historical accuracy
    - Layer 5: 情感层 (Emotional) - Emotional depth, empathy, reader impact
    - Layer 6: 人生关怀层 (Existential Care) - Philosophy, morality, meaning
"""

# SAGE Framework - Main pipeline (lazy import to avoid dependencies)
def get_pipeline():
    """Get SAGEPipeline class (lazy loading)"""
    from .sage.pipeline import SAGEPipeline
    return SAGEPipeline

def evaluate_text(text, config_path="config/sage_layers.yaml", context=None, llm_client=None):
    """Convenience function: evaluate a text with SAGE framework"""
    from .sage.pipeline import evaluate_text as _evaluate_text
    return _evaluate_text(text, config_path, context, llm_client)

def evaluate_file(file_path, config_path="config/sage_layers.yaml", context=None, llm_client=None):
    """Convenience function: evaluate a file with SAGE framework"""
    from .sage.pipeline import evaluate_file as _evaluate_file
    return _evaluate_file(file_path, config_path, context, llm_client)

# SAGE Framework - Base classes (no external dependencies)
from .sage.layers.base_layer import (
    BaseLayer,
    LayerResult,
    LayerType,
)

__version__ = "1.0.0"
__framework__ = "SAGE"

__all__ = [
    # Pipeline functions
    "get_pipeline",
    "evaluate_text",
    "evaluate_file",
    # Base classes
    "BaseLayer",
    "LayerResult",
    "LayerType",
]
