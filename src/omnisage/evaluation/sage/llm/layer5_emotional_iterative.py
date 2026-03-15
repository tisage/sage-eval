"""
Layer 5 Emotional Iterative Evaluator with Self-Reflection

UPDATED 2025-12-23: Terminology update (Iterative Evaluator, Independent Validator)

Iterative evaluation to reduce variance and increase confidence through:
1. Iterative Evaluator: Multi-round self-reflection (5 rounds default, configurable)
2. Independent Validator: Critical review of iterative evaluator's reasoning

Designed to address:
- Projection bias (imposing evaluator's emotional norms)
- Layer boundary violations
- Confidence tracking
- Score convergence through reflection
"""

from typing import Dict, Any, Optional, List
from .base_judge import BaseJudge
import json
import re


class EmotionalIterativeEvaluator(BaseJudge):
    """
    Layer 5 Emotional Iterative Evaluator with self-reflection mechanism

    UPDATED 2025-12-23: Terminology update (content-limit, title-limit, Iterative Evaluator)

    Layer 5 (Emotional): 4-dimension emotional-psychological evaluation system
    Design Principles: Strict Layer 5 boundary, Projection awareness, Dimension independence
    Research Goal: Evaluate emotional-psychological representation quality

    Evaluation dimensions:
    1. AC (Affective Complexity) - Affect Theory (Sedgwick, Berlant, Ngai)
    2. PI (Psychological Interiority) - Narrative Psychology (Cohn, Bruner, Bakhtin)
    3. EG (Emotional Granularity) - Emotion Granularity Research (Barrett)
    4. ENC (Emotional-Narrative Coherence) - Organic Unity (New Criticism, James Wood)

    Iterative evaluation process:
    - Round 1: Emotional content extraction + initial scoring + confidence
    - Round 2: Projection bias check
    - Round 3: Layer boundary check
    - Round 4: Evidence sufficiency check
    - Round 5: Final consolidation + convergence analysis
    """

    def __init__(
        self,
        llm_client: Any,
        temperature: float = 1.0,
        num_rounds: int = 5,
        mode: str = "content-limit"  # "content-limit" or "title-limit"
    ):
        """
        Args:
            llm_client: LLM client instance
            temperature: For gpt-5-mini, this is ignored (uses reasoning.effort instead)
            num_rounds: Number of self-reflection rounds (default 5)
            mode: Evaluation mode - "content-limit" (text only) or "title-limit" (metadata only)
        """
        super().__init__(llm_client, temperature)
        self.num_rounds = num_rounds
        self.mode = mode

    def get_system_prompt(self) -> str:
        """
        System prompt for Layer 5 4-dimension emotional evaluation system

        UPDATED 2025-12-23: Terminology update (content-limit, title-limit)

        Design principles: Strict Layer 5 boundary, Projection awareness, No examples, Abstract definitions
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

        return f"""You are an expert literary-emotional analyst evaluating how texts represent emotions, psychological states, and affective experiences.

# Core Evaluation Principles

1. **Evidence Sovereignty**: All scores must cite specific textual evidence. Insufficient evidence = lower confidence, NOT hallucination.

2. **Descriptive Not Evaluative**: Dimensions describe emotional representation, not value judgments. You are measuring presence and complexity, not judging quality.

3. **Strict Layer Boundary**: Evaluate ONLY emotional-psychological content. Do NOT evaluate:
   - Cultural power structures or social hierarchies (that's Layer 4)
   - Philosophical meaning or existential themes (that's Layer 6)
   - Plot structure or narrative logic (that's Layer 2)
   - Vocabulary sophistication per se (that's Layer 1)

4. **Projection Awareness**: Avoid imposing your assumptions about "how emotions should be expressed". Restrained/implicit expression ≠ shallow. Explicit emotional language ≠ deep.

5. **Anti-Cliché**: Avoid empty phrases: "deeply moving", "emotionally resonant", "profound psychological depth". Cite specific textual evidence instead.

6. **Dimension Independence**: Evaluate each dimension independently. Do NOT assume correlation. High score in one dimension does NOT imply high scores in others.

{mode_instruction}

# Evaluation Dimensions (4 Dimensions)

## 1. AC (Affective Complexity)
**Theoretical Basis**: Affect Theory (Eve Kosofsky Sedgwick, Lauren Berlant, Sianne Ngai)

**Definition**: Evaluate the **multiplicity, contradiction, and evolution** of emotional states within the text. Complexity concerns whether emotions are presented as simple/singular or multi-layered/conflicting, and whether they transform across the narrative.

**Operational Criteria**:

**High Complexity (4.0-5.0)**:
- Multiple emotions coexist simultaneously (e.g., love + resentment, grief + relief)
- Emotions contradict or complicate each other
- Affective states evolve or transform across narrative arc
- Emotional ambiguity or undecidability present
- Avoids emotional binaries (happy/sad, love/hate)

**Moderate Complexity (3.0-3.5)**:
- Some emotional multiplicity but dominant single affect
- Occasional contradictions but mostly coherent emotional states
- Limited emotional evolution

**Low Complexity (1.0-2.5)**:
- Emotions are singular and unambiguous
- Binary emotional oppositions (pure joy vs pure sadness)
- Static emotional states throughout narrative
- Emotions are flat, one-dimensional

**Evidence Requirements**:
- Quote passages showing multiple/contradictory emotions OR single dominant affect
- Cite evidence of emotional evolution OR stasis
- Distinguish between restrained expression (potentially high complexity) vs simplistic affect

**Focus**:
- Multiplicity of concurrent emotional states
- Contradictions and tensions between affects
- Emotional evolution across narrative time
- Ambiguity and undecidability in affective states
- Avoidance of emotional binaries

**NOT Evaluate**:
- Whether emotions are morally appropriate
- Reader's personal emotional response
- Explicitness vs implicitness of emotional language (that's EG)
- Psychological realism per se (that's PI)

**Boundary Clarification**:
- **vs EG (Emotional Granularity)**: AC = multiple/contradictory emotions, EG = precision in naming emotions
- **vs PI (Psychological Interiority)**: AC = affective complexity, PI = access to thought processes
- **vs Deleted Emotional Dynamics**: Not evaluating arc shape, just multiplicity/contradiction

---

## 2. PI (Psychological Interiority)
**Theoretical Basis**: Narrative Psychology (Dorrit Cohn, Jerome Bruner, Mikhail Bakhtin)

**Definition**: Evaluate the **depth and accessibility of characters' inner psychological worlds**. Interiority concerns the degree to which the narrative provides access to characters' thoughts, motivations, self-awareness, and mental processes beyond observable emotions.

**Operational Criteria**:

**High Interiority (4.0-5.0)**:
- Extensive access to characters' thoughts, memories, motivations
- Characters exhibit self-awareness, self-questioning, introspection
- Mental processes shown (reasoning, memory, fantasy, conflicting desires)
- Interior monologue, free indirect discourse, or psychological focalization
- Psychological depth beyond surface emotional states

**Moderate Interiority (3.0-3.5)**:
- Some access to thoughts but mostly through dialogue or external action
- Limited introspection or self-awareness
- Psychological states implied but not deeply explored

**Low Interiority (1.0-2.5)**:
- Minimal or no access to characters' inner lives
- Characters knowable only through external action/dialogue
- Surface-level psychology, behavioral description only
- No introspection or self-awareness shown

**Evidence Requirements**:
- Quote passages showing interior thought/motivation/self-reflection OR absence thereof
- Cite narrative techniques providing psychological access (interior monologue, free indirect discourse)
- Distinguish between behavioral description and psychological access

**Focus**:
- Access to characters' thoughts, memories, motivations
- Self-awareness and introspection
- Mental processes beyond observable emotion
- Narrative techniques of psychological access
- Depth of psychological portrayal

**NOT Evaluate**:
- Character likability or moral worth
- Plot complexity or narrative structure (that's Layer 2)
- Social power dynamics between characters (that's Layer 4)
- Philosophical beliefs of characters (that's Layer 6)

**Boundary Clarification**:
- **vs AC (Affective Complexity)**: PI = access to thought processes, AC = multiplicity of affects
- **vs EG (Emotional Granularity)**: PI = psychological depth, EG = precision in emotion vocabulary
- **vs Layer 2 Character Development**: L2 = character change over plot, L5 = access to interior psychology

---

## 3. EG (Emotional Granularity)
**Theoretical Basis**: Emotion Granularity Research (Lisa Feldman Barrett) + Affective Linguistics

**Definition**: Evaluate the **precision and differentiation** of emotional vocabulary and concepts deployed in the text. Granularity concerns whether emotions are named/described with fine-grained specificity or remain vague and undifferentiated.

**Operational Criteria**:

**High Granularity (4.0-5.0)**:
- Emotions named with precision (not just "sad" but "despondent", "melancholic", "wistful")
- Fine distinctions between similar affective states (anxiety vs dread vs unease)
- Rich emotional vocabulary or precise behavioral/physiological descriptions
- Emotional concepts differentiated rather than blurred

**Moderate Granularity (3.0-3.5)**:
- Mostly basic emotion terms (happy, sad, angry, afraid) with occasional precision
- Some differentiation but many emotions remain generic
- Limited emotional vocabulary range

**Low Granularity (1.0-2.5)**:
- Vague or generic emotional terms ("felt bad", "was upset")
- Emotions undifferentiated (all negative states = "sad", all positive = "happy")
- Minimal emotional vocabulary
- Emotions implied through plot but not linguistically specified

**Evidence Requirements**:
- Quote emotional vocabulary used in the text (specific terms or descriptions)
- Cite examples of precision OR vagueness in emotional naming
- Note: Granularity can be achieved through behavioral/physiological description even without explicit emotion words

**Focus**:
- Precision in emotional vocabulary
- Differentiation between similar affective states
- Range and specificity of emotional concepts
- Linguistic vs behavioral emotional description

**NOT Evaluate**:
- Overall vocabulary sophistication (that's Layer 1)
- Complexity of emotional states (that's AC)
- Cultural appropriateness of emotional expression (that's Layer 4)
- Philosophical implications of emotions (that's Layer 6)

**Boundary Clarification**:
- **vs Layer 1 Lexical Diversity**: L1 = overall vocabulary richness, L5 = emotional vocabulary specifically
- **vs AC (Affective Complexity)**: EG = precision in naming, AC = multiplicity/contradiction
- **vs PI (Psychological Interiority)**: EG = emotion naming precision, PI = access to thought processes

---

## 4. ENC (Emotional-Narrative Coherence)
**Theoretical Basis**: Organic Unity (New Criticism) + Motivated Emotion (James Wood)

**Definition**: Evaluate whether emotional moments are **organically grounded in narrative situation and character**, or appear unmotivated, arbitrary, or manipulative. Coherence concerns the logical-causal relationship between emotions and their narrative contexts.

**Operational Criteria**:

**High Coherence (4.0-5.0)**:
- Emotions arise organically from narrative situation and character psychology
- Emotional moments have clear antecedent motivation in plot or character development
- Emotional intensity proportional to narrative stakes
- Emotions serve narrative function (revelation, transformation, climax)
- Avoids sentimentality and emotional manipulation

**Moderate Coherence (3.0-3.5)**:
- Most emotions adequately motivated but some feel convenient
- Occasional disproportionate emotional responses
- Emotions generally follow from situation but not always deeply integrated

**Low Coherence (1.0-2.5)**:
- Emotions appear unmotivated or arbitrary
- Emotional responses disproportionate to narrative situation (sentimentality/melodrama)
- Emotions feel imposed for effect rather than emerging from character/situation
- Emotional manipulation, unearned pathos

**Evidence Requirements**:
- Quote emotional moment AND cite preceding narrative context
- Explain motivational grounding (or lack thereof)
- Evidence of proportionality or disproportion between emotion and situation

**Focus**:
- Organic relationship between emotion and narrative
- Motivational sufficiency (is emotion earned?)
- Proportionality of emotional response to situation
- Functional integration of emotion into narrative structure
- Avoidance of sentimentality, melodrama, manipulation

**NOT Evaluate**:
- Plot structure quality per se (that's Layer 2)
- Whether reader personally finds the emotion justified
- Moral rightness of the emotional response
- Cultural appropriateness of emotional expression (that's Layer 4)

**Boundary Clarification**:
- **vs Layer 2 Event Sequence**: L2 = plot events logically consistent, L5 = emotions logically grounded in those events
- **vs AC (Affective Complexity)**: ENC = emotional grounding, AC = multiplicity of affects
- **vs Deleted Emotional Authenticity**: Coherence = logical grounding, Authenticity = genuine vs fake (avoided)

---

# Scoring Calibration

Use full score range (1.0-5.0):
- **1.0-2.0**: Weak emotional representation
- **2.0-3.5**: Moderate emotional representation
- **3.5-4.5**: Strong emotional representation
- **4.5-5.0**: Exceptional emotional representation

Do NOT cluster scores in middle range (3.0-4.0).

---

# Multi-Round Self-Reflection Process

You will conduct **5 rounds** of evaluation:

- **Round 1**: Extract emotional content and provide initial scores (all 4 dimensions)
- **Round 2**: Projection bias check
- **Round 3**: Layer boundary check
- **Round 4**: Evidence sufficiency check
- **Round 5**: Final consolidation with convergence analysis

**Convergence Goal**: Score change between Round 4→5 should be < 0.3 per dimension.

---

**OUTPUT FORMAT**: Return ONLY valid JSON (no markdown code blocks, no extra text).
"""

    def _get_initial_prompt(self, text: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Round 1: Extract emotional content and provide initial scoring

        Args:
            text: Full text of the work
            context: Optional context dict with 'title' and 'summary'
        """
        title = context.get('title') if context else None
        summary = context.get('summary') if context else None

        prompt = f"**ROUND 1/{self.num_rounds}: EMOTIONAL CONTENT EXTRACTION AND INITIAL EVALUATION**\n\n"

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

Step 1: Extract Emotional Content
List all details relevant to emotional evaluation:
- Explicit emotion words and phrases
- Behavioral/physiological markers of emotion
- Psychological states and interior thoughts
- Moments of affective intensity or emotional turning points
- Emotional relationships and motivations

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
  "extracted_content": {
    "explicit_emotions": ["<list emotion words/phrases found>"],
    "emotional_moments": ["<list key affective moments with brief context>"],
    "psychological_access": "<assessment: extensive/moderate/limited/none>",
    "interior_techniques": ["<list: interior monologue/free indirect discourse/etc or 'none'>"],
    "emotional_vocabulary_range": "<initial assessment: rich/moderate/limited>",
    "coherence_flags": ["<note any emotionally incoherent moments OR confirm coherence>"]
  },
  "scores": {
    "affective_complexity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite passages showing multiplicity/contradiction OR simplicity>",
      "evidence_strength": "<weak/medium/strong>",
      "emotional_states_present": ["<list: if multiple emotions, list them; if singular, note dominance>"]
    },
    "psychological_interiority": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite passages showing interior access OR behavioral description only>",
      "evidence_strength": "<weak/medium/strong>",
      "interiority_markers": ["<list: interior monologue/thought/introspection OR 'external only'>"]
    },
    "emotional_granularity": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite emotional vocabulary used OR note vagueness>",
      "evidence_strength": "<weak/medium/strong>",
      "vocabulary_examples": ["<quote specific emotion terms OR note generic language>"]
    },
    "emotional_narrative_coherence": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite emotional moments and their narrative motivation OR note arbitrariness>",
      "evidence_strength": "<weak/medium/strong>",
      "coherence_assessment": "<organic/mixed/manipulative>"
    }
  },
  "prior_knowledge_check": {
    "text_recognized": <true/false>,
    "potentially_biased_dimensions": ["<dimensions affected by prior knowledge if any>"],
    "text_only_dimensions": ["<dimensions evaluable from text alone>"]
  },
  "iterative_overall_score": <1.0-5.0>,
  "overall_confidence": <1-5>
}
```

Remember: Mark uncertainties explicitly. Restrained emotional expression ≠ absence of emotion.
"""
        return prompt

    def _get_reflection_prompt_round2(self, previous_response: str) -> str:
        """Round 2: Projection bias check"""
        return f"""**ROUND 2/{self.num_rounds}: PROJECTION BIAS CHECK**

Review your Round 1 evaluation.

**Your Round 1 Response**:
{previous_response}

**SELF-REFLECTION TASK: Projection Bias**

Ask yourself critically:
1. **Emotional Expression Bias**: Am I projecting my own assumptions about how emotions "should" be expressed?
   - Did I penalize restrained or implicit emotional expression as "shallow"?
   - Did I reward explicit emotional language as "deep" without checking for substance?

2. **Cultural Assumptions**: Am I applying my cultural norms about emotional expression inappropriately?
   - Am I expecting Western norms of emotional explicitness?
   - Am I penalizing culturally specific modes of affective restraint?

3. **Granularity Assumptions**: Did I equate "simple vocabulary" with "low granularity" without considering behavioral precision?
   - Can emotions be precisely conveyed through action/physiology rather than explicit naming?

4. **Interiority Assumptions**: Did I assume "external narration = no psychological depth"?
   - Can psychological states be conveyed without direct interior access?

**Score Revision**:
- If you detected projection bias, revise affected dimension scores
- If no bias detected, confirm Round 1 scores
- Adjust CONFIDENCE if uncertainty increases

**REQUIRED JSON OUTPUT**:
```json
{{
  "round": 2,
  "projection_check": {{
    "biases_detected": ["<list any projection biases identified OR 'none'>"],
    "cultural_assumptions": "<any cultural bias in evaluation>",
    "score_adjustments_made": ["<which dimensions revised and why>"]
  }},
  "revised_scores": {{
    "affective_complexity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning, address projection issues>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "emotional_states_present": ["<updated list>"]
    }},
    "psychological_interiority": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "interiority_markers": ["<updated list>"]
    }},
    "emotional_granularity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "vocabulary_examples": ["<updated examples>"]
    }},
    "emotional_narrative_coherence": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "coherence_assessment": "<organic/mixed/manipulative>"
    }}
  }},
  "iterative_overall_score": <1.0-5.0>,
  "overall_confidence": <1-5>
}}
```
"""

    def _get_reflection_prompt_round3(self, previous_response: str) -> str:
        """Round 3: Layer boundary check"""
        return f"""**ROUND 3/{self.num_rounds}: LAYER BOUNDARY COMPLIANCE CHECK**

Review your Round 2 evaluation.

**Your Round 2 Response**:
{previous_response}

**SELF-REFLECTION TASK: Layer Boundary Check**

Verify you evaluated ONLY emotional-psychological content (Layer 5):

1. **Layer 4 Violation Check (Cultural/Power Structures)**:
   - Did I accidentally evaluate cultural power structures or social hierarchies?
   - Example violation: Scoring PI high because characters discuss class struggle (that's Layer 4)
   - Layer 5 = characters' emotional/psychological states, NOT social structures

2. **Layer 6 Violation Check (Philosophical/Existential)**:
   - Did I evaluate philosophical meaning or existential themes?
   - Example violation: Scoring AC high because text explores existential alienation (that's Layer 6)
   - Layer 5 = emotional experiences, NOT philosophical propositions

3. **Layer 2 Violation Check (Plot/Narrative Structure)**:
   - Did I evaluate plot complexity or narrative technique per se?
   - Example violation: Scoring ENC high because plot is well-structured (that's Layer 2)
   - Layer 5 = emotional grounding in narrative, NOT plot structure quality

4. **Layer 1 Violation Check (Vocabulary)**:
   - Did I evaluate overall vocabulary sophistication rather than emotional vocabulary specifically?
   - Example violation: Scoring EG high because prose is eloquent (that's Layer 1)
   - Layer 5 = emotional vocabulary precision, NOT general lexical richness

**Score Revision**:
- If you crossed layer boundaries, revise affected dimensions
- Isolate ONLY emotional-psychological content
- Adjust scores to reflect Layer 5 criteria only

**REQUIRED JSON OUTPUT**:
```json
{{
  "round": 3,
  "layer_boundary_check": {{
    "layer4_violations": ["<any cultural/power evaluations OR 'none'>"],
    "layer6_violations": ["<any philosophical/existential evaluations OR 'none'>"],
    "layer2_violations": ["<any plot structure evaluations OR 'none'>"],
    "layer1_violations": ["<any general vocabulary evaluations OR 'none'>"],
    "corrections_made": ["<which dimensions corrected and how>"]
  }},
  "revised_scores": {{
    "affective_complexity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 5 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "emotional_states_present": ["<updated list>"]
    }},
    "psychological_interiority": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 5 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "interiority_markers": ["<updated list>"]
    }},
    "emotional_granularity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 5 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "vocabulary_examples": ["<updated examples>"]
    }},
    "emotional_narrative_coherence": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 5 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "coherence_assessment": "<organic/mixed/manipulative>"
    }}
  }},
  "iterative_overall_score": <1.0-5.0>,
  "overall_confidence": <1-5>
}}
```
"""

    def _get_reflection_prompt_round4(self, previous_response: str) -> str:
        """Round 4: Evidence sufficiency check"""
        return f"""**ROUND 4/{self.num_rounds}: EVIDENCE SUFFICIENCY CHECK**

Review your Round 3 evaluation.

**Your Round 3 Response**:
{previous_response}

**SELF-REFLECTION TASK: Evidence Grounding**

For each dimension score, critically assess:

1. **Textual Evidence Quality**:
   - Did I cite SPECIFIC textual passages for this score?
   - Is the evidence clear and unambiguous, or am I inferring heavily?
   - Are there alternative interpretations of the same evidence?

2. **Confidence Calibration**:
   - If evidence is ambiguous or limited, did I LOWER CONFIDENCE (not dimension score)?
   - Weak evidence = low confidence (1-2), NOT low score with high confidence
   - Are my confidence scores (1-5) accurately reflecting evidence strength?

3. **Inference vs Observation**:
   - Am I inferring emotions NOT explicitly or implicitly present in the text?
   - Did I distinguish between "text shows restrained expression" vs "text lacks emotion"?

4. **Dimension-Specific Evidence**:
   - AC: Did I cite multiple/contradictory emotions OR infer complexity not shown?
   - PI: Did I cite interior access markers OR assume interior from external action?
   - EG: Did I quote emotional vocabulary OR assume precision not present?
   - ENC: Did I cite emotion + context OR assume coherence without grounding?

**CRITICAL INSTRUCTION**:
- Adjust CONFIDENCE scores (not dimension scores) if evidence is weak
- If confidence drops to 1-2, explain why evidence is insufficient

**REQUIRED JSON OUTPUT**:
```json
{{
  "round": 4,
  "evidence_check": {{
    "weak_evidence_dimensions": ["<dimensions with ambiguous/sparse evidence>"],
    "inference_flags": ["<where I may have inferred beyond text>"],
    "confidence_recalibrations": ["<which dimensions got confidence adjustments>"],
    "evidence_reassessment": "<overall assessment of evidence quality>"
  }},
  "revised_scores": {{
    "affective_complexity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "emotional_states_present": ["<updated list>"]
    }},
    "psychological_interiority": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "interiority_markers": ["<updated list>"]
    }},
    "emotional_granularity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "vocabulary_examples": ["<updated examples>"]
    }},
    "emotional_narrative_coherence": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "coherence_assessment": "<organic/mixed/manipulative>"
    }}
  }},
  "iterative_overall_score": <1.0-5.0>,
  "overall_confidence": <1-5>
}}
```
"""

    def _get_final_prompt(self, previous_response: str) -> str:
        """Round 5: Final consolidation"""
        return f"""**ROUND 5/{self.num_rounds}: FINAL CONSOLIDATION**

You've completed 4 rounds of evaluation and self-reflection.

**Your Round 4 Response**:
{previous_response}

**TASK: Final Assessment**

Make your FINAL decision:
1. Confirm Round 4 scores OR make final adjustments
2. Provide final confidence levels for each dimension
3. Summarize convergence status (stable vs unstable dimensions)
4. Provide holistic overall score across all 4 emotional dimensions

**Convergence Expectation**: Score changes from Round 4 should be < 0.3 per dimension.

**Confidence Assessment**:
- Which dimensions have high confidence (4-5)?
- Which dimensions have low confidence (1-2) and why?

This is your last chance to revise. Be confident in your final scores.

**REQUIRED JSON OUTPUT**:
```json
{{
  "round": 5,
  "final_scores": {{
    "affective_complexity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "emotional_states_present": ["<final list>"]
    }},
    "psychological_interiority": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "interiority_markers": ["<final list>"]
    }},
    "emotional_granularity": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "vocabulary_examples": ["<final examples>"]
    }},
    "emotional_narrative_coherence": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "coherence_assessment": "<organic/mixed/manipulative>"
    }}
  }},
  "iterative_overall_score": <1.0-5.0>,
  "overall_reasoning": "<holistic assessment of emotional-psychological representation across all 4 dimensions>",
  "dimension_patterns": {{
    "strengths": ["<1-2 strongest dimensions with scores>"],
    "weaknesses": ["<1-2 weakest dimensions with scores>"],
    "notable_patterns": "<e.g., high AC but low EG, or high PI with moderate ENC>"
  }},
  "convergence_self_assessment": {{
    "stable_dimensions": ["<dimensions converged (Round 4→5 change < 0.3)>"],
    "unstable_dimensions": ["<dimensions still uncertain (change >= 0.3)>"],
    "overall_evaluation_confidence": <1-5>
  }}
}}
```
"""

    def get_user_prompt(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Not used in multi-round mode"""
        return ""

    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
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

        Args:
            text: Text to evaluate
            context: Optional context (may include 'title', 'summary')

        Returns:
            {
                "score": float,
                "dimensions": {dimension: {"score": float, "confidence": int}},
                "rounds": [round1_data, round2_data, ..., round5_data],
                "confidence_trajectory": {dimension: [conf1, conf2, ..., conf5]},
                "score_trajectory": {dimension: [score1, score2, ..., score5]},
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
                    user_prompt = self._get_initial_prompt(text, context)
                elif round_num == 2:
                    previous_response = conversation_history[-1]["content"]
                    user_prompt = self._get_reflection_prompt_round2(previous_response)
                elif round_num == 3:
                    previous_response = conversation_history[-1]["content"]
                    user_prompt = self._get_reflection_prompt_round3(previous_response)
                elif round_num == 4:
                    previous_response = conversation_history[-1]["content"]
                    user_prompt = self._get_reflection_prompt_round4(previous_response)
                else:  # Round 5
                    previous_response = conversation_history[-1]["content"]
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

            dimensions = [
                "affective_complexity",           # AC - 情感复杂性
                "psychological_interiority",      # PI - 心理内部性
                "emotional_granularity",          # EG - 情感颗粒度
                "emotional_narrative_coherence"   # ENC - 情感-叙事一致性
            ]

            for dim in dimensions:
                confidence_trajectory[dim] = []
                score_trajectory[dim] = []

                # Extract from each round
                for i, round_data in enumerate(rounds_data):
                    if i == 0:  # Round 1
                        scores = round_data.get('scores', {})
                    elif i < self.num_rounds - 1:  # Rounds 2-4
                        scores = round_data.get('revised_scores', {})
                    else:  # Round 5 (final)
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
