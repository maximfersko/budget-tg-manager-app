import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Download, MoreVertical } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';
import { formatCurrencyWithSign } from '../utils/currency';

const Transactions = () => {
  const { t } = useTranslation();
  const { currency } = useSettingsStore();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const transactions = [
    { id: 1, date: '2024-06-15', description: 'Starbucks Coffee', category: 'Dining', amount: -25.50, type: 'expense' },
    { id: 2, date: '2024-06-14', description: 'Salary', category: 'Income', amount: 5000.00, type: 'income' },
    { id: 3, date: '2024-06-14', description: 'Grocery Store', category: 'Groceries', amount: -120.00, type: 'expense' },
    { id: 4, date: '2024-06-13', description: 'Uber Ride', category: 'Transport', amount: -18.50, type: 'expense' },
    { id: 5, date: '2024-06-12', description: 'Amazon Purchase', category: 'Shopping', amount: -89.99, type: 'expense' },
    { id: 6, date: '2024-06-11', description: 'Electricity Bill', category: 'Bills', amount: -85.00, type: 'expense' },
  ];

  const filteredTransactions = transactions.filter(t => {
    const matchesSearch = t.description.toLowerCase().includes(search.toLowerCase()) ||
                         t.category.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || t.type === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="p-2 xs:p-3 sm:p-4 md:p-6 space-y-2 xs:space-y-3 sm:space-y-4 md:space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 xs:gap-3 sm:gap-4">
        <div>
          <h1 className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{t('transactions.title')}</h1>
          <p className="text-xs xs:text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-0.5 xs:mt-1">{t('transactions.subtitle')}</p>
        </div>
        <button className="btn-primary flex items-center justify-center text-xs xs:text-sm sm:text-base px-2.5 xs:px-3 sm:px-4 py-1.5 xs:py-2">
          <Download className="w-3.5 h-3.5 xs:w-4 xs:h-4 mr-1.5 xs:mr-2" />
          <span className="hidden xs:inline">{t('transactions.exportCsv')}</span>
          <span className="xs:hidden">Export</span>
        </button>
      </div>

      <div className="card dark:bg-gray-800 p-4 sm:p-6">
        <div className="flex flex-col md:flex-row gap-3 sm:gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t('transactions.search')}
              className="input pl-10"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'all' 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {t('transactions.all')}
            </button>
            <button
              onClick={() => setFilter('income')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'income' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {t('transactions.income')}
            </button>
            <button
              onClick={() => setFilter('expense')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === 'expense' 
                  ? 'bg-red-500 text-white' 
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {t('transactions.expenses')}
            </button>
          </div>
        </div>
      </div>

      <div className="card dark:bg-gray-800 overflow-hidden p-0">
        <div className="overflow-x-auto -mx-3 sm:mx-0">
          <table className="w-full min-w-[640px]">
            <thead className="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              <tr>
                <th className="px-3 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {t('transactions.date')}
                </th>
                <th className="px-3 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {t('transactions.description')}
                </th>
                <th className="px-3 sm:px-4 md:px-6 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hidden sm:table-cell">
                  {t('transactions.category')}
                </th>
                <th className="px-3 sm:px-4 md:px-6 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {t('transactions.amount')}
                </th>
                <th className="px-3 sm:px-4 md:px-6 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hidden md:table-cell">
                  {t('transactions.actions')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredTransactions.map((transaction) => (
                <tr key={transaction.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-3 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-gray-900 dark:text-gray-100">
                    {new Date(transaction.date).toLocaleDateString()}
                  </td>
                  <td className="px-3 sm:px-4 md:px-6 py-3 sm:py-4 text-xs sm:text-sm font-medium text-gray-900 dark:text-gray-100 max-w-[150px] sm:max-w-none truncate sm:whitespace-nowrap">
                    {transaction.description}
                  </td>
                  <td className="px-3 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap hidden sm:table-cell">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                      {transaction.category}
                    </span>
                  </td>
                  <td className={`px-3 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-xs sm:text-sm text-right font-medium ${
                    transaction.type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    {formatCurrencyWithSign(Math.abs(transaction.amount), currency, transaction.type === 'income')}
                  </td>
                  <td className="px-3 sm:px-4 md:px-6 py-3 sm:py-4 whitespace-nowrap text-right text-xs sm:text-sm hidden md:table-cell">
                    <button className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Transactions;
