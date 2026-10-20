export type AlgorithmType = "greedy" | "dp" | "bnb";

export interface GraphNode {
  id: string;
  label: string;
  file: string;
  kind: "file" | "function";
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AffectedItem {
  id: string;
  distance: number;
}

export interface CandidateTest {
  id: string;
  name: string;
  timeSec: number;
  risk: number;
  covers: string[];
}

export interface AffectedResponse {
  affected: AffectedItem[];
  candidateTests: CandidateTest[];
  sccGroups: string[][];
}

export interface SelectRequest {
  changed: string[];
  budgetSec: number;
  algorithm: AlgorithmType;
}

export interface SelectResponse {
  selected: string[];
  totalTimeSec: number;
  totalRisk: number;
  coveragePct: number;
  algorithmRuntimeMs: number;
}

export interface CompareRequest {
  changed: string[];
  budgetSec: number;
}

export interface AlgorithmCompareResult {
  algorithm: AlgorithmType;
  totalRisk: number;
  totalTimeSec: number;
  testsSelected: number;
  runtimeMs: number;
  memoryKb?: number;
  optimalityGapPct: number;
}

export interface ScalabilityPoint {
  n: number;
  greedyMs: number;
  dpMs: number;
  bnbMs: number;
}

export interface CompareResponse {
  results: AlgorithmCompareResult[];
  scalability: ScalabilityPoint[];
}

export interface ResultsHeadline {
  testReductionPct: number;
  timeSavedPct: number;
  bugDetectionPct: number;
}

export interface DetectionPoint {
  budgetSec: number;
  ours: number;
  random: number;
  dependencyOnly: number;
  runAll: number;
}

export interface StrategyResult {
  name: string;
  testsRun: number;
  timeSec: number;
  bugsCaughtPct: number;
}

export interface MutationTypeCount {
  type: string;
  count: number;
}

export interface DatasetStats {
  mutants: number;
  tests: number;
  rows: number;
  mutationTypes: MutationTypeCount[];
}

export interface ResultsResponse {
  headline: ResultsHeadline;
  detectionVsBudget: DetectionPoint[];
  strategies: StrategyResult[];
  dataset: DatasetStats;
}

export interface ModelMetric {
  name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

export interface ModelsResponse {
  models: ModelMetric[];
  featureImportance: FeatureImportance[];
}

export interface ReplayRequest {
  budgetSec: number;
  numChanges: number;
}

export interface ReplayStep {
  step: number;
  changedId: string;
  testsRun: number;
  cumulativeTestsRun: number;
  caught: boolean;
  cumulativeCaught: number;
  cumulativeRunAll: number;
}

export interface ReplayResponse {
  totalTests: number;
  totalBugs: number;
  steps: ReplayStep[];
}
