# BACKEND BUILD PROMPT: Smart Test Selection Engine

> **How to use:** Paste this entire file into your agentic IDE as the task prompt. It is written to be self-contained: the API contract in Section 10 is the exact contract the React frontend expects, so the two projects will connect without changes.

---

## 0. ROLE AND GOAL

You are a senior Python backend engineer with strong knowledge of algorithms and applied machine learning. Build the **complete backend** for a college DAA (Design and Analysis of Algorithms) project called **Smart Test Selection**.

**What the system does:**
When a developer changes some code, the system
1. finds which code is affected (graph algorithms),
2. finds which tests execute that code (coverage data),
3. predicts how likely each test is to catch a bug caused by this change (machine learning risk score),
4. selects the best subset of tests that fits a time budget (Set Cover + Knapsack, compared across Greedy, Dynamic Programming and Branch and Bound),
5. proves the idea works with controlled experiments (mutation testing, baselines, held-out evaluation),
6. serves everything to a React dashboard through a REST API.

**This is a DAA project, so the algorithms must be implemented by hand** (see Section 7). Libraries such as NetworkX are allowed only to *verify* your own implementations in unit tests.

**Deliverable:** a runnable Python project with (a) a sample software project to analyze, (b) an offline pipeline that builds all data and the ML model, (c) a FastAPI server, (d) experiment scripts, (e) unit tests, and (f) a README.

---

## 1. NON-NEGOTIABLE PRINCIPLES

1. **Honest results.** Every number shown in the UI or report must come from a real run of the pipeline. Never hard-code results. Every output file records its provenance (seed, counts, build time).
2. **No data leakage.** The ML model must never be evaluated on data it could have seen. Split by **bug (mutant)**, not by row, and compute history features only from earlier data (Section 8).
3. **Reproducible.** One global seed (`SEED = 42`). Running the pipeline twice must produce identical artifacts.
4. **Hand-written core algorithms.** BFS, DFS, Tarjan SCC, topological sort, greedy Set Cover, Greedy Knapsack, DP Knapsack and Branch and Bound are your own code with tests.
5. **Same code for training and serving features.** Feature computation lives in one module used by both the offline pipeline and the live API (avoids train/serve skew).
6. **Fast live API.** Heavy work (coverage, mutation runs, training, experiments) runs offline and is saved to `artifacts/`. Live endpoints only do graph lookups, feature computation, model inference and selection, so they respond in well under a second.
7. **Clean, typed, documented code.** Type hints everywhere, docstrings on public functions, small modules, no giant files.

---

## 2. TECH STACK (use exactly these)

| Purpose | Library |
|---|---|
| Language | **Python 3.11+** |
| API framework | **FastAPI** + **Uvicorn** |
| Validation / schemas | **Pydantic v2** (camelCase aliases, see Section 10.1) |
| Testing the sample project | **pytest** |
| Coverage | **coverage.py** (dynamic contexts) |
| Code parsing | **`ast`** (standard library) |
| ML | **scikit-learn**, **joblib** |
| Data | **NumPy**, **Pandas** (CSV for datasets; Parquet optional) |
| Parallelism | `concurrent.futures.ProcessPoolExecutor` |
| Plots for the report | **Matplotlib** |
| Verification only (tests) | **NetworkX** |
| Quality | **pytest** for unit tests, **ruff** for linting |

No databases are needed. Artifacts are JSON, CSV and joblib files.

---

## 3. PROJECT STRUCTURE

```
backend/
├── README.md
├── pyproject.toml            # or requirements.txt
├── Makefile                  # install, build, serve, test, experiments
├── .env.example
├── sample_project/           # the "company codebase" we analyze (Section 4)
│   ├── shop/                 # source package (about 12 modules)
│   └── tests/                # about 120+ tests
├── src/smarttest/
│   ├── config.py             # SEED, paths, constants
│   ├── cli.py                # `python -m smarttest.cli <command>`
│   ├── graph/
│   │   ├── parser.py         # AST -> functions and call edges
│   │   ├── algorithms.py     # BFS, DFS, Tarjan SCC, Kahn topological sort
│   │   └── model.py          # DependencyGraph class
│   ├── coverage/
│   │   ├── plugin.py         # pytest plugin: per-test duration + simulated latency
│   │   └── collector.py      # runs suite, builds test -> functions map
│   ├── mutation/
│   │   ├── operators.py      # AST mutation operators
│   │   └── runner.py         # applies mutants, runs candidate tests, records results
│   ├── features/
│   │   └── builder.py        # feature computation (training + serving)
│   ├── ml/
│   │   ├── dataset.py        # builds the (mutant, test) dataset
│   │   ├── train.py          # trains, calibrates, selects model
│   │   ├── evaluate.py       # metrics, permutation importance
│   │   └── predict.py        # risk scoring used by the API
│   ├── selection/
│   │   ├── set_cover.py      # greedy weighted Set Cover (phase 1)
│   │   ├── knapsack_greedy.py
│   │   ├── knapsack_dp.py
│   │   ├── branch_bound.py
│   │   └── pipeline.py       # two-phase selection + baselines
│   ├── experiments/
│   │   ├── detection.py      # bug detection vs budget, all strategies
│   │   ├── scalability.py    # algorithm runtime/memory vs n
│   │   ├── replay.py         # simulated sequence of changes
│   │   └── plots.py          # Matplotlib PNGs for the report
│   ├── store.py              # loads artifacts once at API startup
│   └── api/
│       ├── main.py           # FastAPI app, CORS, routes
│       └── schemas.py        # Pydantic models (camelCase)
├── artifacts/                # generated, git-ignored (Section 9)
└── tests/                    # unit and API tests (Section 12)
```

---

## 4. THE SAMPLE PROJECT (what we analyze)

Create a realistic, deterministic **e-commerce Python package** `shop/` that serves as the codebase under test. Requirements:

- **About 12 modules and 40 to 60 functions**, for example: `cart`, `pricing`, `discount`, `tax`, `payment`, `order`, `inventory`, `shipping`, `user`, `auth`, `notification`, `report`, `validators`, `utils`.
- **Real logic**, not trivial one-liners: arithmetic, comparisons, boolean conditions, loops, thresholds (coupon rules, tax slabs, stock checks, shipping tiers). This matters because mutation operators need meaningful code to change.
- **Layered call structure:** low-level utilities, mid-level business functions, high-level orchestration (`order.place_order` calling cart, discount, tax, payment, inventory, notification).
- **At least one circular dependency** (for example, `validators.validate_order` and `order.check_limits` call each other, or a three-function cycle) so Strongly Connected Components are visible.
- **Function ids** use the format `module.function` (for example `cart.calculate_total`). Methods are `module.Class.method`.

**Tests (`sample_project/tests/`), at least 120 tests**, deterministic, no randomness and no network:

| Type | Count | Declared duration | Scope |
|---|---|---|---|
| Unit | about 80 | 0.05 to 1 s | one function or two |
| Integration | about 30 | 2 to 10 s | a module chain |
| End-to-end | about 12 | 15 to 40 s | whole order flow, touches many modules |

**Simulated test duration.** Real slow tests wait on databases and networks. To mimic that without waiting, provide a helper `sample_project/tests/helpers.py`:

```python
def simulate_io(seconds: float) -> None:
    """Declare that this test would spend `seconds` on I/O. Does NOT sleep unless REAL_SLEEP=1."""
```

The pytest plugin (Section 5.2) adds the declared seconds to the measured time, so `test_time = measured_time + declared_time`. Document this clearly in the README and expose `durationsSimulated: true` in `/api/meta`. This keeps the demo fast while making test costs realistic and varied (this variety is what makes the knapsack problem interesting).

**Synthetic churn metadata.** The project has no real git history, so generate a seeded `churn` value per module (how often it is edited) in `artifacts/churn.json`, and describe it as **simulated** everywhere it is mentioned.

Optionally support `PROJECT_PATH` in `.env` to analyze a different Python project, but the sample project is the default and must work out of the box.

---

## 5. PIPELINE STAGES (offline build)

Expose each stage as a CLI command and run all in order with `python -m smarttest.cli build-all` (also `make build`). Each stage reads and writes files in `artifacts/`, logs progress, and is skippable if its output already exists (`--force` to rebuild).

### 5.1 Stage 1: Dependency graph (`graph/`)

- Parse every `.py` file with `ast`. Collect every function and method (id, module, file, start line, end line).
- Build call edges `A -> B` meaning **A uses B**. Resolve calls through: same-module calls, `from shop.cart import calculate_total`, `import shop.cart as c; c.calculate_total()`, and `module.function()` attribute calls. Ignore calls that cannot be resolved statically (builtins, third-party libraries, dynamic calls) and count them so the README can report an "unresolved calls" figure.
- Save `artifacts/graph.json`.

### 5.2 Stage 2: Coverage and test timing (`coverage/`)

- Run the full suite **once** under coverage.py with **dynamic contexts** (one context per test) so each executed line is attributed to a test.
- Map executed lines to the enclosing function using the line ranges from Stage 1, producing `test -> set of function ids`.
- Write a small pytest plugin that records, for each test: id, name, file, measured duration, declared simulated duration, total `timeSec`, and pass/fail. Baseline requirement: **every test must pass on unmodified code** (fail the build loudly if not).
- Save `artifacts/tests.json` (test metadata and coverage) and `artifacts/coverage.json`.

### 5.3 Stage 3: Mutation testing (`mutation/`)

Create labeled data by injecting controlled bugs.

**Operators (implemented with `ast.NodeTransformer`, one mutation per mutant):**

| Category | Examples |
|---|---|
| Arithmetic | `+` to `-`, `-` to `+`, `*` to `/`, `//` to `*`, `%` to `*` |
| Comparison | `<` to `<=`, `>` to `>=`, `==` to `!=`, `<=` to `<`, `>=` to `>` |
| Boolean | `and` to `or`, `or` to `and`, remove `not` |
| Constant | `0` to `1`, `1` to `0`, `True` to `False`, `n` to `n + 1` |
| Statement | `return x` to `return None`, delete one statement (replace with `pass`) when safe |

**Process:**
1. Enumerate all possible mutants, then sample **about 400 to 600** with a fixed seed, stratified so every function receives mutants and operator categories are balanced.
2. For each mutant: copy the sample project to a temp directory, patch the one file, determine its **candidate tests** (tests covering any function in the affected set, see Section 6), run those tests in a subprocess with a **per-mutant timeout** (60 s), and record which tests **failed** (errors count as failures; a timeout discards the mutant).
3. Run mutants in parallel with a process pool. Tests that do not cover the affected set cannot detect the mutant, so they are not run.
4. Classify each mutant as **killed** (at least one test failed) or **survived** (none failed). Report the overall **mutation score** (killed / total). Keep survived mutants in `mutants.json` but exclude them from the dataset and from detection-rate denominators (they cannot be detected by any test).
5. Save `artifacts/mutants.json`: id, function id, file, line, operator category, original and mutated snippet, killed flag, list of failing test ids, assigned **round** (Section 8.2), and `split` (`train` or `holdout`).

### 5.4 Stage 4: Dataset (`ml/dataset.py`)

One row per **(killed mutant, candidate test)** with the label `detected` = 1 if the test failed on that mutant, else 0. Columns are the features of Section 8.1, `mutant_id`, `test_id`, `round`, `split`. Save `artifacts/dataset.csv`.

### 5.5 Stage 5: Train the ML model (`ml/train.py`)

See Section 8.

### 5.6 Stage 6: Experiments (`experiments/`)

See Section 11. Produces `results.json`, `models.json`, `scalability.json`, and PNG charts.

---

## 6. GRAPH SEMANTICS (important definitions)

- **Edge `A -> B`:** A uses (calls) B.
- If B changes, everything that can reach B along edges may be affected. So traversal runs on the **reversed** graph, starting from the changed function(s).
- **SCC condensation:** compute SCCs with Tarjan, then build the condensed DAG. All functions inside one SCC are mutually dependent, so they share the same distance.
- **Distance of a node** = minimum number of condensed-graph hops from the changed node's SCC to the node's SCC (nodes in the same SCC as the changed function have distance 0).
- **Affected set `A(changed)`** = the changed functions plus every function that can reach them.
- **Candidate tests** = tests whose coverage set intersects `A(changed)`.
- **`sccGroups`** returned to the UI contains only SCCs with more than one function (real cycles).
- **Topological level** of a function = length of the longest path from it to a leaf in the condensed DAG (computed with Kahn's algorithm). Used as an ML feature (high-level orchestration functions behave differently from utilities).
- **Blast radius** = `|A({f})|` for a single function f.

---

## 7. ALGORITHMS TO IMPLEMENT (by hand, with complexity notes in docstrings)

### 7.1 Graph algorithms (`graph/algorithms.py`)

| Algorithm | Notes |
|---|---|
| **BFS** (multi-source) | Used for dependency distance. O(V + E). |
| **DFS** (iterative, no recursion limit problems) | Reachability and helper for Tarjan tests. O(V + E). |
| **Tarjan's SCC** (iterative) | Returns components. O(V + E). |
| **Kahn's topological sort** | On the condensed DAG; also yields topological levels. O(V + E). |

### 7.2 Selection algorithms (`selection/`)

**Formal problem.** Let `C` be the set of affected functions to protect, `T` the candidate tests, `t_i` the time of test i, `r_i` its predicted risk, `cov(i)` the functions of C it covers, and `B` the budget.

```
maximize   sum(r_i)  over selected tests
subject to sum(t_i) <= B
and        coverage of C is maximized first (Phase 1), then value is maximized (Phase 2)
```

**Two-phase selection (`selection/pipeline.py`):**

- **Phase 1: risk-weighted greedy Set Cover** (`set_cover.py`). Each affected function gets a weight `w_f = 1 / (1 + distance_f)` (closer to the change means more important). Repeatedly pick the test that maximizes `(sum of w_f for newly covered functions) * (0.5 + r_i) / t_i` among tests that still fit in the remaining budget. Stop when all coverable functions are covered or nothing fits. Functions that no candidate test covers are counted as **uncoverable** and excluded from the coverage denominator.
- **Phase 2: value maximization** over the remaining tests with the remaining budget, using the chosen algorithm:

| Algorithm | Implementation requirements |
|---|---|
| **Greedy** | Sort by `r_i / t_i` descending, add while it fits. O(n log n). |
| **DP Knapsack** | Convert times to integers in units of 0.1 s (`ceil`), table over tests and capacity, reconstruct the chosen set. Use a NumPy boolean `keep[n][W+1]` table for reconstruction. O(n W) time and space. |
| **Branch and Bound** | Sort by ratio, depth-first search with the **fractional knapsack upper bound** for pruning. Count `nodesExplored`. Add a **time limit** (default 2 s); if hit, return the best solution found and set `timedOut = true`. |

Return for every run: selected test ids, `totalTimeSec`, `totalRisk`, `coveragePct`, `algorithmRuntimeMs` (measured with `time.perf_counter`), plus extras `nodesExplored`, `timedOut`, `uncoverableCount`, `memoryKb` (measured with `tracemalloc`).

**Rules:** DP and Branch and Bound must return the same optimal total value for Phase 2 (when B&B does not time out). Greedy must never beat them. `optimalityGapPct = (optimal_value - value) / optimal_value * 100`, where optimal comes from DP.

**Edge cases:** budget below the fastest test returns an empty selection with coverage 0 (not an error); duplicate tests with equal ratios break ties by smaller time then by id; zero candidate tests returns an empty selection.

### 7.3 Baselines (`selection/pipeline.py`)

| Strategy | Definition |
|---|---|
| **Run Everything** | The whole suite. Reference point (100% of detectable bugs). |
| **Random** | Random permutation of the **whole suite**, add tests while they fit the budget. Average over 20 seeded repeats. |
| **Dependency-Only** | Candidate tests ordered by dependency distance ascending (ties by id), added while they fit. No risk, no optimization. |
| **Risk-Based** | Candidate tests ordered by predicted risk descending, added while they fit. No optimization. |
| **Ours** | Two-phase selection with DP in Phase 2. |

---

## 8. MACHINE LEARNING COMPONENT

ML only estimates the **value** of each test. The algorithms of Section 7 make the decision.

### 8.1 Features (`features/builder.py`)

One function `build_features(changed_function_id, test_id, graph, test_meta, history) -> dict`, used by both training and the API.

| Feature | Definition |
|---|---|
| `dep_distance` | Minimum condensed-graph distance from the changed function to any function the test covers (candidates only, so always finite) |
| `covers_changed` | 1 if the test directly executes the changed function, else 0 |
| `n_affected_covered` | Number of functions in `A(changed)` the test covers |
| `frac_affected_covered` | `n_affected_covered / |A(changed)|` |
| `test_breadth` | Total functions the test covers |
| `test_time` and `log_test_time` | Test duration |
| `hist_fail_rate` | Smoothed historical detection rate: `(fails + 1) / (appearances + 2)` over **earlier** rounds only (Section 8.2) |
| `recent_fail_count` | Failures in the test's last 5 appearances as a candidate (earlier rounds only) |
| `blast_radius` | `|A(changed)|` |
| `topo_level` | Topological level of the changed function |
| `module_churn` | Simulated churn of the changed function's module |

### 8.2 Rounds and history (anti-leakage design)

- Randomly (seeded) assign mutants to **10 rounds** to imitate a chronological history of changes.
- History features for a mutant in round k use **only mutants in rounds < k**. Round 1 uses the global prior (smoothing makes this well defined).
- **Split:** rounds 1 to 7 are `train`; rounds 8 to 10 are `holdout`. All final reported metrics and all experiment results use the **holdout mutants only**.
- For the model served by the API, history features at inference time come from the **full training history** (a frozen lookup table in `artifacts/history.json`).
- Within training, perform cross-validation with **GroupKFold grouped by `mutant_id`** so rows of the same mutant never appear in both folds.

### 8.3 Models and selection

Train and compare:

1. **Logistic Regression** (with `StandardScaler`, `class_weight="balanced"`), the interpretable baseline.
2. **Random Forest** (`class_weight="balanced_subsample"`).
3. **Gradient Boosting** (`HistGradientBoostingClassifier` or `GradientBoostingClassifier`).

Pick the best model by **PR-AUC** under GroupKFold CV (the data is imbalanced, so accuracy alone is misleading). Then **calibrate** probabilities (`CalibratedClassifierCV`, using the same group-based folds, sigmoid or isotonic) because the scores are used as knapsack values and should behave like probabilities. Save the final model to `artifacts/model.joblib`.

### 8.4 Evaluation (`ml/evaluate.py`)

On the **holdout** split report, for every model: accuracy, precision, recall, F1, ROC-AUC, PR-AUC, and the positive rate. Compute **permutation importance** on the holdout split (more trustworthy than built-in importances) and convert it to a normalized `importance` per feature.

### 8.5 Scoring at inference (`ml/predict.py`)

- For a single changed function: build features for every candidate test and call `predict_proba`.
- For **multiple changed functions**: compute a risk per change and combine them with the noisy-OR rule `1 - product(1 - r_i)`. (The model is trained on single-change mutants, so say so in the README.)
- Round risk to 4 decimals in responses.

---

## 9. ARTIFACTS (written offline, loaded by the API at startup)

| File | Content |
|---|---|
| `graph.json` | Functions and edges |
| `tests.json` | Test metadata: id, name, file, `timeSec`, covered function ids |
| `coverage.json` | Raw coverage summary and unresolved-call statistics |
| `churn.json` | Simulated module churn |
| `mutants.json` | All mutants with killed flag, failing tests, round, split |
| `dataset.csv` | Training dataset |
| `history.json` | Frozen history lookup for serving |
| `model.joblib` | Calibrated model plus feature order |
| `models.json` | Model comparison and feature importance (served at `/api/models`) |
| `results.json` | Detection vs budget, strategy summary, dataset summary, headline (served at `/api/results`) |
| `scalability.json` | Runtime and memory vs n |
| `meta.json` | Provenance: seed, build time, counts, versions |
| `plots/*.png` | Matplotlib charts for the report |

`store.py` loads everything once at startup. If artifacts are missing, the API must fail fast with a clear message: "Run `make build` first."

---

## 10. REST API

### 10.1 Conventions

- Base path `/api`, JSON only.
- **All JSON keys are camelCase** (the frontend expects `timeSec`, `budgetSec`, and so on). Implement this with Pydantic v2 `alias_generator=to_camel`, `populate_by_name=True`, and `response_model_by_alias=True`.
- **CORS:** allow `http://localhost:5173` and `http://127.0.0.1:5173` (configurable through `.env`).
- **Errors:** return `{"error": "<code>", "detail": "<message>"}` with proper status codes: 404 for unknown function ids, 422 for invalid input (budget out of range, empty `changed`), 503 if artifacts are not loaded.
- Responses may include **extra additive fields** (marked "extra" below), but must never rename or remove the fields in the contract.
- Auto-generated docs at `/docs`.

### 10.2 Endpoints and exact response shapes

**`GET /api/health`** returns `{"status": "ok"}`.

**`GET /api/meta`** (extra endpoint, used by the UI to size controls)
```json
{
  "projectName": "shop",
  "numFunctions": 52,
  "numTests": 126,
  "suiteTimeSec": 742.5,
  "durationsSimulated": true,
  "budgetRange": { "min": 5, "max": 300, "step": 5, "default": 30 },
  "seed": 42,
  "builtAt": "2026-10-20T10:00:00Z"
}
```

**`GET /api/graph`**
```json
{
  "nodes": [{ "id": "cart.calculate_total", "label": "calculate_total", "file": "shop/cart.py", "kind": "function" }],
  "edges": [{ "source": "order.place_order", "target": "cart.calculate_total" }]
}
```
(`source` uses `target`. Extra per node: `topoLevel`.)

**`POST /api/affected`** body `{ "changed": ["cart.calculate_total"] }`
```json
{
  "affected": [{ "id": "cart.calculate_total", "distance": 0 }],
  "candidateTests": [
    { "id": "tests/test_cart.py::test_total", "name": "test_total", "timeSec": 2.0, "risk": 0.85, "covers": ["cart.calculate_total"] }
  ],
  "sccGroups": [["validators.validate_order", "order.check_limits"]]
}
```
(`covers` lists only the affected functions the test executes. Candidate tests sorted by risk descending.)

**`POST /api/select`** body `{ "changed": [...], "budgetSec": 30, "algorithm": "greedy" | "dp" | "bnb" }`
```json
{
  "selected": ["tests/test_cart.py::test_total"],
  "totalTimeSec": 12.0,
  "totalRisk": 1.4,
  "coveragePct": 91.7,
  "algorithmRuntimeMs": 3.2
}
```
(Extras: `nodesExplored`, `timedOut`, `uncoverableCount`.)

**`POST /api/compare`** body `{ "changed": [...], "budgetSec": 30 }`
```json
{
  "results": [
    { "algorithm": "greedy", "totalRisk": 1.32, "totalTimeSec": 12, "testsSelected": 4, "runtimeMs": 1.1, "memoryKb": 18, "optimalityGapPct": 5.7 },
    { "algorithm": "dp",     "totalRisk": 1.40, "totalTimeSec": 14, "testsSelected": 5, "runtimeMs": 9.0, "memoryKb": 210, "optimalityGapPct": 0 },
    { "algorithm": "bnb",    "totalRisk": 1.40, "totalTimeSec": 14, "testsSelected": 5, "runtimeMs": 22.0, "memoryKb": 35, "optimalityGapPct": 0 }
  ],
  "scalability": [{ "n": 100, "greedyMs": 0.1, "dpMs": 12.0, "bnbMs": 3.0 }]
}
```
(`scalability` is read from the precomputed `scalability.json`; `results` is computed live. Extra per scalability row: `bnbTimedOut`.)

**`GET /api/results`**
```json
{
  "headline": { "testReductionPct": 0, "timeSavedPct": 0, "bugDetectionPct": 0 },
  "detectionVsBudget": [{ "budgetSec": 10, "ours": 0, "random": 0, "dependencyOnly": 0, "runAll": 100 }],
  "strategies": [{ "name": "Ours", "testsRun": 0, "timeSec": 0, "bugsCaughtPct": 0 }],
  "dataset": { "mutants": 0, "tests": 0, "rows": 0, "mutationTypes": [{ "type": "arithmetic", "count": 0 }] }
}
```
(The zeros above are shape placeholders only; real values come from `artifacts/results.json`. Extras: `referenceBudgetSec`, `mutationScore`, `holdoutMutants`.)

**`GET /api/models`**
```json
{
  "models": [{ "name": "Random Forest", "accuracy": 0, "precision": 0, "recall": 0, "f1": 0 }],
  "featureImportance": [{ "feature": "Dependency distance", "importance": 0 }]
}
```
(Extras: `rocAuc`, `prAuc`, `selectedModel`. Feature names are human-readable labels, sorted by importance descending.)

**`POST /api/replay`** body `{ "budgetSec": 30, "numChanges": 20, "seed": 42 }` (seed optional)
```json
{
  "totalTests": 2520,
  "totalBugs": 20,
  "steps": [
    { "step": 1, "changedId": "cart.calculate_total", "testsRun": 5, "cumulativeTestsRun": 5, "caught": true, "cumulativeCaught": 1, "cumulativeRunAll": 126 }
  ]
}
```
Replay rules: sample `numChanges` **killed holdout mutants** (never training mutants) with the seed; for each, run the two-phase selection at the budget using the mutant's function as the change; `caught` is true if any selected test is in that mutant's failing-test list; `cumulativeRunAll` grows by the full suite size each step; `totalTests = numChanges * suiteSize`; `totalBugs = numChanges`. If `numChanges` exceeds the number of holdout mutants, sample with replacement and say so in a response field `sampledWithReplacement`.

### 10.3 Validation rules

- `changed`: 1 to 5 known function ids.
- `budgetSec`: from `budgetRange.min` to `budgetRange.max` (read from meta, with a sensible lower bound of 1).
- `algorithm`: one of `greedy`, `dp`, `bnb`.
- `numChanges`: 1 to 100.

---

## 11. EXPERIMENTS (`experiments/`)

All experiments use **holdout killed mutants only**, evaluated from the stored mutant result matrix (no re-running of tests needed).

### 11.1 Detection vs budget

- Budget grid: about 12 values from the smallest meaningful budget up to the budget range maximum (fixed in config).
- For each budget and strategy (Section 7.3), simulate every holdout mutant as a change: compute the selection, then check whether any selected test is in the mutant's failing-test list. **Detection rate** = detected / total holdout killed mutants.
- Random is averaged over 20 seeds. `runAll` is 100 (reference line).
- Output `detectionVsBudget` rows.

### 11.2 Strategy summary at a reference budget

- Reference budget `referenceBudgetSec`: configurable, default the budget-grid value closest to 10 percent of the mean candidate-set time (documented in the README).
- For each strategy compute mean `testsRun`, mean `timeSec`, and `bugsCaughtPct`.
- **Headline:** `testReductionPct = 1 - ours.testsRun / suiteSize`, `timeSavedPct = 1 - ours.timeSec / suiteTimeSec`, `bugDetectionPct = ours.bugsCaughtPct`. Report real values, whatever they are.

### 11.3 Dataset summary

Counts of mutants, killed mutants, mutation score, tests, dataset rows, and mutants per operator category (`mutationTypes`).

### 11.4 Scalability of selection algorithms

- Generate synthetic knapsack instances (seeded) for `n` in `[10, 20, 50, 100, 200, 500, 1000, 2000]` with realistic time and risk distributions.
- Measure Greedy, DP and Branch and Bound runtime (median of 5 runs). Branch and Bound uses its time limit and records `bnbTimedOut`.
- Also record peak memory (tracemalloc) for each algorithm and the **greedy optimality gap** statistics (mean, max) over 200 random instances.

### 11.5 Plots for the report (`plots/`)

Matplotlib PNGs with a dark theme matching the UI (black background, green primary series): detection vs budget, time saved, model comparison, feature importance, scalability. High resolution (200 dpi), clear titles and axis labels.

---

## 12. TESTING (`tests/`)

Use pytest. The suite must pass with `make test`.

| Area | Required tests |
|---|---|
| Graph algorithms | BFS distances, DFS reachability, Tarjan SCCs and Kahn ordering match **NetworkX** on at least 100 random graphs (including cyclic ones) |
| Topological order | Every edge goes forward in the returned order; cycles are rejected on the raw graph and handled on the condensation |
| Set Cover | On small instances, greedy coverage respects the budget and covers all coverable functions when the budget allows |
| Knapsack | For n <= 15, **DP == Branch and Bound == brute force** optimal value; Greedy <= optimum; budget 0; budget smaller than every test; ties; single test |
| Branch and Bound | Timeout path returns a valid feasible solution and `timedOut = true` |
| Pipeline | Selected total time never exceeds budget; coverage between 0 and 100; empty candidates handled |
| Mutation | Every operator produces valid Python (`compile` succeeds) and changes exactly one location |
| Leakage | History features for a mutant in round k are computed only from rounds < k; no `mutant_id` appears in both train and holdout; GroupKFold folds are disjoint by mutant |
| Features | Training and serving use the same function (a test calls both paths and compares output) |
| ML sanity | On holdout, tests that directly cover the changed function have a higher mean predicted risk than tests that cover it only indirectly |
| API contract | With FastAPI `TestClient`: every endpoint returns the exact keys in Section 10, camelCase, correct types; validation errors return 422 with the error format |
| Determinism | Running the selection and replay twice with the same seed gives identical outputs |

---

## 13. COMMANDS (Makefile and CLI)

```
make install        # create venv, install dependencies
make build          # run the full offline pipeline (python -m smarttest.cli build-all)
make serve          # uvicorn smarttest.api.main:app --reload --port 8000
make test           # run unit and API tests
make experiments    # re-run experiments and plots only
make clean          # delete artifacts
```

CLI sub-commands: `graph`, `coverage`, `mutate`, `dataset`, `train`, `experiments`, `build-all`, each with `--force`. The README must show the full quick start: install, build, serve, and run the frontend with `VITE_USE_MOCK=false`.

---

## 14. README REQUIREMENTS

The README must contain:

1. One-paragraph project explanation and an architecture diagram (ASCII is fine).
2. Quick start commands.
3. How each DAA topic maps to a file (BFS/DFS, Tarjan, topological sort, Set Cover, Knapsack DP, Greedy, Branch and Bound).
4. How the dataset is created and how leakage is prevented.
5. **Honest limitations:** static call graph is approximate (unresolved calls count), mutants are artificial bugs, test durations and module churn are **simulated**, history features come from our own mutation rounds, and multi-change risk uses a noisy-OR approximation.
6. The API list with example requests (curl).

---

## 15. BUILD ORDER (follow this sequence)

1. Scaffold the project, `config.py`, Makefile, dependencies.
2. Write the **sample project** and its tests; confirm they all pass.
3. Implement `graph/` (parser, algorithms, model) with unit tests against NetworkX.
4. Implement the coverage plugin and collector; produce `tests.json`.
5. Implement `selection/` (set cover, greedy, DP, branch and bound, pipeline) with brute-force tests.
6. Implement mutation operators and runner; produce `mutants.json`.
7. Implement features, dataset, training, evaluation, prediction.
8. Implement experiments and plots; produce `results.json`, `models.json`, `scalability.json`.
9. Implement the FastAPI app, schemas and store; add API contract tests.
10. Write the README, run the full `make build && make test`, and verify the quality checklist.

---

## 16. ACCEPTANCE CHECKLIST

- [ ] `make install && make build && make serve` works on a clean machine, and `/docs` loads.
- [ ] The sample project has at least 40 functions, 120 tests, one dependency cycle, and all tests pass on unmodified code.
- [ ] BFS, DFS, Tarjan, topological sort, Set Cover, Greedy, DP and Branch and Bound are hand-written and verified in tests.
- [ ] DP and Branch and Bound agree with brute force; Greedy never beats them.
- [ ] Mutation pipeline produces at least 300 killed mutants, with the mutation score reported.
- [ ] Train and holdout are split by mutant, history features use earlier rounds only, and the leakage tests pass.
- [ ] Three ML models compared; the best is calibrated and saved; holdout metrics and permutation importance are saved.
- [ ] All results in `/api/results` and `/api/models` come from real runs (no hard-coded numbers), with provenance in `meta.json`.
- [ ] Every endpoint in Section 10 exists, returns the exact camelCase shapes, and passes contract tests.
- [ ] `/api/select` and `/api/compare` respond in under 500 ms for the sample project.
- [ ] Selection never exceeds the budget; coverage and optimality gap are computed as defined.
- [ ] Running the pipeline twice with the same seed produces identical `results.json`.
- [ ] CORS works with the Vite dev server at `http://localhost:5173`.
- [ ] README lists limitations honestly, including the simulated durations and churn.

---

## 17. DO NOT

- Do not hard-code experiment numbers, model scores or results anywhere.
- Do not call NetworkX (or any graph or knapsack library) inside the product code; use it only in tests for verification.
- Do not randomly split dataset rows into train and test; always split by mutant/round.
- Do not evaluate any experiment on training mutants.
- Do not claim the system finds every bug; report measured detection rates.
- Do not rename or remove fields from the API contract; extra fields are allowed.
- Do not require internet access at runtime.
- Do not add databases, message queues, authentication or Docker unless asked.

---

## 18. FRONTEND INTEGRATION NOTES

- The React app switches from mock mode to this backend with `VITE_USE_MOCK=false` and `VITE_API_BASE_URL=http://localhost:8000`.
- The frontend's budget slider should read its min, max, step and default from `GET /api/meta` (`budgetRange`) so the slider always matches the real data scale.
- Function ids (`module.function`) and test ids (`path::test_name`) are the keys the frontend uses across pages, so keep them stable between builds.

---

**Final instruction:** when finished, print a short summary with the run commands, the number of functions, tests, mutants and mutation score, the holdout metrics of the selected model, and the list of API endpoints.
