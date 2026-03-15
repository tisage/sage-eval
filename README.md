# SAGE Framework

<div align="center">

**Six-layer Automated Generation and Evaluation Framework**

A comprehensive framework for multi-dimensional narrative quality assessment combining rule-based metrics and LLM-powered evaluation.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-AAAI%202025-red.svg)](#)

**[🚀 Quick Start](QUICKSTART.md)** • [Features](#-features) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Research](#-research)

</div>

---

## 📖 Overview

**SAGE Framework** is a comprehensive system for multi-dimensional narrative quality assessment. It evaluates literary texts across six hierarchical layers, combining rule-based linguistic analysis (Layers 1-3) with LLM-powered semantic evaluation (Layers 4-6).

### Key Features

- **📊 Six-Layer Evaluation** - From lexical features to existential depth
- **🤖 Hybrid Approach** - Rule-based + LLM evaluation
- **📚 54 Classic Stories** - Curated corpus of world literature
- **🔬 Research-Grade** - Designed for computational narrative analysis
- **⚡ Production-Ready** - Scalable batch processing with gpt-5-mini

---

## 🎯 Evaluation Layers

| Layer | Name | Type | Metrics |
|-------|------|------|---------|
| **Layer 1** | Lexical | Rule-based | TTR, hapax legomena, word length |
| **Layer 2** | Syntactic | Rule-based | Entity coherence, event sequences |
| **Layer 3** | Semantic | Rule-based | Theme extraction, semantic networks |
| **Layer 4** | Cultural | LLM | Cultural depth, context analysis |
| **Layer 5** | Emotional | LLM | Emotional arc, affective impact |
| **Layer 6** | Existential | LLM | Philosophical depth, life concerns |

---

## ✨ Quick Start

### Installation

```bash
# Clone and setup
git clone <repository>
cd sageFramework
pip install -r requirements.txt

# Configure API key
echo "OPENAI_API_KEY=your_key" > .env
```

### Basic Usage

```bash
# Evaluate all 54 stories with GPT-5-mini (baseline)
PYTHONPATH=src ./.venv/bin/python scripts/batch_evaluate.py \
  --profile gpt5mini \
  --skip-confirmation

# Generate analysis report
PYTHONPATH=src ./.venv/bin/python scripts/analyze_results.py -o report.txt
```

**📖 Full documentation: [QUICKSTART.md](QUICKSTART.md)**

---

## 📊 Sample Results

Example output for Kafka's "Metamorphosis":

| Layer | Score | Key Findings |
|-------|-------|--------------|
| Layer 1 | 2.82 | Rich vocabulary (TTR: 0.42) |
| Layer 2 | 1.80 | Strong entity coherence |
| Layer 3 | 1.51 | Clear thematic structure |
| Layer 4 | 4.35 | Deep cultural analysis |
| Layer 5 | 4.50 | Complex emotional arc |
| Layer 6 | 4.25 | Existential themes |
| **Overall** | **3.21** | High-quality literary work |

---

## 🏗️ Architecture

### Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                  SAGE Evaluation Pipeline                │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Input: Literary Text                                    │
│      │                                                    │
│      ▼                                                    │
│  ┌──────────────────────────────────────────┐           │
│  │  Layer 1: Lexical Analysis (Rule-based)  │           │
│  │  • TTR, Hapax, Word Length, Formality    │           │
│  └──────────────┬───────────────────────────┘           │
│                 ▼                                         │
│  ┌──────────────────────────────────────────┐           │
│  │  Layer 2: Syntactic (Rule-based)         │           │
│  │  • Entity Coherence, Event Sequences     │           │
│  └──────────────┬───────────────────────────┘           │
│                 ▼                                         │
│  ┌──────────────────────────────────────────┐           │
│  │  Layer 3: Semantic (Rule-based)          │           │
│  │  • Theme Extraction, Semantic Networks   │           │
│  └──────────────┬───────────────────────────┘           │
│                 ▼                                         │
│  ┌──────────────────────────────────────────┐           │
│  │  Layer 4: Cultural (LLM)                 │           │
│  │  • Cultural Depth, Context Analysis      │           │
│  └──────────────┬───────────────────────────┘           │
│                 ▼                                         │
│  ┌──────────────────────────────────────────┐           │
│  │  Layer 5: Emotional (LLM)                │           │
│  │  • Emotional Arc, Affective Impact       │           │
│  └──────────────┬───────────────────────────┘           │
│                 ▼                                         │
│  ┌──────────────────────────────────────────┐           │
│  │  Layer 6: Existential (LLM)              │           │
│  │  • Philosophical Depth, Life Concerns    │           │
│  └──────────────┬───────────────────────────┘           │
│                 ▼                                         │
│  Output: Six-Layer Scores + Overall Score               │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Rule-Based Metrics (Layers 1-3)
- **Lexical**: Type-token ratio, vocabulary richness
- **Syntactic**: Entity grids, event sequences
- **Semantic**: TF-IDF themes, concept graphs

#### 2. LLM Judges (Layers 4-6)
- **Cultural**: GPT-5 / GPT-5-mini
- **Emotional**: GPT-5 / Gemini-2.5-Pro
- **Existential**: GPT-5 / GPT-5-mini

#### 3. Corpus
54 classic short stories from world literature:
- 19th century: Poe, Chekhov, Maupassant
- Modern: Kafka, Hemingway, Borges, Joyce
- Contemporary: Saunders, Lahiri

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 命令行使用指南
- **[scripts/SCRIPTS_ORGANIZATION.md](scripts/SCRIPTS_ORGANIZATION.md)** - 脚本组织说明
- **[docs/COMPLETE_FIX_SUMMARY.md](docs/COMPLETE_FIX_SUMMARY.md)** - Layer 2/3 修复总结
- **[docs/RESULTS_ANALYSIS.md](docs/RESULTS_ANALYSIS.md)** - 结果分析详细指南
- **[config/llm_models.yaml](config/llm_models.yaml)** - LLM 模型配置

---

## 🔬 Research

### Citation

If you use this framework in your research, please cite:

```bibtex
@article{sage2025,
  title={SAGE: A Six-Layer Framework for Narrative Quality Assessment},
  author={[Authors]},
  journal={[Conference/Journal]},
  year={2025}
}
```

### Publications

- Paper: [Link TBD]
- Dataset: 54 curated classic short stories
- Code: This repository

---

## 📊 Project Status

### ✅ Completed
- [x] Six-layer evaluation pipeline
- [x] Rule-based metrics (Layers 1-3)
- [x] LLM judges (Layers 4-6)
- [x] OpenAI API compatibility (GPT-5, GPT-5-mini)
- [x] Batch evaluation system
- [x] Analysis and reporting tools
- [x] 54-story corpus curation

### 🔧 Recent Fixes (2025-11-21)
- [x] Layer 2/3 scoring normalization (3x improvement)
- [x] OpenAI GPT-5-mini API compatibility
- [x] Temperature parameter handling
- [x] Complete evaluation pipeline verification

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT models
- Google for Gemini models
- The authors of the 54 classic stories in our corpus

---

**Questions?** Check [QUICKSTART.md](QUICKSTART.md) or open an issue.
