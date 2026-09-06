import React, { useEffect, useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, TrendingUp, Scale, Users, Camera, Archive, Sparkles,
  PiggyBank, MessageSquare, CalendarDays, LogOut, Leaf, Moon, Sun, ShieldCheck
} from 'lucide-react'
import LanguageSwitcher from './LanguageSwitcher'
import DemoBanner from './DemoBanner'

export default function Layout() {
  const { t } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [darkMode, setDarkMode] = useState(() => {
    const stored = localStorage.getItem('km_theme')
    const isDark = stored === 'dark'
    // Sync immediately so there's no flash on first render
    document.documentElement.classList.toggle('dark', isDark)
    return isDark
  })

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
    { to: '/admin',        icon: ShieldCheck,      label: 'Admin Portal' },
  ]

  return (
    <div className="min-h-screen bg-surface dark:bg-gray-950 flex transition-colors duration-300">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-64 bg-white/80 dark:bg-gray-950/80 backdrop-blur-2xl border-r border-emerald-500/10 dark:border-emerald-500/20 fixed h-full z-20 shadow-[4_0_24px_rgba(0,0,0,0.02)]">
        <div className="p-5 border-b border-emerald-500/10 dark:border-emerald-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-tr from-emerald-600 via-teal-500 to-green-400 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/25">
              <Leaf className="w-5.5 h-5.5 text-white" />
            </div>
            <div>
              <div className="font-black text-gray-900 dark:text-gray-100 text-base leading-tight tracking-tight flex items-center gap-1.5">
                KhedutMitra <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">AI</span>
              </div>
              <div className="flex items-center gap-1.5 mt-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Agent Network Online</span>
              </div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to} to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-600/25 scale-[1.01]'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-emerald-500/10 hover:text-emerald-600 dark:hover:text-emerald-400'
                }`
              }
            >
              <Icon className="w-4.5 h-4.5 flex-shrink-0" size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-emerald-500/10 dark:border-emerald-500/20 space-y-3">
          <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/15 rounded-xl p-2.5 flex items-center justify-between text-xs">
            <div className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-bold">
              <Sparkles size={13} /> IBM Granite 13B
            </div>
            <span className="text-[10px] bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-extrabold px-1.5 py-0.5 rounded">6 Agents</span>
          </div>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white font-black text-sm shadow-sm">
              {user?.name?.[0] || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-bold text-gray-900 dark:text-gray-100 truncate">{user?.name}</div>
              <div className="text-xs text-gray-400 dark:text-gray-500 capitalize">{user?.role}</div>
            </div>
          </div>
          <div className="flex items-center justify-between gap-2"><LanguageSwitcher />{themeButton}</div>
          <button onClick={() => { logout(); navigate('/') }}
            className="mt-1 flex items-center gap-2 text-xs font-semibold text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors">
            <LogOut size={14} /> {t('nav.logout')}
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
