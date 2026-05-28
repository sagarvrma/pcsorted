export interface Listing {
  id: string
  source: string
  title: string
  url: string
  image_url: string | null
  brand: string | null
  device_type: string | null
  condition: string | null
  in_stock: boolean
  cpu: string | null
  gpu: string | null
  ram_gb: number | null
  storage_gb: number | null
  current_price: number
  last_seen_at: string
}

export interface SearchResponse {
  total: number
  offset: number
  limit: number
  results: Listing[]
}

export const PRICE_MAX = 10000

export interface FilterState {
  gpus: string[]
  cpus: string[]
  minPrice: number
  maxPrice: number
  minRam: string
  conditions: string[]
  sources: string[]
  deviceType: string
  sort: string
}

export const DEFAULT_FILTERS: FilterState = {
  gpus: [],
  cpus: [],
  minPrice: 0,
  maxPrice: PRICE_MAX,
  minRam: "",
  conditions: [],
  sources: [],
  deviceType: "",
  sort: "price_asc",
}
