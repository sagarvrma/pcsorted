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

export interface Filters {
  q: string
  gpu: string
  cpu: string
  min_price: string
  max_price: string
  min_ram: string
  min_storage: string
  source: string
  condition: string
  device_type: string
  sort: string
}

export interface NLPResponse {
  filters: {
    max_price: number | null
    min_price: number | null
    min_ram_gb: number | null
    min_storage_gb: number | null
    gpu: string | null
    cpu: string | null
    condition: string | null
    device_type: string | null
    reasoning: string
  }
  reasoning: string
}