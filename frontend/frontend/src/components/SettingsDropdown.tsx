import { useState } from 'react';
import { Settings, Moon, Sun, Globe, DollarSign, X } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';
import { useLanguage } from '../hooks/useLanguage';
import { useTranslation } from 'react-i18next';
import type { Language, Currency } from '../types';

const SettingsDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { theme, setTheme, currency, setCurrency } = useSettingsStore();
  const { language, setLanguage } = useLanguage();
  const { t } = useTranslation();

  const languages: { value: Language; label: string }[] = [
    { value: 'ru', label: 'Русский' },
    { value: 'en', label: 'English' },
  ];

  const currencies: { value: Currency; label: string; symbol: string }[] = [
    { value: 'USD', label: 'USD', symbol: '$' },
    { value: 'RUB', label: 'RUB', symbol: '₽' },
    { value: 'EUR', label: 'EUR', symbol: '€' },
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-1.5 xs:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
      >
        <Settings className="w-4 h-4 xs:w-5 xs:h-5 text-gray-600 dark:text-gray-300" />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-1.5 xs:mt-2 w-56 xs:w-64 bg-white dark:bg-gray-800 rounded-lg xs:rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 z-20 p-3 xs:p-4 space-y-3 xs:space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm xs:text-base font-semibold text-gray-900 dark:text-white">{t('settings.title')}</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <X className="w-3.5 h-3.5 xs:w-4 xs:h-4 text-gray-500" />
              </button>
            </div>

            <div>
              <label className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5 xs:mb-2">
                {t('settings.theme')}
              </label>
              <div className="flex gap-1.5 xs:gap-2">
                <button
                  onClick={() => setTheme('light')}
                  className={`flex-1 flex items-center justify-center px-2 xs:px-3 py-1.5 xs:py-2 rounded-lg border transition-all text-xs xs:text-sm ${
                    theme === 'light'
                      ? 'bg-primary-500 text-white border-primary-500'
                      : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
                  }`}
                >
                  <Sun className="w-3.5 h-3.5 xs:w-4 xs:h-4 mr-1 xs:mr-2" />
                  Light
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`flex-1 flex items-center justify-center px-2 xs:px-3 py-1.5 xs:py-2 rounded-lg border transition-all text-xs xs:text-sm ${
                    theme === 'dark'
                      ? 'bg-primary-500 text-white border-primary-500'
                      : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
                  }`}
                >
                  <Moon className="w-3.5 h-3.5 xs:w-4 xs:h-4 mr-1 xs:mr-2" />
                  Dark
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5 xs:mb-2">
                {t('settings.language')}
              </label>
              <div className="space-y-1">
                {languages.map((lang) => (
                  <button
                    key={lang.value}
                    onClick={() => setLanguage(lang.value)}
                    className={`w-full flex items-center px-2.5 xs:px-3 py-1.5 xs:py-2 rounded-lg text-xs xs:text-sm transition-all ${
                      language === lang.value
                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Globe className="w-3.5 h-3.5 xs:w-4 xs:h-4 mr-1.5 xs:mr-2" />
                    {lang.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5 xs:mb-2">
                {t('settings.currency')}
              </label>
              <div className="grid grid-cols-3 gap-1.5 xs:gap-2">
                {currencies.map((curr) => (
                  <button
                    key={curr.value}
                    onClick={() => setCurrency(curr.value)}
                    className={`flex flex-col items-center justify-center px-2 xs:px-3 py-1.5 xs:py-2 rounded-lg text-[10px] xs:text-xs sm:text-sm border transition-all ${
                      currency === curr.value
                        ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 border-primary-500'
                        : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
                    }`}
                  >
                    <DollarSign className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 mb-0.5 xs:mb-1" />
                    {curr.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default SettingsDropdown;

