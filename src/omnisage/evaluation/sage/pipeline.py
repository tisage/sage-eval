"""
SAGE Framework - Complete Evaluation Pipeline

Integrates all 6 layers for comprehensive narrative assessment.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import time
import json
from dataclasses import dataclass, asdict

from .layers.base_layer import LayerResult
from .layers.layer1_language import Layer1Language
from .layers.layer2_narrative import Layer2Narrative
from .layers.layer3_thematic import Layer3Thematic
from .layers.layer4_cultural import Layer4Cultural
from .layers.layer5_emotional import Layer5Emotional
from .layers.layer6_existential import Layer6Existential


@dataclass
class SAGEResult:
    """
    Complete SAGE evaluation result for a narrative

    Attributes:
        text_id: Unique identifier for the text
        metadata: Optional metadata (title, author, etc.)
        layer_results: Results from each layer (1-6)
        overall_score: Aggregated overall score
        evaluation_time: Total evaluation time in seconds
        config_version: Configuration version used
        llm_config: LLM configuration used for evaluation (model, provider, params)
    """
    text_id: str
    metadata: Dict[str, Any]
    layer_results: Dict[str, LayerResult]
    overall_score: float
    evaluation_time: float
    config_version: str
    llm_config: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "text_id": self.text_id,
            "metadata": self.metadata,
            "layer_results": {
                layer_name: {
                    "layer_num": result.layer_num,
                    "layer_name": result.layer_name,
                    "score": result.score,
                    "metrics": result.metrics,
                    "sub_scores": result.sub_scores,
                    "rationale": result.rationale,
                    "computation_time": result.computation_time,
                    "error": result.error
                }
                for layer_name, result in self.layer_results.items()
            },
            "overall_score": self.overall_score,
            "evaluation_time": self.evaluation_time,
            "config_version": self.config_version,
            "llm_config": self.llm_config
        }


class SAGEPipeline:
    """
    Complete SAGE evaluation pipeline integrating all 6 layers

    Usage:
        # With YAML config
        pipeline = SAGEPipeline.from_config("config/sage_layers.yaml")

        # Evaluate a story
        result = pipeline.evaluate(text, context={"title": "...", "author": "..."})

        # Save results
        pipeline.save_result(result, "output/results/story_001.json")
    """

    def __init__(
        self,
        layer_configs: Dict[str, Dict[str, Any]],
        llm_client: Optional[Any] = None,
        config_version: str = "1.0",
        llm_config_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize SAGE pipeline with layer configurations

        Args:
            layer_configs: Dictionary with layer1-6 configurations
            llm_client: LLM client for layers 4-6 (optional, uses Mock if None)
            config_version: Version string for tracking
            llm_config_metadata: LLM configuration metadata (model, provider, params)
        """
        self.layer_configs = layer_configs
        self.config_version = config_version
        self.llm_config_metadata = llm_config_metadata or {}

        # Use Mock LLM if none provided
        if llm_client is None:
            from .llm.mock_llm_client import MockLLMClient
            llm_client = MockLLMClient(deterministic=True)
            self.llm_config_metadata = {
                "mode": "mock",
                "model": "MockLLM",
                "provider": "internal",
                "deterministic": True
            }

        self.llm_client = llm_client

        # Initialize all 6 layers
        self.layers = self._initialize_layers()

    def _initialize_layers(self) -> Dict[str, Any]:
        """Initialize all layer evaluators"""
        layers = {}

        # Layer 1: Language (computational)
        if self.layer_configs.get("layer1_language", {}).get("enabled", True):
            layers["layer1_language"] = Layer1Language(
                self.layer_configs["layer1_language"]
            )

        # Layer 2: Narrative (computational + NLP)
        if self.layer_configs.get("layer2_narrative", {}).get("enabled", True):
            layers["layer2_narrative"] = Layer2Narrative(
                self.layer_configs["layer2_narrative"]
            )

        # Layer 3: Thematic (text analysis)
        if self.layer_configs.get("layer3_thematic", {}).get("enabled", True):
            layers["layer3_thematic"] = Layer3Thematic(
                self.layer_configs["layer3_thematic"]
            )

        # Layer 4: Cultural (LLM)
        if self.layer_configs.get("layer4_cultural", {}).get("enabled", True):
            layers["layer4_cultural"] = Layer4Cultural(
                self.layer_configs["layer4_cultural"],
                self.llm_client
            )

        # Layer 5: Emotional (LLM)
        if self.layer_configs.get("layer5_emotional", {}).get("enabled", True):
            layers["layer5_emotional"] = Layer5Emotional(
                self.layer_configs["layer5_emotional"],
                self.llm_client
            )

        # Layer 6: Existential Care (LLM)
        if self.layer_configs.get("layer6_existential", {}).get("enabled", True):
            layers["layer6_existential"] = Layer6Existential(
                self.layer_configs["layer6_existential"],
                self.llm_client
            )

        return layers

    def evaluate(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        text_id: Optional[str] = None
    ) -> SAGEResult:
        """
        Run complete SAGE evaluation on a narrative

        Args:
            text: Input text to evaluate
            context: Optional context (title, author, genre, etc.)
            text_id: Optional unique identifier

        Returns:
            SAGEResult with scores from all enabled layers
        """
        start_time = time.time()

        # Generate text_id if not provided
        if text_id is None:
            import hashlib
            text_id = hashlib.md5(text.encode()).hexdigest()[:12]

        # Initialize context if not provided
        if context is None:
            context = {}

        # Evaluate each layer
        layer_results = {}

        for layer_name, layer in self.layers.items():
            try:
                result = layer.evaluate(text, context)
                layer_results[layer_name] = result
            except Exception as e:
                # Create error result if layer fails
                layer_num = int(layer_name.replace("layer", "").split("_")[0])
                layer_results[layer_name] = LayerResult(
                    layer_num=layer_num,
                    layer_name=f"Layer {layer_num}",
                    score=0.0,
                    error=f"Layer evaluation failed: {str(e)}"
                )

        # Calculate overall score
        overall_score = self._calculate_overall_score(layer_results)

        # Total evaluation time
        evaluation_time = time.time() - start_time

        return SAGEResult(
            text_id=text_id,
            metadata=context,
            layer_results=layer_results,
            overall_score=overall_score,
            evaluation_time=evaluation_time,
            config_version=self.config_version,
            llm_config=self.llm_config_metadata
        )

    def _calculate_overall_score(self, layer_results: Dict[str, LayerResult]) -> float:
        """
        Calculate overall score from layer results

        Strategy: Simple average of all layer scores (1-5 scale for L1-3, already 1-5 for L4-6)

        Note: Layer 1-3 scores are already normalized to 1-5 scale by individual layers
        """
        valid_scores = [
            result.score
            for result in layer_results.values()
            if result.error is None and result.score > 0
        ]

        if not valid_scores:
            return 0.0

        return round(sum(valid_scores) / len(valid_scores), 2)

    @classmethod
    def from_config(
        cls,
        config_path: str,
        llm_client: Optional[Any] = None,
        llm_config_path: Optional[str] = None,
        llm_config_dict: Optional[Dict[str, Any]] = None
    ) -> "SAGEPipeline":
        """
        Create pipeline from YAML configuration file

        Args:
            config_path: Path to sage_layers.yaml
            llm_client: Optional LLM client (if None, uses Mock)
            llm_config_path: Optional path to llm_models.yaml (file)
            llm_config_dict: Optional LLM config dictionary (in-memory, takes precedence)

        Returns:
            Configured SAGEPipeline instance
        """
        # Lazy import to avoid yaml dependency at module load time
        import yaml

        # Load layer configurations from YAML file directly
        with open(config_path, 'r', encoding='utf-8') as f:
            layer_configs = yaml.safe_load(f)

        # Load LLM configuration if provided
        llm_config_metadata = {}
        llm_config_data = None

        # Priority: dict > file path
        if llm_config_dict:
            llm_config_data = llm_config_dict
        elif llm_config_path:
            with open(llm_config_path, 'r', encoding='utf-8') as f:
                llm_config_data = yaml.safe_load(f)

        if llm_config_data and llm_client is None:
            from .llm.client_factory import LLMClientFactory

            factory = LLMClientFactory(llm_config_data)
            # Use primary model for Layer 4 (can be customized)
            llm_client = factory.get_layer_client(layer_num=4, mode="production")

            # Extract model info for each layer
            layer_assignment = llm_config_data.get('layer_assignment', {})
            llm_config_metadata = {
                "mode": "production",
                "config_file": llm_config_path if llm_config_path else "in-memory",
                "layers": {}
            }

            for layer_num in [4, 5, 6]:
                layer_names = {
                    4: "layer4_cultural",
                    5: "layer5_emotional",
                    6: "layer6_existential"
                }
                layer_key = layer_names[layer_num]
                layer_cfg = layer_assignment.get(layer_key, {})

                primary_model = layer_cfg.get('primary_model', 'unknown')

                # Find model details
                model_info = {}
                for model in llm_config_data.get('production', {}).get('models', []):
                    if model.get('model_name') == primary_model:
                        # Priority: layer_cfg (from profile) > model defaults
                        model_info = {
                            "model": model.get('model_name'),
                            "provider": model.get('provider'),
                            "temperature": layer_cfg.get('temperature', model.get('temperature')),
                            "max_tokens": layer_cfg.get('max_tokens', model.get('max_tokens')),
                            "fallback": layer_cfg.get('fallback_model')
                        }
                        break

                llm_config_metadata["layers"][f"layer{layer_num}"] = model_info

        return cls(
            layer_configs=layer_configs,
            llm_client=llm_client,
            config_version="1.0",
            llm_config_metadata=llm_config_metadata
        )

    def save_result(self, result: SAGEResult, output_path: str) -> None:
        """
        Save evaluation result to JSON file

        Args:
            result: SAGEResult to save
            output_path: Output file path
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    def evaluate_corpus(
        self,
        texts: List[Dict[str, Any]],
        output_dir: str
    ) -> List[SAGEResult]:
        """
        Evaluate multiple texts and save results

        Args:
            texts: List of dicts with 'text', 'text_id', and optional 'context'
            output_dir: Directory to save results

        Returns:
            List of SAGEResult objects
        """
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for i, text_data in enumerate(texts):
            print(f"Evaluating {i+1}/{len(texts)}: {text_data.get('text_id', 'unknown')}")

            result = self.evaluate(
                text=text_data["text"],
                context=text_data.get("context", {}),
                text_id=text_data.get("text_id")
            )

            results.append(result)

            # Save individual result
            result_file = output_path / f"{result.text_id}.json"
            self.save_result(result, str(result_file))

        # Save summary
        summary = self._generate_summary(results)
        summary_file = output_path / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        return results

    def _generate_summary(self, results: List[SAGEResult]) -> Dict[str, Any]:
        """Generate summary statistics from multiple results"""
        if not results:
            return {}

        # Aggregate scores by layer
        layer_scores = {}
        for result in results:
            for layer_name, layer_result in result.layer_results.items():
                if layer_name not in layer_scores:
                    layer_scores[layer_name] = []
                if layer_result.error is None:
                    layer_scores[layer_name].append(layer_result.score)

        # Calculate statistics
        summary = {
            "total_texts": len(results),
            "average_scores": {
                layer: round(sum(scores) / len(scores), 2) if scores else 0.0
                for layer, scores in layer_scores.items()
            },
            "overall_average": round(
                sum(r.overall_score for r in results) / len(results), 2
            ),
            "total_evaluation_time": round(
                sum(r.evaluation_time for r in results), 2
            )
        }

        return summary


# ==================== Convenience Functions ====================

def evaluate_text(
    text: str,
    config_path: str = "config/sage_layers.yaml",
    context: Optional[Dict[str, Any]] = None,
    llm_client: Optional[Any] = None
) -> SAGEResult:
    """
    Convenience function: Evaluate a single text with SAGE framework

    Args:
        text: Text to evaluate
        config_path: Path to configuration file
        context: Optional context (title, author, etc.)
        llm_client: Optional LLM client (uses Mock if None)

    Returns:
        SAGEResult with all layer scores
    """
    pipeline = SAGEPipeline.from_config(config_path, llm_client)
    return pipeline.evaluate(text, context)


def evaluate_file(
    file_path: str,
    config_path: str = "config/sage_layers.yaml",
    context: Optional[Dict[str, Any]] = None,
    llm_client: Optional[Any] = None
) -> SAGEResult:
    """
    Convenience function: Evaluate a text file

    Args:
        file_path: Path to text file
        config_path: Path to configuration file
        context: Optional context (if None, extracts from filename)
        llm_client: Optional LLM client

    Returns:
        SAGEResult
    """
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract context from filename if not provided
    if context is None:
        from pathlib import Path
        filename = Path(file_path).stem
        context = {
            "filename": filename,
            "title": filename.replace('_', ' ').title()
        }

    pipeline = SAGEPipeline.from_config(config_path, llm_client)
    return pipeline.evaluate(text, context, text_id=Path(file_path).stem)
