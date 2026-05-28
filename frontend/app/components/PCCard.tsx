"use client"

import { useState } from "react"
import { ExternalLink, Monitor, Cpu, MemoryStick, HardDrive, Zap } from "lucide-react"
import { Badge, badgeVariants } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Listing } from "@/app/types"
import type { VariantProps } from "class-variance-authority"

const SOURCE_VARIANT: Record<string, VariantProps<typeof badgeVariants>["variant"]> = {
  ebay: "ebay",
  "best buy": "bestbuy",
  bestbuy: "bestbuy",
  newegg: "newegg",
  walmart: "walmart",
  "b&h": "bhphoto",
  bhphotovideo: "bhphoto",
}

const SOURCE_LABEL: Record<string, string> = {
  ebay: "eBay",
  "best buy": "Best Buy",
  bestbuy: "Best Buy",
  newegg: "Newegg",
  walmart: "Walmart",
  "b&h": "B&H",
  bhphotovideo: "B&H Photo",
}

const CONDITION_VARIANT: Record<string, VariantProps<typeof badgeVariants>["variant"]> = {
  new: "new",
  refurbished: "refurbished",
  used: "used",
}

function formatPrice(n: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n)
}

function formatStorage(gb: number) {
  if (gb >= 1000 && gb % 1000 === 0) return `${gb / 1000}TB`
  if (gb >= 1000) return `${(gb / 1000).toFixed(1)}TB`
  return `${gb}GB`
}

export default function PCCard({ listing }: { listing: Listing }) {
  const [imgFailed, setImgFailed] = useState(false)

  const srcKey = listing.source?.toLowerCase() ?? ""
  const condKey = listing.condition?.toLowerCase() ?? ""
  const showCondition = condKey && condKey !== "new"

  return (
    <article className="group flex flex-col rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden transition-all duration-200 hover:border-zinc-700 hover:shadow-xl hover:shadow-black/40">
      {/* Image */}
      <div className="relative h-44 bg-zinc-950 flex items-center justify-center overflow-hidden flex-shrink-0">
        {listing.image_url && !imgFailed ? (
          <img
            src={listing.image_url}
            alt={listing.title}
            className="w-full h-full object-contain p-3 transition-transform duration-300 group-hover:scale-[1.04]"
            onError={() => setImgFailed(true)}
          />
        ) : (
          <Monitor className="h-10 w-10 text-zinc-700" strokeWidth={1.5} />
        )}
        {!listing.in_stock && (
          <div className="absolute inset-0 bg-zinc-950/75 flex items-center justify-center">
            <span className="text-xs text-zinc-500 border border-zinc-700 px-2 py-0.5 rounded-full">
              Out of Stock
            </span>
          </div>
        )}
      </div>

      {/* Body */}
      <div className="flex flex-col flex-1 p-4 gap-3">
        {/* Badges row */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <Badge variant={SOURCE_VARIANT[srcKey] ?? "default"}>
            {SOURCE_LABEL[srcKey] ?? listing.source}
          </Badge>
          {showCondition && (
            <Badge variant={CONDITION_VARIANT[condKey] ?? "default"} className="capitalize">
              {listing.condition}
            </Badge>
          )}
        </div>

        {/* Title */}
        <h3 className="text-sm font-medium text-zinc-200 leading-snug line-clamp-2 min-h-[2.5rem]">
          {listing.title}
        </h3>

        {/* Price */}
        <p className="text-2xl font-bold text-white tabular-nums tracking-tight">
          {formatPrice(listing.current_price)}
        </p>

        {/* Spec chips */}
        <div className="flex flex-wrap gap-1.5">
          {listing.gpu && (
            <span className={cn(badgeVariants({ variant: "spec" }), "gap-1 flex items-center")}>
              <Zap className="h-2.5 w-2.5 flex-shrink-0" />
              {listing.gpu}
            </span>
          )}
          {listing.cpu && (
            <span className={cn(badgeVariants({ variant: "spec" }), "gap-1 flex items-center")}>
              <Cpu className="h-2.5 w-2.5 flex-shrink-0" />
              {listing.cpu}
            </span>
          )}
          {listing.ram_gb && (
            <span className={cn(badgeVariants({ variant: "spec" }), "gap-1 flex items-center")}>
              <MemoryStick className="h-2.5 w-2.5 flex-shrink-0" />
              {listing.ram_gb}GB
            </span>
          )}
          {listing.storage_gb && (
            <span className={cn(badgeVariants({ variant: "spec" }), "gap-1 flex items-center")}>
              <HardDrive className="h-2.5 w-2.5 flex-shrink-0" />
              {formatStorage(listing.storage_gb)}
            </span>
          )}
        </div>

        {/* CTA */}
        <a
          href={listing.url}
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            "mt-auto flex items-center justify-center gap-1.5 w-full h-8 rounded-md border text-xs font-medium transition-colors",
            listing.in_stock
              ? "border-zinc-700 text-zinc-300 hover:border-zinc-500 hover:text-white hover:bg-zinc-800"
              : "border-zinc-800 text-zinc-600 pointer-events-none"
          )}
          aria-disabled={!listing.in_stock}
          tabIndex={listing.in_stock ? 0 : -1}
        >
          View Deal
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </article>
  )
}
