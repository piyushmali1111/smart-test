# Smart Test Selection · DAA Dashboard

A presentation-ready React dashboard for the college **Design and Analysis of Algorithms (DAA)** project: **Smart Test Selection**.

Theme: Midnight Indigo — deep navy background with soft periwinkle (#6C8CFF) and cyan (#22D3EE) accents.

---

## 🚀 Quick Start

### 1. Run in Mock Mode (Default, Zero Backend Required)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

In mock mode, the app runs completely standalone using deterministic algorithms (Greedy, DP Knapsack, Branch and Bound, and BFS/Tarjan SCC graph analysis) implemented directly in TypeScript with realistic sample data.

---

## 🔌 Switching to Live FastAPI Backend

To switch from mock mode to the real FastAPI backend, edit `frontend/.env`:

```ini
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=false
```

Restart the dev server:

```bash
npm run dev
```

---

## 🗺️ Routes & Pages

| Route | Page | Purpose |
|---|---|---|
| `/` | **Overview** | 20-second project pitch, interactive 180-test execution grid, 5-step pipeline, and 3 headline KPIs |
| `/analysis` | **Change Analysis** | Interactive code dependency graph (React Flow + Dagre), BFS reachability, Tarjan SCC cycle groups, and change selector |
| `/selection` | **Test Selection** | Live knapsack optimization, debounced budget slider (5s - 150s), animated knapsack budget bar, and sorted candidate tests table |
| `/compare` | **Algorithm Comparison** | Side-by-side DAA comparison of Greedy Heuristic vs 0/1 DP Knapsack vs Branch & Bound with scalability curves and optimality gaps |
| `/results` | **Results & Experiments** | 3-tab empirical verification: Fault detection vs budget curves, ML model comparison (Random Forest vs Gradient Boosting), and AST mutation dataset breakdown |
| `/replay` | **Live Replay** | Cinematic multi-commit simulation with live test flashing grid, rolling change feed, and cumulative test execution counters |
| `/styleguide` | **Style Guide** | Verification gallery of tokens, glowing cards, badges, buttons, sliders, segmented controls, and error states |

---

## 🛠️ Tech Stack

- **Framework:** React 18 + Vite + TypeScript
- **Styling:** Tailwind CSS + Custom CSS Variables Design Tokens
- **Routing:** React Router v6
- **Server State:** TanStack Query (React Query v5)
- **Client State:** Zustand (persisted to `sessionStorage`)
- **Graph Visualization:** `@xyflow/react` (React Flow) + `dagre`
- **Charts:** Recharts
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **Typography:** Manrope (Headings), Inter (Body), JetBrains Mono (Numbers/Code) via `@fontsource`
