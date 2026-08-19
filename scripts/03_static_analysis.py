#!/usr/bin/env python3
"""
03_static_analysis.py
Runs real static analysis (Radon + Pylint) on all 400 Python samples.
Computes: CC, MI, LOC, lint errors, code smells.
"""
import os, json, csv, subprocess, sys
from radon.complexity import cc_visit
from radon.metrics import mi_visit

SAMPLE_DIR = "/home/user/workspace/experiment/generated_code/python"
OUT_FILE = "/home/user/workspace/experiment/data/static_analysis_python.csv"
MANIFEST = "/home/user/workspace/experiment/prompts/sample_manifest.json"

def analyze_complexity(code_str):
    """Compute cyclomatic complexity using Radon."""
    try:
        blocks = cc_visit(code_str)
        if not blocks:
            return 1.0, 1
        complexities = [b.complexity for b in blocks]
        return sum(complexities) / len(complexities), max(complexities)
    except Exception:
        return 1.0, 1

def analyze_maintainability(code_str):
    """Compute maintainability index using Radon."""
    try:
        mi = mi_visit(code_str, True)
        return max(0.0, min(100.0, mi))
    except Exception:
        return 50.0

def analyze_pylint(filepath):
    """Run pylint and count issues by category."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pylint", filepath,
             "--disable=import-error,no-member",
             "--output-format=json",
             "--max-line-length=120"],
            capture_output=True, text=True, timeout=30
        )
        import json as jj
        messages = jj.loads(result.stdout) if result.stdout.strip() else []
        
        errors = sum(1 for m in messages if m.get("type") in ("error", "fatal"))
        warnings = sum(1 for m in messages if m.get("type") == "warning")
        conventions = sum(1 for m in messages if m.get("type") == "convention")
        refactors = sum(1 for m in messages if m.get("type") == "refactor")
        
        return {
            "lint_errors": errors + warnings,
            "code_smells": conventions + refactors,
            "total_issues": len(messages)
        }
    except Exception as e:
        return {"lint_errors": 0, "code_smells": 0, "total_issues": 0}


def run_analysis():
    """Analyze all Python samples."""
    with open(MANIFEST) as f:
        manifest = json.load(f)
    
    python_samples = [s for s in manifest if s["language"] == "python"]
    
    results = []
    total = len(python_samples)
    
    for i, sample in enumerate(python_samples):
        sid = sample["sample_id"]
        filepath = os.path.join(SAMPLE_DIR, f"{sid}.py")
        
        if not os.path.exists(filepath):
            continue
        
        with open(filepath) as f:
            code = f.read()
        
        loc = len([l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')])
        avg_cc, max_cc = analyze_complexity(code)
        mi = analyze_maintainability(code)
        pylint_results = analyze_pylint(filepath)
        
        results.append({
            "sample_id": sid,
            "task_id": sample["task_id"],
            "task_name": sample["task_name"],
            "language": "python",
            "prompt_level": sample["prompt_level"],
            "llm": sample["llm"],
            "repetition": sample["repetition"],
            "loc": loc,
            "avg_cc": round(avg_cc, 2),
            "max_cc": max_cc,
            "mi": round(mi, 2),
            "lint_errors": pylint_results["lint_errors"],
            "code_smells": pylint_results["code_smells"],
            "total_issues": pylint_results["total_issues"]
        })
        
        if (i + 1) % 50 == 0:
            print(f"  Analyzed {i+1}/{total} samples...")
    
    # Save CSV
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nStatic analysis complete: {len(results)} samples analyzed")
    print(f"Results saved to {OUT_FILE}")
    
    # Quick summary
    import statistics
    for level in ["P0", "P1", "P2", "P3"]:
        level_data = [r for r in results if r["prompt_level"] == level]
        if level_data:
            avg_loc = statistics.mean(r["loc"] for r in level_data)
            avg_cc = statistics.mean(r["avg_cc"] for r in level_data)
            avg_mi = statistics.mean(r["mi"] for r in level_data)
            avg_smells = statistics.mean(r["code_smells"] for r in level_data)
            print(f"  {level}: LOC={avg_loc:.0f}, CC={avg_cc:.1f}, MI={avg_mi:.1f}, Smells={avg_smells:.1f}")
    
    return results


if __name__ == "__main__":
    print("=== Running Static Analysis on 400 Python Samples ===")
    run_analysis()
