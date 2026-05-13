import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Language, Theme, Currency } from '../types';

interface SettingsState {
  language: Language;
  theme: Theme;
  currency: Currency;
  sidebarCollapsed: boolean;
  setLanguage: (language: Language) => void;
  setTheme: (theme: Theme) => void;
  setCurrency: (currency: Currency) => void;
  toggleSidebar: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      language: 'ru',
      theme: 'light',
      currency: 'USD',
      sidebarCollapsed: false,
      setLanguage: (language) => {
        set({ language });
      },
      setTheme: (theme) => {
        set({ theme });
      },
      setCurrency: (currency) => set({ currency }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    {
      name: 'cash-manager-settings',
    }
  )
);

