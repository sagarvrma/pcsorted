"use client"

import { Monitor, Search } from "lucide-react"
import PCCard from "./PCCard"
import { cn } from "@/lib/utils"
import type { Listing } from "@/app/types"

interface Props {
  results: Listing[]
  total: number
  loading: boolean
  searched: boolean
  sort: string
  onSortChange: (sort: string) => void
}

const SORT_OPTIONS = [
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "newest", label: "Newest Listed" },
  { value: "recently_seen", label: "Recently Seen" },
]

function SkeletonCard() {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden animate-pulse">
      <div className="h-44 bg-zinc-800/60" />
      <div className="p-4 space-y-3">
        <div className="flex gap-1.5">
          <div className="h-5 w-12 rounded-md bg-zinc-800" />
          <div className="h-5 w-16 rounded-md bg-zinc-800" />
        </div>
        <div className="space-y-1.5">
          <div className="h-3.5 bg-zinc-800 rounded w-full" />
          <div className="h-3.5 bg-zinc-800 rounded w-3/4" />
        </div>
        <div className="h-8 w-28 bg-zinc-800 rounded" />
        <div className="flex gap-1.5">
          <div className="h-5 w-20 rounded-md bg-zinc-800" />
          <div className="h-5 w-14 rounded-md bg-zinc-800" />
          <div className="h-5 w-12 rounded-md bg-zinc-800" />
        </div>
        <div className="h-8 w-full rounded-md bg-zinc-800 mt-1" />
      </div>
    </div>
  )
}

export default function ResultsGrid({ results, total, loading, searched, sort, onSortChange }: Props) {
  return (
    <div className="flex flex-col gap-5">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-zinc-500">
          {loading ? (
            <span className="text-zinc-400">Searching...</span>
          ) : searched ? (
            <>
              <span className="text-zinc-100 font-semibold tabular-nums">{total.toLocaleString()}</span>
              {" "}results
            </>
          ) : (
            "Use filters to find PCs"
          )}
        </p>

        {/* Sort controls */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Quick price sort toggles */}
          <div className="hidden sm:flex rounded-md border border-zinc-800 overflow-hidden text-xs">
            <button
              onClick={() => onSortChange("price_asc")}
              className={cn(
                "px-3 py-1.5 font-medium transition-colors",
                sort === "price_asc"
                  ? "bg-zinc-700 text-zinc-100"
                  : "bg-transparent text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/60"
              )}
            >
              Price ↑
            </button>
            <button
              onClick={() => onSortChange("price_desc")}
              className={cn(
                "px-3 py-1.5 font-medium transition-colors border-l border-zinc-800",
                sort === "price_desc"
                  ? "bg-zinc-700 text-zinc-100"
                  : "bg-transparent text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800/60"
              )}
            >
              Price ↓
            </button>
          </div>

          {/* Full sort dropdown */}
          <select
            value={sort}
            onChange={e => onSortChange(e.target.value)}
            className="text-xs bg-zinc-900 border border-zinc-800 text-zinc-400 rounded-md px-2.5 py-1.5 focus:outline-none focus:border-zinc-600 hover:border-zinc-700 transition-colors cursor-pointer"
          >
            {SORT_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* States */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 9 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : !searched ? (
        <div className="flex flex-col items-center justify-center py-28 gap-4 text-center">
          <div className="h-14 w-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center">
            <Search className="h-6 w-6 text-zinc-600" />
          </div>
          <div>
            <p className="text-zinc-300 font-medium text-sm">Ready to search</p>
            <p className="text-xs text-zinc-600 mt-1">Select your filters then click Search PCs</p>
          </div>
        </div>
      ) : results.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-28 gap-4 text-center">
          <div className="h-14 w-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center">
            <Monitor className="h-6 w-6 text-zinc-600" />
          </div>
          <div>
            <p className="text-zinc-300 font-medium text-sm">No results found</p>
            <p className="text-xs text-zinc-600 mt-1">Try wider filters or a higher price range</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {results.map(listing => (
            <PCCard key={listing.id} listing={listing} />
          ))}
        </div>
      )}
    </div>
  )
}
