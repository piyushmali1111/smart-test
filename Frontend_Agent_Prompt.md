# FRONTEND BUILD PROMPT: Smart Test Selection Dashboard

> **How to use:** Paste this entire file into your agentic IDE as the task prompt. If the IDE accepts images, also attach the reference image (Green Mist UI 2.0: a near-black background with neon green accents, glowing rounded cards and a faint circuit-grid backdrop). The visual direction is fully described below, so the build still works without the image.

---

## 0. ROLE AND GOAL

You are a senior frontend engineer and UI designer. Build a **complete, polished, presentation-ready React dashboard** for a college DAA (Design and Analysis of Algorithms) project called **Smart Test Selection**.

**What the project does (so you understand the data you are showing):**
When a developer changes some code, the system finds which parts of the software are affected (graph algorithms), finds the tests that cover that code, predicts how likely each test is to catch a bug (machine learning risk score), and then selects the best set of tests that fits inside a time budget (Knapsack, Set Cover, Greedy, Branch and Bound). The goal is to run far fewer tests while still catching most bugs.

**The dashboard exists to impress judges and faculty.** It must make the idea obvious within seconds, look premium, and never feel cluttered.

**Deliverable:** a runnable Vite + React project, working **fully with built-in mock data** (no backend required), and switchable to a real FastAPI backend through one environment variable.

---

## 1. NON-NEGOTIABLE DESIGN PRINCIPLES

1. **Visual first, text second.** Communicate with charts, graphs, glowing cards, progress bars, icons and big numbers. Use words only where they are needed.
2. **Strict text budget.** Page title: max 3 words. Subtitle: max 12 words. Card label: max 3 words. Tooltip: max 12 words. At most **one** short insight sentence per page. **No paragraphs anywhere. No lorem ipsum.**
3. **One theme only:** deep black with neon green accents, glow effects, and a faint circuit-grid background. No purple, no blue gradients, no rainbow charts.
4. **Presentation-friendly:** the demo will be shown on a projector. Use large KPI numbers (40 to 56 px), generous spacing, high contrast, and big click targets.
5. **Everything animated gently:** smooth, purposeful motion (never flashy). Respect `prefers-reduced-motion`.
6. **Consistent semantic colors:** the same color always means the same thing on every page (see Section 3.2).
7. **Never present fake results as real.** All mock numbers must be clearly marked with a small "Sample data" badge in the top bar whenever mock mode is on.

---

## 2. TECH STACK (use exactly these)

| Purpose | Library |
|---|---|
| Framework | **React 18 + Vite + TypeScript** |
| Styling | **Tailwind CSS** (with a custom theme from Section 3) |
| Routing | **React Router v6** |
| Server state / caching | **TanStack Query (React Query)** |
| Client state | **Zustand** |
| HTTP | **Axios** |
| Graph visualization | **@xyflow/react (React Flow)** with **dagre** for auto layout |
| Charts | **Recharts** |
| Animation | **framer-motion** |
| Icons | **lucide-react** |
| Fonts | **Manrope** (headings), **Inter** (body), **JetBrains Mono** (numbers, code) via `@fontsource` packages (no external CDN calls) |
| Utilities | `clsx`, `tailwind-merge`, `react-countup` (or a small custom hook) |

Do not use Streamlit, Material UI, Ant Design, Bootstrap or any heavy UI kit. Build the components yourself using Tailwind so the look is fully custom.

---

## 3. DESIGN SYSTEM

### 3.1 Color tokens

Define these as CSS variables in `src/styles/tokens.css` **and** mirror them in `tailwind.config.ts`.

```css
:root {
  /* Backgrounds (darkest to lightest) */
  --bg-0: #030706;   /* page background */
  --bg-1: #060D0A;   /* sidebar, top bar */
  --bg-2: #0A1410;   /* cards */
  --bg-3: #0F1D17;   /* inner panels, inputs */
  --bg-4: #152A20;   /* hover states */

  /* Greens (brand) */
  --green-50:  #E8FFF1;  /* primary text */
  --green-200: #A6FFCB;
  --green-400: #3DFF94;  /* bright neon accent */
  --green-500: #22E27A;  /* primary brand green */
  --green-600: #14B863;
  --green-800: #0B6B3A;
  --green-900: #073D22;

  /* Text */
  --text:       #E8FFF1;
  --text-muted: #8AA595;
  --text-dim:   #5A7366;

  /* Borders and glow */
  --border:        rgba(61, 255, 148, 0.12);
  --border-strong: rgba(61, 255, 148, 0.35);
  --glow-sm: 0 0 12px rgba(61, 255, 148, 0.25);
  --glow-md: 0 0 24px rgba(61, 255, 148, 0.35);
  --glow-lg: 0 0 48px rgba(61, 255, 148, 0.30);

  /* Semantic colors */
  --danger: #FF4D5E;  /* changed code, failed */
  --warn:   #FFB020;  /* affected code, dependency-only baseline */
  --info:   #2DD4BF;  /* secondary series (teal) */
  --lime:   #A3E635;  /* tertiary series */
  --neutral:#8A9A92;  /* random baseline, unaffected */
}
```

### 3.2 Semantic color meaning (use consistently everywhere)

| Meaning | Color |
|---|---|
| Changed code | `--danger` red |
| Affected code (darker amber = closer to the change) | `--warn` amber |
| Unaffected code / skipped tests | dim grey-green (`--text-dim`, 40% opacity) |
| Selected test / our method / success | `--green-400` neon green |
| Random baseline | `--neutral` grey, dashed line |
| Dependency-only baseline | `--warn` amber |
| Run-everything baseline | `--green-50` near-white, thin line |
| Secondary chart series | `--info` teal, then `--lime` |

### 3.3 Background

The page background is `--bg-0` with two layers:

1. **Circuit-grid:** 1px lines of `rgba(61,255,148,0.045)` every 64px (use two `linear-gradient` backgrounds), slightly masked with a radial fade so the grid is visible mainly near the top.
2. **Top glow:** a large radial gradient at top center, `radial-gradient(60% 40% at 50% 0%, rgba(34,226,122,0.18), transparent 70%)`.

Add a fixed, very subtle noise or vignette so the edges feel darker than the center.

### 3.4 Typography

| Use | Font | Weight | Size |
|---|---|---|---|
| Hero headline | Manrope | 800 | 56 to 72 px, **gradient text** |
| Page title | Manrope | 700 | 32 px |
| Card title | Manrope | 700 | 20 px |
| Body | Inter | 400 / 500 | 15 to 16 px |
| Muted label | Inter | 500 | 13 px, uppercase, letter-spacing 0.06em, `--text-muted` |
| KPI numbers | JetBrains Mono | 700 | 40 to 56 px |
| Table numbers / code | JetBrains Mono | 500 | 14 px |

**Gradient text (hero and big KPI numbers):**
`background: linear-gradient(180deg, #F0FFF6 0%, #A6FFCB 45%, #22E27A 100%); -webkit-background-clip: text; color: transparent;`

### 3.5 Shape, spacing, elevation

- Card radius: **20 px**. Inner panel radius: **14 px**. Pill/badge radius: **12 px**. Buttons: **10 px**.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64.
- Cards: `background: var(--bg-2); border: 1px solid var(--border);` with a very faint inner top highlight (`inset 0 1px 0 rgba(255,255,255,0.03)`).
- **Nested "framed" panels:** key visuals sit in an inner panel (`--bg-3`, radius 14, 1px border) inside the card, like the reference image's framed illustrations.
- Hover on cards: border becomes `--border-strong`, add `--glow-sm`, translateY(-2px), 200 ms ease.

### 3.6 Signature details (copy the reference mood)

- **Three-dot motif:** three small neon-green glowing dots (6 px, `--green-400`, `--glow-sm`) appear (a) centered in the top bar as a decorative element and (b) in the top-right corner of every chart card as a menu trigger.
- **Pill badge** (like "2k milestone updates!"): bold green text, 1px `--border-strong` border, `rgba(34,226,122,0.06)` background, radius 12, small padding.
- **Primary button:** transparent background, 1px `--green-500` border, green text; on hover: background `rgba(34,226,122,0.12)` plus `--glow-md`. Pressed: scale 0.98.
- **Ghost button** (like "Learn more"): 1px neutral border (`rgba(255,255,255,0.12)`), muted text; on hover: border turns green.
- Selected/active elements get a soft **glow pulse** (box-shadow animating between `--glow-sm` and `--glow-md`, 2.4 s loop).

---

## 4. APP SHELL (layout shared by all pages)

```
┌──────────┬────────────────────────────────────────────────────────┐
│          │  Top bar:  Page title        ● ● ●       [Sample data] ●│
│ Sidebar  ├────────────────────────────────────────────────────────┤
│  240px   │                                                        │
│          │   Page content (max-width 1440px, padding 32px)        │
│          │                                                        │
│ [context │                                                        │
│  chip]   │                                                        │
└──────────┴────────────────────────────────────────────────────────┘
```

### 4.1 Sidebar (240 px, `--bg-1`, right border `--border`)

- **Top:** logo mark (a small green hexagon or shield icon with a check) + wordmark "SmartTest" in Manrope 700.
- **Nav items** (icon + label, 44 px tall, radius 12). Active item: green text, `rgba(34,226,122,0.10)` background, 3 px green left bar, `--glow-sm`. Hover: `--bg-4`.
  1. Overview (`LayoutDashboard`)
  2. Change Analysis (`GitBranch`)
  3. Test Selection (`ListChecks`)
  4. Compare (`Scale`)
  5. Results (`BarChart3`)
  6. Live Replay (`Play`)
- **Bottom: "Current Scenario" chip:** a small framed card showing the shared state: `Changed: calculate_total` and `Budget: 30 s`. Clicking it goes to Change Analysis. This chip is how the user feels that the pages are connected.
- Below 1100 px width, the sidebar collapses to a 72 px icon rail (labels hidden, tooltips on hover).

### 4.2 Top bar (64 px, `--bg-1`, bottom border `--border`)

- Left: page title (Manrope 700, 24 px) with a tiny muted breadcrumb above.
- Center: the **three glowing dots** motif.
- Right: a **"Sample data"** pill (amber-tinted, only when mock mode is active) and a **backend status dot** (green pulsing = live API, amber = mock mode, red = API error) with a tooltip.

### 4.3 Page transitions

Wrap routes in `AnimatePresence`: fade in plus 8 px upward rise, 250 ms. Cards inside a page enter with a stagger of 60 ms.

---

## 5. SHARED STATE (Zustand store: `useScenarioStore`)

```ts
{
  changedIds: string[];            // default: ["cart.calculate_total"]
  budgetSec: number;               // default: 30
  algorithm: "greedy" | "dp" | "bnb"; // default: "dp"
  setChanged(ids), setBudget(n), setAlgorithm(a)
}
```

- Persist to `sessionStorage`.
- Pages 2, 3, 4 and 6 all read this store, so the user picks a change and budget once and every page reacts.
- Slider changes must be **debounced (300 ms)** before triggering API/mock calls.

---

## 6. SHARED COMPONENTS (build these in `src/components/ui`)

| Component | Spec |
|---|---|
| `Card` | Section 3.5 style; props: `title?`, `menu?` (shows three green dots), `glow?`, children |
| `FramedPanel` | The nested inner panel for visuals |
| `Badge` | Pill badge (Section 3.6) with variants: `green`, `amber`, `red`, `grey` |
| `Button` | Variants `primary`, `ghost`, `icon`; sizes `sm`, `md`, `lg`; loading state with a small green spinner |
| `StatCard` | Large gradient KPI number (count-up animation on mount), small muted label, optional trend icon, optional tiny sparkline |
| `Slider` | Custom range input: 6 px track (`--bg-4`), filled part with green gradient, 20 px thumb with green ring and glow, value bubble above thumb, keyboard accessible |
| `SegmentedControl` | Pill track `--bg-3`; active segment is a green-bordered, glowing sliding highlight (use framer-motion `layoutId`) |
| `Tabs` | Underline tabs, active underline is green with glow |
| `RiskBar` | 8 px rounded bar, gradient from `--green-800` to `--green-400` filled to the risk value, numeric value in mono font to the right |
| `ProgressRing` | SVG circular progress, green stroke with glow, big center number |
| `Tooltip` | Dark glass (`rgba(10,20,16,0.9)` plus backdrop blur), 1px border, 12-word max |
| `DotsMenu` | The three green dots; opens a small menu with "Export CSV" (downloads the chart's data) |
| `Skeleton` | Shimmering dark-green placeholder blocks used while loading |
| `EmptyState` | Centered icon, one short line, one action button |
| `ErrorState` | Red-tinted card, one line, "Retry" button |
| `Legend` | Row of small colored dots plus labels |
| `Toast` | Small bottom-right dark glass notification |
| `Insight` | A single-line callout with a green sparkle icon and 1px green left border; max one per page |

**Charts theme (shared Recharts config in `src/components/charts/theme.ts`):**
grid lines `rgba(255,255,255,0.06)`, no vertical grid lines, axis text `--text-muted` 12 px, axis lines hidden, custom dark-glass tooltip, rounded bar corners (6 px), line stroke width 3 for the hero series and 2 for others, subtle area gradient fill under the hero series (green 25% to 0%), 700 ms entry animation.

---

## 7. PAGES

Routes: `/`, `/analysis`, `/selection`, `/compare`, `/results`, `/replay`.

### PAGE 1: Overview (`/`)

**Purpose:** explain the project and its payoff in 20 seconds.

```
 [ 2026 · DAA Project ]  (pill badge)

        Smart Test Selection          (huge gradient headline)
   Run fewer tests. Catch the same bugs.   (subtitle)

   [ Start Demo ]  [ View Results ]

 ┌──────────────────────────────────────────────────────────┐
 │  All tests:  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  │
 │  Selected:   ■□□□■□□□□□■□□□□□□■□□□□□■□□□□□□□■□□□□□□□□□□  │ (test grid)
 └──────────────────────────────────────────────────────────┘

  Change ──► Graph ──► ML Risk ──► Optimize ──► Run         (pipeline)

  [ Tests reduced ]  [ Time saved ]  [ Bugs still caught ]   (3 stat cards)
```

**Elements:**
1. **Pill badge** at the top-left of the hero (like "2k milestone updates!"): text "DAA Project".
2. **Hero headline** "Smart Test Selection" with the gradient text, plus a one-line subtitle.
3. **Two buttons:** "Start Demo" (primary, goes to `/analysis`) and "View Results" (ghost, goes to `/results`).
4. **Test grid visual** (the signature visual): a framed panel with a grid of about 200 small rounded squares representing all tests. Most are dim (`--bg-4`). A small subset lights up neon green with a glow, animated in sequence (a ripple from the left, 8 ms stagger). Caption on the left: "All tests", on the right: "Selected". A small toggle "Run all / Smart" re-animates it. This visual makes the whole project obvious.
5. **Pipeline strip:** five glowing node cards connected by animated dashed lines (a pulse travels along the line): Change, Graph, ML Risk, Optimize, Run. Each has an icon and a one- or two-word label only. Clicking a node scrolls or navigates to the matching page.
6. **Three StatCards** (from `/api/results` headline): Tests reduced %, Time saved %, Bugs still caught %. Gradient numbers with count-up.
7. A footer line in `--text-dim`: team names / subject (read from `src/config/project.ts`, easy to edit).

### PAGE 2: Change Analysis (`/analysis`)

**Purpose:** show that the system understands how code is connected.

```
┌───────────────────────────────────────────┬───────────────────┐
│                                           │ Pick change       │
│        INTERACTIVE DEPENDENCY GRAPH       │ [search select ▾] │
│        (React Flow canvas, framed)        │                   │
│                                           │ Affected    12    │
│   ● changed  ● affected  ● unaffected     │ Tests       18    │
│                                           │ Cycles       1    │
│                                           │ [ Continue → ]    │
└───────────────────────────────────────────┴───────────────────┘
```

**Graph canvas (about 68% width, inside a FramedPanel with the faint grid visible):**
- Auto-layout with dagre, left-to-right.
- **Node design:** rounded rectangle, dark fill, 1px border, label in mono font, tiny icon for file vs function. **Colors by state:** changed = red border and glow, affected = amber border (darker amber for nearer nodes), unaffected = dim grey-green at 40% opacity.
- **Edges:** thin dim lines. Edges on the affected path turn amber and animate (moving dashes).
- **Click a node** to set it as the changed function (updates the store). Multi-select with Shift.
- **Ripple animation:** when the changed node changes, affected nodes light up in order of dependency distance, 120 ms stagger (a visible BFS).
- **Cycle groups (SCC):** nodes in a circular dependency are wrapped in a dashed rounded boundary with a small "Cycle" badge.
- Controls: zoom, fit view, a mini-map (styled dark green), and a "Reset" icon button.
- Hover a node: a tooltip with name and "Distance: N".

**Right panel (about 32%, a Card):**
- Title "Pick Change". A searchable select listing functions, showing the current one.
- Three stat rows with icons and mono numbers: **Affected** (count), **Tests** (candidate count), **Cycles** (SCC groups).
- Legend (changed / affected / unaffected).
- Primary button "Continue" that goes to `/selection`.
- Optional `Insight`: e.g. "1 change reaches 12 functions." (computed, not hard-coded).

### PAGE 3: Test Selection (`/selection`)

**Purpose:** the core optimization, with a live budget slider.

```
┌──────────────────────────────────────────────────────────────┐
│ Budget  [=========●-----------]  30 s     [Greedy|DP|B&B]    │
└──────────────────────────────────────────────────────────────┘
 [ Time used ◔ ]  [ Risk covered % ]  [ Tests 5 of 18 ]  [ Coverage % ]

 ┌── Budget bar (the knapsack, visualized) ─────────────────────┐
 │ [T1 ▇▇][T4 ▇▇▇▇▇][T7 ▇▇▇]░░░░░░░░ free                       │
 └──────────────────────────────────────────────────────────────┘

 ┌── Candidate tests table ─────────────────────────────────────┐
 │ ✔ Test        Time    Risk            Covers   Status        │
 │ ✔ test_total  2.0 s   ▇▇▇▇▇▇▇▇░ 0.85   3      Selected      │
 │ ✔ test_pay    10 s    ▇▇▇▇▇░░░░ 0.55   2      Selected      │
 │   test_full   30 s    ▇▇▇▇▇▇░░░ 0.60   5      Skipped       │
 └──────────────────────────────────────────────────────────────┘
```

**Elements:**
1. **Control bar (Card):** the big budget `Slider` (range 5 to 300 s, step 5, large value bubble) and the `SegmentedControl` for algorithm (Greedy / DP / Branch and Bound).
2. **Four KPI cards:** 
   - Time used vs budget as a `ProgressRing` (turns amber above 90% of budget).
   - Risk covered (%), gradient number.
   - Tests selected, "5 / 18".
   - Coverage (% of affected functions covered).
3. **Budget bar (signature visual):** a horizontal bar whose total width equals the budget. Each selected test is a green segment sized by its time (label appears on hover, short name inside if it fits), and the remaining free time is a dim hatched area. When the slider moves, segments animate (framer-motion layout animation). This makes Knapsack tangible.
4. **Tests table (Card, sticky header):**
   - Columns: Test (mono), Time, Risk (`RiskBar`), Covers (small count chip), Status.
   - Sorted by risk descending by default; clickable headers to sort.
   - Selected rows: 3 px green left bar, faint green background, soft glow, a check icon. Skipped rows: 45% opacity. Rows reorder with a smooth layout animation.
   - Status uses `Badge` (green "Selected", grey "Skipped"; a test that is skipped because it alone exceeds the budget shows a small amber "Too slow" badge).
   - A search box and a filter toggle "Selected only".
5. **Footer row:** "Algorithm runtime: 3 ms" in muted mono text, plus a ghost button "Compare algorithms" going to `/compare`.

### PAGE 4: Algorithm Comparison (`/compare`)

**Purpose:** show the DAA trade-off (optimality vs speed).

```
  ┌── Greedy ─────┐  ┌── Dynamic Prog. ┐  ┌── Branch & Bound ┐
  │  Value 1.32   │  │  Value 1.40  ★  │  │  Value 1.40  ★   │
  │  Time  12 s   │  │  Time  14 s     │  │  Time  14 s      │
  │  Tests 4      │  │  Tests 5        │  │  Tests 5         │
  │  Runtime 1 ms │  │  Runtime 9 ms   │  │  Runtime 22 ms   │
  │  Gap  5.7%    │  │  Gap  0%        │  │  Gap  0%         │
  └───────────────┘  └─────────────────┘  └──────────────────┘

  ┌── Runtime vs tests (line, log toggle) ─┐ ┌── Value achieved (bars) ─┐
  └────────────────────────────────────────┘ └──────────────────────────┘
  Insight: Greedy is N× faster and within X% of optimal.
```

**Elements:**
1. **Three algorithm cards side by side** (equal width, `FramedPanel` inside). Each shows an icon, the algorithm name, one **huge gradient number** (total risk value), and four small mono stats: Time used, Tests, Runtime (ms), Optimality gap (%). The best-value card(s) get a glowing green border and a "Optimal" `Badge` with a star icon. The fastest card gets a "Fastest" badge.
2. **Scalability line chart:** algorithm runtime vs number of tests, one line per algorithm (green shades plus teal and lime), with a **linear / log toggle** (`SegmentedControl`). Branch and Bound's curve rising steeply should be visible.
3. **Value comparison bar chart:** total risk achieved by each algorithm for the current scenario.
4. **One `Insight` line**, computed from data, for example "Greedy is 7x faster and within 5.7% of optimal."
5. Memory usage (KB) appears as a fifth small stat on each card only if the data includes it.

### PAGE 5: Results and Experiments (`/results`)

**Purpose:** prove the idea works. Use **three tabs** so the page stays clean: **Performance | ML Model | Dataset**.

**Tab 1: Performance**
- **Hero line chart (full width, framed):** "Bugs caught vs time budget". Four lines: Ours (neon green, thick, soft area fill), Dependency-only (amber), Random (grey, dashed), Run-all (near-white, thin, flat at the top). X axis: time budget, Y axis: % bugs caught.
- **Below, two cards:** (a) bar chart "Time saved" per strategy (tests run and time as grouped bars or two small charts), (b) a compact comparison table of the five strategies with columns Tests run, Time, Bugs caught, where our row is highlighted in green.
- A `StatCard` row repeating the three headline numbers.

**Tab 2: ML Model**
- **Model comparison:** grouped bar chart (Logistic Regression vs Random Forest, and Gradient Boosting if present) across Accuracy, Precision, Recall, F1.
- **Feature importance:** horizontal bar chart, sorted descending, green gradient bars, feature names in clean labels (for example "Dependency distance", "Past failure rate").
- A small framed card with a mini "Risk score distribution" histogram if data is available.

**Tab 3: Dataset**
- Three `StatCard`s: Mutants injected, Tests in suite, Training rows.
- A donut chart of mutation types (arithmetic, comparison, boolean, constant, statement), using green shades and teal/lime.
- One muted line: "Split by bug, not by row." (a trust-building detail).

Every chart card has the three-dot `DotsMenu` with "Export CSV".

### PAGE 6: Live Replay (`/replay`)

**Purpose:** a cinematic simulation proving the saving is consistent across many changes.

```
 [ Budget 30s ]  [ Changes: 10 | 20 | 50 ]  [ ▶ Start ][ ⏸ ][ ↺ ]  Speed [1x|2x|4x]

   Tests run                       Bugs caught
   340 / 4,000   (huge number)     19 / 20    (huge number)
   ▇▇░░░░░░░░                      ▇▇▇▇▇▇▇▇▇░

 ┌── Live test grid ─────────────┐  ┌── Change feed ─────────────────┐
 │ ■■■□□□□□■■□□□□□□■□□□□□        │  │ #12 order.total   ✔ caught     │
 │ (lit squares = tests executed)│  │ #11 login.auth    ✔ caught     │
 └───────────────────────────────┘  │ #10 cart.discount ✖ missed     │
                                    └────────────────────────────────┘
 ┌── Cumulative tests run (ours vs run-all, line builds live) ───────┐
 └───────────────────────────────────────────────────────────────────┘
```

**Elements:**
1. **Control bar:** budget slider (shared with the store), segmented control for number of changes (10, 20, 50), Start / Pause / Reset buttons, and speed (1x, 2x, 4x).
2. **Two giant counters** with count-up animation and thin progress bars: "Tests run / total" and "Bugs caught / total". When finished, the counters pulse once and a green `Badge` appears: "Complete".
3. **Live test grid:** the same dot-grid language as the Overview page. Each simulated change lights up the squares of tests that were run (neon green flash that decays to a dim green), so the viewer sees how few tests are touched.
4. **Change feed:** the latest 6 changes slide in from the top, each with the changed function (mono), tests run, and a green "caught" or red "missed" chip.
5. **Cumulative line chart** that draws itself as steps arrive: "Ours" (green) vs "Run all" (grey), showing the widening gap.
6. The replay is driven by the `/api/replay` response (an array of steps) animated client-side with timers, so it works identically in mock mode.

---

## 8. DATA LAYER AND API CONTRACT

### 8.1 Environment

```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=true        # true = use built-in mock adapter, false = real API
```

Create `src/api/client.ts` exposing one function per endpoint below. Each function calls the real API when `VITE_USE_MOCK=false`, and otherwise calls the mock adapter in `src/mocks/`. If a real API call fails, show `ErrorState` with Retry; do not silently fall back to mock data. Show the "Sample data" pill whenever mock mode is active.

### 8.2 Endpoints and shapes (TypeScript types in `src/api/types.ts`)

```ts
// GET /api/graph
type GraphResponse = {
  nodes: { id: string; label: string; file: string; kind: "file" | "function" }[];
  edges: { source: string; target: string }[];   // source USES target
};

// POST /api/affected   body: { changed: string[] }
type AffectedResponse = {
  affected: { id: string; distance: number }[];
  candidateTests: { id: string; name: string; timeSec: number; risk: number; covers: string[] }[];
  sccGroups: string[][];                          // circular dependency groups
};

// POST /api/select   body: { changed: string[]; budgetSec: number; algorithm: "greedy"|"dp"|"bnb" }
type SelectResponse = {
  selected: string[];                             // test ids
  totalTimeSec: number; totalRisk: number; coveragePct: number;
  algorithmRuntimeMs: number;
};

// POST /api/compare  body: { changed: string[]; budgetSec: number }
type CompareResponse = {
  results: { algorithm: "greedy"|"dp"|"bnb"; totalRisk: number; totalTimeSec: number;
             testsSelected: number; runtimeMs: number; memoryKb?: number; optimalityGapPct: number }[];
  scalability: { n: number; greedyMs: number; dpMs: number; bnbMs: number }[];
};

// GET /api/results
type ResultsResponse = {
  headline: { testReductionPct: number; timeSavedPct: number; bugDetectionPct: number };
  detectionVsBudget: { budgetSec: number; ours: number; random: number; dependencyOnly: number; runAll: number }[];
  strategies: { name: string; testsRun: number; timeSec: number; bugsCaughtPct: number }[];
  dataset: { mutants: number; tests: number; rows: number; mutationTypes: { type: string; count: number }[] };
};

// GET /api/models
type ModelsResponse = {
  models: { name: string; accuracy: number; precision: number; recall: number; f1: number }[];
  featureImportance: { feature: string; importance: number }[];
};

// POST /api/replay   body: { budgetSec: number; numChanges: number }
type ReplayResponse = {
  totalTests: number; totalBugs: number;
  steps: { step: number; changedId: string; testsRun: number; cumulativeTestsRun: number;
           caught: boolean; cumulativeCaught: number; cumulativeRunAll: number }[];
};
```

### 8.3 Mock adapter requirements (`src/mocks/`)

Build the mock data around a believable **shopping-app codebase**, deterministic (use a seeded random generator so it is identical on every run):

- **About 24 function nodes** across modules such as `cart`, `discount`, `tax`, `payment`, `order`, `inventory`, `shipping`, `user`, `login`, `notification`; about 35 edges; **include one circular dependency** so SCC grouping is visible.
- **About 30 tests** with times between 0.2 s and 40 s and coverage lists over the function ids.
- **Risk scores must react to the scenario:** in the mock `affected` logic, compute risk from dependency distance (closer = higher), plus a small seeded variation, so changing the selected function visibly changes the table.
- **Implement real Greedy, DP Knapsack and Branch and Bound in TypeScript** inside the mock adapter (they are short). Use integer time units (0.1 s) for the DP. Report actual measured runtime with `performance.now()`. This makes the slider and the comparison page genuinely live and correct.
- Provide plausible **placeholder** results data for `/api/results`, `/api/models` and `/api/replay`, stored as JSON in `src/mocks/data/`. Mark the files with a comment: "PLACEHOLDER VALUES, replace with real experiment output." Never hard-code these numbers into components.

---

## 9. MOTION SPEC

| Element | Animation |
|---|---|
| Page change | Fade plus 8 px rise, 250 ms |
| Card entrance | Stagger 60 ms |
| KPI numbers | Count-up over 900 ms |
| Overview test grid | Left-to-right ripple, 8 ms per square |
| Pipeline lines | Pulse traveling along dashed line, 2 s loop |
| Graph change | BFS ripple, 120 ms per distance level |
| Active/selected glow | 2.4 s pulse loop |
| Table rows | Layout animation when re-sorted/selected |
| Budget bar segments | Layout animation, spring (stiffness 260, damping 28) |
| Button press | Scale 0.98 |
| Charts | 700 ms entry draw |

If `prefers-reduced-motion` is set, disable loops and ripples and keep only fades.

---

## 10. RESPONSIVENESS AND ACCESSIBILITY

- **Primary target:** 1280 to 1920 px wide (laptop and projector). Make this look perfect first.
- **1100 px and below:** sidebar becomes a 72 px icon rail; two-column layouts stack.
- **Mobile (under 640 px):** single column; the graph is shown at a fixed 420 px height with pan and zoom; tables scroll horizontally inside their card.
- All interactive elements keyboard reachable with a visible green focus ring (`outline: 2px solid var(--green-400); outline-offset: 2px`).
- Text contrast at least 4.5:1 (the palette above satisfies this for `--text` on `--bg-2`; use `--text-muted` only for secondary labels).
- Add `aria-label`s to icon buttons, `role="img"` with short descriptions for charts, and never use color as the only signal (always add an icon or label as well).

---

## 11. LOADING, EMPTY AND ERROR STATES

- **Loading:** `Skeleton` blocks matching the final layout. Never show a blank page.
- **Empty (no change selected):** `EmptyState` with a graph icon and "Pick a change to begin" plus a button.
- **Zero candidate tests:** `EmptyState` "No tests affected".
- **Budget too small for any test:** amber `Insight` "Budget is below the fastest test."
- **API error:** `ErrorState` with Retry; toast on transient errors.

---

## 12. FOLDER STRUCTURE

```
frontend/
├── index.html
├── package.json
├── tailwind.config.ts
├── postcss.config.js
├── vite.config.ts
├── .env.example
└── src/
    ├── main.tsx
    ├── App.tsx                     # router + shell
    ├── styles/
    │   ├── tokens.css              # CSS variables (Section 3.1)
    │   └── globals.css             # background grid, glow, scrollbars
    ├── config/project.ts           # project name, team, subject (editable)
    ├── api/
    │   ├── client.ts
    │   └── types.ts
    ├── mocks/
    │   ├── adapter.ts              # mock implementation of every endpoint
    │   ├── algorithms.ts           # greedy, dp knapsack, branch and bound
    │   ├── seed.ts                 # seeded random generator
    │   └── data/                   # graph, tests, results, models, replay JSON
    ├── store/useScenarioStore.ts
    ├── hooks/                      # useGraph, useAffected, useSelect, useCompare, useResults, useReplay, useDebounce
    ├── components/
    │   ├── layout/                 # Sidebar, TopBar, AppShell, ScenarioChip
    │   ├── ui/                     # Card, Badge, Button, StatCard, Slider, SegmentedControl, Tabs, RiskBar, ProgressRing, Tooltip, DotsMenu, Skeleton, EmptyState, ErrorState, Insight, Toast
    │   ├── charts/                 # theme.ts, DetectionChart, TimeSavedChart, ModelChart, FeatureChart, RuntimeChart, DonutChart
    │   ├── graph/                  # DependencyGraph, GraphNode, GraphLegend
    │   ├── selection/              # BudgetBar, TestsTable
    │   └── visuals/                # TestGrid, PipelineStrip
    ├── pages/
    │   ├── Overview.tsx
    │   ├── ChangeAnalysis.tsx
    │   ├── TestSelection.tsx
    │   ├── Compare.tsx
    │   ├── Results.tsx
    │   └── LiveReplay.tsx
    └── utils/                      # format.ts (numbers, seconds), cn.ts (clsx + tailwind-merge)
```

---

## 13. BUILD ORDER (follow this sequence)

1. Scaffold Vite + React + TypeScript, install dependencies, configure Tailwind with the tokens, load fonts locally.
2. Build global styles (background grid, glow, scrollbar) and the app shell (sidebar, top bar, routes, transitions).
3. Build all shared UI components and the chart theme. Create a hidden `/styleguide` route that renders every component so the theme can be checked quickly.
4. Build the mock data, seeded generator and the three algorithms; wire the API client with the mock switch.
5. Build pages in this order: **Overview, Change Analysis, Test Selection, Compare, Results, Live Replay**.
6. Add loading, empty and error states, motion polish and accessibility.
7. Run a visual QA pass against the checklist in Section 14.

---

## 14. ACCEPTANCE CHECKLIST

- [ ] The app starts with `npm install && npm run dev` and works with no backend (mock mode).
- [ ] Setting `VITE_USE_MOCK=false` switches to the real API without code changes.
- [ ] All 6 pages exist, are reachable from the sidebar, and match the layouts above.
- [ ] Background, cards, badges, buttons, three-dot motif and glow match the dark black and neon green theme.
- [ ] No page has paragraphs of text; every page follows the text budget in Section 1.
- [ ] Choosing a changed function on page 2 updates pages 3, 4 and 6 (shared state), and the sidebar scenario chip.
- [ ] Moving the budget slider on page 3 live-updates the KPIs, budget bar and table (debounced).
- [ ] Greedy, DP and Branch and Bound produce correct results in mock mode (DP and Branch and Bound agree on total value; Greedy is never better).
- [ ] The dependency graph shows changed (red), affected (amber) and unaffected (dim) states, the BFS ripple, and a dashed cycle boundary.
- [ ] Charts use only the approved palette and the shared chart theme; every chart card has a working "Export CSV".
- [ ] "Sample data" pill is visible in mock mode.
- [ ] Layout is clean at 1920, 1440 and 1280 px, and degrades gracefully below 1100 px.
- [ ] Keyboard navigation and focus rings work; reduced-motion is respected.
- [ ] No console errors or warnings.

---

## 15. DO NOT

- Do not use Streamlit, Material UI, Ant Design, Bootstrap or stock illustration packs.
- Do not use purple, blue, pink or multi-color gradients. Stay within black, green, plus the semantic red, amber, teal and lime defined above.
- Do not write long descriptions, marketing copy or lorem ipsum.
- Do not hard-code experiment numbers inside components.
- Do not show mock numbers as if they were real results.
- Do not use external CDNs, remote fonts or remote images (everything must work offline).
- Do not add pages, features or libraries beyond this specification without asking.

---

**Final instruction:** when finished, print a short summary with the run commands, the list of routes, and how to switch from mock mode to the real FastAPI backend.
