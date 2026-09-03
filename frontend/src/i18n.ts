// KhedutMitra AI — i18n setup
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import gu from './locales/gu.json'
import hi from './locales/hi.json'

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, gu: { translation: gu }, hi: { translation: hi } },
  lng: localStorage.getItem('km_lang') || 'gu',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
