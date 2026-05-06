import { useTranslation } from 'react-i18next';
import { Download, Calendar, FileText } from 'lucide-react';

const Reports = () => {
  const { t } = useTranslation();
  const reports = [
    { id: 1, name: 'Monthly Report - June 2024', date: '2024-06-30', type: 'Monthly' },
    { id: 2, name: 'Quarterly Report - Q2 2024', date: '2024-06-30', type: 'Quarterly' },
    { id: 3, name: 'Annual Report - 2024', date: '2024-12-31', type: 'Annual' },
  ];

  return (
    <div className="p-2 xs:p-3 sm:p-4 md:p-6 space-y-3 xs:space-y-4 sm:space-y-5 md:space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 xs:gap-3 sm:gap-4">
        <div>
          <h1 className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{t('reports.title')}</h1>
          <p className="text-xs xs:text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-0.5 xs:mt-1">{t('reports.subtitle')}</p>
        </div>
        <button className="btn-primary flex items-center justify-center text-xs xs:text-sm sm:text-base px-2.5 xs:px-3 sm:px-4 py-1.5 xs:py-2">
          <FileText className="w-3.5 h-3.5 xs:w-4 xs:h-4 mr-1.5 xs:mr-2" />
          {t('reports.createReport')}
        </button>
      </div>

      <div className="grid grid-cols-1 xs:grid-cols-2 lg:grid-cols-3 gap-3 xs:gap-4 sm:gap-5 md:gap-6">
        {reports.map((report) => (
          <div key={report.id} className="card p-3 xs:p-4 sm:p-6 hover:shadow-soft-lg transition-all group">
            <div className="flex items-start justify-between mb-2 xs:mb-3 sm:mb-4">
              <div className="w-9 h-9 xs:w-10 xs:h-10 sm:w-12 sm:h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg sm:rounded-xl flex items-center justify-center flex-shrink-0">
                <FileText className="w-4 h-4 xs:w-5 xs:h-5 sm:w-6 sm:h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <span className="px-1.5 xs:px-2 py-0.5 xs:py-1 text-[10px] xs:text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 ml-2">
                {report.type}
              </span>
            </div>
            <h3 className="text-xs xs:text-sm sm:text-base font-semibold text-gray-900 dark:text-white mb-1.5 xs:mb-2 line-clamp-2">{report.name}</h3>
            <div className="flex items-center text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-2 xs:mb-3 sm:mb-4">
              <Calendar className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 mr-1.5 xs:mr-2 flex-shrink-0" />
              {new Date(report.date).toLocaleDateString()}
            </div>
            <button className="btn-secondary w-full flex items-center justify-center text-[10px] xs:text-xs sm:text-sm opacity-0 group-hover:opacity-100 transition-opacity py-1.5 xs:py-2">
              <Download className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 mr-1.5 xs:mr-2" />
              {t('reports.download')}
            </button>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xs:grid-cols-3 gap-3 xs:gap-4 sm:gap-5 md:gap-6">
        <div className="card p-3 xs:p-4 sm:p-6">
          <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1.5 xs:mb-2">{t('reports.totalReports')}</p>
          <p className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">12</p>
        </div>
        <div className="card p-3 xs:p-4 sm:p-6">
          <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1.5 xs:mb-2">{t('reports.thisMonth')}</p>
          <p className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">3</p>
        </div>
        <div className="card p-3 xs:p-4 sm:p-6">
          <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1.5 xs:mb-2">{t('reports.lastExport')}</p>
          <p className="text-base xs:text-lg sm:text-lg font-semibold text-gray-900 dark:text-white">2 {t('reports.daysAgo')}</p>
        </div>
      </div>
    </div>
  );
};

export default Reports;
