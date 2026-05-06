import { Outlet, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { 
  LayoutDashboard, 
  Receipt, 
  Upload, 
  FolderTree, 
  FileText, 
  Settings,
  Bell,
  User,
  LogOut,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import SettingsDropdown from './SettingsDropdown';
import { useLanguage } from '../hooks/useLanguage';
import { useSettingsStore } from '../store/settingsStore';
import { formatCurrency } from '../utils/currency';

const Layout = () => {
  const location = useLocation();
  const { t } = useTranslation();
  useLanguage();
  const { currency, sidebarCollapsed, toggleSidebar } = useSettingsStore();

  const navigation = [
    { name: t('nav.dashboard'), path: '/dashboard', icon: LayoutDashboard, key: 'dashboard' },
    { name: t('nav.transactions'), path: '/transactions', icon: Receipt, key: 'transactions' },
    { name: t('nav.upload'), path: '/import', icon: Upload, key: 'upload' },
    { name: t('nav.categories'), path: '/categories', icon: FolderTree, key: 'categories' },
    { name: t('nav.reports'), path: '/reports', icon: FileText, key: 'reports' },
    { name: t('nav.settings'), path: '/settings', icon: Settings, key: 'settings' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      <aside className="hidden lg:flex w-56 xl:w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 xl:p-6 border-b border-gray-200 dark:border-gray-700">
          <Link to="/dashboard" className="block hover:opacity-80 transition-opacity">
            <h1 className="text-xl xl:text-2xl font-bold text-gray-900 dark:text-white">{t('common.appName')}</h1>
          </Link>
          <p className="text-xs xl:text-sm text-gray-500 dark:text-gray-400 mt-1">{t('common.personalFinance')}</p>
        </div>
        
        <nav className="flex-1 p-3 xl:p-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 xl:px-4 py-2 xl:py-3 rounded-xl text-xs xl:text-sm font-medium transition-all duration-200 ${
                  isActive(item.path)
                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4 xl:w-5 xl:h-5 mr-2 xl:mr-3" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-3 xl:p-4 border-t border-gray-200 dark:border-gray-700">
          <Link
            to="/settings"
            className="flex items-center px-3 xl:px-4 py-2 xl:py-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <User className="w-4 h-4 xl:w-5 xl:h-5 mr-2 xl:mr-3 text-gray-600 dark:text-gray-300" />
            <div className="flex-1 min-w-0">
              <p className="text-xs xl:text-sm font-medium text-gray-900 dark:text-white truncate">John Doe</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">john@example.com</p>
            </div>
          </Link>
          <button className="flex items-center px-3 xl:px-4 py-2 xl:py-3 rounded-xl text-xs xl:text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 w-full mt-2 transition-colors">
            <LogOut className="w-4 h-4 xl:w-5 xl:h-5 mr-2 xl:mr-3" />
            {t('nav.logout')}
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden lg:ml-0 min-w-0">
        <div className="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-2 xs:px-3 sm:px-4 py-1.5 xs:py-2 sm:py-3 flex items-center justify-between">
          <Link to="/dashboard" className="hover:opacity-80 transition-opacity min-w-0 flex-1">
            <h1 className="text-base xs:text-lg sm:text-xl font-bold text-gray-900 dark:text-white truncate">{t('common.appName')}</h1>
          </Link>
          <div className="flex items-center gap-1 xs:gap-2">
            <button className="p-1.5 xs:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <Bell className="w-4 h-4 xs:w-5 xs:h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <SettingsDropdown />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </main>

      <aside className={`${sidebarCollapsed ? 'w-0' : 'w-64 xl:w-80'} bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col hidden xl:flex transition-all duration-300 overflow-visible relative`}>
        <button
          onClick={toggleSidebar}
          className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 z-10 w-10 h-10 flex items-center justify-center bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-full hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-primary-500 dark:hover:border-primary-400 transition-all shadow-md hover:shadow-lg"
        >
          {sidebarCollapsed ? (
            <ChevronLeft className="w-5 h-5 text-gray-700 dark:text-gray-200" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-700 dark:text-gray-200" />
          )}
        </button>
        {!sidebarCollapsed && (
          <>
            <div className="p-4 xl:p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-base xl:text-lg font-semibold text-gray-900 dark:text-white">{t('summary.title')}</h2>
                <Bell className="w-4 h-4 xl:w-5 xl:h-5 text-gray-400 dark:text-gray-500" />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 xl:p-6 space-y-4 xl:space-y-6">
              <div className="space-y-3 xl:space-y-4">
                <div className="card p-4 xl:p-6">
                  <p className="text-xs xl:text-sm text-gray-500 dark:text-gray-400 mb-1">{t('summary.totalBalance')}</p>
                  <p className="text-2xl xl:text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(12450, currency)}</p>
                  <p className="text-xs text-green-500 dark:text-green-400 mt-1 xl:mt-2">+{formatCurrency(1200, currency)} this month</p>
                </div>

                <div className="grid grid-cols-2 gap-3 xl:gap-4">
                  <div className="card p-3 xl:p-4">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('summary.income')}</p>
                    <p className="text-lg xl:text-xl font-semibold text-green-600 dark:text-green-400">{formatCurrency(5000, currency)}</p>
                  </div>
                  <div className="card p-3 xl:p-4">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('summary.expenses')}</p>
                    <p className="text-lg xl:text-xl font-semibold text-red-600 dark:text-red-400">{formatCurrency(3800, currency)}</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xs xl:text-sm font-semibold text-gray-900 dark:text-white mb-3 xl:mb-4">{t('summary.recentActivity')}</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-300">{t('summary.receiptUploaded')}</p>
                    <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">Starbucks - $25.50</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">2 {t('summary.hoursAgo')}</p>
                  </div>
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800">
                    <p className="text-sm font-medium text-green-900 dark:text-green-300">{t('summary.categorySuggested')}</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">"Food & Dining" for recent transactions</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">5 {t('summary.hoursAgo')}</p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </aside>
    </div>
  );
};

export default Layout;
