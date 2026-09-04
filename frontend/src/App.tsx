import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import MarketPage from './pages/MarketPage'
import SellOrStorePage from './pages/SellOrStorePage'
import BuyersPage from './pages/BuyersPage'
import QualityPage from './pages/QualityPage'
import IncomePage from './pages/IncomePage'
import AIAssistantPage from './pages/AIAssistantPage'
import DemoPage from './pages/DemoPage'
import FarmPlannerPage from './pages/FarmPlannerPage'
import InventoryPage from './pages/InventoryPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isInitializing } = useAuth()
  if (isInitializing) return null
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/demo" element={<DemoPage />} />
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/inventory" element={<ProtectedRoute><InventoryPage /></ProtectedRoute>} />
        <Route path="/market" element={<ProtectedRoute><MarketPage /></ProtectedRoute>} />
        <Route path="/sell-or-store" element={<ProtectedRoute><SellOrStorePage /></ProtectedRoute>} />
        <Route path="/buyers" element={<ProtectedRoute><BuyersPage /></ProtectedRoute>} />
        <Route path="/quality" element={<ProtectedRoute><QualityPage /></ProtectedRoute>} />
        <Route path="/income" element={<ProtectedRoute><IncomePage /></ProtectedRoute>} />
        <Route path="/ai" element={<ProtectedRoute><AIAssistantPage /></ProtectedRoute>} />
        <Route path="/farm-planner" element={<ProtectedRoute><FarmPlannerPage /></ProtectedRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
