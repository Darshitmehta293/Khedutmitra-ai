import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'
import { aiService } from '../services/api'
import { ChatMessage, Language } from '../types'
import { Send, Loader2, Bot, User, Sparkles } from 'lucide-react'
import LanguageSwitcher from '../components/LanguageSwitcher'
import AgentTracePanel from '../components/AgentTracePanel'
import { v4 as uuidv4 } from 'uuid'

// uuid shim
function makeId() { return Math.random().toString(36).slice(2) + Date.now().toString(36) }

const SUGGESTIONS = {
  en: ['What is today\'s cotton price?', 'Should I sell my 50 quintal cotton now?', 'Find buyers for groundnut in Rajkot', 'What\'s the 7-day price forecast?'],
  gu: ['આજે કપાસનો ભાવ શું છે?', 'મારા 50 ક્વિ. કપાસ હવે વેચું?', 'રાજકોટ પાસે મગફળીના ખરીદ', '7 દિ. ભવિષ્ય ભાવ?'],
  hi: ['आज कपास का भाव क्या है?', 'मेरे 50 क्विंटल अभी बेचूं?', 'मूंगफली के खरीदार खोजें', '7 दिन का पूर्वानुमान?'],
}

export default function AIAssistantPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(makeId)
  const [lastTrace, setLastTrace] = useState<any[]>([])
  const [showTrace, setShowTrace] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const language = (user?.language || 'gu') as Language

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (msg?: string) => {
    const text = msg || input.trim()
    if (!text || loading) return
    setInput('')

    const userMsg: ChatMessage = { role: 'user', content: text, language }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await aiService.chat({
        message: text,
        language,
        session_id: sessionId,
        crop_id: 'crop_cotton',
        district: 'Ahmedabad',
      })
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: res.data.reply,
        language,
        agent_trace: res.data.agent_trace,
      }
      setMessages(prev => [...prev, assistantMsg])
      setLastTrace(res.data.agent_trace || [])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I am having trouble connecting. Please try again.',
        language: 'en',
      }])
    } finally {
      setLoading(false)
    }
  }

  const suggestions = SUGGESTIONS[language] || SUGGESTIONS.en

  return (
    <div className="space-y-4 flex flex-col h-[calc(100vh-200px)]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black">{t('ai.title')}</h1>
          <div className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
            <Sparkles size={12} className="text-blue-400" /> {t('ai.powered_by')}
            {' · '}
            <span className="text-amber-600">{t('ai.demo_mode')}</span>
          </div>
        </div>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto space-y-3 pb-2">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="w-14 h-14 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-3">
              <Bot size={28} className="text-primary" />
            </div>
            <p className="text-gray-500 text-sm mb-4">{t('ai.placeholder')}</p>
            <div className="space-y-2">
              {suggestions.map((s, i) => (
                <button key={i} onClick={() => send(s)}
                  className="block w-full text-left bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-gray-700 hover:border-primary hover:bg-green-50 transition">
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot size={15} className="text-primary" />
              </div>
            )}
            <div className={`max-w-xs rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
              m.role === 'user'
                ? 'bg-primary text-white rounded-br-sm'
                : 'bg-white border border-gray-100 text-gray-800 rounded-bl-sm'
            }`}>
              {m.content}
            </div>
            {m.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                <User size={15} className="text-gray-500" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5">
            <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot size={15} className="text-primary" />
            </div>
            <div className="bg-white border border-gray-100 rounded-2xl px-4 py-3 flex gap-1">
              {[0,1,2].map(i => (
                <div key={i} className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" style={{ animationDelay: `${i*0.15}s` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Agent trace toggle */}
      {lastTrace.length > 0 && (
        <button onClick={() => setShowTrace(!showTrace)}
          className="text-xs text-primary underline text-left">
          {showTrace ? 'Hide' : 'Show'} Agent Trace ({lastTrace.length} steps)
        </button>
      )}
      {showTrace && lastTrace.length > 0 && <AgentTracePanel trace={lastTrace} />}

      {/* Input */}
      <div className="flex gap-2 items-end">
        <input
          value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder={t('ai.placeholder')}
          className="input-field flex-1"
        />
        <button onClick={() => send()} disabled={loading || !input.trim()}
          className="w-11 h-11 bg-primary rounded-xl flex items-center justify-center text-white disabled:opacity-40 flex-shrink-0">
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
