# SAGE Framework - Example Narratives

This directory contains sample narrative texts for testing the SAGE 6-layer evaluation framework.

---

## Available Examples

### 1. The Gift of the Magi (O. Henry)
- **File**: `henry_gift_of_magi.txt`
- **Author**: O. Henry (1862-1910)
- **Genre**: Short story, Literary fiction
- **Length**: ~2,065 words
- **Theme**: Sacrifice, love, irony
- **Copyright**: Public domain

**Why this example?**
- Classic American short story with strong emotional depth
- Rich cultural context (early 20th century New York)
- Clear thematic elements and narrative structure
- Well-suited for demonstrating all 6 evaluation layers

**Expected Evaluation Scores** (approximate):
- Layer 1 (Language): 2.0-2.5/5.0
- Layer 2 (Narrative): 0.5-1.0/5.0
- Layer 3 (Thematic): 0.5-1.0/5.0
- Layer 4 (Cultural): 4.0-4.5/5.0
- Layer 5 (Emotional): 4.0-4.5/5.0
- Layer 6 (Existential): 4.0-4.5/5.0
- **Overall**: ~2.6-2.8/5.0

### 2. The Necklace (Guy de Maupassant)
- **File**: `maupassant_necklace.txt`
- **Author**: Guy de Maupassant (1850-1893)
- **Genre**: Short story, Literary fiction
- **Length**: ~2,838 words
- **Theme**: Vanity, social class, irony
- **Copyright**: Public domain

**Why this example?**
- Classic French literature with universal themes
- Strong narrative arc and character development
- Cultural insights into 19th century French society
- Demonstrates evaluation across different cultural contexts

**Expected Evaluation Scores** (approximate):
- Layer 1 (Language): 2.3-2.5/5.0
- Layer 2 (Narrative): 0.5-1.0/5.0
- Layer 3 (Thematic): 0.5-1.0/5.0
- Layer 4 (Cultural): 4.0-4.5/5.0
- Layer 5 (Emotional): 3.5-4.5/5.0
- Layer 6 (Existential): 3.5-4.5/5.0
- **Overall**: ~2.6-2.9/5.0

---

## Quick Start

### Test with a single example

Using the CLI tool:
```bash
# Default configuration (gpt-4.1-mini for all layers)
PYTHONPATH=src ./.venv/bin/python scripts/evaluate_cli.py \
  data/examples/henry_gift_of_magi.txt

# Using quality profile
PYTHONPATH=src ./.venv/bin/python scripts/evaluate_cli.py \
  data/examples/henry_gift_of_magi.txt \
  --profile=quality
```

Using the shell script:
```bash
./scripts/evaluate_single_story.sh \
  data/examples/henry_gift_of_magi.txt \
  gift_of_magi_test
```

### Test both examples

```bash
# Evaluate first example
PYTHONPATH=src ./.venv/bin/python scripts/evaluate_cli.py \
  data/examples/henry_gift_of_magi.txt \
  --profile=quality \
  --output=gift_of_magi

# Evaluate second example
PYTHONPATH=src ./.venv/bin/python scripts/evaluate_cli.py \
  data/examples/maupassant_necklace.txt \
  --profile=quality \
  --output=necklace

# Compare results
ls -lh results/analysis/gift_of_magi/
ls -lh results/analysis/necklace/
```

---

## Understanding the Output

Each evaluation generates 3 files in `results/analysis/<story_name>/`:

1. **`<story_name>.json`**
   - Machine-readable evaluation data
   - Complete scores, metrics, and metadata
   - Includes LLM configuration used

2. **`<story_name>_REPORT.txt`**
   - Detailed human-readable report
   - Layer-by-layer analysis with rationales
   - Full evaluation context

3. **`<story_name>_SUMMARY.txt`**
   - Quick summary report
   - Key scores and timing information
   - Console output in text format

---

## Adding Your Own Examples

To test with your own narrative:

1. **Prepare the text file**:
   - Plain text (.txt) format
   - UTF-8 encoding
   - Remove excessive whitespace
   - Minimum ~500 words recommended

2. **Run evaluation**:
   ```bash
   PYTHONPATH=src ./.venv/bin/python scripts/evaluate_cli.py \
     /path/to/your/story.txt \
     --profile=quality \
     --output=my_story
   ```

3. **Review results**:
   ```bash
   cat results/analysis/my_story/my_story_SUMMARY.txt
   ```

---

## Notes on Example Selection

### Why Public Domain Classics?

1. **No Copyright Issues**: Can be freely distributed
2. **Quality Benchmark**: Well-crafted narratives with recognized literary merit
3. **Diverse Themes**: Cover different cultural contexts and human experiences
4. **Validation**: Results can be compared with literary criticism

### What These Examples Demonstrate

- **Layer 1-3 (Computational)**: These layers score lower (0.5-2.5/5.0) as they use computational metrics designed to detect AI-generated text patterns. Classic literature typically scores lower on these metrics.

- **Layer 4-6 (LLM-based)**: These layers score higher (3.5-4.5/5.0) as they evaluate cultural depth, emotional resonance, and existential themes - areas where classic literature excels.

- **Overall Score**: The weighted average provides a holistic quality assessment, with classic literature typically scoring 2.5-3.0/5.0.

---

## Troubleshooting

### If evaluation fails:

1. **Check API keys**: Ensure `.env` file contains valid API keys
   ```bash
   # Required for default configuration
   OPENAI_API_KEY=sk-...

   # Optional (for other models)
   GOOGLE_API_KEY=...
   OPENROUTER_API_KEY=...
   ```

2. **Verify file path**: Use absolute or relative path from project root
   ```bash
   # Correct
   data/examples/henry_gift_of_magi.txt

   # Incorrect (don't use ~)
   ~/Notebooks/sageFramework/data/examples/...
   ```

3. **Check Python environment**:
   ```bash
   # Verify virtual environment is activated
   which python3
   # Should point to .venv/bin/python3
   ```

4. **Review logs**: Check console output for detailed error messages

---

## Additional Resources

- **QUICKSTART Guide**: `docs/QUICKSTART.md`
- **CLI Usage Guide**: `docs/CLI_USAGE.md`
- **Framework Design**: `docs/six_layer_framework_design.md`

---

**For more examples or custom evaluation scenarios, see the full documentation in `docs/`.**
