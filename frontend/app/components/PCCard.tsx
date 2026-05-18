'use client'

import { Listing } from '../types'
import { ExternalLink, Cpu, Monitor, HardDrive, MemoryStick } from 'lucide-react'
import Image from 'next/image'

interface Props {
  listing: Listing
}

const SOURCE_COLORS: Record<string, string> = {
  ebay: 'bg-yellow-500/20 text-yellow-300',
  bestbuy: 'bg-blue-500/20 text-blue-300',
  antonline: 'bg-green-500/20 text-green-300',
  newegg: 'bg-orange-500/20 text-orange-300',
}

export default function PCCard({ listing }: Props) {
  return (
    <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl overflow-hidden hover:border-purple-500/40 transition-all hover:shadow-lg hover:shadow-purple-900/20 flex flex-col">
      <div className="relative aspect-square bg-white/5">
        {listing.image_url ? (
          <Image
            src={listing.image_url}
            alt={listing.title}
            fill
            className="object-contain p-4"
            unoptimized
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Monitor className="w-16 h-16 text-white/20" />
          </div>
        )}

        <div className="absolute top-2 right-2">
          <span
            className={`text-xs px-2 py-1 rounded-full font-medium ${
              SOURCE_COLORS[listing.source] || 'bg-white/10 text-white/60'
            }`}
          >
            {listing.source}
          </span>
        </div>

        {listing.condition === 'refurbished' && (
          <div className="absolute top-2 left-2">
            <span className="text-xs px-2 py-1 rounded-full font-medium bg-yellow-500/20 text-yellow-300">
              Refurbished
            </span>
          </div>
        )}
      </div>

      <div className="p-4 flex flex-col flex-1">
        <h3 className="text-white font-medium text-sm line-clamp-2 mb-3 flex-1">
          {listing.title}
        </h3>

        <div className="text-2xl font-bold text-purple-300 mb-3">
          ${listing.current_price.toLocaleString()}
        </div>

        <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
          {listing.gpu && (
            <div className="flex items-center gap-1.5 text-white/60">
              <Monitor className="w-3 h-3" />
              <span className="truncate">{listing.gpu}</span>
            </div>
          )}

          {listing.cpu && (
            <div className="flex items-center gap-1.5 text-white/60">
              <Cpu className="w-3 h-3" />
              <span className="truncate">{listing.cpu}</span>
            </div>
          )}

          {listing.ram_gb && (
            <div className="flex items-center gap-1.5 text-white/60">
              <MemoryStick className="w-3 h-3" />
              <span>{listing.ram_gb}GB RAM</span>
            </div>
          )}

          {listing.storage_gb && (
            <div className="flex items-center gap-1.5 text-white/60">
              <HardDrive className="w-3 h-3" />
              <span>
                {listing.storage_gb >= 1024
                  ? `${listing.storage_gb / 1024}TB`
                  : `${listing.storage_gb}GB`}
              </span>
            </div>
          )}
        </div>

        <a
          href={listing.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full bg-purple-600 hover:bg-purple-700 text-white py-2.5 rounded-xl text-sm font-medium transition-colors"
        >
          View Deal
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  )
}