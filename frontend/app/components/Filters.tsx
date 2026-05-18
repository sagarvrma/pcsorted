'use client'

import { Filters } from '../types'
import { SlidersHorizontal } from 'lucide-react'

interface Props {
  filters: Filters
  onChange: (filters: Filters) => void
  onSearch: () => void
  loading: boolean
}

const GPU_OPTIONS = [
  'RTX 5090', 'RTX 5080', 'RTX 5070 Ti', 'RTX 5070',
  'RTX 4090', 'RTX 4080', 'RTX 4070 Ti', 'RTX 4070 Super',
  'RTX 4070', 'RTX 4060 Ti', 'RTX 4060',
  'RTX 3080', 'RTX 3070', 'RTX 3060',
  'RX 7900 XTX', 'RX 7800 XT', 'RX 6700 XT',
]

const CPU_OPTIONS = [
  'i9', 'i7', 'i5', 'i3',
  'Ryzen 9', 'Ryzen 7', 'Ryzen 5', 'Ryzen 3',
]

export default function FilterPanel({ filters, onChange, onSearch, loading }: Props) {
  const update = (key: keyof Filters, value: string) => {
    onChange({ ...filters, [key]: value })
  }

  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <SlidersHorizontal className="w-5 h-5 text-purple-400" />
        <h2 className="text-white font-semibold text-lg">Filters</h2>
      </div>

      <div className="space-y-5">
        {/* Device Type */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">Device Type</label>
          <div className="flex gap-2">
            {['', 'desktop', 'laptop'].map((t) => (
              <button
                key={t}
                onClick={() => update('device_type', t)}
                className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  filters.device_type === t
                    ? 'bg-purple-600 text-white'
                    : 'bg-white/10 text-white/60 hover:text-white'
                }`}
              >
                {t === '' ? 'All' : t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* GPU */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">GPU</label>
          <select
            value={filters.gpu}
            onChange={(e) => update('gpu', e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none"
          >
            <option value="">Any GPU</option>
            {GPU_OPTIONS.map((g) => (
              <option key={g} value={g} className="bg-gray-900">{g}</option>
            ))}
          </select>
        </div>

        {/* CPU */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">CPU</label>
          <select
            value={filters.cpu}
            onChange={(e) => update('cpu', e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none"
          >
            <option value="">Any CPU</option>
            {CPU_OPTIONS.map((c) => (
              <option key={c} value={c} className="bg-gray-900">{c}</option>
            ))}
          </select>
        </div>

        {/* Price Range */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">Price Range</label>
          <div className="flex gap-2">
            <input
              type="number"
              value={filters.min_price}
              onChange={(e) => update('min_price', e.target.value)}
              placeholder="Min $"
              className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none placeholder-white/30"
            />
            <input
              type="number"
              value={filters.max_price}
              onChange={(e) => update('max_price', e.target.value)}
              placeholder="Max $"
              className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none placeholder-white/30"
            />
          </div>
        </div>

        {/* RAM */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">Min RAM (GB)</label>
          <select
            value={filters.min_ram}
            onChange={(e) => update('min_ram', e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none"
          >
            <option value="" className="bg-gray-900">Any</option>
            {[8, 16, 32, 64].map((r) => (
              <option key={r} value={r} className="bg-gray-900">{r}GB</option>
            ))}
          </select>
        </div>

        {/* Storage */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">Min Storage (GB)</label>
          <select
            value={filters.min_storage}
            onChange={(e) => update('min_storage', e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none"
          >
            <option value="" className="bg-gray-900">Any</option>
            {[256, 512, 1024, 2048].map((s) => (
              <option key={s} value={s} className="bg-gray-900">{s >= 1024 ? `${s/1024}TB` : `${s}GB`}</option>
            ))}
          </select>
        </div>

        {/* Condition */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">Condition</label>
          <select
            value={filters.condition}
            onChange={(e) => update('condition', e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none"
          >
            <option value="" className="bg-gray-900">Any</option>
            <option value="new" className="bg-gray-900">New</option>
            <option value="refurbished" className="bg-gray-900">Refurbished</option>
            <option value="used" className="bg-gray-900">Used</option>
          </select>
        </div>

        {/* Source */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">Source</label>
          <select
            value={filters.source}
            onChange={(e) => update('source', e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none"
          >
            <option value="" className="bg-gray-900">All Sources</option>
            <option value="antonline" className="bg-gray-900">Antonline</option>
            <option value="ebay" className="bg-gray-900">eBay</option>
            <option value="bestbuy" className="bg-gray-900">Best Buy</option>
            <option value="newegg" className="bg-gray-900">Newegg</option>
          </select>
        </div>

        {/* Sort */}
        <div>
          <label className="text-white/60 text-sm mb-2 block">Sort By</label>
          <select
            value={filters.sort}
            onChange={(e) => update('sort', e.target.value)}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white text-sm outline-none"
          >
            <option value="price_asc" className="bg-gray-900">Price: Low to High</option>
            <option value="price_desc" className="bg-gray-900">Price: High to Low</option>
            <option value="newest" className="bg-gray-900">Newest</option>
            <option value="last_seen" className="bg-gray-900">Recently Seen</option>
          </select>
        </div>

        <button
          onClick={onSearch}
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-3 rounded-xl font-semibold transition-colors"
        >
          {loading ? 'Searching...' : 'Apply Filters'}
        </button>
      </div>
    </div>
  )
}