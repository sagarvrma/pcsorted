import re

GPU_TIERS = {
    'RTX 5090': 100, 'RTX 5080': 95, 'RTX 5070 Ti': 90, 'RTX 5070': 85,
    'RTX 4090': 88, 'RTX 4080 Super': 83, 'RTX 4080': 80, 'RTX 4070 Ti Super': 75,
    'RTX 4070 Ti': 72, 'RTX 4070 Super': 68, 'RTX 4070': 65, 'RTX 4060 Ti': 58,
    'RTX 4060': 52, 'RTX 3090': 70, 'RTX 3080': 65, 'RTX 3070': 58,
    'RTX 3060 Ti': 52, 'RTX 3060': 45, 'RX 7900 XTX': 85, 'RX 7900 XT': 78,
    'RX 7800 XT': 62, 'RX 7700 XT': 55, 'RX 6800 XT': 65, 'RX 6700 XT': 55,
}

CPU_TIERS = {
    'i9': 90, 'i7': 75, 'i5': 60, 'i3': 40,
    'Ryzen 9': 90, 'Ryzen 7': 75, 'Ryzen 5': 60, 'Ryzen 3': 40,
}

def extract_ram(title):
    match = re.search(r'(\d+)\s*GB\s*(DDR\d)?(?:\s*RAM)?', title, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        if val in [4, 8, 16, 32, 64, 128]:
            return val
    return None

def extract_storage(title):
    title_lower = title.lower()
    pattern = r'(\d+)\s*(tb|gb)\s*(?:ssd|hdd|nvme|m\.2)?'
    matches = re.findall(pattern, title_lower)
    valid = []
    for size, unit in matches:
        size = int(size)
        if unit == 'tb':
            size_gb = size * 1024
        else:
            size_gb = size
        if 120 <= size_gb <= 8192:
            valid.append(size_gb)
    return max(valid) if valid else None

def extract_gpu(title):
    title_upper = title.upper()
    for gpu in GPU_TIERS:
        gpu_clean = gpu.upper().replace(' ', '').replace('-', '')
        title_clean = title_upper.replace(' ', '').replace('-', '')
        if gpu_clean in title_clean:
            return gpu
    return None

def extract_cpu(title):
    title_lower = title.lower()
    for cpu in CPU_TIERS:
        if cpu.lower() in title_lower:
            return cpu
    return None

def extract_brand(title):
    brands = ['HP', 'Dell', 'ASUS', 'Acer', 'MSI', 'Lenovo',
              'CyberPowerPC', 'iBUYPOWER', 'Apple', 'Samsung', 'LG']
    title_lower = title.lower()
    for brand in brands:
        if brand.lower() in title_lower:
            return brand
    return 'Generic'

def extract_condition(title):
    title_lower = title.lower()
    if 'refurb' in title_lower:
        return 'refurbished'
    if 'used' in title_lower:
        return 'used'
    return 'new'

def extract_device_type(title):
    title_lower = title.lower()
    if 'laptop' in title_lower or 'notebook' in title_lower:
        return 'laptop'
    if any(w in title_lower for w in ['desktop', 'tower', 'gaming pc', 'prebuilt']):
        return 'desktop'
    return 'unknown'

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