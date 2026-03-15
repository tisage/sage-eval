"""
Layer 4 Cultural Iterative Evaluator with Self-Reflection

Iterative evaluation to reduce variance and increase confidence through:
1. Iterative Evaluator: Multi-round self-reflection (5 rounds default, configurable)
2. Independent Validator: Critical review of iterative evaluator's reasoning

Designed to address:
- Historical accuracy hallucinations
- Variance reduction across prompt versions
- Confidence tracking
- Score convergence through reflection
"""

from typing import Dict, Any, Optional, List
from .base_judge import BaseJudge
import json
import re


class CulturalIterativeEvaluator(BaseJudge):
    """
    Layer 4 Cultural Iterative Evaluator with self-reflection mechanism

    UPDATED 2025-12-23: Terminology update (content-limit, title-limit, Iterative Evaluator)
    UPDATED 2025-12-20: v4.0 4-dimension cultural evaluation system
    Design Principles: Strict Layer 4 boundary, Cultural neutrality, Dimension independence
    Research Goal: Evaluate cultural representation quality with theoretically grounded dimensions

    Evaluation dimensions (v4.0):
    1. IPD (Intersectional Power Dynamics) - Bourdieu + Marxist + Feminist + Postcolonial + Intersectionality
    2. CVP (Cultural Voice & Perspective) - Said's Orientalism + Spivak + Narrative Theory
    3. CSP (Cultural Specificity) - Geertz's Thick Description + Cultural Anthropology
    4. CPC (Cultural Pattern Complexity) - Lévi-Strauss + Cultural Systems + 4 sub-dimensions:
       - Relational Complexity
       - Conflict Structuration
       - Cultural Self-Reflexivity
       - Pattern Archetypal Quality

    Iterative evaluation process:
    - Round 1: Cultural fact extraction + initial scoring + confidence
    - Rounds 2-4: Self-reflection, hallucination check, layer boundary check
    - Round 5: Final confirmation + iterative_overall_score + convergence analysis
    """

    def __init__(
        self,
        llm_client: Any,
        temperature: float = 1.0,  # Note: gpt-5-mini doesn't support custom temperature
        num_rounds: int = 5,  # UPDATED: default 5 rounds
        mode: str = "content-limit"  # "content-limit" or "title-limit"
    ):
        """
        Args:
            llm_client: LLM client instance
            temperature: For gpt-5-mini, this is ignored (uses reasoning.effort instead)
            num_rounds: Number of self-reflection rounds (default 5, configurable)
            mode: Evaluation mode - "content-limit" (text only) or "title-limit" (metadata only)
        """
        super().__init__(llm_client, temperature)
        self.num_rounds = num_rounds
        self.mode = mode

    def get_system_prompt(self) -> str:
        """
        System prompt for v4.0 4-dimension cultural evaluation system

        Design principles: Strict Layer 4 boundary, Cultural neutrality, No examples, Abstract definitions
        """
        mode_instruction = ""
        if self.mode == "title-limit":
            mode_instruction = """
**EVALUATION MODE**: title-limit
- You are provided with ONLY the work's title and author (NO text content)
- Synthesize assessments from literary critics, scholars, and historical reception
- Draw on academic analyses and critical consensus about this specific work
- Cite specific critics or scholarly perspectives where relevant
- Distinguish reliable assessments from speculative interpretations
"""
        else:  # content-limit
            mode_instruction = """
**EVALUATION MODE**: content-limit
- You are provided with the story text ONLY (no title, author, or metadata)
- Evaluate based SOLELY on textual evidence present in the provided content
- DO NOT use any prior knowledge about literary works or authors
- Base all judgments exclusively on what appears in the text itself
- Cite specific passages to support all claims
"""

        return f"""You are an expert cultural-literary analyst evaluating how texts represent culture, power, and social structures.

# Core Evaluation Principles

1. **Evidence Sovereignty**: All scores must cite specific textual evidence. Insufficient evidence = lower confidence.

2. **Descriptive Not Evaluative**: Dimensions describe cultural representation, not value judgments. You are measuring, not judging quality.

3. **Strict Layer Boundary**: Evaluate ONLY cultural-social structures. Do NOT evaluate:
   - Emotional responses or reader impact (beyond your scope)
   - Philosophical meaning or existential themes (beyond your scope)
   - Narrative techniques or plot logic (beyond your scope)

4. **Cultural Neutrality**: Apply standards equally to all cultural contexts (Western/non-Western, historical/contemporary). Do NOT privilege any culture as normative.

5. **Anti-Cliché**: Avoid empty phrases: "profound depth", "transcends time", "rich tapestry", "nuanced portrayal". Use specific textual evidence instead.

6. **Dimension Independence**: Evaluate each dimension independently. Do NOT assume correlation. High score in one dimension does NOT imply high scores in others.

{mode_instruction}

# Evaluation Dimensions (4 Dimensions)

## 1. IPD (Intersectional Power Dynamics)
**Theoretical Basis**: Bourdieu's Field Theory + Marxist Criticism + Feminist Theory + Postcolonial Theory + Power Structure Analysis

**Definition**: Evaluate the complexity and configuration of power relations as they operate through social structures and relationships in the text. Power may be organized along various social axes including but not limited to: class, gender, race/ethnicity, kinship, occupation, age, religion, institutional position.

**Focus**:
- How power is distributed, negotiated, and legitimated through social structures
- Interaction between different forms of capital (economic, cultural, symbolic) or authority
- Structural mechanisms through which power operates (institutions, norms, hierarchies, family systems)
- Complexity of power configuration: simple binary oppositions (low) vs. multi-layered structural tensions (high)

**Evidence Requirement**: Cite textual moments where power relations are enacted. May involve single or multiple axes - what matters is structural complexity and concrete textual grounding.

**NOT Evaluate**: Characters' emotional responses to power, moral judgments about power, whether power dynamics make plot compelling.

---

## 2. CVP (Cultural Voice & Perspective)
**Theoretical Basis**: Postcolonial Theory (Said, Spivak) + Narrative Theory

**Definition**: Evaluate the positioning of narrative voice in relation to cultural material - insider perspective with cultural authority vs. outsider gaze with potential exoticization.

**Focus**:
- Epistemic stance of narrator toward cultural elements
- Linguistic markers of insider vs. outsider positioning
- Whether cultural systems are presented coherently from within or as spectacle from without

**Evidence Requirement**: Cite textual markers of narrative positioning (voice, focalization, language register, cultural knowledge deployment).

**NOT Evaluate**: Reader empathy with characters, first-person vs. third-person narration per se, moral authority of narrator.

---

## 3. CSP (Cultural Specificity)
**Theoretical Basis**: Geertz's Thick Description + Cultural Anthropology

**Definition**: Evaluate the density and precision of cultural particularities in representing time, place, social practices, and material culture.

**Focus**:
- Temporal specificity (historical period, chronological markers)
- Geographic specificity (place names, spatial organization)
- Social practices and customs (rituals, norms, behaviors)
- Material culture (objects, technologies, built environment)

**Evidence Requirement**: Cite specific cultural elements across at least three domains (temporal/spatial/social/material).

**NOT Evaluate**: Whether cultural details make story emotionally engaging, whether setting serves plot, philosophical significance of elements.

---

## 4. CPC (Cultural Pattern Complexity)
**Theoretical Basis**: Structural Anthropology (Lévi-Strauss) + Cultural Systems Theory + Postcolonial Reflexivity

**Definition**: Evaluate structural complexity of cultural patterns, including relational systems, conflict structures, self-reflexivity, and archetypal depth.

**Focus - Four Sub-Dimensions**:

**4.1 Relational Complexity**: Structural complexity of social relationship systems (beyond binary good/bad)

**4.2 Conflict Structuration**: Whether conflicts are structural tensions or stereotypical oppositions

**4.3 Cultural Self-Reflexivity**: Whether text reflects on its own cultural conditions (critical distance vs. transparency)

**4.4 Pattern Archetypal Quality**: Deep structural patterns vs. surface clichés (archetype vs. genre conventions)

**Evidence Requirement**: Cite evidence for at least three sub-dimensions (relational/conflict/reflexivity/archetypal).

**NOT Evaluate**: Character psychological complexity, philosophical proposition depth, plot complexity.

---

# Scoring Calibration

Use full score range (1.0-5.0):
- **1.0-2.0**: Weak cultural representation
- **2.0-3.5**: Moderate cultural representation
- **3.5-4.5**: Strong cultural representation
- **4.5-5.0**: Exceptional cultural representation

Do NOT cluster scores in middle range (3.0-4.0).

---

# Multi-Round Self-Reflection Process

You will conduct **5 rounds** of evaluation:

- **Round 1**: Extract cultural facts and provide initial scores (all 4 dimensions)
- **Round 2-4**: Self-critique, identify issues, revise scores with reasoning
- **Round 5**: Final scores with convergence analysis and holistic overall judgment

**Convergence Goal**: Score change between Round 4→5 should be < 0.3 per dimension.

---

**OUTPUT FORMAT**: Return ONLY valid JSON (no markdown code blocks, no extra text).
"""

    def _get_initial_prompt(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Round 1: Extract facts and provide initial scoring
        UPDATED 2025-12-20: 4-dimension system (IPD, CVP, CSP, CPC)

        Args:
            text: Full text of the work
            context: Optional context dict with 'title' and 'summary'
        """
        title = context.get('title') if context else None
        summary = context.get('summary') if context else None

        prompt = f"**ROUND 1/{self.num_rounds}: FACT EXTRACTION AND INITIAL EVALUATION**\n\n"

        if self.mode == "title-limit" and title:
            prompt += f"**Work Title**: {title}\n"
            if summary:
                prompt += f"**Summary**: {summary}\n"
            prompt += "\n**Instructions**:\n"
            prompt += "- Synthesize assessments from literary scholars and critics about this work\n"
            prompt += "- Draw on academic analyses and historical reception\n"
            prompt += "- Clearly distinguish reliable scholarly consensus from speculative interpretations\n\n"
        else:  # content-limit mode
            prompt += "**Instructions**:\n"
            prompt += "- Evaluate based ONLY on the provided text content\n"
            prompt += "- Do NOT use any prior knowledge about this work or author\n\n"

        prompt += f"**Text to Evaluate**:\n{text}\n\n"

        prompt += """**TASK**:

Step 1: Extract Cultural Facts
List all details relevant to cultural evaluation:
- Time period indicators
- Social structures and power hierarchies
- Cultural practices, rituals, customs
- Material culture (objects, clothing, technology, architecture)
- Narrative voice characteristics (insider/outsider markers)

Step 2: Evaluate Each Dimension
For each dimension, provide:
- Score (1.0-5.0, use full range)
- Confidence (1-5, where 5=highly confident, 1=very uncertain)
- Reasoning (cite specific textual evidence)
- Dimension-specific analysis fields

**REQUIRED JSON OUTPUT**:
```json
{
  "round": 1,
  "extracted_facts": {
    "time_period": "<identified temporal setting or 'uncertain'>",
    "social_structures": ["<list key power relationships and hierarchies>"],
    "cultural_elements": ["<list customs, practices, rituals>"],
    "material_culture": ["<list significant objects, technologies, built environment>"],
    "power_configurations": ["<list observed power relations across class/gender/race>"],
    "narrative_positioning": "<initial assessment: insider/outsider/mixed>"
  },
  "scores": {
    "intersectional_power_dynamics": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite specific textual moments demonstrating power structures>",
      "evidence_strength": "<weak/medium/strong>",
      "power_axes": ["<list social axes, e.g., class/gender/race/kinship/occupation/age/religion/institutional>"]
    },
    "cultural_voice_perspective": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite textual markers of narrative positioning>",
      "evidence_strength": "<weak/medium/strong>",
      "positioning": "<insider/outsider/mixed>"
    },
    "cultural_specificity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite specific cultural details across domains>",
      "evidence_strength": "<weak/medium/strong>",
      "domains_covered": ["<list: temporal/spatial/social/material>"]
    },
    "cultural_pattern_complexity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite evidence for structural complexity>",
      "evidence_strength": "<weak/medium/strong>",
      "sub_dimension_scores": {
        "relational_complexity": <1.0-5.0>,
        "conflict_structuration": <1.0-5.0>,
        "cultural_self_reflexivity": <1.0-5.0>,
        "pattern_archetypal_quality": <1.0-5.0>
      },
      "sub_dimension_notes": "<brief analysis of each sub-dimension>"
    }
  },
  "prior_knowledge_check": {
    "text_recognized": <true/false>,
    "potentially_biased_dimensions": ["<list dimensions that might be affected by prior knowledge>"],
    "text_only_dimensions": ["<list dimensions evaluable from text alone>"]
  },
  "iterative_overall_score": <1.0-5.0>,
  "overall_confidence": <1-5>
}
```

Remember: Mark uncertainties explicitly. It's better to acknowledge unknowns than to hallucinate facts.
"""
        return prompt

    def _get_reflection_prompt(self, round_num: int, previous_response: str) -> str:
        """
        Rounds 2 to (N-1): Self-reflection and critical review
        UPDATED 2025-12-20: 4-dimension system (IPD, CVP, CSP, CPC)

        Args:
            round_num: Current round number
            previous_response: Response from previous round (raw JSON string)
        """
        return f"""**ROUND {round_num}/{self.num_rounds}: CRITICAL SELF-REFLECTION**

Review your previous evaluation from Round {round_num - 1}.

**Your Previous Response**:
{previous_response}

**TASK**:

1. **Hallucination Check**:
   - Did you make any claims not supported by the text?
   - Did you fabricate cultural or historical details?
   - Did you over-interpret ambiguous evidence?

2. **Confidence Calibration**:
   - Were your confidence scores accurate?
   - Should any be lowered due to insufficient evidence?

3. **Reasoning Quality**:
   - Are your arguments logically sound?
   - Did you cite specific textual evidence?
   - Are there alternative interpretations?

4. **Layer Boundary Check**:
   - Did you accidentally evaluate emotions (Layer 5) or philosophy (Layer 6)?
   - Did all evaluations stay within Layer 4 (cultural-social structures)?

5. **Score Adjustment** (if needed):
   - Revise scores based on stricter evidence standards
   - Increase uncertainty markers where appropriate

**REQUIRED JSON OUTPUT**:
```json
{{
  "round": {round_num},
  "self_critique": {{
    "potential_hallucinations": ["<list any unsupported claims>"],
    "confidence_adjustments": "<explanation of any confidence changes>",
    "reasoning_issues": "<any logical gaps or weak arguments identified>",
    "layer_boundary_violations": ["<any dimensions where you evaluated beyond Layer 4>"]
  }},
  "revised_scores": {{
    "intersectional_power_dynamics": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning with evidence>",
      "changes_from_previous": "<what changed and why>",
      "power_axes": ["<updated list of social axes>"]
    }},
    "cultural_voice_perspective": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning with evidence>",
      "changes_from_previous": "<what changed and why>",
      "positioning": "<insider/outsider/mixed>"
    }},
    "cultural_specificity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning with evidence>",
      "changes_from_previous": "<what changed and why>",
      "domains_covered": ["<updated list: temporal/spatial/social/material>"]
    }},
    "cultural_pattern_complexity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning with evidence>",
      "changes_from_previous": "<what changed and why>",
      "sub_dimension_scores": {{
        "relational_complexity": <1.0-5.0>,
        "conflict_structuration": <1.0-5.0>,
        "cultural_self_reflexivity": <1.0-5.0>,
        "pattern_archetypal_quality": <1.0-5.0>
      }}
    }}
  }},
  "iterative_overall_score": <1.0-5.0>,
  "overall_confidence": <1-5>
}}
```
"""

    def _get_final_prompt(self, previous_response: str) -> str:
        """
        Round N (final): Final confirmation
        UPDATED 2025-12-20: 4-dimension system (IPD, CVP, CSP, CPC)

        Args:
            previous_response: Response from round N-1 (raw JSON string)
        """
        return f"""**ROUND {self.num_rounds}/{self.num_rounds}: FINAL CONFIRMATION**

You've now completed {self.num_rounds - 1} rounds of evaluation and self-reflection.

**Your Round {self.num_rounds - 1} Response**:
{previous_response}

**TASK**:

Make your FINAL decision:
1. Confirm your Round {self.num_rounds - 1} scores OR make final adjustments
2. Provide final confidence levels
3. Summarize key reasoning for each dimension
4. Provide holistic overall score (weighted average or considered judgment)

**Convergence Expectation**: Score changes from Round {self.num_rounds - 1} should be < 0.3 per dimension.

This is your last chance to revise. Be confident in your final scores.

**REQUIRED JSON OUTPUT**:
```json
{{
  "round": {self.num_rounds},
  "final_scores": {{
    "intersectional_power_dynamics": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "power_axes": ["<final list of social axes>"]
    }},
    "cultural_voice_perspective": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "positioning": "<insider/outsider/mixed>"
    }},
    "cultural_specificity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "domains_covered": ["<final list: temporal/spatial/social/material>"]
    }},
    "cultural_pattern_complexity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "sub_dimension_scores": {{
        "relational_complexity": <1.0-5.0>,
        "conflict_structuration": <1.0-5.0>,
        "cultural_self_reflexivity": <1.0-5.0>,
        "pattern_archetypal_quality": <1.0-5.0>
      }},
      "sub_dimension_reasoning": "<brief explanation of each sub-dimension score>"
    }}
  }},
  "iterative_overall_score": <1.0-5.0>,
  "overall_reasoning": "<holistic assessment of cultural representation quality across all 4 dimensions>",
  "dimension_patterns": {{
    "strengths": ["<list 1-2 strongest dimensions with scores>"],
    "weaknesses": ["<list 1-2 weakest dimensions with scores>"],
    "notable_patterns": "<e.g., high CSP but outsider CVP, or high CPC with moderate IPD>"
  }},
  "convergence_self_assessment": {{
    "stable_dimensions": ["<dimensions that converged (change < 0.3)>"],
    "unstable_dimensions": ["<dimensions still uncertain (change >= 0.3)>"],
    "overall_evaluation_confidence": <1-5>
  }}
}}
```
"""

    def get_user_prompt(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Not used in multi-round mode (overridden by evaluate())
        """
        return ""

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM
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
        Execute multi-round evaluation with self-reflection

        REFACTORED: Now supports dynamic num_rounds (no longer hard-coded to 3)

        Args:
            text: Text to evaluate
            context: Optional context (may include 'title', 'summary')

        Returns:
            {
                "score": float,
                "dimensions": {dimension: {"score": float, "confidence": int}},
                "rounds": [round1_data, round2_data, ..., roundN_data],
                "confidence_trajectory": {dimension: [conf1, conf2, ..., confN]},
                "score_trajectory": {dimension: [score1, score2, ..., scoreN]},
                "conversation_history": [...],
                "final_summary": str,
                "error": Optional[str]
            }
        """
        try:
            rounds_data = []
            conversation_history = []

            # System prompt (constant across all rounds)
            system_prompt = self.get_system_prompt()

            # Execute multi-round evaluation
            for round_num in range(1, self.num_rounds + 1):
                # Generate prompt based on round type
                if round_num == 1:
                    # Round 1: Initial evaluation
                    user_prompt = self._get_initial_prompt(text, context)
                elif round_num < self.num_rounds:
                    # Rounds 2 to (N-1): Self-reflection
                    previous_response = conversation_history[-1]["content"]  # Last assistant response
                    user_prompt = self._get_reflection_prompt(round_num, previous_response)
                else:
                    # Round N: Final confirmation
                    previous_response = conversation_history[-1]["content"]  # Last assistant response
                    user_prompt = self._get_final_prompt(previous_response)

                # Add user prompt to conversation
                conversation_history.append({"role": "user", "content": user_prompt})

                # Generate LLM response
                response = self.llm_client.generate_with_messages(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *conversation_history
                    ],
                    temperature=self.temperature
                )

                # Add assistant response to conversation
                conversation_history.append({"role": "assistant", "content": response})

                # Parse and store round data
                round_data = self.parse_response(response)
                round_data['round'] = round_num
                rounds_data.append(round_data)

            # Extract trajectories
            confidence_trajectory = {}
            score_trajectory = {}

            # UPDATED 2025-12-20: 4-dimension system (v4.0)
            dimensions = [
                "intersectional_power_dynamics",    # IPD - 交叉性权力动力
                "cultural_voice_perspective",       # CVP - 文化声音与视角
                "cultural_specificity",             # CSP - 文化具体性
                "cultural_pattern_complexity"       # CPC - 文化模式复杂性
            ]

            for dim in dimensions:
                confidence_trajectory[dim] = []
                score_trajectory[dim] = []

                # Extract from each round
                for i, round_data in enumerate(rounds_data):
                    if i == 0:  # Round 1
                        scores = round_data.get('scores', {})
                    elif i < self.num_rounds - 1:  # Rounds 2 to (N-1)
                        scores = round_data.get('revised_scores', {})
                    else:  # Round N (final)
                        scores = round_data.get('final_scores', {})

                    dim_data = scores.get(dim, {})
                    confidence_trajectory[dim].append(dim_data.get('confidence', 0))
                    score_trajectory[dim].append(dim_data.get('score', 0.0))

            # Final scores (from last round)
            final_round = rounds_data[-1]
            final_scores = final_round.get('final_scores', {})
            final_dimensions = {}

            for dim in dimensions:
                dim_data = final_scores.get(dim, {})
                final_dimensions[dim] = {
                    "score": dim_data.get('score', 0.0),
                    "confidence": dim_data.get('confidence', 0),
                    "reasoning": dim_data.get('final_reasoning', '')
                }

            # UPDATED 2025-12-23: Extract iterative_overall_score from final round
            overall_score = final_round.get('iterative_overall_score', 0.0)
            # Overall confidence from convergence_self_assessment
            convergence_assessment = final_round.get('convergence_self_assessment', {})
            overall_confidence = convergence_assessment.get('overall_evaluation_confidence', 0)

            return {
                "score": overall_score,
                "overall_confidence": overall_confidence,
                "dimensions": final_dimensions,
                "rounds": rounds_data,
                "confidence_trajectory": confidence_trajectory,
                "score_trajectory": score_trajectory,
                "conversation_history": conversation_history,
                "overall_reasoning": final_round.get('overall_reasoning', ''),
                "dimension_patterns": final_round.get('dimension_patterns', {}),
                "convergence_self_assessment": convergence_assessment,
                "error": None
            }

        except Exception as e:
            return {
                "score": 0.0,
                "dimensions": {},
                "rounds": [],
                "confidence_trajectory": {},
                "score_trajectory": {},
                "error": str(e)
            }
