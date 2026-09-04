import React, { useEffect, useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, TrendingUp, Scale, Users, Camera, Archive, Sparkles,
  PiggyBank, MessageSquare, CalendarDays, LogOut, Leaf, Moon, Sun
} from 'lucide-react'
import LanguageSwitcher from './LanguageSwitcher'
import DemoBanner from './DemoBanner'

export default function Layout() {
  const { t } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('km_theme') === 'dark')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem('km_theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const themeButton = (
    <button
      type="button"
      onClick={() => setDarkMode(value => !value)}
      title={darkMode ? 'Switch to light mode' : 'Switch to night mode'}
      aria-label={darkMode ? 'Switch to light mode' : 'Switch to night mode'}
      className="p-2 rounded-lg text-gray-500 hover:bg-primary/10 hover:text-primary transition-colors"
    >
      {darkMode ? <Sun size={17} /> : <Moon size={17} />}
    </button>
  )

  const navItems = [
    { to: '/dashboard',    icon: LayoutDashboard, label: t('nav.dashboard') },
    { to: '/inventory',    icon: Archive,          label: 'My Inventory' },
    { to: '/intelligence', icon: Sparkles,          label: 'Intelligence Hub' },
    { to: '/market',       icon: TrendingUp,       label: t('nav.market') },
    { to: '/sell-or-store',icon: Scale,            label: t('nav.sell_or_store') },
    { to: '/buyers',       icon: Users,            label: t('nav.buyers') },
    { to: '/quality',      icon: Camera,           label: t('nav.quality') },
    { to: '/income',       icon: PiggyBank,        label: t('nav.income') },
    { to: '/ai',           icon: MessageSquare,    label: t('nav.ai_assistant') },
    { to: '/farm-planner', icon: CalendarDays,     label: 'Farm Planner' },
  ]

  return (
    <div className="min-h-screen bg-surface flex">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-64 bg-[#fbfcf9]/95 border-r border-[#dce7dd] fixed h-full z-20">
        <div className="p-5 border-b border-[#dce7dd]">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center shadow-sm shadow-primary/25">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900 text-sm leading-tight tracking-tight">KhedutMitra</div>
              <div className="text-[10px] text-primary/70 uppercase tracking-[0.16em] mt-1">Farmer intelligence</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to} to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive ? 'bg-primary text-white shadow-sm shadow-primary/20' : 'text-gray-600 hover:bg-primary/5 hover:text-primary'
                }`
              }
            >
              <Icon className="w-4.5 h-4.5 flex-shrink-0" size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-[#dce7dd]">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm">
              {user?.name?.[0] || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">{user?.name}</div>
              <div className="text-xs text-gray-400 capitalize">{user?.role}</div>
            </div>
          </div>
          <div className="flex items-center justify-between gap-2"><LanguageSwitcher />{themeButton}</div>
          <button onClick={() => { logout(); navigate('/') }}
            className="mt-2 flex items-center gap-2 text-sm text-gray-500 hover:text-red-500 transition-colors">
            <LogOut size={15} /> {t('nav.logout')}
          </button>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 bg-[#fbfcf9]/95 border-b border-[#dce7dd] z-20 flex items-center justify-between px-4 py-3 backdrop-blur">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-primary rounded-md flex items-center justify-center">
            <Leaf className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-sm">KhedutMitra AI</span>
        </div>
        <div className="flex items-center gap-1"><LanguageSwitcher />{themeButton}</div>
      </div>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-[#fbfcf9]/95 border-t border-[#dce7dd] z-20 flex backdrop-blur">
        {navItems.slice(0, 5).map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center py-2 text-xs gap-0.5 ${isActive ? 'text-primary' : 'text-gray-400'}`
            }>
            <Icon size={20} />
            <span className="truncate w-full text-center px-0.5">{label.split(' ')[0]}</span>
          </NavLink>
        ))}
      </nav>

      {/* Main content */}
      <main className="flex-1 md:ml-64 mt-14 md:mt-0 mb-16 md:mb-0 min-h-screen">
        <DemoBanner />
        <div className="p-4 md:p-6 max-w-5xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
