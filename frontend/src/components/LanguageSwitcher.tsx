import React from 'react'
import { useTranslation } from 'react-i18next'
import i18n from '../i18n'
import { Language } from '../types'

const LANGS: { code: Language; label: string }[] = [
  { code: 'gu', label: 'ગુ' },
  { code: 'hi', label: 'हि' },
  { code: 'en', label: 'EN' },
]

export default function LanguageSwitcher() {
  const { i18n: i18nHook } = useTranslation()
  const currentLang = i18nHook.language as Language

  const handleChange = (lang: Language) => {
    i18n.changeLanguage(lang)
    localStorage.setItem('km_lang', lang)
  }

  return (
    <div className="flex gap-1 bg-gray-100 rounded-lg p-0.5">
      {LANGS.map(({ code, label }) => (
        <button
          key={code}
          onClick={() => handleChange(code)}
          className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
            currentLang === code ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
