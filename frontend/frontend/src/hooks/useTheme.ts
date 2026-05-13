import { useEffect } from 'react';
import { useSettingsStore } from '../store/settingsStore';

export const useTheme = () => {
  const { theme, setTheme } = useSettingsStore();

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  return { theme, setTheme };
};

