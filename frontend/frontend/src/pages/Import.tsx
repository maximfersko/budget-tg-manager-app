import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, X, FileText, Image as ImageIcon, File } from 'lucide-react';

const Import = () => {
  const { t } = useTranslation();
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles([...files, ...droppedFiles]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles([...files, ...selectedFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <ImageIcon className="w-6 h-6 xs:w-7 xs:h-7 sm:w-8 sm:h-8 text-blue-500" />;
    if (file.type === 'application/pdf') return <FileText className="w-6 h-6 xs:w-7 xs:h-7 sm:w-8 sm:h-8 text-red-500" />;
    return <File className="w-6 h-6 xs:w-7 xs:h-7 sm:w-8 sm:h-8 text-gray-500" />;
  };

  return (
    <div className="p-2 xs:p-3 sm:p-4 md:p-6 space-y-3 xs:space-y-4 sm:space-y-5 md:space-y-6 animate-fade-in">
      <div>
        <h1 className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{t('upload.title')}</h1>
        <p className="text-xs xs:text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-0.5 xs:mt-1">{t('upload.subtitle')}</p>
      </div>

      <div className="card p-3 xs:p-4 sm:p-6">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg xs:rounded-xl sm:rounded-2xl p-4 xs:p-5 sm:p-6 md:p-8 lg:p-12 text-center transition-all ${
            isDragging 
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
              : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500 hover:bg-gray-50 dark:hover:bg-gray-700/50'
          }`}
        >
          <Upload className="w-10 h-10 xs:w-12 xs:h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 text-gray-400 dark:text-gray-500 mx-auto mb-2 xs:mb-3 sm:mb-4" />
          <h3 className="text-sm xs:text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-1.5 xs:mb-2">
            {t('upload.dropFiles')}
          </h3>
          <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-2.5 xs:mb-3 sm:mb-4 px-2">
            {t('upload.supportFormats')}
          </p>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-primary"
          >
            {t('upload.selectFiles')}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.heic"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      </div>

      {files.length > 0 && (
        <div className="card p-3 xs:p-4 sm:p-6">
          <h2 className="text-sm xs:text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2 xs:mb-3 sm:mb-4">{t('upload.selectedFiles')}</h2>
          <div className="space-y-2 sm:space-y-3">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2.5 xs:p-3 sm:p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors animate-slide-up"
              >
                <div className="flex items-center space-x-2 xs:space-x-3 sm:space-x-4 min-w-0 flex-1">
                  <div className="flex-shrink-0">{getFileIcon(file)}</div>
                  <div className="min-w-0 flex-1">
                    <p className="text-[11px] xs:text-xs sm:text-sm font-medium text-gray-900 dark:text-white truncate">{file.name}</p>
                    <p className="text-[10px] xs:text-xs text-gray-500 dark:text-gray-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 transition-colors flex-shrink-0 ml-1.5 xs:ml-2"
                >
                  <X className="w-3.5 h-3.5 xs:w-4 xs:h-4 sm:w-5 sm:h-5" />
                </button>
              </div>
            ))}
          </div>
          <button className="btn-primary w-full mt-2.5 xs:mt-3 sm:mt-4 text-xs xs:text-sm sm:text-base py-2 xs:py-2.5">
            {t('upload.uploadAndProcess')}
          </button>
        </div>
      )}

      <div className="card p-3 xs:p-4 sm:p-6">
        <h2 className="text-sm xs:text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-2 xs:mb-3 sm:mb-4">{t('upload.recentUploads')}</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">receipt_001.pdf</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{t('upload.processed')} • 2 {t('summary.hoursAgo')}</p>
              </div>
            </div>
            <span className="px-2 py-1 text-xs font-medium text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-900/30 rounded-full">
              {t('upload.processed')}
            </span>
          </div>
          <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <ImageIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">screenshot_001.jpg</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{t('upload.processing')} • 5 {t('summary.hoursAgo')}</p>
              </div>
            </div>
            <span className="px-2 py-1 text-xs font-medium text-blue-700 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30 rounded-full">
              {t('upload.processing')}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Import;
