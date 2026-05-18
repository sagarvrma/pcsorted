'use client'

import { useState } from 'react'
import axios from 'axios'
import SearchBar from './components/SearchBar'
import FilterPanel from './components/Filters'
import ResultsGrid from './components/ResultsGrid'
import { Filters, Listing, NLPResponse } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

const DEFAULT_FILTERS: Filters = {
  q: '',
  gpu: '',
  cpu: '',
  min_price: '',
  max_price: '',
  min_ram: '',
  min_storage: '',
  source: '',
  condition: '',
  device_type: '',
  sort: 'price_asc',
}

export default function Home() {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS)
  const [results, setResults] = useState<Listing[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [nlpLoading, setNlpLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [reasoning, setReasoning] = useState('')

  const buildParams = (f: Filters) => {
    const params: Record<string, string> = {}
    if (f.q) params.q = f.q
    if (f.gpu) params.gpu = f.gpu
    if (f.cpu) params.cpu = f.cpu
    if (f.min_price) params.min_price = f.min_price
    if (f.max_price) params.max_price = f.max_price
    if (f.min_ram) params.min_ram = f.min_ram
    if (f.min_storage) params.min_storage = f.min_storage
    if (f.source) params.source = f.source
    if (f.condition) params.condition = f.condition
    if (f.device_type) params.device_type = f.device_type
    if (f.sort) params.sort = f.sort
    return params
  }

  const search = async (f: Filters = filters) => {
    setLoading(true)
    setSearched(true)
    try {
      const { data } = await axios.get(`${API_URL}/search`, { params: buildParams(f) })
      setResults(data.results)
      setTotal(data.total)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleNLPSearch = async (query: string) => {
    setNlpLoading(true)
    try {
      const { data }: { data: NLPResponse } = await axios.post(`${API_URL}/nlp`, { query })
      const f = data.filters
      const newFilters: Filters = {
        ...DEFAULT_FILTERS,
        gpu: f.gpu || '',
        cpu: f.cpu || '',
        max_price: f.max_price?.toString() || '',
        min_price: f.min_price?.toString() || '',
        min_ram: f.min_ram_gb?.toString() || '',
        min_storage: f.min_storage_gb?.toString() || '',
        condition: f.condition || '',
        device_type: f.device_type || '',
        sort: 'price_asc',
      }
      setFilters(newFilters)
      setReasoning(f.reasoning || '')
      await search(newFilters)
    } catch (err) {
      console.error(err)
    } finally {
      setNlpLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">PCSorted</h1>
            <p className="text-white/40 text-xs">Find the right PC at the right price</p>
          </div>
          <div className="flex items-center gap-2 text-white/40 text-sm">
            <span className="w-2 h-2 bg-green-400 rounded-full" />
            Live
          </div>
        </div>
      </header>

      {/* Search */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold text-white mb-2">
            Find your perfect PC
          </h2>
          <p className="text-white/40">Describe what you need — we'll find the best options across multiple retailers</p>
        </div>
        <SearchBar
          onNLPSearch={handleNLPSearch}
          loading={nlpLoading}
          reasoning={reasoning}
        />
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters sidebar */}
          <div className="lg:w-72 flex-shrink-0">
            <FilterPanel
              filters={filters}
              onChange={setFilters}
              onSearch={() => search()}
              loading={loading}
            />
          </div>

          {/* Results */}
          <div className="flex-1">
            <ResultsGrid
              results={results}
              total={total}
              loading={loading}
              searched={searched}
            />
          </div>
        </div>
      </div>
    </div>
  )
}