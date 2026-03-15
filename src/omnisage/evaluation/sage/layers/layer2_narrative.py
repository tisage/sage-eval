"""
Layer 2: Narrative Layer (叙事层)

Implements narrative structure analysis using computational + lightweight NLP metrics.

Metrics:
- Entity Coherence (Entity Grid Model)
- Emotional Arc (Sentiment Timeline, Tension Curve)
- Event Sequence (Verb Extraction, Tense Analysis)
"""

from typing import Dict, Any, Optional
import time

from .base_layer import BaseLayer, LayerResult, LayerType
from ..metrics.coherence import EntityCoherenceAnalyzer
from ..metrics.emotional_arc import EmotionalArcAnalyzer
from ..metrics.event_sequence import EventSequenceAnalyzer


class Layer2Narrative(BaseLayer):
    """
    Layer 2: Narrative Structure Evaluator

    Evaluates narrative coherence, emotional progression, and event sequences
    using computational metrics and lightweight NLP.

    Configuration requirements:
    - entity_coherence: {density, salient, entropy weights}
    - emotional_arc: {intensity, tension weights}
    - event_sequence: {density, diversity, consistency weights}
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Layer 2 with configuration

        Args:
            config: Layer 2 configuration from YAML
                {
                    "enabled": True,
                    "entity_coherence": {
                        "density": {"enabled": True, "weight": 0.15},
                        "salient": {"enabled": True, "weight": 0.10},
                        "entropy": {"enabled": True, "weight": 0.10}
                    },
                    "emotional_arc": {
                        "intensity": {"enabled": True, "weight": 0.15},
                        "tension": {"enabled": True, "weight": 0.15}
                    },
                    "event_sequence": {
                        "density": {"enabled": True, "weight": 0.15},
                        "diversity": {"enabled": True, "weight": 0.10},
                        "consistency": {"enabled": True, "weight": 0.10}
                    },
                    "use_spacy": False,
                    "spacy_model": "en_core_web_sm",
                    "segment_size": 100
                }
        """
        super().__init__(LayerType.NARRATIVE, config)

        # Extract global settings
        self.use_spacy = config.get("use_spacy", False)
        self.spacy_model = config.get("spacy_model", "en_core_web_sm")
        self.segment_size = config.get("segment_size", 100)

        # Initialize analyzers
        self.coherence_analyzer = EntityCoherenceAnalyzer(
            use_spacy=self.use_spacy,
            spacy_model=self.spacy_model
        )

        self.emotional_analyzer = EmotionalArcAnalyzer()

        self.event_analyzer = EventSequenceAnalyzer(
            use_spacy=self.use_spacy,
            spacy_model=self.spacy_model
        )

        # Store configuration for weighted scoring
        self.coherence_config = config.get("entity_coherence", {})
        self.emotional_config = config.get("emotional_arc", {})
        self.event_config = config.get("event_sequence", {})

    def _validate_config(self) -> None:
        """Validate configuration"""
        if "enabled" not in self.config:
            raise ValueError("Layer 2 config must have 'enabled' field")

        # Check required sections
        required_sections = ["entity_coherence", "emotional_arc", "event_sequence"]
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Layer 2 config missing '{section}' section")

    def evaluate(self, text: str, context: Optional[Dict[str, Any]] = None) -> LayerResult:
        """
        Evaluate narrative structure of text

        Args:
            text: Input text to evaluate
            context: Optional context (not used in Layer 2)

        Returns:
            LayerResult with narrative scores and metrics
        """
        start_time = time.time()

        try:
            # ==================== Entity Coherence ====================
            coherence_metrics = self.coherence_analyzer.calculate_all(text)

            coherence_score, coherence_breakdown = self.coherence_analyzer.score_entity_coherence(
                entity_density=coherence_metrics["entity_density"],
                salient_entities=coherence_metrics["salient_entities"],
                transition_entropy=coherence_metrics["transition_entropy"],
                density_weight=self._get_weight(self.coherence_config, "density"),
                salient_weight=self._get_weight(self.coherence_config, "salient"),
                entropy_weight=self._get_weight(self.coherence_config, "entropy")
            )

            # ==================== Emotional Arc ====================
            emotional_metrics = self.emotional_analyzer.calculate_all(
                text,
                segment_size=self.segment_size
            )

            emotional_score, emotional_breakdown = self.emotional_analyzer.score_emotional_arc(
                average_intensity=emotional_metrics["average_intensity"],
                tension_variance=emotional_metrics["tension_variance"],
                intensity_weight=self._get_weight(self.emotional_config, "intensity"),
                tension_weight=self._get_weight(self.emotional_config, "tension")
            )

            # ==================== Event Sequence ====================
            event_metrics = self.event_analyzer.calculate_all(text)

            event_score, event_breakdown = self.event_analyzer.score_event_sequence(
                action_density=event_metrics["action_density"],
                verb_diversity=event_metrics["verb_diversity"],
                tense_shifts=event_metrics["tense_shifts"],
                total_words=event_metrics["total_words"],
                density_weight=self._get_weight(self.event_config, "density"),
                diversity_weight=self._get_weight(self.event_config, "diversity"),
                consistency_weight=self._get_weight(self.event_config, "consistency")
            )

            # ==================== Calculate Final Score ====================
            # Collect all enabled weights
            total_weight = 0.0
            weighted_sum = 0.0

            # Coherence weights
            coherence_total_weight = (
                self._get_weight(self.coherence_config, "density") +
                self._get_weight(self.coherence_config, "salient") +
                self._get_weight(self.coherence_config, "entropy")
            )
            if coherence_total_weight > 0:
                total_weight += coherence_total_weight
                weighted_sum += coherence_total_weight * coherence_score

            # Emotional weights
            emotional_total_weight = (
                self._get_weight(self.emotional_config, "intensity") +
                self._get_weight(self.emotional_config, "tension")
            )
            if emotional_total_weight > 0:
                total_weight += emotional_total_weight
                weighted_sum += emotional_total_weight * emotional_score

            # Event weights
            event_total_weight = (
                self._get_weight(self.event_config, "density") +
                self._get_weight(self.event_config, "diversity") +
                self._get_weight(self.event_config, "consistency")
            )
            if event_total_weight > 0:
                total_weight += event_total_weight
                weighted_sum += event_total_weight * event_score

            if total_weight == 0:
                raise ValueError("No metrics enabled for Layer 2")

            final_score = weighted_sum / total_weight

            # Prepare result
            computation_time = time.time() - start_time

            return LayerResult(
                layer_num=2,
                layer_name="Narrative Layer (叙事层)",
                score=round(final_score, 2),
                metrics={
                    "coherence": coherence_metrics,
                    "emotional": emotional_metrics,
                    "event": event_metrics
                },
                sub_scores={
                    "coherence_score": round(coherence_score, 2),
                    "coherence_density_score": round(coherence_breakdown["density_score"], 2),
                    "coherence_salient_score": round(coherence_breakdown["salient_score"], 2),
                    "coherence_entropy_score": round(coherence_breakdown["entropy_score"], 2),
                    "emotional_score": round(emotional_score, 2),
                    "emotional_intensity_score": round(emotional_breakdown["intensity_score"], 2),
                    "emotional_tension_score": round(emotional_breakdown["tension_score"], 2),
                    "event_score": round(event_score, 2),
                    "event_density_score": round(event_breakdown["density_score"], 2),
                    "event_diversity_score": round(event_breakdown["diversity_score"], 2),
                    "event_consistency_score": round(event_breakdown["consistency_score"], 2)
                },
                computation_time=computation_time
            )

        except Exception as e:
            return LayerResult(
                layer_num=2,
                layer_name="Narrative Layer (叙事层)",
                score=0.0,
                error=f"Layer 2 evaluation failed: {str(e)}",
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
