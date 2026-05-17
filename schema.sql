-- Listings table
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    external_id TEXT,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    brand TEXT,
    device_type TEXT,
    condition TEXT,
    in_stock BOOLEAN DEFAULT true,
    cpu TEXT,
    gpu TEXT,
    ram_gb INT,
    storage_gb INT,
    current_price NUMERIC(10,2),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Price history table
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    price NUMERIC(10,2) NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pipeline runs metadata
CREATE TABLE pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    rows_ingested INT DEFAULT 0,
    rows_rejected INT DEFAULT 0,
    duration_seconds NUMERIC(8,2),
    status TEXT,
    ran_at TIMESTAMPTZ DEFAULT NOW()
);

-- User saved listings
CREATE TABLE saved_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    saved_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, listing_id)
);

-- User saved searches
CREATE TABLE saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    name TEXT,
    filters JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_listings_gpu ON listings(gpu);
CREATE INDEX idx_listings_cpu ON listings(cpu);
CREATE INDEX idx_listings_price ON listings(current_price);
CREATE INDEX idx_listings_source ON listings(source);
CREATE INDEX idx_listings_ram ON listings(ram_gb);
CREATE INDEX idx_listings_device_type ON listings(device_type);
CREATE INDEX idx_price_history_listing ON price_history(listing_id, recorded_at DESC);
CREATE INDEX idx_saved_listings_user ON saved_listings(user_id);
CREATE INDEX idx_saved_searches_user ON saved_searches(user_id);