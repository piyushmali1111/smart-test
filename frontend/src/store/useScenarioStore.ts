import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AlgorithmType } from '../api/types';

interface ScenarioState {
  changedIds: string[];
  budgetSec: number;
  algorithm: AlgorithmType;
  setChanged: (ids: string[]) => void;
  toggleChanged: (id: string, multiSelect?: boolean) => void;
  setBudget: (budget: number) => void;
  setAlgorithm: (algo: AlgorithmType) => void;
  resetScenario: () => void;
}

const DEFAULT_STATE = {
  changedIds: ['cart.calculate_total'],
  budgetSec: 30,
  algorithm: 'dp' as AlgorithmType,
};

export const useScenarioStore = create<ScenarioState>()(
  persist(
    (set, get) => ({
      ...DEFAULT_STATE,

      setChanged: (ids: string[]) => set({ changedIds: ids.length > 0 ? ids : ['cart.calculate_total'] }),

      toggleChanged: (id: string, multiSelect = false) => {
        const current = get().changedIds;
        if (multiSelect) {
          if (current.includes(id)) {
            const next = current.filter(x => x !== id);
            set({ changedIds: next.length > 0 ? next : [id] });
          } else {
            set({ changedIds: [...current, id] });
          }
        } else {
          set({ changedIds: [id] });
        }
      },

      setBudget: (budgetSec: number) => set({ budgetSec: Math.max(5, Math.min(300, budgetSec)) }),

      setAlgorithm: (algorithm: AlgorithmType) => set({ algorithm }),

      resetScenario: () => set(DEFAULT_STATE),
    }),
    {
      name: 'smarttest_scenario_v1',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
