import { 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useSettingsStore } from '../store/settingsStore';
import { formatCurrency } from '../utils/currency';

const Dashboard = () => {
  const { t } = useTranslation();
  const { currency } = useSettingsStore();
  
  const balanceData = [
    { month: 'Jan', balance: 8500 },
    { month: 'Feb', balance: 9200 },
    { month: 'Mar', balance: 8800 },
    { month: 'Apr', balance: 10200 },
    { month: 'May', balance: 11000 },
    { month: 'Jun', balance: 12450 },
  ];

  const categoryData = [
    { name: 'Groceries', value: 450, color: '#3b82f6' },
    { name: 'Transport', value: 320, color: '#10b981' },
    { name: 'Dining', value: 280, color: '#f59e0b' },
    { name: 'Shopping', value: 220, color: '#ef4444' },
    { name: 'Bills', value: 180, color: '#8b5cf6' },
    { name: 'Other', value: 150, color: '#6b7280' },
  ];

  const spendingData = [
    { category: 'Groceries', amount: 450 },
    { category: 'Transport', amount: 320 },
    { category: 'Dining', amount: 280 },
    { category: 'Shopping', amount: 220 },
    { category: 'Bills', amount: 180 },
  ];

  const COLORS = categoryData.map(item => item.color);

  return (
    <div className="p-2 xs:p-3 sm:p-4 md:p-6 space-y-1.5 xs:space-y-2 sm:space-y-3 md:space-y-4 animate-fade-in">
      <div className="mb-1 xs:mb-1.5 sm:mb-2">
        <h1 className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{t('dashboard.title')}</h1>
        <p className="text-xs xs:text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-0.5 xs:mt-1">{t('dashboard.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 xs:grid-cols-2 lg:grid-cols-3 gap-1.5 xs:gap-2 sm:gap-3 md:gap-4">
        <div className="card p-2.5 xs:p-3 sm:p-4 md:p-5">
          <div className="flex items-center justify-between mb-1 xs:mb-1.5 sm:mb-2">
            <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400">{t('dashboard.totalBalance')}</p>
            <DollarSign className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 md:w-5 md:h-5 text-gray-400 dark:text-gray-500 flex-shrink-0" />
          </div>
          <p className="text-base xs:text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white break-words leading-tight">{formatCurrency(12450, currency)}</p>
          <div className="flex items-center mt-0.5 xs:mt-1 sm:mt-1.5">
            <TrendingUp className="w-2.5 h-2.5 xs:w-3 xs:h-3 sm:w-3.5 sm:h-3.5 text-green-500 dark:text-green-400 mr-0.5 xs:mr-1 flex-shrink-0" />
            <span className="text-[9px] xs:text-[10px] sm:text-xs text-green-600 dark:text-green-400 leading-tight">+12.5% {t('dashboard.fromLastMonth')}</span>
          </div>
        </div>

        <div className="card p-2.5 xs:p-3 sm:p-4 md:p-5">
          <div className="flex items-center justify-between mb-1 xs:mb-1.5 sm:mb-2">
            <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400">{t('dashboard.monthlyIncome')}</p>
            <TrendingUp className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 md:w-5 md:h-5 text-green-400 dark:text-green-500 flex-shrink-0" />
          </div>
          <p className="text-base xs:text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-green-600 dark:text-green-400 break-words leading-tight">{formatCurrency(5000, currency)}</p>
          <p className="text-[9px] xs:text-[10px] sm:text-xs text-gray-500 dark:text-gray-400 mt-0.5 xs:mt-1 sm:mt-1.5 leading-tight">{t('dashboard.expectedThisMonth')}</p>
        </div>

        <div className="card p-2.5 xs:p-3 sm:p-4 md:p-5">
          <div className="flex items-center justify-between mb-1 xs:mb-1.5 sm:mb-2">
            <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400">{t('dashboard.monthlyExpenses')}</p>
            <TrendingDown className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 md:w-5 md:h-5 text-red-400 dark:text-red-500 flex-shrink-0" />
          </div>
          <p className="text-base xs:text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-red-600 dark:text-red-400 break-words leading-tight">{formatCurrency(3800, currency)}</p>
          <p className="text-[9px] xs:text-[10px] sm:text-xs text-gray-500 dark:text-gray-400 mt-0.5 xs:mt-1 sm:mt-1.5 leading-tight">-5.2% {t('dashboard.fromLastMonth')}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-1.5 xs:gap-2 sm:gap-3 md:gap-4">
        <div className="card p-2.5 xs:p-3 sm:p-4 md:p-5">
          <h2 className="text-xs xs:text-sm sm:text-base md:text-lg font-semibold text-gray-900 dark:text-white mb-1.5 xs:mb-2 sm:mb-3">{t('dashboard.balanceOverTime')}</h2>
          <div 
            className="h-[120px] xs:h-[140px] sm:h-[160px] md:h-[180px] lg:h-[220px] xl:h-[260px] select-none"
            onMouseDown={(e) => e.preventDefault()}
            style={{ userSelect: 'none', WebkitUserSelect: 'none', MozUserSelect: 'none', msUserSelect: 'none' }}
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={balanceData} style={{ userSelect: 'none', outline: 'none' }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" stroke="#9ca3af" tick={{ fontSize: 10 }} />
                <YAxis stroke="#9ca3af" tick={{ fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '8px',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                  }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="balance" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-2.5 xs:p-3 sm:p-4 md:p-5">
          <h2 className="text-xs xs:text-sm sm:text-base md:text-lg font-semibold text-gray-900 dark:text-white mb-1.5 xs:mb-2 sm:mb-3">{t('dashboard.expenseCategories')}</h2>
          <div 
            className="h-[120px] xs:h-[140px] sm:h-[160px] md:h-[180px] lg:h-[220px] xl:h-[260px] select-none"
            onMouseDown={(e) => e.preventDefault()}
            style={{ userSelect: 'none', WebkitUserSelect: 'none', MozUserSelect: 'none', msUserSelect: 'none' }}
          >
            <ResponsiveContainer width="100%" height="100%">
            <PieChart style={{ userSelect: 'none', outline: 'none' }}>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(props: any) => {
                  const percent = props.percent as number;
                  return `${(percent * 100).toFixed(0)}%`;
                }}
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '8px',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card p-2.5 xs:p-3 sm:p-4 md:p-5">
        <h2 className="text-xs xs:text-sm sm:text-base md:text-lg font-semibold text-gray-900 dark:text-white mb-1.5 xs:mb-2 sm:mb-3">{t('dashboard.topSpendings')}</h2>
        <div 
          className="h-[120px] xs:h-[140px] sm:h-[160px] md:h-[180px] lg:h-[220px] xl:h-[260px] select-none"
          onMouseDown={(e) => e.preventDefault()}
          style={{ userSelect: 'none', WebkitUserSelect: 'none', MozUserSelect: 'none', msUserSelect: 'none' }}
        >
          <ResponsiveContainer width="100%" height="100%">
          <BarChart data={spendingData} style={{ userSelect: 'none', outline: 'none' }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="category" stroke="#9ca3af" tick={{ fontSize: 13 }} angle={-45} textAnchor="end" height={50} />
            <YAxis stroke="#9ca3af" tick={{ fontSize: 10 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb', 
                borderRadius: '8px',
                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
              }} 
            />
            <Bar dataKey="amount" fill="#3b82f6" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
