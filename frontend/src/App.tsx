import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppShell } from './components/layout/AppShell';
import { Overview } from './pages/Overview';
import { ChangeAnalysis } from './pages/ChangeAnalysis';
import { TestSelection } from './pages/TestSelection';
import { Compare } from './pages/Compare';
import { Results } from './pages/Results';
import { LiveReplay } from './pages/LiveReplay';
import { Styleguide } from './pages/Styleguide';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<Overview />} />
            <Route path="/analysis" element={<ChangeAnalysis />} />
            <Route path="/selection" element={<TestSelection />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/results" element={<Results />} />
            <Route path="/replay" element={<LiveReplay />} />
            <Route path="/styleguide" element={<Styleguide />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
