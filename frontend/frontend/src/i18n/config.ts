import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from './locales/en.json';
import ruTranslations from './locales/ru.json';

const getStoredLanguage = (): string => {
  try {
    const stored = localStorage.getItem('cash-manager-settings');
    if (stored) {
      const parsed = JSON.parse(stored);
      return parsed.state?.language || 'ru';
    }
  } catch (e) {
  }
  return 'ru';
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslations,
      },
      ru: {
        translation: ruTranslations,
      },
    },
    lng: getStoredLanguage(),
    fallbackLng: 'ru',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;

