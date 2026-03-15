"""
Layer 3: Thematic Layer (思想层)

Implements thematic depth analysis using computational topic modeling.

Metrics:
- Theme Extraction (TF-IDF based keywords)
- Semantic Network (Co-occurrence analysis)
- Concept Density (Abstract vs Concrete concepts)
"""

from typing import Dict, Any, Optional
import time

from .base_layer import BaseLayer, LayerResult, LayerType
from ..metrics.theme_extraction import ThemeExtractor
from ..metrics.semantic_network import SemanticNetworkAnalyzer
from ..metrics.concept_density import ConceptDensityAnalyzer


class Layer3Thematic(BaseLayer):
    """
    Layer 3: Thematic Depth Evaluator

    Evaluates thematic richness, semantic relationships, and conceptual depth
    using computational text analysis.

    Configuration requirements:
    - theme_extraction: {consistency, diversity weights}
    - semantic_network: {density, centrality, connectivity weights}
    - concept_density: {abstract_density, abstraction_ratio weights}
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Layer 3 with configuration

        Args:
            config: Layer 3 configuration from YAML
                {
                    "enabled": True,
                    "theme_extraction": {
                        "consistency": {"enabled": True, "weight": 0.10},
                        "diversity": {"enabled": True, "weight": 0.10},
                        "top_k": 10,
                        "segment_size": 200
                    },
                    "semantic_network": {
                        "density": {"enabled": True, "weight": 0.10},
                        "centrality": {"enabled": True, "weight": 0.15},
                        "connectivity": {"enabled": True, "weight": 0.10},
                        "window_size": 5,
                        "min_cooccurrence": 2
                    },
                    "concept_density": {
                        "abstract_density": {"enabled": True, "weight": 0.25},
                        "abstraction_ratio": {"enabled": True, "weight": 0.20}
                    }
                }
        """
        super().__init__(LayerType.THEMATIC, config)

        # Extract configuration parameters
        theme_config = config.get("theme_extraction", {})
        network_config = config.get("semantic_network", {})
        concept_config = config.get("concept_density", {})

        # Initialize analyzers
        self.theme_extractor = ThemeExtractor(
            top_k=theme_config.get("top_k", 10)
        )

        self.semantic_analyzer = SemanticNetworkAnalyzer(
            window_size=network_config.get("window_size", 5),
            min_cooccurrence=network_config.get("min_cooccurrence", 2)
        )

        self.concept_analyzer = ConceptDensityAnalyzer()

        # Store configuration for weighted scoring
        self.theme_config = theme_config
        self.network_config = network_config
        self.concept_config = concept_config

    def _validate_config(self) -> None:
        """Validate configuration"""
        if "enabled" not in self.config:
            raise ValueError("Layer 3 config must have 'enabled' field")

        # Check required sections
        required_sections = [
            "theme_extraction",
            "semantic_network",
            "concept_density"
        ]
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Layer 3 config missing '{section}' section")

    def evaluate(self, text: str, context: Optional[Dict[str, Any]] = None) -> LayerResult:
        """
        Evaluate thematic depth of text

        Args:
            text: Input text to evaluate
            context: Optional context (not used in Layer 3)

        Returns:
            LayerResult with thematic scores and metrics
        """
        start_time = time.time()

        try:
            # ==================== Theme Extraction ====================
            segment_size = self.theme_config.get("segment_size", 200)
            theme_metrics = self.theme_extractor.calculate_all(
                text,
                segment_size=segment_size
            )

            theme_score, theme_breakdown = self.theme_extractor.score_theme_extraction(
                theme_consistency=theme_metrics["theme_consistency"],
                theme_diversity=theme_metrics["theme_diversity"],
                consistency_weight=self._get_weight(self.theme_config, "consistency"),
                diversity_weight=self._get_weight(self.theme_config, "diversity")
            )

            # ==================== Semantic Network ====================
            network_metrics = self.semantic_analyzer.calculate_all(text)

            network_score, network_breakdown = self.semantic_analyzer.score_semantic_network(
                network_density=network_metrics["network_density"],
                average_centrality=network_metrics["average_centrality"],
                connectivity=network_metrics["connectivity"],
                density_weight=self._get_weight(self.network_config, "density"),
                centrality_weight=self._get_weight(self.network_config, "centrality"),
                connectivity_weight=self._get_weight(self.network_config, "connectivity")
            )

            # ==================== Concept Density ====================
            concept_metrics = self.concept_analyzer.calculate_all(text)

            concept_score, concept_breakdown = self.concept_analyzer.score_concept_density(
                abstract_density=concept_metrics["abstract_density"],
                abstraction_ratio=concept_metrics["abstraction_ratio"],
                density_weight=self._get_weight(self.concept_config, "abstract_density"),
                ratio_weight=self._get_weight(self.concept_config, "abstraction_ratio")
            )

            # ==================== Calculate Final Score ====================
            # Collect all enabled weights
            total_weight = 0.0
            weighted_sum = 0.0

            # Theme weights
            theme_total_weight = (
                self._get_weight(self.theme_config, "consistency") +
                self._get_weight(self.theme_config, "diversity")
            )
            if theme_total_weight > 0:
                total_weight += theme_total_weight
                weighted_sum += theme_total_weight * theme_score

            # Network weights
            network_total_weight = (
                self._get_weight(self.network_config, "density") +
                self._get_weight(self.network_config, "centrality") +
                self._get_weight(self.network_config, "connectivity")
            )
            if network_total_weight > 0:
                total_weight += network_total_weight
                weighted_sum += network_total_weight * network_score

            # Concept weights
            concept_total_weight = (
                self._get_weight(self.concept_config, "abstract_density") +
                self._get_weight(self.concept_config, "abstraction_ratio")
            )
            if concept_total_weight > 0:
                total_weight += concept_total_weight
                weighted_sum += concept_total_weight * concept_score

            if total_weight == 0:
                raise ValueError("No metrics enabled for Layer 3")

            final_score = weighted_sum / total_weight

            # Prepare result
            computation_time = time.time() - start_time

            return LayerResult(
                layer_num=3,
                layer_name="Thematic Layer (思想层)",
                score=round(final_score, 2),
                metrics={
                    "theme": theme_metrics,
                    "network": network_metrics,
                    "concept": concept_metrics
                },
                sub_scores={
                    "theme_score": round(theme_score, 2),
                    "theme_consistency_score": round(theme_breakdown["consistency_score"], 2),
                    "theme_diversity_score": round(theme_breakdown["diversity_score"], 2),
                    "network_score": round(network_score, 2),
                    "network_density_score": round(network_breakdown["density_score"], 2),
                    "network_centrality_score": round(network_breakdown["centrality_score"], 2),
                    "network_connectivity_score": round(network_breakdown["connectivity_score"], 2),
                    "concept_score": round(concept_score, 2),
                    "concept_density_score": round(concept_breakdown["density_score"], 2),
                    "concept_ratio_score": round(concept_breakdown["ratio_score"], 2)
                },
                computation_time=computation_time
            )

        except Exception as e:
            return LayerResult(
                layer_num=3,
                layer_name="Thematic Layer (思想层)",
                score=0.0,
                error=f"Layer 3 evaluation failed: {str(e)}",
                computation_time=time.time() - start_time
            )

    def _get_weight(self, config: Dict[str, Any], metric_name: str) -> float:
        """
        Extract weight for a metric from config

        Args:
            config: Configuration dict
            metric_name: Name of metric

        Returns:
            Weight value (0.0 if disabled)
        """
        metric_config = config.get(metric_name, {})

        if not isinstance(metric_config, dict):
            return 0.0

        if not metric_config.get("enabled", False):
            return 0.0

        weight = metric_config.get("weight", 0.0)

        if weight is None:
            raise ValueError(
                f"Weight for '{metric_name}' is enabled but weight value is missing. "
                f"Fail-fast principle: no defaults provided."
            )

        return float(weight)
