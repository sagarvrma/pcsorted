"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { SlidersHorizontal, X } from "lucide-react"
import axios from "axios"
import FilterPanel from "./components/Filters"
import ResultsGrid from "./components/ResultsGrid"
import { DEFAULT_FILTERS, PRICE_MAX, type FilterState, type Listing } from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

function buildParams(f: FilterState): Record<string, string> {
  const p: Record<string, string> = {}
  if (f.gpus.length) p.gpu = f.gpus.join(",")
  if (f.cpus.length) p.cpu = f.cpus.join(",")
  if (f.minPrice > 0) p.min_price = String(f.minPrice)
  if (f.maxPrice < PRICE_MAX) p.max_price = String(f.maxPrice)
  if (f.minRam) p.min_ram = f.minRam
  if (f.conditions.length) p.condition = f.conditions.join(",")
  if (f.sources.length) p.source = f.sources.join(",")
  if (f.deviceType) p.device_type = f.deviceType
  p.sort = f.sort
  p.limit = "60"
  return p
}

export default function Home() {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS)
  const [results, setResults] = useState<Listing[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)
  const filtersRef = useRef<FilterState>(filters)
  filtersRef.current = filters

  const search = useCallback(async (f: FilterState) => {
    setLoading(true)
    setSearched(true)
    try {
      const { data } = await axios.get(`${API_URL}/search`, { params: buildParams(f) })
      setResults(data.results ?? [])
      setTotal(data.total ?? 0)
    } catch {
      setResults([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    search(DEFAULT_FILTERS)
  }, [search])

  const handleSearch = () => {
    setMobileFiltersOpen(false)
    search(filtersRef.current)
  }

  const handleSortChange = (sort: string) => {
    const updated = { ...filtersRef.current, sort }
    setFilters(updated)
    search(updated)
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#0a0a0a" }}>
      {/* Header */}
      <header className="sticky top-0 z-50 h-14 border-b border-zinc-800 bg-[#0a0a0a]/95 backdrop-blur-sm">
        <div className="flex items-center justify-between h-full px-5 max-w-screen-2xl mx-auto">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-md bg-zinc-100 flex items-center justify-center flex-shrink-0">
              <span className="text-[10px] font-black text-zinc-900 leading-none">PC</span>
            </div>
            <span className="font-semibold text-zinc-100 text-[15px] tracking-tight">PCSorted</span>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* Mobile filter toggle */}
            <button
              className="lg:hidden flex items-center gap-1.5 text-xs text-zinc-400 border border-zinc-800 rounded-md px-3 py-1.5 hover:border-zinc-700 hover:text-zinc-200 transition-colors"
              onClick={() => setMobileFiltersOpen(true)}
            >
              <SlidersHorizontal className="h-3.5 w-3.5" />
              Filters
            </button>

            {/* Live indicator */}
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-zinc-600">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              Updated daily
            </div>
          </div>
        </div>
      </header>

      {/* Mobile filters overlay */}
      {mobileFiltersOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setMobileFiltersOpen(false)}
          />
          <div className="relative z-10 w-80 max-w-full h-full bg-zinc-950 border-r border-zinc-800 flex flex-col">
            <div className="flex items-center justify-between px-4 h-14 border-b border-zinc-800">
              <span className="font-medium text-zinc-200 text-sm">Filters</span>
              <button
                onClick={() => setMobileFiltersOpen(false)}
                className="h-8 w-8 flex items-center justify-center rounded-md text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden flex flex-col">
              <FilterPanel
                filters={filters}
                onChange={setFilters}
                onSearch={handleSearch}
                loading={loading}
              />
            </div>
          </div>
        </div>
      )}

      {/* Main layout */}
      <div className="flex max-w-screen-2xl mx-auto">
        {/* Desktop sidebar */}
        <aside className="hidden lg:flex flex-col w-72 flex-shrink-0 border-r border-zinc-800 sticky top-14 h-[calc(100vh-3.5rem)]">
          <FilterPanel
            filters={filters}
            onChange={setFilters}
            onSearch={handleSearch}
            loading={loading}
          />
        </aside>

        {/* Results */}
        <main className="flex-1 min-w-0 px-5 py-6">
          <ResultsGrid
            results={results}
            total={total}
            loading={loading}
            searched={searched}
            sort={filters.sort}
            onSortChange={handleSortChange}
          />
        </main>
      </div>
    </div>
  )
}
