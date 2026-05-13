import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Plus, Edit, Trash2, ShoppingBag, Car, Utensils, ShoppingCart, Receipt, X, Save, Home, Coffee, Film, Gamepad2, Heart, Laptop, Music, Plane, Book, Pill } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';
import { formatCurrency } from '../utils/currency';

interface Category {
  id: number;
  name: string;
  icon: any;
  color: string;
  budget: number;
  spent: number;
}

const iconOptions = [
  ShoppingBag, Car, Utensils, ShoppingCart, Receipt, Home, Coffee, Film, Gamepad2, Heart, Laptop, Music, Plane, Book, Pill
];

const colorOptions = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
];

const Categories = () => {
  const { t } = useTranslation();
  const { currency } = useSettingsStore();
  const [categories, setCategories] = useState<Category[]>([
    { id: 1, name: 'Groceries', icon: ShoppingBag, color: '#3b82f6', budget: 500, spent: 450 },
    { id: 2, name: 'Transport', icon: Car, color: '#10b981', budget: 400, spent: 320 },
    { id: 3, name: 'Dining', icon: Utensils, color: '#f59e0b', budget: 300, spent: 280 },
    { id: 4, name: 'Shopping', icon: ShoppingCart, color: '#ef4444', budget: 250, spent: 220 },
    { id: 5, name: 'Bills', icon: Receipt, color: '#8b5cf6', budget: 200, spent: 180 },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    icon: ShoppingBag,
    color: '#3b82f6',
    budget: 0,
  });

  const openAddModal = () => {
    setEditingCategory(null);
    setFormData({ name: '', icon: ShoppingBag, color: '#3b82f6', budget: 0 });
    setIsModalOpen(true);
  };

  const openEditModal = (category: Category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      icon: category.icon,
      color: category.color,
      budget: category.budget,
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingCategory(null);
  };

  const handleSave = () => {
    if (!formData.name.trim()) return;

    if (editingCategory) {
      setCategories(categories.map(cat =>
        cat.id === editingCategory.id
          ? { ...cat, ...formData, spent: editingCategory.spent }
          : cat
      ));
    } else {
      const newCategory: Category = {
        id: Date.now(),
        ...formData,
        spent: 0,
      };
      setCategories([...categories, newCategory]);
    }
    closeModal();
  };

  const handleDelete = (id: number) => {
    if (window.confirm(t('categories.deleteConfirm'))) {
      setCategories(categories.filter(cat => cat.id !== id));
    }
  };

  const SelectedIcon = formData.icon;

  return (
    <div className="p-2 xs:p-3 sm:p-4 md:p-6 space-y-3 xs:space-y-4 sm:space-y-5 md:space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 xs:gap-3 sm:gap-4">
        <div>
          <h1 className="text-xl xs:text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{t('categories.title')}</h1>
          <p className="text-xs xs:text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-0.5 xs:mt-1">{t('categories.subtitle')}</p>
        </div>
        <button onClick={openAddModal} className="btn-primary flex items-center justify-center text-xs xs:text-sm sm:text-base px-2.5 xs:px-3 sm:px-4 py-1.5 xs:py-2">
          <Plus className="w-3.5 h-3.5 xs:w-4 xs:h-4 mr-1.5 xs:mr-2" />
          {t('categories.addCategory')}
        </button>
      </div>

      <div className="grid grid-cols-1 xs:grid-cols-2 lg:grid-cols-3 gap-3 xs:gap-4 sm:gap-5 md:gap-6">
        {categories.map((category) => {
          const Icon = category.icon;
          const percentage = (category.spent / category.budget) * 100;

          return (
            <div key={category.id} className="card p-3 xs:p-4 sm:p-6 group hover:shadow-soft-lg transition-all">
              <div className="flex items-center justify-between mb-2 xs:mb-3 sm:mb-4">
                <div className="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
                  <div
                    className="w-9 h-9 xs:w-10 xs:h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: `${category.color}20` }}
                  >
                    <Icon className="w-4 h-4 xs:w-5 xs:h-5 sm:w-6 sm:h-6" style={{ color: category.color }} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-xs xs:text-sm sm:text-base font-semibold text-gray-900 dark:text-white truncate">{category.name}</h3>
                    <p className="text-[10px] xs:text-xs sm:text-sm text-gray-500 dark:text-gray-400 truncate">{formatCurrency(category.spent, currency)} / {formatCurrency(category.budget, currency)}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1 sm:space-x-2 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                  <button onClick={() => openEditModal(category)} className="p-1 xs:p-1.5 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                    <Edit className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 text-gray-600 dark:text-gray-300" />
                  </button>
                  <button onClick={() => handleDelete(category.id)} className="p-1 xs:p-1.5 sm:p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors">
                    <Trash2 className="w-3 h-3 xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4 text-red-600 dark:text-red-400" />
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">{t('categories.progress')}</span>
                  <span className="font-medium text-gray-900 dark:text-white">{percentage.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${Math.min(percentage, 100)}%`,
                      backgroundColor: category.color
                    }}
                  />
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {formatCurrency(category.budget - category.spent, currency)} {t('categories.remaining')}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 xs:p-3 sm:p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg xs:rounded-xl shadow-xl max-w-2xl w-full max-h-[95vh] xs:max-h-[90vh] overflow-y-auto">
            <div className="p-3 xs:p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-base xs:text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">
                  {editingCategory ? t('categories.editCategory') : t('categories.addCategory')}
                </h2>
                <button onClick={closeModal} className="p-1.5 xs:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                  <X className="w-3.5 h-3.5 xs:w-4 xs:h-4 sm:w-5 sm:h-5 text-gray-600 dark:text-gray-300" />
                </button>
              </div>
            </div>

            <div className="p-3 xs:p-4 sm:p-6 space-y-3 xs:space-y-4 sm:space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('categories.categoryName')}
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input"
                  placeholder={t('categories.categoryNamePlaceholder')}
                />
              </div>

              <div>
                <label className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 sm:mb-3">
                  {t('categories.icon')}
                </label>
                <div className="grid grid-cols-5 xs:grid-cols-6 sm:grid-cols-8 gap-1.5 xs:gap-2 sm:gap-3">
                  {iconOptions.map((IconComponent, index) => (
                    <button
                      key={index}
                      onClick={() => setFormData({ ...formData, icon: IconComponent })}
                      className={`p-1.5 xs:p-2 sm:p-3 rounded-lg border-2 transition-all ${
                        formData.icon === IconComponent
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <IconComponent className={`w-3.5 h-3.5 xs:w-4 xs:h-4 sm:w-5 sm:h-5 ${formData.icon === IconComponent ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-400'}`} />
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 sm:mb-3">
                  {t('categories.color')}
                </label>
                <div className="flex flex-wrap gap-1.5 xs:gap-2 sm:gap-3">
                  {colorOptions.map((color) => (
                    <button
                      key={color}
                      onClick={() => setFormData({ ...formData, color })}
                      className={`w-7 h-7 xs:w-8 xs:h-8 sm:w-10 sm:h-10 rounded-full border-2 transition-all ${
                        formData.color === color
                          ? 'border-gray-900 dark:border-white scale-110'
                          : 'border-gray-300 dark:border-gray-600 hover:scale-105'
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('categories.budgetLimit')}
                </label>
                <input
                  type="number"
                  value={formData.budget || ''}
                  onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) || 0 })}
                  className="input"
                  placeholder="0"
                  min="0"
                  step="0.01"
                />
              </div>

              <div className="flex items-center gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg flex-1">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${formData.color}20` }}
                  >
                    <SelectedIcon className="w-5 h-5" style={{ color: formData.color }} />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-white">{formData.name || t('categories.categoryNamePlaceholder')}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{formatCurrency(formData.budget, currency)}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-3 xs:p-4 sm:p-6 border-t border-gray-200 dark:border-gray-700 flex flex-col sm:flex-row justify-end gap-2 sm:gap-3">
              <button onClick={closeModal} className="btn-secondary text-xs xs:text-sm sm:text-base order-2 sm:order-1 py-2 xs:py-2.5">
                {t('categories.cancel')}
              </button>
              <button onClick={handleSave} className="btn-primary flex items-center justify-center text-xs xs:text-sm sm:text-base order-1 sm:order-2 py-2 xs:py-2.5" disabled={!formData.name.trim()}>
                <Save className="w-3.5 h-3.5 xs:w-4 xs:h-4 mr-1.5 xs:mr-2" />
                {t('categories.save')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Categories;
