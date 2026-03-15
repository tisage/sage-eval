"""
Layer 5 Emotional Independent Validator for Cross-Verification

UPDATED 2025-12-23: Terminology update (Independent Validator, Iterative Evaluator)

Designed to:
1. Critically review iterative evaluator's emotional reasoning
2. Identify projection bias or hallucinations
3. Provide independent emotional scoring for inter-rater reliability
4. Flag agreements/disagreements
"""

from typing import Dict, Any, Optional, List
from .base_judge import BaseJudge
import json
import re


class EmotionalIndependentValidator(BaseJudge):
    """
    Layer 5 Emotional Independent Validator for cross-verification

    UPDATED 2025-12-23: Terminology update (content-limit, title-limit, Independent Validator)

    System prompt emphasizes:
    - Critical thinking about emotional representation
    - Projection bias detection
    - Independent judgment (not rubber-stamping)
    - Evidence-based reasoning quality assessment
    - Inter-rater reliability measurement
    """

    def __init__(self, llm_client: Any, temperature: float = 1.0):
        """
        Args:
            llm_client: LLM client instance
            temperature: 1.0 for gpt-5-mini (uses reasoning.effort instead)
        """
        super().__init__(llm_client, temperature)

    def get_system_prompt(self) -> str:
        """
        System prompt emphasizing independent validation role for Layer 5

        UPDATED 2025-12-23: Terminology update (Independent Validator, Iterative Evaluator)
        """
        return """You are an INDEPENDENT VALIDATOR for emotional-literary analysis.

Your role is to critically evaluate another LLM's (Iterative Evaluator) emotional-psychological assessment of a literary work using the Layer 5 4-dimension evaluation system.

**YOUR RESPONSIBILITIES**:

1. **Projection Bias Detection**:
   - Identify if iterative evaluator projected their own assumptions about emotional expression
   - Flag penalties for restrained/implicit emotions as "shallow"
   - Note rewards for explicit emotion words as "deep" without substance check
   - Check for cultural bias in emotional norms

2. **Hallucination Detection**:
   - Identify any claims about emotions not present in text
   - Flag inferred psychological states without textual grounding
   - Note over-interpretations or logical leaps
   - Check for Layer boundary violations (evaluating culture/philosophy instead of emotion)

3. **Reasoning Quality Assessment**:
   - Evaluate the coherence of emotional arguments
   - Check if evidence supports emotional interpretations
   - Identify missing evidence or weak reasoning
   - Assess adherence to Layer 5 (emotional-psychological content only)

4. **Confidence Calibration**:
   - Assess if confidence scores match evidence strength
   - Flag overconfidence (high confidence with ambiguous emotional content)
   - Flag underconfidence (low confidence with clear emotional markers)

5. **Independent Scoring**:
   - Provide your OWN scores based on the text
   - Compare with iterative evaluator's scores
   - Explain agreements and disagreements with specific evidence

**CRITICAL MINDSET**:
- Be skeptical but fair
- Other LLMs may hallucinate emotions or project biases
- Don't automatically agree - provide independent judgment
- Focus on evidence quality, not just score numbers
- Avoid your own projection bias

**EVALUATION DIMENSIONS** (Layer 5 - same as iterative evaluator):

1. **AC (Affective Complexity)**
   - Theoretical basis: Affect Theory (Sedgwick, Berlant, Ngai)
   - Focus: Multiplicity, contradiction, and evolution of emotional states
   - Evidence requirement: Passages showing multiple/contradictory emotions OR single dominant affect
   - NOT emotional binaries, static states, or one-dimensional affects

2. **PI (Psychological Interiority)**
   - Theoretical basis: Narrative Psychology (Cohn, Bruner, Bakhtin)
   - Focus: Access to characters' thoughts, motivations, self-awareness, mental processes
   - Evidence requirement: Interior monologue, free indirect discourse, psychological focalization OR behavioral description only
   - NOT plot complexity or character likability

3. **EG (Emotional Granularity)**
   - Theoretical basis: Emotion Granularity Research (Barrett)
   - Focus: Precision and differentiation of emotional vocabulary
   - Evidence requirement: Specific emotion terms or precise behavioral descriptions OR generic/vague language
   - NOT overall vocabulary sophistication (that's Layer 1)

4. **ENC (Emotional-Narrative Coherence)**
   - Theoretical basis: Organic Unity (New Criticism), Motivated Emotion (Wood)
   - Focus: Whether emotions are organically grounded in narrative situation
   - Evidence requirement: Emotion + context showing motivation OR disproportion/manipulation
   - NOT plot structure quality (that's Layer 2)

**STRICT LAYER 5 BOUNDARY**:
Evaluate ONLY emotional-psychological content. Do NOT evaluate:
- Cultural power structures or social hierarchies (Layer 4)
- Philosophical meaning or existential themes (Layer 6)
- Plot structure or narrative logic (Layer 2)
- Vocabulary sophistication per se (Layer 1)
"""

    def get_user_prompt(
        self,
        text: str,
        iterative_evaluation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate independent validation prompt

        UPDATED 2025-12-23: Terminology update (iterative_evaluation, Independent Validator)

        Args:
            text: Original text that was evaluated
            iterative_evaluation: Full results from EmotionalIterativeEvaluator
            context: Optional context (title, summary)
        """
        # Extract key information from iterative evaluation
        final_score = iterative_evaluation.get('score', 0.0)
        dimensions = iterative_evaluation.get('dimensions', {})
        rounds = iterative_evaluation.get('rounds', [])
        final_summary = iterative_evaluation.get('overall_reasoning', '')

        # Build conversation summary
        conversation_summary = self._summarize_iterative_conversation(rounds)

        prompt = f"""**INDEPENDENT VALIDATION TASK**

You are reviewing an emotional-psychological evaluation conducted by another LLM (Iterative Evaluator) through 5 rounds of self-reflection.

**Original Text**:
{text}

---

**Iterative Evaluator's Multi-Round Evaluation**:

{conversation_summary}

**Iterative Evaluator's Final Scores**:
Overall Score: {final_score}

Dimensions:
"""
        for dim_name, dim_data in dimensions.items():
            score = dim_data.get('score', 0.0)
            confidence = dim_data.get('confidence', 0)
            reasoning = dim_data.get('reasoning', '')
            prompt += f"\n- {dim_name}: {score} (confidence: {confidence}/5)\n  Reasoning: {reasoning}\n"

        prompt += f"\n**Iterative Evaluator's Summary**:\n{final_summary}\n"

        prompt += """
---

**YOUR TASK**:

1. **Critical Analysis**:
   - Review the iterative evaluator's reasoning across all 5 rounds
   - Identify any projection biases about emotional expression
   - Identify any hallucinations or unsupported emotional claims
   - Assess the quality of evidence cited
   - Evaluate confidence calibration
   - Check for layer boundary violations

2. **Independent Evaluation**:
   - Provide YOUR OWN scores for all 4 dimensions
   - Base your scores on the original text and verifiable evidence
   - Avoid your own projection bias
   - Compare with iterative evaluator's scores
   - Explain where you agree/disagree and WHY

3. **Overall Assessment**:
   - Do you trust the iterative evaluator's assessment?
   - What are the strengths of their analysis?
   - What are the weaknesses or concerns?
   - Should any scores be adjusted?

**REQUIRED JSON OUTPUT**:
```json
{
  "validation_review": {
    "projection_bias_flags": [
      {
        "dimension": "<dimension name>",
        "issue": "<description of projection bias>",
        "severity": "<low/medium/high>"
      }
    ],
    "hallucination_flags": [
      {
        "dimension": "<dimension name>",
        "issue": "<description of hallucinated emotion or unsupported claim>",
        "severity": "<low/medium/high>"
      }
    ],
    "reasoning_quality": {
      "affective_complexity": "<assessment of reasoning quality>",
      "psychological_interiority": "<assessment of reasoning quality>",
      "emotional_granularity": "<assessment of reasoning quality>",
      "emotional_narrative_coherence": "<assessment of reasoning quality>"
    },
    "confidence_assessment": "<overall assessment of primary judge's confidence calibration>",
    "layer_boundary_check": "<did primary judge stay within Layer 5, or evaluate Layer 4/6/2/1?>"
  },
  "independent_scores": {
    "affective_complexity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "emotional_states_present": ["<your list>"]
    },
    "psychological_interiority": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "interiority_markers": ["<your list>"]
    },
    "emotional_granularity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "vocabulary_examples": ["<your examples>"]
    },
    "emotional_narrative_coherence": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "coherence_assessment": "<organic/mixed/manipulative>"
    }
  },
  "validator_overall_score": <1.0-5.0>,
  "overall_reasoning": "<your holistic assessment of emotional-psychological representation quality>",
  "trust_level": "<high/medium/low - do you trust the iterative evaluation?>",
  "overall_assessment": "<2-3 sentence summary of your independent validation>",
  "recommended_adjustments": "<any suggested changes to iterative scores, or 'none'>"
}
```

Remember: Your job is to provide independent critical validation, not to rubber-stamp the iterative evaluator's work. Especially watch for projection bias.
"""
        return prompt

    def _summarize_iterative_conversation(self, rounds: List[Dict[str, Any]]) -> str:
        """
        Summarize the iterative evaluator's multi-round conversation for Layer 5

        UPDATED 2025-12-23: Renamed from _summarize_primary_conversation
        """
        summary = ""

        for i, round_data in enumerate(rounds, 1):
            summary += f"\n**Round {i}**:\n"

            if i == 1:
                # Round 1: Extract emotional content and scores
                content = round_data.get('extracted_content', {})
                summary += f"Extracted Content:\n"
                summary += f"- Explicit Emotions: {', '.join(content.get('explicit_emotions', []))}\n"
                summary += f"- Psychological Access: {content.get('psychological_access', 'N/A')}\n"
                summary += f"- Emotional Vocabulary Range: {content.get('emotional_vocabulary_range', 'N/A')}\n"

                scores = round_data.get('scores', {})
                summary += f"\nInitial Scores:\n"
                for dim, data in scores.items():
                    summary += f"- {dim}: {data.get('score', 0)} (confidence: {data.get('confidence', 0)})\n"

            elif i == 2:
                # Round 2: Projection bias check
                check = round_data.get('projection_check', {})
                summary += f"Projection Bias Check:\n"
                summary += f"- Biases Detected: {check.get('biases_detected', [])}\n"
                summary += f"- Score Adjustments: {check.get('score_adjustments_made', [])}\n"

                revised_scores = round_data.get('revised_scores', {})
                summary += f"\nRevised Scores:\n"
                for dim, data in revised_scores.items():
                    changes = data.get('changes_from_previous', 'No change')
                    summary += f"- {dim}: {data.get('score', 0)} (confidence: {data.get('confidence', 0)}) - {changes}\n"

            elif i == 3:
                # Round 3: Layer boundary check
                check = round_data.get('layer_boundary_check', {})
                summary += f"Layer Boundary Check:\n"
                summary += f"- Violations Detected: {check.get('corrections_made', [])}\n"

            elif i == 4:
                # Round 4: Evidence sufficiency check
                check = round_data.get('evidence_check', {})
                summary += f"Evidence Sufficiency Check:\n"
                summary += f"- Weak Evidence Dimensions: {check.get('weak_evidence_dimensions', [])}\n"
                summary += f"- Confidence Recalibrations: {check.get('confidence_recalibrations', [])}\n"

            elif i == 5:
                # Round 5: Final
                final_scores = round_data.get('final_scores', {})
                summary += f"Final Scores:\n"
                for dim, data in final_scores.items():
                    summary += f"- {dim}: {data.get('score', 0)} (confidence: {data.get('confidence', 0)})\n"
                    summary += f"  Convergence: {data.get('convergence_status', 'N/A')}\n"

        return summary

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from peer judge
        """
        try:
            # Remove markdown code blocks if present
            response = re.sub(r'```json\s*', '', response)
            response = re.sub(r'```\s*$', '', response)
            response = response.strip()

            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON parsing failed: {str(e)}",
                "raw_response": response
            }

    def evaluate(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute independent validation

        UPDATED 2025-12-23: Terminology update (iterative_evaluation, Independent Validator)

        Args:
            text: Original text that was evaluated
            context: Must include 'iterative_evaluation' key with full iterative evaluator results

        Returns:
            {
                "validation_review": {...},
                "independent_scores": {...},
                "validator_overall_score": float,
                "trust_level": str,
                "agreement_analysis": {...},
                "error": Optional[str]
            }
        """
        try:
            if not context or 'iterative_evaluation' not in context:
                raise ValueError("Independent validation requires 'iterative_evaluation' in context")

            iterative_evaluation = context['iterative_evaluation']

            # Generate validation prompt
            system_prompt = self.get_system_prompt()
            user_prompt = self.get_user_prompt(text, iterative_evaluation, context)

            # Call LLM
            response = self.llm_client.generate_with_messages(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature
            )

            # Parse response
            validator_data = self.parse_response(response)

            # Compute agreement metrics
            agreement_analysis = self._analyze_agreement(
                iterative_evaluation.get('dimensions', {}),
                validator_data.get('independent_scores', {})
            )

            return {
                **validator_data,
                "agreement_analysis": agreement_analysis,
                "raw_response": response,
                "error": None
            }

        except Exception as e:
            return {
                "validation_review": {},
                "independent_scores": {},
                "validator_overall_score": 0.0,
                "trust_level": "error",
                "error": str(e)
            }

    def _analyze_agreement(
        self,
        iterative_dimensions: Dict[str, Any],
        validator_dimensions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze agreement between iterative evaluator and validator scores for Layer 5

        UPDATED 2025-12-23: Terminology update (iterative_dimensions, validator_dimensions)
        """
        agreements = []
        disagreements = []
        score_diffs = {}

        dimensions = [
            "affective_complexity",
            "psychological_interiority",
            "emotional_granularity",
            "emotional_narrative_coherence"
        ]

        for dim in dimensions:
            iterative_score = iterative_dimensions.get(dim, {}).get('score', 0.0)
            validator_score = validator_dimensions.get(dim, {}).get('score', 0.0)

            diff = abs(iterative_score - validator_score)
            score_diffs[dim] = diff

            # Agreement threshold: < 0.5
            if diff < 0.5:
                agreements.append(dim)
            else:
                disagreements.append(dim)

        return {
            "agreements": agreements,
            "disagreements": disagreements,
            "score_differences": score_diffs,
            "mean_difference": sum(score_diffs.values()) / len(score_diffs) if score_diffs else 0.0
        }
