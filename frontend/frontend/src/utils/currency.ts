import type { Currency } from '../types';

export const currencySymbols: Record<Currency, string> = {
  USD: '$',
  RUB: '₽',
  EUR: '€',
};

export const formatCurrency = (amount: number, currency: Currency): string => {
  const symbol = currencySymbols[currency];
  const formattedAmount = new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Math.abs(amount));
  
  return `${symbol}${formattedAmount}`;
};

export const formatCurrencyWithSign = (
  amount: number, 
  currency: Currency, 
  isIncome: boolean = false
): string => {
  const sign = isIncome ? '+' : '-';
  return `${sign}${formatCurrency(amount, currency)}`;
};

