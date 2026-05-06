export type Language = 'ru' | 'en';
export type Theme = 'light' | 'dark';
export type Currency = 'USD' | 'RUB' | 'EUR';

export interface AppSettings {
  language: Language;
  theme: Theme;
  currency: Currency;
}

