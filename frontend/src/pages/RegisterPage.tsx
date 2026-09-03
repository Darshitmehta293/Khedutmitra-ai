import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { Leaf } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'

const DISTRICTS = ['Ahmedabad','Rajkot','Junagadh','Bhavnagar','Amreli','Surendranagar','Anand','Gondal']

export default function RegisterPage() {
  const { t } = useTranslation()
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '', phone: '', password: '', village: '', district: 'Ahmedabad',
    email: '', role: 'farmer', language: 'gu',
  })
  const [loading, setLoading] = useState(false)

  const set = (key: string, val: string) => setForm(f => ({ ...f, [key]: val }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await register({
        ...form,
        email: form.email.trim() || undefined,
        village: form.village.trim() || undefined,
      })
      toast.success('Account created!')
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-between mb-8">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-9 h-9 bg-primary rounded-xl flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold">KhedutMitra AI</span>
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="card">
          <h1 className="text-xl font-bold mb-5">{t('auth.register_title')}</h1>
          <form onSubmit={handleSubmit} className="space-y-3.5">
            <input value={form.name} onChange={e => set('name', e.target.value)}
              className="input-field" placeholder={t('auth.name')} required />
            <input value={form.phone} onChange={e => set('phone', e.target.value)}
              className="input-field" placeholder={t('auth.phone')} required maxLength={15} />
            <input value={form.password} onChange={e => set('password', e.target.value)}
              type="password" className="input-field" placeholder={t('auth.password')} required minLength={6} />
            <input value={form.village} onChange={e => set('village', e.target.value)}
              className="input-field" placeholder={t('auth.village')} />
            <select value={form.district} onChange={e => set('district', e.target.value)} className="select-field">
              {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
            <select value={form.language} onChange={e => set('language', e.target.value)} className="select-field">
              <option value="gu">ગુજરાતી</option>
              <option value="hi">हिन्दी</option>
              <option value="en">English</option>
            </select>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? t('common.loading') : t('auth.register_btn')}
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-gray-500">
            {t('auth.have_account')}{' '}
            <Link to="/login" className="text-primary font-medium">{t('nav.login')}</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
