"""
Layer 4 Cultural Independent Validator for Cross-Verification

UPDATED 2025-12-23: Terminology update (Independent Validator, Iterative Evaluator)

Designed to:
1. Critically review iterative evaluator's reasoning
2. Identify potential hallucinations or logical gaps
3. Provide independent scoring for inter-rater reliability
4. Flag agreements/disagreements
"""

from typing import Dict, Any, Optional, List
from .base_judge import BaseJudge
import json
import re


class CulturalIndependentValidator(BaseJudge):
    """
    Layer 4 Cultural Independent Validator for cross-verification

    UPDATED 2025-12-23: Terminology update (content-limit, title-limit, Independent Validator)
    UPDATED 2025-12-20: v4.0 4-dimension cultural evaluation system

    System prompt emphasizes:
    - Critical thinking and hallucination detection
    - Independent judgment (not rubber-stamping)
    - Evidence-based reasoning quality assessment
    - Inter-rater reliability measurement
    """

    def __init__(self, llm_client: Any, temperature: float = 0.2):
        """
        Args:
            llm_client: LLM client instance
            temperature: 0.2 recommended (consistent with iterative evaluator)
        """
        super().__init__(llm_client, temperature)

    def get_system_prompt(self) -> str:
        """
        System prompt emphasizing independent validation role
        UPDATED 2025-12-23: Terminology update (Independent Validator, Iterative Evaluator)
        UPDATED 2025-12-20: v4.0 4-dimension cultural evaluation system
        """
        return """You are an INDEPENDENT VALIDATOR for cultural literary analysis.

Your role is to critically evaluate another LLM's iterative cultural assessment of a literary work using the v4.0 4-dimension evaluation system.

**YOUR RESPONSIBILITIES**:

1. **Hallucination Detection**:
   - Identify any claims made without textual evidence
   - Flag fabricated historical facts or cultural details
   - Note over-interpretations or logical leaps
   - Check for Layer boundary violations (evaluating emotions/philosophy instead of culture)

2. **Reasoning Quality Assessment**:
   - Evaluate the coherence of arguments
   - Check if evidence supports conclusions
   - Identify missing evidence or weak reasoning
   - Assess adherence to Layer 4 (cultural-social structures only)

3. **Confidence Calibration**:
   - Assess if confidence scores match evidence strength
   - Flag overconfidence (high confidence with weak evidence)
   - Flag underconfidence (low confidence with strong evidence)

4. **Independent Scoring**:
   - Provide your OWN scores based on the text
   - Compare with primary judge's scores
   - Explain agreements and disagreements with specific evidence

**CRITICAL MINDSET**:
- Be skeptical but fair
- Other LLMs may hallucinate - your job is to catch this
- Don't automatically agree - provide independent judgment
- Focus on evidence quality, not just score numbers
- Apply cultural neutrality - no Western-centric bias

**EVALUATION DIMENSIONS** (v4.0 - same as primary judge):

1. **IPD (Intersectional Power Dynamics)**
   - Theoretical basis: Bourdieu + Marxist + Feminist + Postcolonial + Power Structure Analysis
   - Focus: Power distribution, negotiation, and legitimation through social structures (may include class, gender, race, kinship, occupation, age, religion, etc.)
   - Evidence requirement: Textual moments demonstrating power structures with concrete grounding

2. **CVP (Cultural Voice & Perspective)**
   - Theoretical basis: Said's Orientalism + Spivak + Narrative Theory
   - Focus: Insider vs. outsider narrative positioning
   - Evidence requirement: Linguistic markers of cultural authority or exoticization

3. **CSP (Cultural Specificity)**
   - Theoretical basis: Geertz's Thick Description + Cultural Anthropology
   - Focus: Density of cultural details (temporal/spatial/social/material)
   - Evidence requirement: Specific cultural elements across at least 3 domains

4. **CPC (Cultural Pattern Complexity)**
   - Theoretical basis: Lévi-Strauss + Cultural Systems Theory
   - Focus: Structural complexity (4 sub-dimensions)
     * Relational Complexity
     * Conflict Structuration
     * Cultural Self-Reflexivity
     * Pattern Archetypal Quality
   - Evidence requirement: Evidence for at least 3 sub-dimensions

**STRICT LAYER 4 BOUNDARY**:
Evaluate ONLY cultural-social structures. Do NOT evaluate:
- Emotional responses or reader impact (Layer 5)
- Philosophical meaning or existential themes (Layer 6)
- Narrative techniques or plot logic (Layer 2)
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
            iterative_evaluation: Full results from CulturalIterativeEvaluator
            context: Optional context (title, summary)
        """
        # Extract key information from iterative evaluation
        final_score = iterative_evaluation.get('score', 0.0)
        dimensions = iterative_evaluation.get('dimensions', {})
        rounds = iterative_evaluation.get('rounds', [])
        final_summary = iterative_evaluation.get('final_summary', '')

        # Build conversation summary
        conversation_summary = self._summarize_iterative_conversation(rounds)

        prompt = f"""**INDEPENDENT VALIDATION TASK**

You are reviewing a cultural evaluation conducted by another LLM (Iterative Evaluator) through 5 rounds of self-reflection.

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
   - Identify any hallucinations or unsupported claims
   - Assess the quality of evidence cited
   - Evaluate confidence calibration

2. **Independent Evaluation**:
   - Provide YOUR OWN scores for all 4 dimensions
   - Base your scores on the original text and verifiable evidence
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
    "hallucination_flags": [
      {
        "dimension": "<dimension name>",
        "issue": "<description of hallucination or unsupported claim>",
        "severity": "<low/medium/high>"
      }
    ],
    "reasoning_quality": {
      "intersectional_power_dynamics": "<assessment of reasoning quality>",
      "cultural_voice_perspective": "<assessment of reasoning quality>",
      "cultural_specificity": "<assessment of reasoning quality>",
      "cultural_pattern_complexity": "<assessment of reasoning quality>"
    },
    "confidence_assessment": "<overall assessment of primary judge's confidence calibration>",
    "layer_boundary_check": "<did primary judge stay within Layer 4, or evaluate Layer 5/6?>"
  },
  "independent_scores": {
    "intersectional_power_dynamics": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "power_axes": ["<your list of social axes>"]
    },
    "cultural_voice_perspective": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "positioning": "<insider/outsider/mixed>"
    },
    "cultural_specificity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "domains_covered": ["<your list: temporal/spatial/social/material>"]
    },
    "cultural_pattern_complexity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "sub_dimension_scores": {
        "relational_complexity": <1.0-5.0>,
        "conflict_structuration": <1.0-5.0>,
        "cultural_self_reflexivity": <1.0-5.0>,
        "pattern_archetypal_quality": <1.0-5.0>
      }
    }
  },
  "validator_overall_score": <1.0-5.0>,
  "overall_reasoning": "<your holistic assessment of cultural representation quality>",
  "trust_level": "<high/medium/low - do you trust the iterative evaluation?>",
  "overall_assessment": "<2-3 sentence summary of your independent validation>",
  "recommended_adjustments": "<any suggested changes to iterative scores, or 'none'>"
}
```

Remember: Your job is to provide independent critical validation, not to rubber-stamp the iterative evaluator's work.
"""
        return prompt

    def _summarize_iterative_conversation(self, rounds: List[Dict[str, Any]]) -> str:
        """
        Summarize the iterative evaluator's multi-round conversation

        UPDATED 2025-12-23: Renamed from _summarize_primary_conversation
        """
        summary = ""

        for i, round_data in enumerate(rounds, 1):
            summary += f"\n**Round {i}**:\n"

            if i == 1:
                # Round 1: Extract facts and scores
                facts = round_data.get('extracted_facts', {})
                summary += f"Extracted Facts:\n"
                summary += f"- Time Period: {facts.get('time_period', 'N/A')}\n"
                summary += f"- Social Structures: {', '.join(facts.get('social_structures', []))}\n"
                summary += f"- Cultural Elements: {', '.join(facts.get('cultural_elements', []))}\n"

                scores = round_data.get('scores', {})
                summary += f"\nInitial Scores:\n"
                for dim, data in scores.items():
                    summary += f"- {dim}: {data.get('score', 0)} (confidence: {data.get('confidence', 0)})\n"

            elif i == 2:
                # Round 2: Self-critique
                critique = round_data.get('self_critique', {})
                summary += f"Self-Critique:\n"
                summary += f"- Potential Hallucinations: {critique.get('potential_hallucinations', [])}\n"
                summary += f"- Confidence Adjustments: {critique.get('confidence_adjustments', 'None')}\n"

                revised_scores = round_data.get('revised_scores', {})
                summary += f"\nRevised Scores:\n"
                for dim, data in revised_scores.items():
                    changes = data.get('changes_from_round1', 'No change')
                    summary += f"- {dim}: {data.get('score', 0)} (confidence: {data.get('confidence', 0)}) - {changes}\n"

            elif i == 3:
                # Round 3: Final
                final_scores = round_data.get('final_scores', {})
                summary += f"Final Scores:\n"
                for dim, data in final_scores.items():
                    summary += f"- {dim}: {data.get('score', 0)} (confidence: {data.get('confidence', 0)})\n"
                    summary += f"  Reasoning: {data.get('final_reasoning', '')}\n"

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
        Analyze agreement between iterative evaluator and validator scores

        UPDATED 2025-12-23: Terminology update (iterative_dimensions, validator_dimensions)
        UPDATED 2025-12-20: 4-dimension system (v4.0)
        """
        agreements = []
        disagreements = []
        score_diffs = {}

        # UPDATED 2025-12-20: 4-dimension system (v4.0)
        dimensions = [
            "intersectional_power_dynamics",
            "cultural_voice_perspective",
            "cultural_specificity",
            "cultural_pattern_complexity"
        ]

        for dim in dimensions:
            iterative_score = iterative_dimensions.get(dim, {}).get('score', 0.0)
            validator_score = validator_dimensions.get(dim, {}).get('score', 0.0)

            diff = abs(iterative_score - validator_score)
            score_diffs[dim] = diff

            # Agreement threshold: < 0.5 (as specified in layer4_refactor_plan_v4.0.md)
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
