'use client'

import { Listing } from '../types'
import PCCard from './PCCard'
import { Monitor } from 'lucide-react'

interface Props {
  results: Listing[]
  total: number
  loading: boolean
  searched: boolean
}

export default function ResultsGrid({ results, total, loading, searched }: Props) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden animate-pulse">
            <div className="aspect-square bg-white/10" />
            <div className="p-4 space-y-3">
              <div className="h-4 bg-white/10 rounded w-3/4" />
              <div className="h-4 bg-white/10 rounded w-1/2" />
              <div className="h-8 bg-white/10 rounded" />
              <div className="h-10 bg-purple-600/30 rounded-xl" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!searched) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <Monitor className="w-16 h-16 text-purple-400/40 mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Find Your Perfect PC</h2>
        <p className="text-white/40 max-w-md">
          Describe what you need in plain English, or use the filters to narrow down your search across multiple retailers.
        </p>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <Monitor className="w-16 h-16 text-purple-400/40 mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">No Results Found</h2>
        <p className="text-white/40">Try adjusting your filters or search query.</p>
      </div>
    )
  }

  return (
    <div>
      <p className="text-white/40 text-sm mb-4">{total} listings found</p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {results.map((listing) => (
          <PCCard key={listing.id} listing={listing} />
        ))}
      </div>
    </div>
  )
}