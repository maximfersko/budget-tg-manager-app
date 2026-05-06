import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { User, Bell, Download, Moon, Sun, MessageCircle, Save, Globe, DollarSign } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';
import { useLanguage } from '../hooks/useLanguage';
import type { Language, Currency } from '../types';

const Settings = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { theme, setTheme, currency, setCurrency } = useSettingsStore();
  const { language, setLanguage } = useLanguage();
  const [telegramConnected, setTelegramConnected] = useState(false);

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
    <div className="p-2 xs:p-3 sm:p-4 md:p-6 space-y-3 xs:space-y-4 sm:space-y-5 md:space-y-6 animate-fade-in max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{t('settings.title')}</h1>
        <p className="text-xs xs:text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-0.5 xs:mt-1">{t('settings.subtitle')}</p>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex items-center space-x-3 mb-4 sm:mb-6">
          <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.profile')}</h2>
        </div>
        <div className="space-y-3 sm:space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('settings.fullName')}
            </label>
            <input
              type="text"
              defaultValue="John Doe"
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('settings.email')}
            </label>
            <input
              type="email"
              defaultValue="john@example.com"
              className="input"
            />
          </div>
          <button className="btn-primary flex items-center">
            <Save className="w-4 h-4 mr-2" />
            {t('settings.saveChanges')}
          </button>
        </div>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex items-center space-x-3 mb-3 sm:mb-4">
          <Globe className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.language')}</h2>
        </div>
        <div className="space-y-2">
          {languages.map((lang) => (
            <button
              key={lang.value}
              onClick={() => setLanguage(lang.value)}
              className={`w-full flex items-center px-4 py-3 rounded-lg text-sm transition-all ${
                language === lang.value
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 border-2 border-primary-500'
                  : 'bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 border-2 border-transparent hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex items-center space-x-3 mb-3 sm:mb-4">
          <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.currency')}</h2>
        </div>
        <div className="grid grid-cols-3 gap-2 sm:gap-3">
          {currencies.map((curr) => (
            <button
              key={curr.value}
              onClick={() => setCurrency(curr.value)}
              className={`flex flex-col items-center justify-center px-4 py-4 rounded-lg text-sm border-2 transition-all ${
                currency === curr.value
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 border-primary-500'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <span className="text-2xl font-bold mb-1">{curr.symbol}</span>
              <span className="text-xs">{curr.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0 mb-3 sm:mb-4">
          <div className="flex items-center space-x-3">
            {theme === 'dark' ? (
              <Moon className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <Sun className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
            )}
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.theme')}</h2>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setTheme('light')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                theme === 'light'
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <Sun className="w-4 h-4 inline-block mr-2" />
              Light
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                theme === 'dark'
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <Moon className="w-4 h-4 inline-block mr-2" />
              Dark
            </button>
          </div>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {t('settings.themeDescription')}
        </p>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0 mb-4 sm:mb-6">
          <div className="flex items-center space-x-3">
            <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.categories')}</h2>
          </div>
          <button onClick={() => navigate('/categories')} className="btn-secondary text-sm sm:text-base">{t('settings.manageCategories')}</button>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {t('settings.categoriesDescription')}
        </p>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex items-center space-x-3 mb-3 sm:mb-4">
          <Download className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.exportData')}</h2>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {t('settings.exportDescription')}
        </p>
        <button className="btn-secondary flex items-center">
          <Download className="w-4 h-4 mr-2" />
          {t('settings.exportCsv')}
        </button>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0 mb-3 sm:mb-4">
          <div className="flex items-center space-x-3">
            <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.telegram')}</h2>
          </div>
          {telegramConnected ? (
            <span className="px-3 py-1 text-sm font-medium text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-900/20 rounded-full">
              {t('settings.connected')}
            </span>
          ) : (
            <button 
              onClick={() => setTelegramConnected(true)}
              className="btn-primary"
            >
              {t('settings.connect')}
            </button>
          )}
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {t('settings.telegramDescription')}
        </p>
        {telegramConnected && (
          <button 
            onClick={() => setTelegramConnected(false)}
            className="btn-secondary text-red-600 dark:text-red-400 border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            {t('settings.disconnect')}
          </button>
        )}
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div className="flex items-center space-x-3 mb-3 sm:mb-4">
          <Bell className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{t('settings.notifications')}</h2>
        </div>
        <div className="space-y-3">
          <label className="flex items-center">
            <input type="checkbox" defaultChecked className="rounded border-gray-300 dark:border-gray-600 text-primary-500 focus:ring-primary-500 dark:bg-gray-700" />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{t('settings.emailNotifications')}</span>
          </label>
          <label className="flex items-center">
            <input type="checkbox" defaultChecked className="rounded border-gray-300 dark:border-gray-600 text-primary-500 focus:ring-primary-500 dark:bg-gray-700" />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{t('settings.pushNotifications')}</span>
          </label>
          <label className="flex items-center">
            <input type="checkbox" className="rounded border-gray-300 dark:border-gray-600 text-primary-500 focus:ring-primary-500 dark:bg-gray-700" />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{t('settings.weeklySummary')}</span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default Settings;
