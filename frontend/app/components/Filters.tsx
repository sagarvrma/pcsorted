"use client"

import { Loader2, Search, SlidersHorizontal, X } from "lucide-react"
import { Checkbox } from "@/components/ui/checkbox"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import { PRICE_MAX, type FilterState } from "@/app/types"

const GPU_GROUPS = [
  {
    label: "RTX 50 Series",
    options: ["RTX 5090", "RTX 5080", "RTX 5070 Ti", "RTX 5070", "RTX 5060 Ti", "RTX 5060"],
  },
  {
    label: "RTX 40 Series",
    options: ["RTX 4090", "RTX 4080 Super", "RTX 4080", "RTX 4070 Ti Super", "RTX 4070 Ti", "RTX 4070 Super", "RTX 4070", "RTX 4060 Ti", "RTX 4060"],
  },
  {
    label: "RTX 30 Series",
    options: ["RTX 3090", "RTX 3080 Ti", "RTX 3080", "RTX 3070 Ti", "RTX 3070", "RTX 3060 Ti", "RTX 3060"],
  },
  {
    label: "RX 7000 Series",
    options: ["RX 7900 XTX", "RX 7900 XT", "RX 7800 XT", "RX 7700 XT", "RX 7600"],
  },
  {
    label: "RX 6000 Series",
    options: ["RX 6900 XT", "RX 6800 XT", "RX 6700 XT", "RX 6600 XT", "RX 6600"],
  },
]

const CPU_GROUPS = [
  {
    label: "Intel Core",
    options: ["Core Ultra 9", "Core Ultra 7", "Core Ultra 5", "i9", "i7", "i5", "i3"],
  },
  {
    label: "AMD Ryzen",
    options: ["Ryzen 9", "Ryzen 7", "Ryzen 5"],
  },
]

interface SectionProps {
  title: string
  count?: number
  children: React.ReactNode
}

function FilterSection({ title, count, children }: SectionProps) {
  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between h-5">
        <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-widest">{title}</span>
        {count != null && count > 0 && (
          <span className="text-[10px] font-medium bg-zinc-700/80 text-zinc-300 rounded-full px-1.5 py-0.5 min-w-[1.25rem] text-center leading-none">
            {count}
          </span>
        )}
      </div>
      {children}
    </div>
  )
}

interface CheckItemProps {
  id: string
  label: string
  checked: boolean
  onChange: () => void
}

function CheckItem({ id, label, checked, onChange }: CheckItemProps) {
  return (
    <div className="flex items-center gap-2.5">
      <Checkbox id={id} checked={checked} onCheckedChange={onChange} />
      <Label
        htmlFor={id}
        className={cn(
          "text-sm font-normal cursor-pointer transition-colors",
          checked ? "text-zinc-100" : "text-zinc-500 hover:text-zinc-300"
        )}
      >
        {label}
      </Label>
    </div>
  )
}

interface FiltersProps {
  filters: FilterState
  onChange: (filters: FilterState) => void
  onSearch: () => void
  loading: boolean
}

export default function FilterPanel({ filters, onChange, onSearch, loading }: FiltersProps) {
  const set = <K extends keyof FilterState>(key: K, value: FilterState[K]) =>
    onChange({ ...filters, [key]: value })

  const toggle = (key: "gpus" | "cpus" | "conditions" | "sources", value: string) => {
    const arr = filters[key] as string[]
    set(key, arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value])
  }

  const clearAll = () =>
    onChange({
      gpus: [], cpus: [], minPrice: 0, maxPrice: PRICE_MAX,
      minRam: "", conditions: [], sources: [], deviceType: "",
      sort: filters.sort,
    })

  const activeCount =
    filters.gpus.length + filters.cpus.length + filters.conditions.length +
    filters.sources.length + (filters.deviceType ? 1 : 0) + (filters.minRam ? 1 : 0) +
    (filters.minPrice > 0 || filters.maxPrice < PRICE_MAX ? 1 : 0)

  const priceLabel =
    filters.minPrice === 0 && filters.maxPrice >= PRICE_MAX
      ? "Any price"
      : filters.maxPrice >= PRICE_MAX
      ? `$${filters.minPrice.toLocaleString()}+`
      : `$${filters.minPrice.toLocaleString()} – $${filters.maxPrice.toLocaleString()}`

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 h-12 border-b border-zinc-800 flex-shrink-0">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-3.5 w-3.5 text-zinc-500" />
          <span className="text-sm font-medium text-zinc-300">Filters</span>
          {activeCount > 0 && (
            <span className="text-[10px] font-medium bg-zinc-700 text-zinc-300 rounded-full px-1.5 py-0.5">
              {activeCount}
            </span>
          )}
        </div>
        {activeCount > 0 && (
          <button
            onClick={clearAll}
            className="flex items-center gap-1 text-xs text-zinc-600 hover:text-zinc-300 transition-colors"
          >
            <X className="h-3 w-3" /> Clear
          </button>
        )}
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">

        {/* Device Type */}
        <FilterSection title="Device">
          <div className="flex rounded-md border border-zinc-800 overflow-hidden text-xs">
            {[
              { value: "", label: "All" },
              { value: "desktop", label: "Desktop" },
              { value: "laptop", label: "Laptop" },
            ].map(opt => (
              <button
                key={opt.value}
                onClick={() => set("deviceType", opt.value)}
                className={cn(
                  "flex-1 py-1.5 font-medium transition-colors",
                  filters.deviceType === opt.value
                    ? "bg-zinc-700 text-zinc-100"
                    : "bg-transparent text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/60"
                )}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </FilterSection>

        <Separator />

        {/* GPU */}
        <FilterSection title="GPU" count={filters.gpus.length}>
          <div className="max-h-56 overflow-y-auto space-y-3.5 pr-0.5">
            {GPU_GROUPS.map(group => (
              <div key={group.label}>
                <p className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold mb-1.5">
                  {group.label}
                </p>
                <div className="space-y-1.5">
                  {group.options.map(gpu => (
                    <CheckItem
                      key={gpu}
                      id={`gpu-${gpu}`}
                      label={gpu}
                      checked={filters.gpus.includes(gpu)}
                      onChange={() => toggle("gpus", gpu)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </FilterSection>

        <Separator />

        {/* CPU */}
        <FilterSection title="CPU" count={filters.cpus.length}>
          <div className="space-y-3.5">
            {CPU_GROUPS.map(group => (
              <div key={group.label}>
                <p className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold mb-1.5">
                  {group.label}
                </p>
                <div className="space-y-1.5">
                  {group.options.map(cpu => (
                    <CheckItem
                      key={cpu}
                      id={`cpu-${cpu}`}
                      label={cpu}
                      checked={filters.cpus.includes(cpu)}
                      onChange={() => toggle("cpus", cpu)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </FilterSection>

        <Separator />

        {/* Price */}
        <FilterSection title="Price Range">
          <div className="space-y-3">
            <div className="text-xs text-zinc-400">{priceLabel}</div>
            <Slider
              min={0}
              max={PRICE_MAX}
              step={50}
              value={[filters.minPrice, filters.maxPrice]}
              onValueChange={([min, max]) => onChange({ ...filters, minPrice: min, maxPrice: max })}
            />
            <div className="flex gap-2">
              <div className="relative flex-1">
                <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-600 text-xs pointer-events-none">$</span>
                <input
                  type="number"
                  value={filters.minPrice === 0 ? "" : filters.minPrice}
                  onChange={e => set("minPrice", e.target.value ? Math.max(0, parseInt(e.target.value)) : 0)}
                  placeholder="Min"
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-md pl-5 pr-2 py-1.5 text-xs text-zinc-300 placeholder-zinc-700 focus:outline-none focus:border-zinc-600 transition-colors"
                />
              </div>
              <div className="relative flex-1">
                <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-600 text-xs pointer-events-none">$</span>
                <input
                  type="number"
                  value={filters.maxPrice >= PRICE_MAX ? "" : filters.maxPrice}
                  onChange={e => set("maxPrice", e.target.value ? parseInt(e.target.value) : PRICE_MAX)}
                  placeholder="Max"
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-md pl-5 pr-2 py-1.5 text-xs text-zinc-300 placeholder-zinc-700 focus:outline-none focus:border-zinc-600 transition-colors"
                />
              </div>
            </div>
          </div>
        </FilterSection>

        <Separator />

        {/* RAM */}
        <FilterSection title="Min RAM">
          <select
            value={filters.minRam}
            onChange={e => set("minRam", e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 text-zinc-300 text-sm rounded-md px-3 py-1.5 focus:outline-none focus:border-zinc-600 hover:border-zinc-700 transition-colors cursor-pointer"
          >
            <option value="">Any RAM</option>
            {[8, 16, 32, 64].map(r => (
              <option key={r} value={r}>{r}GB+</option>
            ))}
          </select>
        </FilterSection>

        <Separator />

        {/* Condition */}
        <FilterSection title="Condition" count={filters.conditions.length}>
          <div className="space-y-1.5">
            {[
              { value: "new", label: "New" },
              { value: "refurbished", label: "Refurbished" },
              { value: "used", label: "Used" },
            ].map(c => (
              <CheckItem
                key={c.value}
                id={`cond-${c.value}`}
                label={c.label}
                checked={filters.conditions.includes(c.value)}
                onChange={() => toggle("conditions", c.value)}
              />
            ))}
          </div>
        </FilterSection>

        <Separator />

        {/* Source */}
        <FilterSection title="Source" count={filters.sources.length}>
          <div className="space-y-1.5">
            {[
              { value: "ebay", label: "eBay" },
              { value: "bestbuy", label: "Best Buy" },
              { value: "newegg", label: "Newegg" },
              { value: "walmart", label: "Walmart" },
            ].map(s => (
              <CheckItem
                key={s.value}
                id={`src-${s.value}`}
                label={s.label}
                checked={filters.sources.includes(s.value)}
                onChange={() => toggle("sources", s.value)}
              />
            ))}
          </div>
        </FilterSection>

      </div>

      {/* Sticky search button */}
      <div className="p-4 border-t border-zinc-800 flex-shrink-0">
        <button
          onClick={onSearch}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 h-9 rounded-md bg-zinc-100 text-zinc-900 text-sm font-semibold hover:bg-white transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? (
            <><Loader2 className="h-4 w-4 animate-spin" /> Searching...</>
          ) : (
            <><Search className="h-4 w-4" /> Search PCs</>
          )}
        </button>
      </div>
    </div>
  )
}
