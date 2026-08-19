# Do Architectural Constraints in Prompts Matter?

An empirical study on the impact of software architecture design constraints on the quality of LLM-generated code.

This repository contains the full experimental pipeline: prompt construction, code sample generation, static analysis, architecture conformance scoring and statistical analysis for four research questions.

---

## Research questions

| RQ | Question |
|----|----------|
| **RQ1** | Do architectural constraints in a prompt significantly change the quality of the generated code? |
| **RQ2** | Which type of constraint contributes the most to that improvement? |
| **RQ3** | How does prompt specificity relate to quality - linear, or with diminishing returns? |
| **RQ4** | What trade-offs appear between architectural conformance and other quality metrics? |

## Experimental design

Prompts are built along three factors:

- **10 tasks** (`T01`-`T10`), each targeting a distinct architectural concern: CRUD REST API, authentication, file management, notifications (observer), shopping cart, task scheduler, caching (decorator), event bus (pub-sub), data pipeline (chain of responsibility) and RBAC (strategy + composite).
- **4 constraint levels**, cumulative - each level adds requirements on top of the previous one:

  | Level | Prompt content |
  |-------|----------------|
  | `P0` | Task description only (baseline) |
  | `P1` | + separation of concerns, cohesive modules, short focused methods |
  | `P2` | + design patterns: Repository, Factory, Strategy, explicit interfaces, dependency injection |
  | `P3` | + Clean Architecture (4 layers, inward dependencies, DTOs) and all five SOLID principles |

- **2 target languages**: Python and Java.

This yields 80 unique prompts, expanded across 2 LLM labels × 5 repetitions per prompt into the sample manifest.

## Quality metrics

**Architecture Conformance Score (ACS)** - computed by AST analysis in `04_acs_scorer.py`. Five dimensions, scored 0-2 each, for a total of 0-10:

1. Separation of concerns
2. Dependency direction
3. Encapsulation
4. Pattern implementation
5. Interface design

**Static analysis metrics** - computed in `03_static_analysis.py`:

- Cyclomatic complexity (average and maximum), via Radon
- Maintainability Index, via Radon
- Lines of code
- Lint errors and code smells, via Pylint (JSON output, grouped by message type)

## Statistical methods

Distributions are non-normal (verified with Shapiro-Wilk), so all tests are non-parametric:

- **Kruskal-Wallis H** - omnibus test across the four constraint levels
- **Mann-Whitney U** with **Bonferroni** correction - pairwise level comparisons
- **Cliff's delta** - effect size, interpreted with the usual negligible/small/medium/large thresholds
- **Spearman ρ** - monotonic association between constraint level and each metric, and between metrics

## Repository structure

```
.
├── run_all.py                  # Runs the 5 pipeline steps in order
├── scripts/
│   ├── 01_prompt_dataset.py    # Task × level × language → prompt set + sample manifest
│   ├── 02_generate_code.py     # Produces the Python code samples
│   ├── 03_static_analysis.py   # Radon (CC, MI) + Pylint over every sample
│   ├── 04_acs_scorer.py        # AST-based Architecture Conformance Score
│   └── 05_statistical_analysis.py  # RQ1-RQ4 tests, tables and figures
├── prompts/
│   ├── prompt_dataset.json     # The prompt texts
│   └── sample_manifest.json    # One entry per sample: task, level, language, model, repetition
├── generated_code/python/      # Generated Python samples, one file per sample id
├── data/
│   ├── static_analysis_python.csv
│   └── acs_scores.csv
└── results/
    ├── full_dataset.csv            # Merged per-sample dataset used by all tests
    ├── rq1_*.csv, rq2_*.csv, ...   # Per-RQ result tables
    ├── statistical_summary.txt     # Human-readable report of every test
    └── figures/*.png               # Figures used in the paper
```

## Pipeline

Each step reads the output of the previous one:

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1 | `01_prompt_dataset.py` | task/level definitions in the script | `prompts/` |
| 2 | `02_generate_code.py` | `sample_manifest.json` | `generated_code/python/` |
| 3 | `03_static_analysis.py` | generated samples | `data/static_analysis_python.csv` |
| 4 | `04_acs_scorer.py` | generated samples | `data/acs_scores.csv` |
| 5 | `05_statistical_analysis.py` | both CSVs in `data/` | `results/` + `results/figures/` |

## Requirements

```
python >= 3.9
radon
pylint
pandas
numpy
scipy
matplotlib
seaborn
```

```bash
pip install -r requirements.txt
```

## Running

```bash
python run_all.py
```

`run_all.py` executes the five steps in sequence and aborts on the first non-zero exit code. Individual steps can also be run on their own, as long as the earlier steps have produced their outputs.

All scripts set `random.seed(42)` / `np.random.seed(42)`, so a rerun on the same inputs reproduces the same outputs.

