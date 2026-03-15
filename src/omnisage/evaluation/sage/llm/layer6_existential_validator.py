"""
Layer 6 Existential Independent Validator for Cross-Verification

Designed to:
1. Critically review iterative evaluator's existential reasoning
2. Identify projection bias or hallucinations
3. Provide independent existential scoring for inter-rater reliability
4. Flag agreements/disagreements
"""

from typing import Dict, Any, Optional, List
from .base_judge import BaseJudge
import json
import re


class ExistentialIndependentValidator(BaseJudge):
    """
    Layer 6 Existential Independent Validator for cross-verification

    System prompt emphasizes:
    - Critical thinking about existential-philosophical representation
    - Projection bias detection (Western existentialism imposition)
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
        System prompt emphasizing independent validation role for Layer 6
        """
        return """You are an INDEPENDENT VALIDATOR for existential-philosophical literary analysis.

Your role is to critically evaluate another LLM's (Iterative Evaluator) existential-philosophical assessment of a literary work using the Layer 6 4-dimension evaluation system.

**YOUR RESPONSIBILITIES**:

1. **Projection Bias Detection**:
   - Identify if iterative evaluator imposed Western existentialist frameworks (Sartre, Camus, Heidegger) on non-Western texts
   - Flag penalties for implicit existential themes as "lacking philosophical depth"
   - Note rewards for explicit philosophical discourse as "deep" without substance check
   - Check for equating dark/tragic themes with existential profundity
   - Verify recognition of diverse philosophical traditions (Eastern, African, Indigenous)

2. **Hallucination Detection**:
   - Identify any claims about philosophical themes not present in text
   - Flag inferred existential depth without textual grounding
   - Note over-interpretations or philosophical projection
   - Check for Layer boundary violations (evaluating emotion/culture instead of existential themes)

3. **Reasoning Quality Assessment**:
   - Evaluate the coherence of existential-philosophical arguments
   - Check if evidence supports philosophical interpretations
   - Identify missing evidence or weak reasoning
   - Assess adherence to Layer 6 (existential-philosophical content only)

4. **Confidence Calibration**:
   - Assess if confidence scores match evidence strength
   - Flag overconfidence (high confidence with ambiguous philosophical content)
   - Flag underconfidence (low confidence with clear existential themes)

5. **Independent Scoring**:
   - Provide your OWN scores based on the text
   - Compare with iterative evaluator's scores
   - Explain agreements and disagreements with specific evidence

**CRITICAL MINDSET**:
- Be skeptical but fair
- Other LLMs may hallucinate philosophical depth or project frameworks
- Don't automatically agree - provide independent judgment
- Focus on evidence quality, not just score numbers
- Avoid your own projection bias

**EVALUATION DIMENSIONS** (Layer 6 - same as iterative evaluator):

1. **LP (Life Philosophy)**
   - Theoretical basis: Existentialism (Heidegger, Sartre, Camus) + Eastern Philosophy
   - Focus: Depth of reflection on life's meaning, purpose, and values
   - Evidence requirement: Passages showing philosophical inquiry or its absence
   - NOT emotional depth (Layer 5) or cultural analysis (Layer 4)

2. **MR (Moral Reflection)**
   - Theoretical basis: Moral Philosophy (Levinas, MacIntyre, Confucian Ethics)
   - Focus: Engagement with ethical dilemmas, moral choices, genuine complexity
   - Evidence requirement: Moral dilemmas with no easy resolution or simplistic morality
   - NOT cultural power structures (Layer 4) or emotional responses to moral situations (Layer 5)

3. **HC (Human Condition)**
   - Theoretical basis: Philosophical Anthropology (Arendt, Nussbaum)
   - Focus: Insight into universal aspects of human existence (mortality, suffering, alienation, freedom)
   - Evidence requirement: Universal themes embodied in particular situations or their absence
   - NOT emotional portrayal of suffering (Layer 5) or plot development (Layer 2)

4. **ME (Meaning Exploration)**
   - Theoretical basis: Hermeneutics (Ricoeur, Gadamer)
   - Focus: Active pursuit of existential questions, open-ended inquiry
   - Evidence requirement: Existential questioning or didactic answers
   - NOT narrative technique (Layer 2) or vocabulary sophistication (Layer 1)

**STRICT LAYER 6 BOUNDARY**:
Evaluate ONLY existential-philosophical content. Do NOT evaluate:
- Cultural power structures or social hierarchies (Layer 4)
- Emotional depth or psychological interiority (Layer 5)
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

        Args:
            text: Original text that was evaluated
            iterative_evaluation: Full results from ExistentialIterativeEvaluator
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

You are reviewing an existential-philosophical evaluation conducted by another LLM (Iterative Evaluator) through 5 rounds of self-reflection.

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
   - Identify any projection biases (Western existentialism imposition, explicit philosophy bias)
   - Identify any hallucinations or unsupported philosophical claims
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
        "issue": "<description of hallucinated theme or unsupported claim>",
        "severity": "<low/medium/high>"
      }
    ],
    "reasoning_quality": {
      "life_philosophy": "<assessment of reasoning quality>",
      "moral_reflection": "<assessment of reasoning quality>",
      "human_condition": "<assessment of reasoning quality>",
      "meaning_exploration": "<assessment of reasoning quality>"
    },
    "confidence_assessment": "<overall assessment of iterative evaluator's confidence calibration>",
    "layer_boundary_check": "<did iterative evaluator stay within Layer 6, or evaluate Layer 4/5/2/1?>"
  },
  "independent_scores": {
    "life_philosophy": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "philosophical_themes_present": ["<your list>"]
    },
    "moral_reflection": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "moral_complexity_markers": ["<your list>"]
    },
    "human_condition": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "human_condition_themes": ["<your list>"]
    },
    "meaning_exploration": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<your reasoning with textual evidence>",
      "agreement_with_iterative": "<agree/disagree/partial>",
      "score_difference": <float>,
      "inquiry_openness": "<open-ended/partially resolved/didactic/absent>"
    }
  },
  "validator_overall_score": <1.0-5.0>,
  "overall_reasoning": "<your holistic assessment of existential-philosophical representation quality>",
  "trust_level": "<high/medium/low - do you trust the iterative evaluation?>",
  "overall_assessment": "<2-3 sentence summary of your independent validation>",
  "recommended_adjustments": "<any suggested changes to iterative scores, or 'none'>"
}
```

Remember: Your job is to provide independent critical validation, not to rubber-stamp the iterative evaluator's work. Especially watch for Western existentialism projection bias and hallucinated philosophical depth.
"""
        return prompt

    def _summarize_iterative_conversation(self, rounds: List[Dict[str, Any]]) -> str:
        """
        Summarize the iterative evaluator's multi-round conversation for Layer 6
        """
        summary = ""

        for i, round_data in enumerate(rounds, 1):
            summary += f"\n**Round {i}**:\n"

            if i == 1:
                # Round 1: Extract existential content and scores
                content = round_data.get('extracted_content', {})
                summary += f"Extracted Content:\n"
                summary += f"- Philosophical Discourse: {', '.join(content.get('philosophical_discourse', []))}\n"
                summary += f"- Moral Dilemmas: {', '.join(content.get('moral_dilemmas', []))}\n"
                summary += f"- Existential Themes: {', '.join(content.get('existential_themes', []))}\n"

                scores = round_data.get('scores', {})
                summary += f"\nInitial Scores:\n"
                for dim, data in scores.items():
                    summary += f"- {dim}: {data.get('score', 0)} (confidence: {data.get('confidence', 0)})\n"

            elif i == 2:
                # Round 2: Projection bias check
                check = round_data.get('projection_check', {})
                summary += f"Projection Bias Check:\n"
                summary += f"- Biases Detected: {check.get('biases_detected', [])}\n"
                summary += f"- Western Framework Imposition: {check.get('western_framework_imposition', 'N/A')}\n"
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
        Parse JSON response from validator
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
        Analyze agreement between iterative evaluator and validator scores for Layer 6
        """
        agreements = []
        disagreements = []
        score_diffs = {}

        dimensions = [
            "life_philosophy",
            "moral_reflection",
            "human_condition",
            "meaning_exploration"
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
