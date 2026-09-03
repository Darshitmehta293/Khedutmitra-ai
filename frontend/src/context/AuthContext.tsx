// KhedutMitra AI — Auth Context
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, AuthState } from '../types'
import { authService } from '../services/api'

interface AuthContextType extends AuthState {
  isInitializing: boolean
  login: (phone: string, password: string) => Promise<void>
  register: (data: object) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isInitializing, setIsInitializing] = useState(true)
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
  })

  useEffect(() => {
    const token = localStorage.getItem('km_token')
    const userStr = localStorage.getItem('km_user')
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User
        setState({ user, token, isAuthenticated: true })
      } catch {
        localStorage.removeItem('km_token')
        localStorage.removeItem('km_user')
      }
    }
    setIsInitializing(false)
  }, [])

  const login = async (phone: string, password: string) => {
    const res = await authService.login(phone, password)
    const { access_token, user_id, name, role, language } = res.data
    const user: User = { id: user_id, name, phone, role, language: language || 'gu', is_active: true, created_at: new Date().toISOString() }
    localStorage.setItem('km_token', access_token)
    localStorage.setItem('km_user', JSON.stringify(user))
    setState({ user, token: access_token, isAuthenticated: true })
  }

  const register = async (data: object) => {
    const res = await authService.register(data)
    const { access_token, user_id, name, role, language } = res.data
    const registration = data as { phone?: string }
    const user: User = { id: user_id, name, phone: registration.phone || '', role, language: language || 'gu', is_active: true, created_at: new Date().toISOString() }
    localStorage.setItem('km_token', access_token)
    localStorage.setItem('km_user', JSON.stringify(user))
    setState({ user, token: access_token, isAuthenticated: true })
  }

  const logout = () => {
    localStorage.removeItem('km_token')
    localStorage.removeItem('km_user')
    setState({ user: null, token: null, isAuthenticated: false })
  }

  const updateUser = (user: User) => {
    localStorage.setItem('km_user', JSON.stringify(user))
    setState((prev) => ({ ...prev, user }))
  }

  return (
    <AuthContext.Provider value={{ ...state, isInitializing, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
