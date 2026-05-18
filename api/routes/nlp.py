from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SYSTEM_PROMPT = """
You are a PC shopping assistant. Convert natural language queries into structured filter JSON.
Return ONLY valid JSON, no explanation, no markdown.

Schema:
{
  "max_price": number | null,
  "min_price": number | null,
  "min_ram_gb": number | null,
  "min_storage_gb": number | null,
  "gpu": string | null,
  "cpu": string | null,
  "condition": "new" | "refurbished" | "used" | null,
  "device_type": "desktop" | "laptop" | null,
  "reasoning": string
}

Examples:
Input: "PC my kid can play Fortnite on under $800"
Output: {"max_price": 800, "min_price": null, "min_ram_gb": 16, "min_storage_gb": 512, "gpu": "RTX 4060", "cpu": "i5", "condition": null, "device_type": "desktop", "reasoning": "Fortnite runs well on mid-range GPUs. RTX 4060 handles 1080p gaming easily. 16GB RAM and 512GB SSD are the sweet spot under $800."}

Input: "cheap refurbished desktop for office work"
Output: {"max_price": 400, "min_price": null, "min_ram_gb": 8, "min_storage_gb": 256, "gpu": null, "cpu": "i5", "condition": "refurbished", "device_type": "desktop", "reasoning": "Office work doesn't need a GPU. A refurbished i5 with 8GB RAM and 256GB SSD handles Word, Excel, and browsing easily under $400."}
"""

class NLPRequest(BaseModel):
    query: str

@router.post("/nlp")
def nlp_search(body: NLPRequest):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": body.query}
        ],
        max_tokens=300,
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()

    try:
        filters = json.loads(raw)
    except json.JSONDecodeError:
        raw = raw.replace("```json", "").replace("```", "").strip()
        filters = json.loads(raw)

    return {"filters": filters, "reasoning": filters.get("reasoning", "")}