import React, { useState, useEffect } from 'react';
import { useLocation, Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

export const AppShell: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  useEffect(() => {
    function handleResize() {
      if (window.innerWidth < 1100) {
        setCollapsed(true);
      } else {
        setCollapsed(false);
      }
    }
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="min-h-screen bg-bg-0 bg-midnight-indigo text-text-main flex flex-col">
      <Sidebar collapsed={collapsed} />
      <TopBar collapsed={collapsed} />

      <main
        className="flex-1 transition-all duration-300"
        style={{
          marginLeft: collapsed ? '72px' : '240px',
          width: `calc(100% - ${collapsed ? '72px' : '240px'})`,
        }}
      >
        <div className="mx-auto max-w-[1440px] p-6 lg:p-8">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0.2, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
          >
            <Outlet />
          </motion.div>
        </div>
      </main>
    </div>
  );
};
