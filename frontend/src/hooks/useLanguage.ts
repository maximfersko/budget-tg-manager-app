import { useEffect } from 'react';
import { useSettingsStore } from '../store/settingsStore';
import i18n from '../i18n/config';

export const useLanguage = () => {
  const { language, setLanguage } = useSettingsStore();

  useEffect(() => {
    if (i18n.language !== language) {
      i18n.changeLanguage(language);
    }
  }, [language]);

  return { language, setLanguage };
};

