# 🚀 Smart Test Selection: DAA-Driven Test Prioritization & Optimization

An intelligent test selection and prioritization engine designed for Continuous Integration (CI/CD) pipelines. By combining **Graph Algorithms**, **Greedy Heuristics**, **Dynamic Programming**, and **Branch & Bound** with **Machine Learning Risk Scoring**, Smart Test reduces regression testing time by **up to 85%** while catching over **90% of faults**.

Built as a comprehensive **Sem-5 Design and Analysis of Algorithms (DAA)** project.

---

## 📌 Problem Statement

In enterprise CI/CD workflows (e.g., Google, Meta, Netflix), executing full regression test suites on every pull request is prohibitively expensive, often taking hours. 
When a developer modifies only a few lines of code in a specific function:
1. Running all tests wastes computational resources and developer time.
2. Naive test selection risks missing cascading regressions in dependent modules.

**Smart Test** solves this by:
* Mapping the full AST call dependency graph and computing the exact change blast radius via reverse reachability.
* Formulating test selection under execution time budgets as a **Two-Phase DAA Optimization Problem**:
  * **Phase 1: Weighted Greedy Set Cover** to ensure complete coverage of every affected function.
  * **Phase 2: 0/1 Knapsack Optimization** (comparing Greedy, Dynamic Programming, and Branch & Bound) to maximize bug detection probability within a strict time budget.

---

## 🧠 DAA Algorithms Implemented (from Scratch)

| DAA Domain | Algorithm | Purpose in Smart Test | Complexity | File Location |
|---|---|---|---|---|
| **Graph Traversal** | **Multi-Source BFS** | Shortest path distance calculation from modified functions along reverse call edges | $O(V + E)$ | `backend/src/smarttest/graph/algorithms.py` |
| **Reachability** | **Iterative DFS** | Reachability analysis without recursion limits | $O(V + E)$ | `backend/src/smarttest/graph/algorithms.py` |
| **Cycles & Condensation** | **Tarjan's SCC** | Strongly Connected Component detection to condense cyclic dependencies into a DAG | $O(V + E)$ | `backend/src/smarttest/graph/algorithms.py` |
| **DAG Ordering** | **Kahn's Algorithm** | Topological sorting and level assignment across condensed architectural modules | $O(V + E)$ | `backend/src/smarttest/graph/algorithms.py` |
| **Coverage Guarantee** | **Weighted Greedy Set Cover** | Phase 1: Minimal test set selection guaranteeing $\ge 1$ test covers each affected function | $O(k \cdot n)$ | `backend/src/smarttest/selection/set_cover.py` |
| **Budget Optimization** | **Greedy Ratio Knapsack** | Phase 2: Ultra-fast selection by $\frac{\text{risk}}{\text{duration}}$ ratio | $O(n \log n)$ | `backend/src/smarttest/selection/knapsack_greedy.py` |
| **Exact Optimization** | **0/1 Knapsack DP** | Phase 2: Mathematically optimal test selection with boolean backtracking | $O(n \cdot W)$ | `backend/src/smarttest/selection/knapsack_dp.py` |
| **Pruning Optimization** | **Branch & Bound** | Phase 2: Best-first search tree traversal with fractional knapsack upper bounding | $O(2^n)$ worst, pruned | `backend/src/smarttest/selection/branch_bound.py` |

---

## 🎨 System Architecture & Features

### 🖥️ Frontend (React 18 + Vite + TypeScript + Tailwind CSS)
* **Theme:** Custom *"Midnight Indigo"* developer palette (calm dark navy `#0B1020`, periwinkle `#6C8CFF`, and cyan `#22D3EE`).
* **Interactive Pages:**
  1. **Overview (`/`)**: High-level execution stats, 136-test interactive grid, and execution time savings.
  2. **Change Analysis (`/analysis`)**: Interactive AST call graph with visual blast radius (Red $d=0$ modified node, Amber $d=1..k$ callers, dashed Tarjan SCC cycle groups).
  3. **Test Selection (`/selection`)**: Dynamic budget slider (1s–60s) controlling Phase 1 Set Cover + Phase 2 Knapsack allocation.
  4. **Algorithm Comparison (`/compare`)**: Side-by-side benchmarking of Greedy vs. DP vs. Branch & Bound showing optimality gaps, memory, and runtime curves.
  5. **Results & Experiments (`/results`)**: Mutation testing validation on 351 synthetic mutants across 13 budget points + ML feature importance.
  6. **Live Replay (`/replay`)**: Interactive 20-commit development sprint simulation tracking cumulative hours saved.

### ⚙️ Backend (Python 3.12+ / 3.14 + FastAPI)
* **REST API:** High-throughput async endpoints for live graph queries, impact traversal, and algorithm optimization.
* **Offline Pipeline:**
  * AST parser for Python codebases generating call graphs.
  * Line-by-line coverage collection using `pytest` and `coverage.py`.
  * AST mutation engine (AOR, ROR, LCR, COD) producing 351 mutants with 69.5% kill score.
  * ML classifier (Random Forest / Logistic Regression) predicting test risk based on AST distance, git churn, and historical failure rates.

---

## 📦 Project Structure

```text
├── backend/
│   ├── sample_project/      # E-commerce store target codebase (53 functions, 14 modules, 136 tests)
│   ├── src/smarttest/
│   │   ├── api/             # FastAPI REST endpoints and Pydantic schemas
│   │   ├── graph/           # AST parser, DependencyGraph model, BFS/DFS/Tarjan/Kahn algorithms
│   │   ├── selection/       # Set Cover, Knapsack DP, Knapsack Greedy, Branch & Bound
│   │   ├── ml/              # Feature engineering, model training, risk inference
│   │   ├── mutation/        # AST mutant generators and runner
│   │   ├── coverage/        # Dynamic pytest per-test coverage collector
│   │   ├── experiments/     # Scalability benchmarks and replay simulator
│   │   ├── cli.py           # Unified CLI ('smarttest build-all', 'smarttest serve')
│   │   └── store.py         # In-memory artifact store
│   ├── artifacts/           # Precomputed graph, models, coverage, and benchmark results
│   ├── tests/               # 25 automated unit & contract tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI cards, tables, badges, sliders, navigation
│   │   ├── pages/           # Overview, Analysis, Selection, Compare, Results, Replay
│   │   ├── services/        # Live API client with fallback to mock data
│   │   ├── store/           # Zustand state management
│   │   └── styles/          # Tokens and Tailwind theme configuration
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python:** 3.11+
* **Node.js:** 18+ and `npm`
* **Git**

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Start the FastAPI server (runs on http://localhost:8000)
uvicorn smarttest.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server (runs on http://localhost:5173)
npm run dev
```

Visit **http://localhost:5173** to interact with the dashboard.

---

## 📊 Experimental Results Summary

* **Target Application:** `shop/` (53 functions, 14 modules, 1 SCC cycle between `validators.validate_order` and `order.check_limits`).
* **Test Suite:** 136 unit and integration tests.
* **Mutation Testing:** 351 injected mutants, 244 killed (69.5% score).
* **Efficiency:** At **20% budget**, the DAA selection pipeline catches **>90% of mutants**, reducing CI execution time by over **80%**.

---

## 📜 License
Developed for academic and educational purposes under the Sem-5 Design and Analysis of Algorithms curriculum.
