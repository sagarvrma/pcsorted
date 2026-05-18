'use client'

import { useState } from 'react'
import { Search, Loader2, Sparkles } from 'lucide-react'

interface Props {
  onNLPSearch: (query: string) => void
  loading: boolean
  reasoning?: string
}

export default function SearchBar({ onNLPSearch, loading, reasoning }: Props) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) onNLPSearch(query.trim())
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center bg-white/10 backdrop-blur border border-white/20 rounded-2xl px-4 py-3 gap-3 focus-within:border-purple-400 transition-colors">
          <Sparkles className="w-5 h-5 text-purple-400 flex-shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder='Try "gaming PC under $800" or "laptop for video editing"'
            className="flex-1 bg-transparent text-white placeholder-white/40 outline-none text-lg"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-5 py-2 rounded-xl font-medium flex items-center gap-2 transition-colors"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Search
          </button>
        </div>
      </form>

      {reasoning && (
        <div className="mt-3 bg-purple-900/40 border border-purple-500/30 rounded-xl px-4 py-3">
          <p className="text-purple-300 text-sm">
            <span className="font-semibold text-purple-200">AI: </span>
            {reasoning}
          </p>
        </div>
      )}
    </div>
  )
}