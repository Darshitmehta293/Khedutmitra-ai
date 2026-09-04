import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Leaf, TrendingUp, Users, MessageSquare, ArrowRight, Info, Mail, Github } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'

export default function LandingPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="border-b border-gray-100 px-4 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-primary rounded-xl flex items-center justify-center">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-gray-900">KhedutMitra AI</div>
            <div className="text-xs text-gray-400">ખેડૂત મિત્ર</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <a href="#about" className="hidden sm:inline text-sm font-medium text-gray-600 hover:text-primary">About</a>
          <a href="#contact" className="hidden sm:inline text-sm font-medium text-gray-600 hover:text-primary">Contact</a>
          <LanguageSwitcher />
          <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-primary">{t('nav.login')}</Link>
          <Link to="/register" className="btn-primary text-sm py-2 px-4">
            {t('nav.register')}
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-16 px-4 text-center max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-green-50 text-primary text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          <Leaf size={14} /> IBM Granite + AI Agents
        </div>
        <h1 className="text-4xl md:text-5xl font-black text-gray-900 mb-4 leading-tight">
          {t('tagline')}
        </h1>
        <p className="text-lg text-gray-500 mb-8 max-w-2xl mx-auto">
          AI-powered market intelligence for Gujarat's cotton and groundnut farmers.
          Real-time mandi prices, price forecasting, direct buyer connections.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button onClick={() => navigate('/register')} className="btn-primary flex items-center justify-center gap-2">
            Start Selling Smarter <ArrowRight size={18} />
          </button>
          <button onClick={() => navigate('/demo')} className="btn-secondary flex items-center justify-center gap-2">
            Watch Demo Scenario
          </button>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-primary py-10 px-4">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center text-white">
          {[
            { value: '₹7,050', label: 'Avg Cotton Price /quintal' },
            { value: '8+', label: 'Gujarat Mandis Covered' },
            { value: '6', label: 'AI Agents Working' },
            { value: '3', label: 'Languages Supported' },
          ].map(({ value, label }) => (
            <div key={label}>
              <div className="text-3xl font-black mb-1">{value}</div>
              <div className="text-sm opacity-80">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-14 px-4 max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-10">How KhedutMitra AI Works</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: TrendingUp, title: 'Real-Time Price Intelligence', desc: 'Compare prices across all major Gujarat mandis. AI detects trends and price movements instantly.' },
            { icon: MessageSquare, title: 'Multi-Agent AI Analysis', desc: '6 specialized AI agents analyze your crop, calculate storage economics, and find the best buyers.' },
            { icon: Users, title: 'Direct Buyer Connections', desc: 'Match with verified buyers based on crop type, quantity, quality, location, and price.' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card text-center">
              <div className="w-12 h-12 bg-green-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Icon className="text-primary" size={22} />
              </div>
              <h3 className="font-semibold mb-2">{title}</h3>
              <p className="text-sm text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* AI Agents showcase */}
      <section className="py-12 px-4 bg-surface">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-2">6 Specialized AI Agents</h2>
          <p className="text-center text-gray-500 text-sm mb-8">Powered by IBM Granite LLM + IBM Cloud</p>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { emoji: '📊', name: 'Mandi Price Agent', desc: 'Real-time price across mandis' },
              { emoji: '📈', name: 'Forecasting Agent', desc: '3/7/15/30-day price predictions' },
              { emoji: '🏪', name: 'Storage Advisor', desc: 'Sell vs Store economics' },
              { emoji: '🤝', name: 'Buyer Matching', desc: 'Direct buyer connections' },
              { emoji: '🌾', name: 'Quality Grading', desc: 'AI crop quality assessment' },
              { emoji: '💰', name: 'Income Dashboard', desc: 'Revenue scenarios & planning' },
            ].map(({ emoji, name, desc }) => (
              <div key={name} className="bg-white rounded-xl border border-gray-100 p-4 flex items-start gap-3">
                <span className="text-2xl">{emoji}</span>
                <div>
                  <div className="font-semibold text-sm">{name}</div>
                  <div className="text-xs text-gray-500">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* IBM Tech */}
      <section className="py-12 px-4 max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-8">Built on IBM Technology</h2>
        <div className="grid sm:grid-cols-3 gap-4 text-center">
          {[
            { label: 'IBM Granite LLM', sub: 'watsonx.ai' },
            { label: 'IBM Cloud', sub: 'Scalable deployment' },
            { label: 'IBM Bob', sub: 'AI development' },
          ].map(({ label, sub }) => (
            <div key={label} className="bg-blue-50 border border-blue-100 rounded-xl p-5">
              <div className="font-bold text-blue-800">{label}</div>
              <div className="text-sm text-blue-500">{sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* About and contact */}
      <section id="about" className="py-14 px-4 bg-surface scroll-mt-6">
        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-6">
          <div className="card">
            <div className="flex items-center gap-2 text-primary mb-3"><Info size={20} /><h2 className="text-xl font-bold text-gray-900">About KhedutMitra AI</h2></div>
            <p className="text-sm text-gray-600 leading-6">KhedutMitra AI is a farmer-focused market intelligence platform for Gujarat. It brings mandi prices, forecasts, buyer discovery, quality guidance, storage economics, and multilingual decision support into one simple workspace.</p>
            <p className="text-sm text-gray-600 leading-6 mt-3">The platform is built as an IBM technology and AI agent demonstration, with transparent demo fallbacks when live providers are not configured.</p>
          </div>
          <div id="contact" className="card scroll-mt-6">
            <div className="flex items-center gap-2 text-primary mb-3"><Mail size={20} /><h2 className="text-xl font-bold text-gray-900">Contact & Developer</h2></div>
            <p className="text-sm text-gray-600 leading-6">Developed by <strong className="text-gray-900">Darshit Mehta</strong>.</p>
            <div className="mt-4 space-y-2 text-sm">
              <a href="https://github.com/Darshitmehta293" target="_blank" rel="noreferrer" className="flex items-center gap-2 text-primary hover:text-primary-dark"><Github size={17} /> GitHub developer profile</a>
              <a href="https://github.com/Darshitmehta293/Khedutmitra-ai" target="_blank" rel="noreferrer" className="flex items-center gap-2 text-primary hover:text-primary-dark"><Github size={17} /> KhedutMitra AI source repository</a>
            </div>
            <p className="text-xs text-gray-400 mt-4">For project questions, open an issue in the source repository.</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-14 px-4 text-center bg-primary text-white">
        <h2 className="text-3xl font-black mb-3">Ready to Sell Smarter?</h2>
        <p className="text-green-100 mb-6">Join Gujarat farmers using AI for better market decisions</p>
        <div className="flex gap-3 justify-center">
          <Link to="/register" className="bg-white text-primary font-bold px-7 py-3 rounded-xl hover:bg-green-50 transition">
            Create Free Account
          </Link>
          <Link to="/demo" className="border-2 border-white text-white font-bold px-7 py-3 rounded-xl hover:bg-white/10 transition">
            View Demo
          </Link>
        </div>
      </section>

      <footer className="text-center py-6 text-xs text-gray-400 border-t border-gray-100">
        © 2024 KhedutMitra AI · Developed by Darshit Mehta · IBM Hackathon Challenge 13 | Economic Development
      </footer>
    </div>
  )
}
