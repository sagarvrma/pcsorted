import re

# GPU tiers for scoring later
GPU_TIERS = {
    'RTX 5090': 100, 'RTX 5080': 95, 'RTX 5070 Ti': 90, 'RTX 5070': 85,
    'RTX 5060 Ti': 80, 'RTX 5060': 75,
    'RTX 4090': 88, 'RTX 4080 Super': 84, 'RTX 4080': 82,
    'RTX 4070 Ti Super': 78, 'RTX 4070 Ti': 75, 'RTX 4070 Super': 70,
    'RTX 4070': 67, 'RTX 4060 Ti': 60, 'RTX 4060': 54,
    'RTX 3090 Ti': 72, 'RTX 3090': 70, 'RTX 3080 Ti': 67,
    'RTX 3080': 65, 'RTX 3070 Ti': 60, 'RTX 3070': 58,
    'RTX 3060 Ti': 52, 'RTX 3060': 46, 'RTX 3050': 38,
    'RX 9070 XT': 82, 'RX 9070': 78,
    'RX 7900 XTX': 86, 'RX 7900 XT': 80, 'RX 7900 GRE': 74,
    'RX 7800 XT': 65, 'RX 7700 XT': 58, 'RX 7600': 48,
    'RX 6950 XT': 72, 'RX 6900 XT': 68, 'RX 6800 XT': 64,
    'RX 6800': 60, 'RX 6700 XT': 54, 'RX 6700': 50,
    'RX 6600 XT': 44, 'RX 6600': 40,
    'Arc A770': 52, 'Arc A750': 46,
}

CPU_TIERS = {
    'Core Ultra 9': 95, 'Core Ultra 7': 85, 'Core Ultra 5': 72,
    'i9': 90, 'i7': 75, 'i5': 60, 'i3': 40,
    'Ryzen 9': 90, 'Ryzen 7': 75, 'Ryzen 5': 60, 'Ryzen 3': 40,
    'Threadripper': 98,
    'Xeon': 70,
}

def extract_gpu(title):
    title_clean = re.sub(r'\s+', ' ', title)

    # Order matters — match longer/more specific strings first
    for gpu in sorted(GPU_TIERS.keys(), key=len, reverse=True):
        # Build flexible pattern: "RTX 4070 Ti" matches "RTX4070Ti", "RTX 4070Ti", "RTX4070 Ti" etc
        pattern = re.sub(r'\s+', r'[\\s\\-]?', re.escape(gpu))
        if re.search(pattern, title_clean, re.IGNORECASE):
            return gpu

    # Fallback patterns for common variants
    # "GeForce RTX XXXX" or "NVIDIA RTX XXXX"
    m = re.search(r'(?:GeForce|NVIDIA)?\s*RTX\s*(\d{4})\s*(Ti\s*Super|Ti\s*Ultra|Super|Ti|XT)?', title_clean, re.IGNORECASE)
    if m:
        num = m.group(1)
        suffix = (' ' + m.group(2).strip()) if m.group(2) else ''
        candidate = f"RTX {num}{suffix}"
        if candidate in GPU_TIERS:
            return candidate

    # "Radeon RX XXXX" variants
    m = re.search(r'(?:Radeon)?\s*RX\s*(\d{4})\s*(XTX|GRE|XT)?', title_clean, re.IGNORECASE)
    if m:
        num = m.group(1)
        suffix = (' ' + m.group(2).strip()) if m.group(2) else ''
        candidate = f"RX {num}{suffix}"
        if candidate in GPU_TIERS:
            return candidate

    return None

def extract_cpu(title):
    title_lower = title.lower()

    # Intel Core Ultra (must check before generic i7/i9)
    if re.search(r'core\s*ultra\s*9', title_lower):
        return 'Core Ultra 9'
    if re.search(r'core\s*ultra\s*7', title_lower):
        return 'Core Ultra 7'
    if re.search(r'core\s*ultra\s*5', title_lower):
        return 'Core Ultra 5'

    # Intel Core iX — match i9, i7, i5, i3 with optional dash or space
    for tier in ['i9', 'i7', 'i5', 'i3']:
        if re.search(rf'\b{tier}[\s\-]?\d{{4,5}}\b', title_lower) or \
           re.search(rf'\bcore\s+{tier}\b', title_lower) or \
           re.search(rf'\b{tier}\b', title_lower):
            return tier

    # AMD Ryzen
    for tier in ['Ryzen 9', 'Ryzen 7', 'Ryzen 5', 'Ryzen 3']:
        if tier.lower() in title_lower:
            return tier

    # Threadripper
    if 'threadripper' in title_lower:
        return 'Threadripper'

    # Xeon
    if 'xeon' in title_lower:
        return 'Xeon'

    return None

def extract_ram(title):
    # Match patterns like: 16GB RAM, 16GB DDR5, 16 GB, 16G RAM
    # Avoid matching storage (512GB SSD etc) by checking context
    matches = re.findall(
        r'(\d+)\s*GB\s*(?:DDR\d|RAM|SDRAM|LPDDR\d)?(?!\s*(?:SSD|HDD|NVMe|M\.2|storage|hard))',
        title, re.IGNORECASE
    )
    for m in matches:
        val = int(m)
        if val in [4, 8, 12, 16, 24, 32, 48, 64, 96, 128]:
            return val

    # Fallback: any GB value that looks like RAM
    m = re.search(r'(\d+)\s*GB\s+(?:DDR|RAM|Memory)', title, re.IGNORECASE)
    if m:
        val = int(m.group(1))
        if val in [4, 8, 12, 16, 24, 32, 48, 64, 96, 128]:
            return val

    return None

def extract_storage(title):
    title_lower = title.lower()
    pattern = r'(\d+(?:\.\d+)?)\s*(tb|gb)\s*(?:ssd|hdd|nvme|m\.2|pcie|sata|hard\s*drive|solid\s*state)?'
    matches = re.findall(pattern, title_lower)

    valid = []
    for size_str, unit in matches:
        size = float(size_str)
        if unit == 'tb':
            size_gb = int(size * 1024)
        else:
            size_gb = int(size)
        # Only count as storage if it's a realistic storage size
        if 120 <= size_gb <= 32768:
            valid.append(size_gb)

    return max(valid) if valid else None

def extract_brand(title):
    brands = [
        'ASUS', 'MSI', 'Alienware', 'Dell', 'HP', 'Lenovo', 'Acer',
        'CyberPowerPC', 'iBUYPOWER', 'NZXT', 'Skytech', 'CLX',
        'Thermaltake', 'MAINGEAR', 'Velztorm', 'Corsair', 'Origin',
        'Falcon Northwest', 'Digital Storm', 'Periphio', 'Hoengager',
        'Apple', 'Samsung', 'LG', 'Razer',
    ]
    title_lower = title.lower()
    for brand in brands:
        if brand.lower() in title_lower:
            return brand
    # First word as fallback
    first_word = title.split()[0] if title.split() else 'Generic'
    return first_word if len(first_word) > 2 else 'Generic'

def extract_condition(title):
    title_lower = title.lower()
    if any(w in title_lower for w in ['refurb', 'refurbished', 'renewed', 'remanufactured']):
        return 'refurbished'
    if any(w in title_lower for w in ['used', 'open box', 'open-box', 'pre-owned', 'preowned']):
        return 'used'
    return 'new'

def extract_device_type(title):
    title_lower = title.lower()
    if any(w in title_lower for w in ['laptop', 'notebook', 'portable']):
        return 'laptop'
    if any(w in title_lower for w in ['desktop', 'tower', 'gaming pc', 'prebuilt', 'pre-built', 'mini pc']):
        return 'desktop'
    return 'desktop'  # default to desktop since that's our focus

def get_gpu_tier(gpu):
    return GPU_TIERS.get(gpu, 0)

def get_cpu_tier(cpu):
    return CPU_TIERS.get(cpu, 0)

def normalize(raw: dict, source: str) -> dict:
    title = raw.get('title', '')
    return {
        'source': source,
        'external_id': raw.get('external_id'),
        'title': title,
        'url': raw.get('url'),
        'image_url': raw.get('image_url'),
        'brand': extract_brand(title),
        'device_type': extract_device_type(title),
        'condition': extract_condition(title),
        'in_stock': raw.get('in_stock', True),
        'cpu': extract_cpu(title),
        'gpu': extract_gpu(title),
        'ram_gb': extract_ram(title),
        'storage_gb': extract_storage(title),
        'current_price': raw.get('price'),
    }