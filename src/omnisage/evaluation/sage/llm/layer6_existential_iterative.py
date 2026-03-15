"""
Layer 6 Existential Iterative Evaluator with Self-Reflection

Iterative evaluation to reduce variance and increase confidence through:
1. Iterative Evaluator: Multi-round self-reflection (5 rounds default, configurable)
2. Independent Validator: Critical review of iterative evaluator's reasoning

Designed to address:
- Projection bias (imposing Western existentialist frameworks)
- Layer boundary violations
- Confidence tracking
- Score convergence through reflection
"""

from typing import Dict, Any, Optional, List
from .base_judge import BaseJudge
import json
import re


class ExistentialIterativeEvaluator(BaseJudge):
    """
    Layer 6 Existential Iterative Evaluator with self-reflection mechanism

    Layer 6 (Existential): 4-dimension existential-philosophical evaluation system
    Design Principles: Strict Layer 6 boundary, Projection awareness, Dimension independence
    Research Goal: Evaluate existential-philosophical representation quality

    Evaluation dimensions:
    1. LP (Life Philosophy) - Existentialism (Heidegger, Sartre, Camus, Eastern Philosophy)
    2. MR (Moral Reflection) - Moral Philosophy (Levinas, MacIntyre, Confucian Ethics)
    3. HC (Human Condition) - Philosophical Anthropology (Arendt, Nussbaum)
    4. ME (Meaning Exploration) - Hermeneutics (Ricoeur, Gadamer)

    Iterative evaluation process:
    - Round 1: Existential content extraction + initial scoring + confidence
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
        System prompt for Layer 6 4-dimension existential evaluation system

        Design principles: Strict Layer 6 boundary, Projection awareness, No examples, Abstract definitions
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

        return f"""You are an expert literary-philosophical analyst evaluating how texts engage with existential questions, philosophical themes, moral inquiry, and the human condition.

# Core Evaluation Principles

1. **Evidence Sovereignty**: All scores must cite specific textual evidence. Insufficient evidence = lower confidence, NOT hallucination.

2. **Descriptive Not Evaluative**: Dimensions describe existential-philosophical representation, not value judgments. You are measuring presence and depth, not judging quality.

3. **Strict Layer Boundary**: Evaluate ONLY existential-philosophical content. Do NOT evaluate:
   - Cultural power structures or social hierarchies (that's Layer 4)
   - Emotional depth or psychological interiority (that's Layer 5)
   - Plot structure or narrative logic (that's Layer 2)
   - Vocabulary sophistication per se (that's Layer 1)

4. **Projection Awareness**: Avoid imposing specific philosophical frameworks.
   - DO NOT impose Western existentialist frameworks (Sartre, Camus, Heidegger) on non-Western texts
   - DO NOT equate explicit philosophical discourse with depth; implicit existential themes through action, structure, or symbolism are equally valid
   - DO NOT penalize texts for not conforming to any particular philosophical tradition
   - Recognize diverse philosophical traditions: Eastern (Buddhist impermanence, Confucian ethics, Daoist wu-wei), African (Ubuntu), Indigenous, etc.

5. **Anti-Cliché**: Avoid empty phrases: "profoundly existential", "deeply philosophical", "explores the meaning of life". Cite specific textual evidence instead.

6. **Dimension Independence**: Evaluate each dimension independently. Do NOT assume correlation. High score in one dimension does NOT imply high scores in others.

{mode_instruction}

# Evaluation Dimensions (4 Dimensions)

## 1. LP (Life Philosophy)
**Theoretical Basis**: Existentialism (Heidegger, Sartre, Camus) + Eastern Philosophy (Buddhist, Confucian, Daoist)

**Definition**: Evaluate the **depth of reflection on life's meaning, purpose, and values**. Life Philosophy concerns whether the text engages with fundamental questions about how to live, what constitutes a meaningful existence, and what values guide human choices.

**Operational Criteria**:

**High Depth (4.0-5.0)**:
- Text raises fundamental questions about meaning, purpose, or value
- Philosophical inquiry is sustained, not incidental
- Multiple perspectives on life's meaning coexist or are explored
- Avoids didactic answers; embraces complexity, ambiguity, or open-endedness
- Philosophical insight arises from narrative situation, not imposed upon it

**Moderate Depth (3.0-3.5)**:
- Some philosophical reflection but subordinate to plot or character
- Questions about meaning raised but not deeply pursued
- Occasional philosophical insight but not sustained

**Low Depth (1.0-2.5)**:
- No engagement with questions of meaning, purpose, or values
- Narrative is purely plot-driven or entertainment-focused
- If philosophical content present, it is clichéd or superficial ("life is precious")

**Evidence Requirements**:
- Quote passages showing philosophical inquiry OR its absence
- Cite evidence of sustained vs. incidental engagement
- Distinguish between genuine philosophical depth and moralizing platitudes

**Focus**:
- Questions about meaning, purpose, and value
- Sustained philosophical engagement
- Open-endedness vs. didacticism
- Integration of philosophy with narrative

**NOT Evaluate**:
- Emotional depth of characters (that's Layer 5)
- Cultural traditions as power structures (that's Layer 4)
- Plot complexity (that's Layer 2)
- Whether the philosophy is "correct"

**Boundary Clarification**:
- **vs MR (Moral Reflection)**: LP asks "what is worth pursuing?" (meaning, identity, purpose); MR asks "what is right to do?" (duty, justice, responsibility). Test: "Does life have meaning?" = LP. "Is it right to sacrifice one for many?" = MR. A character questioning whether to pursue passion or duty is LP if the focus is on what makes life meaningful, but MR if the focus is on ethical obligation.
- **vs HC (Human Condition)**: LP = philosophical inquiry, HC = portrayal of universal existential realities
- **vs Layer 5 PI**: LP = philosophical themes, L5 PI = access to psychological states

---

## 2. MR (Moral Reflection)
**Theoretical Basis**: Moral Philosophy (Levinas, MacIntyre, Confucian Ethics)

**Definition**: Evaluate the **engagement with ethical dilemmas, moral choices, and questions of right and wrong**. Moral Reflection concerns whether the text presents genuine ethical complexity rather than simplistic good/evil binaries.

**Operational Criteria**:

**High Complexity (4.0-5.0)**:
- Genuine ethical dilemmas with no easy resolution
- Moral complexity: competing goods, tragic choices, ethical ambiguity
- Characters face consequences that illuminate moral questions
- Multiple moral perspectives presented without didactic resolution
- Ethical inquiry through action, not just discourse

**Moderate Complexity (3.0-3.5)**:
- Some moral dilemmas but with relatively clear resolution
- Ethical dimension present but not the narrative's primary concern
- Limited moral ambiguity; right and wrong largely distinguishable

**Low Complexity (1.0-2.5)**:
- Simplistic good/evil moral framework
- No genuine ethical dilemmas or moral ambiguity
- Moralizing or didactic tone
- Characters' moral choices are obvious or irrelevant

**Evidence Requirements**:
- Quote passages showing ethical dilemmas or moral choices OR their absence
- Cite evidence of moral complexity vs. simplicity
- Distinguish between moralizing (telling) and moral inquiry (exploring)

**Focus**:
- Ethical dilemmas and moral choices
- Moral complexity and ambiguity
- Consequences that illuminate ethics
- Multiple moral perspectives

**NOT Evaluate**:
- Whether the morality is culturally "correct" (that's Layer 4)
- Characters' emotional responses to moral situations (that's Layer 5)
- Plot consequences per se (that's Layer 2)
- Philosophical propositions about ethics in the abstract (that's LP)

**Boundary Clarification**:
- **vs LP (Life Philosophy)**: MR asks "what is right to do?" while LP asks "what is worth pursuing?". Test: "Should I betray my friend to save strangers?" = MR. "What kind of life is worth living?" = LP. When a dilemma involves both, score MR for the ethical dimension and LP for the meaning dimension separately.
- **vs HC (Human Condition)**: MR = ethical choices, HC = universal existential realities
- **vs Layer 4**: MR = individual moral inquiry, L4 = systemic cultural/power structures

---

## 3. HC (Human Condition)
**Theoretical Basis**: Philosophical Anthropology (Arendt, Nussbaum) + Existential Phenomenology

**Definition**: Evaluate the **insight into universal aspects of human existence**: mortality, suffering, joy, alienation, connection, growth, freedom, finitude. Human Condition concerns the text's portrayal of what it means to be human.

**Operational Criteria**:

**High Insight (4.0-5.0)**:
- Text illuminates universal existential realities (mortality, suffering, alienation, connection)
- Particular situations reveal general truths about human existence
- Engagement with fundamental human limitations and possibilities
- Avoids sentimentalizing or trivializing existential themes
- Concrete particulars embody universal conditions

**Moderate Insight (3.0-3.5)**:
- Some engagement with universal themes but not deeply pursued
- Human condition themes present but incidental to plot
- Occasional insight but not sustained or central

**Low Insight (1.0-2.5)**:
- No engagement with universal aspects of human existence
- Characters' situations are purely particular with no broader resonance
- Human condition themes absent or trivialized

**Evidence Requirements**:
- Quote passages showing engagement with universal existential realities OR their absence
- Cite evidence of particular situations illuminating general truths
- Distinguish between genuine insight and sentimental cliché

**Focus**:
- Mortality, suffering, joy, alienation, connection, freedom, finitude
- Universal existential realities embodied in particulars
- What it means to be human

**NOT Evaluate**:
- Emotional portrayal of suffering (that's Layer 5)
- Cultural-specific experiences as power dynamics (that's Layer 4)
- Character development arcs (that's Layer 2)
- Abstract philosophy about human nature (that's LP)

**Boundary Clarification**:
- **vs LP (Life Philosophy)**: HC = portrayal of existential realities, LP = philosophical inquiry about them
- **vs ME (Meaning Exploration)**: HC = what the human condition IS, ME = questioning what it MEANS
- **vs Layer 5 AC**: HC = existential themes, L5 AC = emotional complexity

---

## 4. ME (Meaning Exploration)
**Theoretical Basis**: Hermeneutics (Ricoeur, Gadamer) + Existential Inquiry

**Definition**: Evaluate the **pursuit of existential questions**: Why do we exist? What matters? How should we live? Meaning Exploration concerns whether the text actively interrogates questions of existential significance rather than providing ready-made answers.

**Operational Criteria**:

**High Exploration (4.0-5.0)**:
- Active interrogation of existential questions
- Questions remain genuinely open (not rhetorical with predetermined answers)
- Multiple interpretive possibilities sustained
- Narrative structure itself embodies existential inquiry (circularity, ambiguity, fragmentation)
- Reader drawn into questioning, not given answers

**Moderate Exploration (3.0-3.5)**:
- Some existential questions raised but quickly resolved or backgrounded
- Meaning-seeking present but not central to narrative
- Limited interpretive openness

**Low Exploration (1.0-2.5)**:
- No active questioning of existential themes
- Narrative provides clear answers rather than raising questions
- No engagement with "why" questions of existence
- Meaning is assumed or irrelevant

**Evidence Requirements**:
- Quote passages showing existential questioning OR its absence
- Cite evidence of open-ended inquiry vs. didactic answers
- Note structural features that embody existential inquiry (if any)

**Focus**:
- Active existential questioning
- Open-endedness and interpretive possibility
- Inquiry vs. answers
- Structural embodiment of existential themes

**NOT Evaluate**:
- Emotional impact of existential themes (that's Layer 5)
- Cultural significance of meaning-making (that's Layer 4)
- Narrative technique per se (that's Layer 2)
- Vocabulary used in philosophical passages (that's Layer 1)

**Boundary Clarification**:
- **vs LP (Life Philosophy)**: ME = questioning, LP = philosophical depth of the inquiry
- **vs HC (Human Condition)**: ME = questioning what it means, HC = portraying what it is
- **vs Layer 2 Theme**: ME = existential questioning, L2 = thematic coherence as narrative craft

---

# Scoring Calibration

Use full score range (1.0-5.0):
- **1.0-2.0**: Weak existential-philosophical representation
- **2.0-3.5**: Moderate existential-philosophical representation
- **3.5-4.5**: Strong existential-philosophical representation
- **4.5-5.0**: Exceptional existential-philosophical representation

Do NOT cluster scores in middle range (3.0-4.0).

---

# Multi-Round Self-Reflection Process

You will conduct **5 rounds** of evaluation:

- **Round 1**: Extract existential content and provide initial scores (all 4 dimensions)
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
        Round 1: Extract existential content and provide initial scoring

        Args:
            text: Full text of the work
            context: Optional context dict with 'title' and 'summary'
        """
        title = context.get('title') if context else None
        summary = context.get('summary') if context else None

        prompt = f"**ROUND 1/{self.num_rounds}: EXISTENTIAL CONTENT EXTRACTION AND INITIAL EVALUATION**\n\n"

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

Step 1: Extract Existential Content
List all details relevant to existential-philosophical evaluation:
- Explicit philosophical discourse or reflection
- Moral dilemmas and ethical choices faced by characters
- Engagement with mortality, suffering, alienation, freedom, finitude
- Existential questions raised (explicitly or implicitly)
- Symbolic or structural elements embodying existential themes
- Moments of meaning-seeking or meaning-questioning

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
    "philosophical_discourse": ["<list explicit philosophical reflections or discourse found>"],
    "moral_dilemmas": ["<list ethical dilemmas or moral choices with brief context>"],
    "existential_themes": ["<list themes: mortality, alienation, freedom, etc.>"],
    "existential_questions": ["<list questions raised, explicitly or implicitly>"],
    "structural_existential_elements": ["<list: circular structure/ambiguity/symbolism or 'none'>"],
    "meaning_seeking_moments": ["<list moments of meaning-questioning or meaning-making>"]
  },
  "scores": {
    "life_philosophy": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite passages showing philosophical inquiry OR its absence>",
      "evidence_strength": "<weak/medium/strong>",
      "philosophical_themes_present": ["<list: if philosophical themes found, list them; if absent, note>"]
    },
    "moral_reflection": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite passages showing ethical dilemmas OR simplistic morality>",
      "evidence_strength": "<weak/medium/strong>",
      "moral_complexity_markers": ["<list: ethical dilemmas/competing goods OR 'simplistic/absent'>"]
    },
    "human_condition": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite passages showing universal existential realities OR their absence>",
      "evidence_strength": "<weak/medium/strong>",
      "human_condition_themes": ["<list: mortality/suffering/alienation/connection OR 'absent'>"]
    },
    "meaning_exploration": {
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<cite passages showing existential questioning OR didactic answers>",
      "evidence_strength": "<weak/medium/strong>",
      "inquiry_openness": "<open-ended/partially resolved/didactic/absent>"
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

Remember: Mark uncertainties explicitly. Existential depth can be conveyed through action, structure, or symbolism, not just explicit philosophical discourse.
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
1. **Western Existentialism Imposition**: Am I projecting Western existentialist frameworks (Sartre, Camus, Heidegger) onto a text from a different philosophical tradition?
   - Did I penalize a text for not engaging with "absurdity" or "authenticity" when it explores meaning through different concepts?
   - Did I overlook Eastern philosophical depth (Buddhist impermanence, Confucian relational ethics, Daoist acceptance)?

2. **Explicit Philosophy Bias**: Am I equating explicit philosophical discourse with depth?
   - Did I penalize texts that convey existential themes through action, symbolism, or narrative structure rather than philosophical dialogue?
   - Did I reward explicit philosophical language as "deep" without checking for genuine insight?

3. **Profundity Bias**: Am I assuming that "dark" or "tragic" themes are more existentially profound than themes of joy, connection, or ordinary life?
   - Existential depth includes affirmation, not only negation
   - A text exploring the meaning of everyday existence can be as profound as one exploring death

4. **Framework Imposition**: Did I impose any philosophical framework as the standard for existential depth?
   - Am I measuring texts against a specific philosophical tradition rather than evaluating their own engagement with existential questions?

5. **Implicit Existentialism Omission**: Did I MISS existential depth because the text uses a non-Western or non-canonical vocabulary?
   - A Confucian text exploring duty (li), relational identity (ren), and harmony (he) engages existential questions without using words like "absurdity" or "freedom"
   - A Buddhist narrative exploring impermanence (anicca), suffering (dukkha), or non-self (anatta) is existentially rich even without Western existentialist framing
   - A text conveying existential themes entirely through action, ritual, or cyclical structure (not philosophical dialogue) may have been underscored
   - Re-examine: did I give LOW scores to any dimension because I failed to recognize existential engagement in an unfamiliar form?

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
    "western_framework_imposition": "<any Western existentialism bias in evaluation>",
    "explicit_philosophy_bias": "<did I favor explicit discourse over implicit themes?>",
    "implicit_existentialism_missed": "<did I underScore any dimension because existential themes were expressed in non-Western or non-canonical forms? Specify which dimensions and what was missed, or 'none'>",
    "score_adjustments_made": ["<which dimensions revised and why>"]
  }},
  "revised_scores": {{
    "life_philosophy": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning, address projection issues>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "philosophical_themes_present": ["<updated list>"]
    }},
    "moral_reflection": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "moral_complexity_markers": ["<updated list>"]
    }},
    "human_condition": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "human_condition_themes": ["<updated list>"]
    }},
    "meaning_exploration": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<updated reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 1'>",
      "inquiry_openness": "<open-ended/partially resolved/didactic/absent>"
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

Verify you evaluated ONLY existential-philosophical content (Layer 6):

1. **Layer 4 Violation Check (Cultural/Power Structures)**:
   - Did I accidentally evaluate cultural power structures or social hierarchies?
   - Example violation: Scoring MR high because text depicts class oppression (that's Layer 4)
   - Layer 6 = moral/ethical inquiry by individuals, NOT systemic cultural analysis

2. **Layer 5 Violation Check (Emotional/Psychological)**:
   - Did I evaluate emotional depth or psychological interiority?
   - Example violation: Scoring HC high because characters show deep suffering emotionally (that's Layer 5)
   - Layer 6 = existential themes about the human condition, NOT emotional portrayal quality

3. **Layer 2 Violation Check (Plot/Narrative Structure)**:
   - Did I evaluate plot complexity or narrative technique per se?
   - Example violation: Scoring ME high because plot has an ambiguous ending (that's Layer 2)
   - Layer 6 = existential questioning, NOT narrative craft quality

4. **Layer 1 Violation Check (Vocabulary)**:
   - Did I evaluate overall vocabulary sophistication rather than philosophical content?
   - Example violation: Scoring LP high because prose is eloquent (that's Layer 1)
   - Layer 6 = philosophical depth, NOT general lexical richness

**Score Revision**:
- If you crossed layer boundaries, revise affected dimensions
- Isolate ONLY existential-philosophical content
- Adjust scores to reflect Layer 6 criteria only

**REQUIRED JSON OUTPUT**:
```json
{{
  "round": 3,
  "layer_boundary_check": {{
    "layer4_violations": ["<any cultural/power evaluations OR 'none'>"],
    "layer5_violations": ["<any emotional/psychological evaluations OR 'none'>"],
    "layer2_violations": ["<any plot structure evaluations OR 'none'>"],
    "layer1_violations": ["<any general vocabulary evaluations OR 'none'>"],
    "corrections_made": ["<which dimensions corrected and how>"]
  }},
  "revised_scores": {{
    "life_philosophy": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 6 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "philosophical_themes_present": ["<updated list>"]
    }},
    "moral_reflection": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 6 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "moral_complexity_markers": ["<updated list>"]
    }},
    "human_condition": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 6 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "human_condition_themes": ["<updated list>"]
    }},
    "meaning_exploration": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<Layer 6 only reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 2'>",
      "inquiry_openness": "<open-ended/partially resolved/didactic/absent>"
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
   - Am I inferring philosophical depth NOT explicitly or implicitly present in the text?
   - Did I distinguish between "text has existential themes through action" vs "text lacks existential engagement"?

4. **Dimension-Specific Evidence**:
   - LP: Did I cite philosophical inquiry OR infer depth not shown?
   - MR: Did I cite genuine ethical dilemmas OR assume moral complexity?
   - HC: Did I cite universal existential themes OR project them?
   - ME: Did I cite existential questioning OR assume open-endedness?

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
    "life_philosophy": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "philosophical_themes_present": ["<updated list>"]
    }},
    "moral_reflection": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "moral_complexity_markers": ["<updated list>"]
    }},
    "human_condition": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "human_condition_themes": ["<updated list>"]
    }},
    "meaning_exploration": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "reasoning": "<evidence-grounded reasoning>",
      "changes_from_previous": "<what changed and why, or 'confirmed Round 3'>",
      "inquiry_openness": "<open-ended/partially resolved/didactic/absent>"
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
4. Provide holistic overall score across all 4 existential dimensions

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
    "life_philosophy": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "philosophical_themes_present": ["<final list>"]
    }},
    "moral_reflection": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "moral_complexity_markers": ["<final list>"]
    }},
    "human_condition": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "human_condition_themes": ["<final list>"]
    }},
    "meaning_exploration": {{
      "score": <1.0-5.0>,
      "confidence": <1-5>,
      "final_reasoning": "<consolidated reasoning with key textual evidence>",
      "convergence_status": "<converged/unstable>",
      "inquiry_openness": "<open-ended/partially resolved/didactic/absent>"
    }}
  }},
  "iterative_overall_score": <1.0-5.0>,
  "overall_reasoning": "<holistic assessment of existential-philosophical representation across all 4 dimensions>",
  "dimension_patterns": {{
    "strengths": ["<1-2 strongest dimensions with scores>"],
    "weaknesses": ["<1-2 weakest dimensions with scores>"],
    "notable_patterns": "<e.g., high LP but low MR, or high HC with moderate ME>"
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
                "life_philosophy",
                "moral_reflection",
                "human_condition",
                "meaning_exploration"
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

            # Extract iterative_overall_score from final round
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
