import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { useSettingsStore } from '../store/settingsStore';

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider = ({ children }: ThemeProviderProps) => {
  const { theme } = useSettingsStore();

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  useEffect(() => {
    const stored = localStorage.getItem('cash-manager-settings');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        const storedTheme = parsed.state?.theme;
        if (storedTheme === 'dark') {
          document.documentElement.classList.add('dark');
        }
      } catch (e) {
      }
    }
  }, []);

  return <>{children}</>;
};

