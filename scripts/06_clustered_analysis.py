#!/usr/bin/env python3
"""
06_clustered_analysis.py
Dependence-aware re-analysis requested in review round 3.

The 788 samples are NOT independent: every (task, level, LLM, language)
condition is sampled 5 times, and every task is reused across all
levels, LLMs and languages. This script re-analyses the outcomes with
methods that respect that structure:

  A. Cell-level (unit-of-analysis) re-analysis
     Each (task, level, LLM, language) cell is collapsed to its median
     (160 cells, 40 per level). Kruskal-Wallis, Bonferroni-corrected
     Mann-Whitney U, Cliff's delta and Spearman rho are recomputed on
     these 40-per-level cell medians. LOC is included in RQ3 here.

  B. Linear mixed-effects models
     metric ~ C(level) + C(llm) + C(language) with a random intercept
     for task and a nested random intercept for the (task, llm,
     language) cell. Fitted with statsmodels MixedLM (REML). Reported:
     fixed-effect estimates, 95% CIs, Wald p-values, variance
     components, and the marginal/conditional R^2 (Nakagawa).
     Because ACS is bounded and non-normal, we additionally refit the
     same model on the rank-transformed outcome (rank-based LMM).

  C. Cluster bootstrap over tasks
     Tasks (the top-level cluster, k = 10) are resampled with
     replacement (B = 10,000). For every bootstrap replicate all
     observations belonging to the drawn tasks are kept, so the whole
     within-task dependence structure is preserved. Percentile 95% CIs
     are reported for median differences, Cliff's delta, the
     per-transition share of total gain, and Spearman rho.

  D. Stratified (design-respecting) permutation test
     Level labels are permuted only WITHIN each (task, llm, language)
     stratum (10,000 permutations), which is the exact randomisation
     that the experimental design licenses. Yields a permutation
     p-value for the Kruskal-Wallis H statistic and for each pairwise
     median difference.

  E. Cell-level LLM comparison (GPT-4o vs Claude), per level, using
     Wilcoxon signed-rank on the paired (task, language) cell medians.

Outputs: results/rq_clustered_*.csv and results/clustered_summary.txt
"""
import os
import warnings
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
np.random.seed(42)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS_DIR = os.path.join(ROOT, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

METRICS = ["acs", "avg_cc", "mi", "code_smells", "loc"]
LABELS = {"acs": "ACS", "avg_cc": "CC", "mi": "MI", "code_smells": "CS", "loc": "LOC"}
LEVELS = ["P0", "P1", "P2", "P3"]
PAIRS = [("P0", "P1"), ("P0", "P2"), ("P0", "P3"), ("P1", "P2"), ("P1", "P3"), ("P2", "P3")]
TRANSITIONS = [("P0", "P1"), ("P1", "P2"), ("P2", "P3")]
N_BOOT = 10000
N_PERM = 10000

report = []


def log(s=""):
    print(s)
    report.append(s)


def fmt_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def cliffs_delta(x, y):
    """delta > 0 means x tends to be larger than y."""
    x = np.asarray(x)[:, None]
    y = np.asarray(y)[None, :]
    return float(((x > y).sum() - (x < y).sum()) / (x.size * y.size))


def interp_delta(d):
    d = abs(d)
    return "large" if d >= 0.474 else "medium" if d >= 0.33 else "small" if d >= 0.147 else "negligible"


# --------------------------------------------------------------------------
# Load
# --------------------------------------------------------------------------
df = pd.read_csv(os.path.join(RESULTS_DIR, "full_dataset.csv"))
df["level_num"] = df["prompt_level"].map({l: i for i, l in enumerate(LEVELS)})
df["cell"] = df["task_id"] + "_" + df["llm"] + "_" + df["language"]
df["cond"] = df["cell"] + "_" + df["prompt_level"]

log("DEPENDENCE-AWARE RE-ANALYSIS (review round 3)")
log("=" * 72)
log(f"Observations (generation samples): n = {len(df)}")
log(f"Tasks (top-level cluster): {df['task_id'].nunique()}")
log(f"(task, llm, language) strata: {df['cell'].nunique()}")
log(f"(task, level, llm, language) conditions: {df['cond'].nunique()}")
sizes = df.groupby("cond").size()
log(f"Condition sizes: {dict(sizes.value_counts().sort_index())}")

# --------------------------------------------------------------------------
# A. Cell-level re-analysis
# --------------------------------------------------------------------------
log("\n" + "=" * 72)
log("A. CELL-LEVEL RE-ANALYSIS (unit = (task, level, LLM, language) median; 40 cells / level)")
log("=" * 72)
cell = (df.groupby(["task_id", "prompt_level", "llm", "language"])[METRICS]
          .median().reset_index())
cell["level_num"] = cell["prompt_level"].map({l: i for i, l in enumerate(LEVELS)})
cell.to_csv(os.path.join(RESULTS_DIR, "rq_clustered_cell_medians.csv"), index=False)

rows_desc, rows_kw, rows_pw, rows_sp = [], [], [], []
for m in METRICS:
    groups = [cell.loc[cell.prompt_level == l, m].values for l in LEVELS]
    H, p = stats.kruskal(*groups)
    rows_kw.append({"metric": LABELS[m], "n_per_level": [len(g) for g in groups],
                    "H": round(H, 2), "p_value": fmt_p(p)})
    med = {l: np.median(g) for l, g in zip(LEVELS, groups)}
    iqr = {l: np.subtract(*np.percentile(g, [75, 25])) for l, g in zip(LEVELS, groups)}
    rows_desc.append({"metric": LABELS[m], **{f"{l}_median": round(med[l], 2) for l in LEVELS},
                      **{f"{l}_iqr": round(iqr[l], 2) for l in LEVELS}})
    log(f"\n{LABELS[m]}: cell medians  " + "  ".join(f"{l}={med[l]:.1f}[{iqr[l]:.1f}]" for l in LEVELS))
    log(f"  Kruskal-Wallis on 40 cells/level: H(3)={H:.2f}, p={fmt_p(p)}")
    rho, prho = stats.spearmanr(cell["level_num"], cell[m])
    rows_sp.append({"metric": LABELS[m], "spearman_rho": round(rho, 3), "p_value": fmt_p(prho), "n": len(cell)})
    log(f"  Spearman(level, {LABELS[m]}) over 160 cells: rho={rho:.3f}, p={fmt_p(prho)}")

for a, b in PAIRS:
    x = cell.loc[cell.prompt_level == a, "acs"].values
    y = cell.loc[cell.prompt_level == b, "acs"].values
    U, p = stats.mannwhitneyu(x, y, alternative="two-sided")
    pc = min(1.0, p * len(PAIRS))
    d = cliffs_delta(y, x)
    rows_pw.append({"pair": f"{a} vs {b}", "n_a": len(x), "n_b": len(y), "U": int(U),
                    "p_bonferroni": fmt_p(pc), "cliffs_delta": round(d, 3), "effect": interp_delta(d)})
    log(f"  ACS {a} vs {b} (40 vs 40 cells): U={U:.0f}, p_Bonf={fmt_p(pc)}, delta={d:.3f} ({interp_delta(d)})")

pd.DataFrame(rows_desc).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_cell_descriptives.csv"), index=False)
pd.DataFrame(rows_kw).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_cell_kruskal.csv"), index=False)
pd.DataFrame(rows_pw).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_cell_pairwise_acs.csv"), index=False)
pd.DataFrame(rows_sp).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_cell_spearman.csv"), index=False)

# Sample-level Spearman incl. LOC (to complete Table 7 of the paper)
rows = []
for m in METRICS:
    rho, p = stats.spearmanr(df["level_num"], df[m])
    rows.append({"metric": LABELS[m], "spearman_rho": round(rho, 3), "p_value": fmt_p(p), "n": len(df)})
pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "rq3_spearman_with_loc.csv"), index=False)
log("\nSample-level Spearman including LOC (n=788): " +
    ", ".join(f"{r['metric']}={r['spearman_rho']}" for r in rows))

# --------------------------------------------------------------------------
# B. Mixed-effects models
# --------------------------------------------------------------------------
log("\n" + "=" * 72)
log("B. LINEAR MIXED-EFFECTS MODELS")
log("   metric ~ C(level) + C(llm) + C(language), random intercept: task, task:llm:language")
log("=" * 72)


def fit_lmm(data, y):
    md = smf.mixedlm(f"{y} ~ C(prompt_level) + C(llm) + C(language)", data,
                     groups=data["task_id"], re_formula="1",
                     vc_formula={"cell": "0 + C(cell)"})
    return md.fit(reml=True, method=["lbfgs", "powell"], maxiter=2000)


def nakagawa_r2(res, data, y):
    X = res.model.exog
    fixed = X @ res.fe_params.values
    var_f = np.var(fixed, ddof=1)
    var_task = float(res.cov_re.iloc[0, 0])
    var_cell = float(res.vcomp[0]) if len(res.vcomp) else 0.0
    var_e = float(res.scale)
    tot = var_f + var_task + var_cell + var_e
    return var_f / tot, (var_f + var_task + var_cell) / tot, var_task, var_cell, var_e


lmm_rows = []
for m in METRICS:
    for outcome_label, data_m in [("raw", df.copy()),
                                  ("rank", df.assign(**{m: stats.rankdata(df[m])}))]:
        try:
            res = fit_lmm(data_m, m)
        except Exception as e:  # pragma: no cover
            log(f"  {LABELS[m]} ({outcome_label}): fit failed: {e}")
            continue
        r2m, r2c, vt, vc, ve = nakagawa_r2(res, data_m, m)
        icc_task = vt / (vt + vc + ve)
        icc_cell = (vt + vc) / (vt + vc + ve)
        log(f"\n{LABELS[m]} [{outcome_label} outcome]  converged={res.converged}  "
            f"var(task)={vt:.3f} var(cell)={vc:.3f} var(resid)={ve:.3f}  "
            f"ICC(task)={icc_task:.2f} ICC(cell)={icc_cell:.2f}  R2m={r2m:.2f} R2c={r2c:.2f}")
        ci = res.conf_int()
        for name in res.fe_params.index:
            if name == "Intercept":
                continue
            est, se, p = res.fe_params[name], res.bse[name], res.pvalues[name]
            lo, hi = ci.loc[name, 0], ci.loc[name, 1]
            clean = (name.replace("C(prompt_level)[T.", "level ").replace("C(llm)[T.", "llm ")
                         .replace("C(language)[T.", "language ").replace("]", ""))
            log(f"    {clean:<28s} est={est:8.3f}  SE={se:6.3f}  95%CI=[{lo:7.3f},{hi:7.3f}]  p={fmt_p(p)}")
            lmm_rows.append({"metric": LABELS[m], "outcome": outcome_label, "term": clean,
                             "estimate": round(est, 3), "se": round(se, 3),
                             "ci_low": round(lo, 3), "ci_high": round(hi, 3), "p_value": fmt_p(p),
                             "var_task": round(vt, 3), "var_cell": round(vc, 3), "var_resid": round(ve, 3),
                             "icc_task": round(icc_task, 3), "icc_task_cell": round(icc_cell, 3),
                             "R2_marginal": round(r2m, 3), "R2_conditional": round(r2c, 3)})
pd.DataFrame(lmm_rows).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_lmm.csv"), index=False)

# Likelihood-ratio test for the omnibus level effect (ML fits, full vs. reduced)
lrt_rows = []
for m in METRICS:
    full = smf.mixedlm(f"{m} ~ C(prompt_level) + C(llm) + C(language)", df, groups=df["task_id"],
                       re_formula="1", vc_formula={"cell": "0 + C(cell)"}).fit(reml=False, method=["lbfgs", "powell"])
    red = smf.mixedlm(f"{m} ~ C(llm) + C(language)", df, groups=df["task_id"],
                      re_formula="1", vc_formula={"cell": "0 + C(cell)"}).fit(reml=False, method=["lbfgs", "powell"])
    lr = 2 * (full.llf - red.llf)
    p = stats.chi2.sf(lr, df=3)
    lrt_rows.append({"metric": LABELS[m], "LR_chi2_df3": round(lr, 1), "p_value": fmt_p(p)})
    log(f"  LRT omnibus level effect, {LABELS[m]}: chi2(3)={lr:.1f}, p={fmt_p(p)}")
pd.DataFrame(lrt_rows).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_lmm_lrt.csv"), index=False)

# --------------------------------------------------------------------------
# C. Cluster bootstrap over tasks
# --------------------------------------------------------------------------
log("\n" + "=" * 72)
log(f"C. CLUSTER BOOTSTRAP OVER TASKS (k = 10 clusters, B = {N_BOOT})")
log("=" * 72)
tasks = sorted(df["task_id"].unique())
by_task = {t: df[df.task_id == t] for t in tasks}
rng = np.random.default_rng(42)


def stat_bundle(d):
    med = {l: d.loc[d.prompt_level == l, "acs"].median() for l in LEVELS}
    total = med["P3"] - med["P0"]
    out = {"gain_total": total}
    for a, b in TRANSITIONS:
        out[f"diff_{a}{b}"] = med[b] - med[a]
        out[f"share_{a}{b}"] = (med[b] - med[a]) / total * 100 if total else np.nan
    out["share_P2_of_total"] = (med["P2"] - med["P0"]) / total * 100 if total else np.nan
    for a, b in PAIRS:
        out[f"delta_{a}{b}"] = cliffs_delta(d.loc[d.prompt_level == b, "acs"].values,
                                            d.loc[d.prompt_level == a, "acs"].values)
    for m in METRICS:
        out[f"rho_{m}"] = stats.spearmanr(d["level_num"], d[m])[0]
        out[f"rho_acs_{m}"] = stats.spearmanr(d["acs"], d[m])[0] if m != "acs" else 1.0
    return out


point = stat_bundle(df)
boot = []
for _ in range(N_BOOT):
    draw = rng.choice(tasks, size=len(tasks), replace=True)
    d = pd.concat([by_task[t] for t in draw], ignore_index=True)
    boot.append(stat_bundle(d))
boot = pd.DataFrame(boot)
brows = []
for k in point:
    lo, hi = np.nanpercentile(boot[k], [2.5, 97.5])
    brows.append({"statistic": k, "point": round(point[k], 3), "ci_low": round(lo, 3), "ci_high": round(hi, 3)})
    log(f"  {k:<22s} point={point[k]:8.3f}   95% cluster-bootstrap CI=[{lo:8.3f}, {hi:8.3f}]")
pd.DataFrame(brows).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_task_bootstrap.csv"), index=False)

# --------------------------------------------------------------------------
# D. Stratified permutation test (permute level within task x llm x language)
# --------------------------------------------------------------------------
log("\n" + "=" * 72)
log(f"D. STRATIFIED PERMUTATION TEST ({N_PERM} permutations of level within (task, llm, language))")
log("=" * 72)
strata = [g.index.values for _, g in df.groupby("cell")]
levels_arr = df["prompt_level"].values.copy()


def H_and_diffs(lvls, y):
    groups = [y[lvls == l] for l in LEVELS]
    H = stats.kruskal(*groups)[0]
    meds = {l: np.median(g) for l, g in zip(LEVELS, groups)}
    return H, {f"{a}{b}": meds[b] - meds[a] for a, b in PAIRS}


prow = []
# D1. Omnibus: permute all four level labels within each stratum; statistic = Kruskal-Wallis H
for m in METRICS:
    y = df[m].values
    H_obs, _ = H_and_diffs(levels_arr, y)
    cntH = 0
    for _ in range(N_PERM):
        perm = levels_arr.copy()
        for idx in strata:
            perm[idx] = rng.permutation(perm[idx])
        H_p, _ = H_and_diffs(perm, y)
        cntH += H_p >= H_obs
    pH = (cntH + 1) / (N_PERM + 1)
    log(f"  {LABELS[m]}: observed H={H_obs:.2f}, stratified permutation p={fmt_p(pH)}")
    prow.append({"metric": LABELS[m], "test": "Kruskal-Wallis H (omnibus)", "observed": round(H_obs, 2),
                 "perm_p": fmt_p(pH), "perm_p_bonferroni": ""})

# D2. Pairwise (ACS): restrict to the two levels compared, permute the two labels within each
#     stratum; statistic = |rank-sum of group b - its expectation| (equivalent to Mann-Whitney U).
#     Ranks are computed once because permuting labels does not change them. Bonferroni over 6 pairs.
for a, b in PAIRS:
    sub = df[df.prompt_level.isin([a, b])].reset_index(drop=True)
    idx_strata = [g.index.values for _, g in sub.groupby("cell")]
    lab = (sub["prompt_level"].values == b)          # True = level b
    r = stats.rankdata(sub["acs"].values)
    n_b, n_a = lab.sum(), (~lab).sum()
    expect = n_b * (n_a + n_b + 1) / 2
    t_obs = abs(r[lab].sum() - expect)
    cnt = 0
    for _ in range(N_PERM):
        perm = lab.copy()
        for ix in idx_strata:
            perm[ix] = rng.permutation(perm[ix])
        cnt += abs(r[perm].sum() - expect) >= t_obs
    pk = (cnt + 1) / (N_PERM + 1)
    pk_b = min(1.0, pk * len(PAIRS))
    y = sub["acs"].values
    med_diff = np.median(y[lab]) - np.median(y[~lab])
    log(f"     ACS {a} vs {b}: median diff={med_diff:.2f}, stratified perm p={fmt_p(pk)} (Bonf. {fmt_p(pk_b)})")
    prow.append({"metric": "ACS", "test": f"pairwise {a} vs {b} (rank-sum)", "observed": round(med_diff, 2),
                 "perm_p": fmt_p(pk), "perm_p_bonferroni": fmt_p(pk_b)})
pd.DataFrame(prow).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_permutation.csv"), index=False)

# --------------------------------------------------------------------------
# E. LLM comparison at the cell level (paired on task x language)
# --------------------------------------------------------------------------
log("\n" + "=" * 72)
log("E. LLM COMPARISON (GPT-4o vs Claude) ON PAIRED CELL MEDIANS (20 pairs per level)")
log("=" * 72)
erows = []
for l in LEVELS:
    c = cell[cell.prompt_level == l].pivot_table(index=["task_id", "language"], columns="llm", values="acs")
    g, k = c["gpt-4o"].values, c["claude-3.5-sonnet"].values
    try:
        W, p = stats.wilcoxon(g, k)
    except ValueError:
        W, p = np.nan, 1.0
    log(f"  {l}: GPT-4o cell Mdn={np.median(g):.2f}, Claude cell Mdn={np.median(k):.2f}, "
        f"n_pairs={len(g)}, Wilcoxon W={W}, p={fmt_p(p)}")
    erows.append({"level": l, "gpt4o_cell_median": round(np.median(g), 2),
                  "claude_cell_median": round(np.median(k), 2), "n_pairs": len(g),
                  "wilcoxon_W": W, "p_value": fmt_p(p)})
pd.DataFrame(erows).to_csv(os.path.join(RESULTS_DIR, "rq_clustered_llm_paired.csv"), index=False)

with open(os.path.join(RESULTS_DIR, "clustered_summary.txt"), "w") as f:
    f.write("\n".join(report))
print(f"\nSaved to {RESULTS_DIR}/rq_clustered_*.csv and clustered_summary.txt")
