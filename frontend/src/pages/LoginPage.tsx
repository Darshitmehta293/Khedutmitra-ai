import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { Leaf, Eye, EyeOff } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'

export default function LoginPage() {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(phone, password)
      navigate('/dashboard')
      toast.success('Welcome back!')
    } catch {
      toast.error('Invalid phone or password')
    } finally {
      setLoading(false)
    }
  }

  const demoLogin = async () => {
    setPhone('9876543210')
    setPassword('demo1234')
    setLoading(true)
    try {
      await login('9876543210', 'demo1234')
      navigate('/dashboard')
      toast.success('Demo login: Ramesh Patel')
    } catch {
      toast.error('Demo login failed — please seed the database first')
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
            <span className="font-bold text-gray-900">KhedutMitra AI</span>
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="card">
          <h1 className="text-xl font-bold mb-6">{t('auth.login_title')}</h1>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('auth.phone')}</label>
              <input value={phone} onChange={e => setPhone(e.target.value)}
                className="input-field" placeholder="10-digit mobile" required maxLength={15} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">{t('auth.password')}</label>
              <div className="relative">
                <input value={password} onChange={e => setPassword(e.target.value)}
                  type={showPw ? 'text' : 'password'} className="input-field pr-10"
                  placeholder="Password" required />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? t('common.loading') : t('auth.login_btn')}
            </button>
          </form>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-200" /></div>
            <div className="relative flex justify-center"><span className="bg-white px-3 text-xs text-gray-400">OR</span></div>
          </div>

          <button onClick={demoLogin} disabled={loading}
            className="w-full bg-amber-50 border border-amber-200 text-amber-800 font-semibold py-3 rounded-xl text-sm hover:bg-amber-100 transition">
            🎯 {t('auth.demo_login')} (Ramesh Patel)
          </button>

          <p className="mt-4 text-center text-sm text-gray-500">
            {t('auth.no_account')}{' '}
            <Link to="/register" className="text-primary font-medium">{t('nav.register')}</Link>
          </p>
        </div>

        <p className="mt-4 text-xs text-center text-gray-400">
          Demo credentials: Phone 9876543210 / Password demo1234
        </p>
      </div>
    </div>
  )
}
