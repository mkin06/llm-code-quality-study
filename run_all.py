#!/usr/bin/env python3
"""
run_all.py - Master script to run the full experimental pipeline.

Usage:
    python run_all.py

Prerequisites:
    pip install radon pylint scipy pandas numpy matplotlib seaborn

Pipeline:
    Step 1: Generate prompt dataset (80 prompts, 800 sample configs)
    Step 2: Generate code samples (400 Python samples)
    Step 3: Run static analysis (Radon CC/MI + Pylint)
    Step 4: Compute Architecture Conformance Scores (AST-based)
    Step 5: Run statistical analysis + generate figures
"""
import os
import sys
import time
import subprocess


SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_ORDER = [
    ("01_prompt_dataset.py", "Generating prompt dataset..."),
    ("02_generate_code.py", "Generating code samples..."),
    ("03_static_analysis.py", "Running static analysis (Radon + Pylint)..."),
    ("04_acs_scorer.py", "Computing Architecture Conformance Scores..."),
    ("05_statistical_analysis.py", "Running statistical analysis + figures..."),
]


def run_step(script_name, description):
    """Run a single pipeline step."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"  Script: {script_name}")
    print(f"{'='*60}")
    
    script_path = os.path.join(SCRIPTS_DIR, "scripts", script_name)
    if not os.path.exists(script_path):
        print(f"  ERROR: Script not found: {script_path}")
        return False
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=False,
        text=True
    )
    elapsed = time.time() - start
    
    if result.returncode != 0:
        print(f"\n  FAILED (exit code {result.returncode}) after {elapsed:.1f}s")
        return False
    
    print(f"\n  Completed in {elapsed:.1f}s")
    return True


def main():
    print("="*60)
    print("  EXPERIMENT PIPELINE")
    print("  Do Architectural Constraints in Prompts Matter?")
    print("  An Empirical Study on the Impact of Software Architecture")
    print("  Design Constraints on LLM-Generated Code Quality")
    print("="*60)
    
    start_total = time.time()
    
    for script_name, description in SCRIPT_ORDER:
        success = run_step(script_name, description)
        if not success:
            print(f"\nPipeline ABORTED at step: {script_name}")
            sys.exit(1)
    
    elapsed_total = time.time() - start_total
    
    print("\n" + "="*60)
    print(f"  PIPELINE COMPLETE ({elapsed_total:.1f}s total)")
    print("="*60)
    print("\nOutput files:")
    print("  prompts/prompt_dataset.json      - 80 unique prompts")
    print("  prompts/sample_manifest.json      - 800 sample configurations")
    print("  generated_code/python/S0001-S0400 - 400 Python code samples")
    print("  data/static_analysis_python.csv   - Static analysis results")
    print("  data/acs_scores.csv               - Architecture Conformance Scores")
    print("  results/full_dataset.csv          - Full merged dataset (788 samples)")
    print("  results/rq1_*.csv                 - RQ1 analysis tables")
    print("  results/rq2_*.csv                 - RQ2 analysis tables")
    print("  results/rq3_*.csv                 - RQ3 analysis tables")
    print("  results/rq4_*.csv                 - RQ4 analysis tables")
    print("  results/statistical_summary.txt   - Full statistical report")
    print("  results/figures/*.png             - 5 analysis figures")


if __name__ == "__main__":
    main()
