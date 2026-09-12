#!/usr/bin/env python3
"""
Heliosis Terminal - Market Data Automation Engine
Fetches live funding rates, calculates annualized basis yields & cross-exchange arbitrage spreads.
Zero external pip dependencies (standard library only).
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Major high-liquidity symbols to track primarily + dynamic top volume list
FEATURED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", 
    "SUIUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "NEARUSDT", "APTUSDT", 
    "PEPEUSDT", "WIFUSDT", "SHIBUSDT", "LTCUSDT", "DOTUSDT", "OPUSDT", 
    "ARBUSDT", "INJUSDT", "TIAUSDT", "SEIUSDT", "FETUSDT", "RENDERUSDT",
    "TAOUSDT", "KASUSDT", "AAVEUSDT", "UNIUSDT", "MKRUSDT", "PENDLEUSDT"
]

def fetch_json(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARN] Error fetching {url}: {e}", file=sys.stderr)
    return None

def get_binance_data():
    """Fetch Binance USDT-M Perpetual premium index (funding & prices)."""
    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    raw = fetch_json(url)
    if not raw:
        return {}
    
    data = {}
    for item in raw:
        sym = item.get("symbol", "")
        if not sym.endswith("USDT"):
            continue
        try:
            rate = float(item.get("lastFundingRate", 0.0))
            mark = float(item.get("markPrice", 0.0))
            index_p = float(item.get("indexPrice", 0.0))
            next_time = int(item.get("nextFundingTime", 0))
            data[sym] = {
                "rate": rate,
                "mark_price": mark,
                "index_price": index_p,
                "next_settlement_ms": next_time
            }
        except (ValueError, TypeError):
            continue
    return data

def get_bybit_data():
    """Fetch Bybit Linear Tickers (funding & prices)."""
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    raw = fetch_json(url)
    if not raw or "result" not in raw or "list" not in raw["result"]:
        return {}
    
    data = {}
    for item in raw["result"]["list"]:
        sym = item.get("symbol", "")
        if not sym.endswith("USDT"):
            continue
        try:
            rate = float(item.get("fundingRate", 0.0))
            mark = float(item.get("markPrice", 0.0))
            index_p = float(item.get("indexPrice", 0.0))
            next_time = int(item.get("nextFundingTime", 0))
            data[sym] = {
                "rate": rate,
                "mark_price": mark,
                "index_price": index_p,
                "next_settlement_ms": next_time
            }
        except (ValueError, TypeError):
            continue
    return data

def calculate_yields(rate_8h):
    """
    Given an 8-hour funding rate (as decimal, e.g. 0.0001 = 0.01%):
    - Annualized Percentage Rate (APR) = rate * 3 settlements/day * 365 days
    - Annualized Percentage Yield (APY) = (1 + rate)^(3 * 365) - 1
    """
    apr = rate_8h * 3 * 365 * 100  # in %
    try:
        if rate_8h > -0.5:
            apy = ((1 + rate_8h) ** (3 * 365) - 1) * 100
        else:
            apy = apr
    except OverflowError:
        apy = 9999.99
    return round(apr, 2), round(apy, 2)

def build_dataset():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Fetching market data...")
    binance = get_binance_data()
    bybit = get_bybit_data()
    
    all_symbols = set(binance.keys()).union(set(bybit.keys()))
    print(f"Total symbols found: Binance={len(binance)}, Bybit={len(bybit)}, Union={len(all_symbols)}")
    
    unified_list = []
    arbitrage_list = []
    
    for sym in all_symbols:
        b_data = binance.get(sym)
        y_data = bybit.get(sym)
        
        base_asset = sym.replace("USDT", "")
        
        # Primary reference price & rate
        ref_price = (b_data["mark_price"] if b_data else (y_data["mark_price"] if y_data else 0.0))
        b_rate = b_data["rate"] if b_data else None
        y_rate = y_data["rate"] if y_data else None
        
        # Calculate rates
        b_rate_pct = round(b_rate * 100, 4) if b_rate is not None else None
        y_rate_pct = round(y_rate * 100, 4) if y_rate is not None else None
        
        # Average rate for APR estimation
        rates = [r for r in (b_rate, y_rate) if r is not None]
        avg_rate = sum(rates) / len(rates) if rates else 0.0
        apr, apy = calculate_yields(avg_rate)
        
        # Next funding time
        next_funding_ms = (b_data["next_settlement_ms"] if b_data else 
                           (y_data["next_settlement_ms"] if y_data else 0))
        
        entry = {
            "symbol": sym,
            "base_asset": base_asset,
            "price": ref_price,
            "binance_rate_pct": b_rate_pct,
            "bybit_rate_pct": y_rate_pct,
            "avg_rate_8h_pct": round(avg_rate * 100, 4),
            "apr_pct": apr,
            "apy_pct": apy,
            "next_settlement_ms": next_funding_ms,
            "is_featured": sym in FEATURED_SYMBOLS
        }
        unified_list.append(entry)
        
        # Check cross-exchange arbitrage if both exchanges exist
        if b_rate is not None and y_rate is not None:
            spread_8h = b_rate - y_rate
            abs_spread_8h = abs(spread_8h)
            spread_apr, _ = calculate_yields(abs_spread_8h)
            
            if abs_spread_8h >= 0.0001:  # Spread >= 0.01% per 8h (>10% APR)
                if spread_8h > 0:
                    strategy = "Short Binance / Long Bybit"
                else:
                    strategy = "Short Bybit / Long Binance"
                
                arbitrage_list.append({
                    "symbol": sym,
                    "base_asset": base_asset,
                    "price": ref_price,
                    "binance_rate_pct": b_rate_pct,
                    "bybit_rate_pct": y_rate_pct,
                    "spread_8h_pct": round(abs_spread_8h * 100, 4),
                    "spread_apr_pct": spread_apr,
                    "strategy": strategy,
                    "is_featured": sym in FEATURED_SYMBOLS
                })
    
    # Sortings
    # Featured first, then by absolute APR
    unified_list.sort(key=lambda x: (not x["is_featured"], -abs(x["apr_pct"])))
    # Arbitrage sorted by spread APR descending
    arbitrage_list.sort(key=lambda x: -x["spread_apr_pct"])
    
    # Top cash & carry opportunities (positive funding rate: Spot Long + Perp Short)
    cash_carry = [x for x in unified_list if x["apr_pct"] > 5.0 and (x["price"] > 0.0)]
    cash_carry.sort(key=lambda x: -x["apr_pct"])
    
    # Market overview metrics
    positive_count = sum(1 for x in unified_list if x["avg_rate_8h_pct"] > 0)
    negative_count = sum(1 for x in unified_list if x["avg_rate_8h_pct"] < 0)
    neutral_count = len(unified_list) - positive_count - negative_count
    
    market_sentiment = "BULLISH (Longs Pay Shorts)" if positive_count > negative_count else "BEARISH (Shorts Pay Longs)"
    
    now_utc = datetime.now(timezone.utc)
    
    output = {
        "metadata": {
            "title": "Heliosis Terminal - Crypto Basis & Funding Intelligence",
            "domain": "heliosis.xyz",
            "updated_at_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "updated_at_timestamp": int(now_utc.timestamp()),
            "total_pairs_tracked": len(unified_list),
            "arbitrage_opportunities_count": len(arbitrage_list)
        },
        "market_summary": {
            "sentiment": market_sentiment,
            "positive_funding_pairs": positive_count,
            "negative_funding_pairs": negative_count,
            "neutral_pairs": neutral_count,
            "highest_basis_apr": cash_carry[0] if cash_carry else None,
            "highest_arbitrage_spread": arbitrage_list[0] if arbitrage_list else None
        },
        "featured_pairs": [x for x in unified_list if x["is_featured"]],
        "all_pairs": unified_list[:150],  # Keep file light & blazing fast
        "top_cash_and_carry": cash_carry[:25],
        "top_arbitrage_spreads": arbitrage_list[:25]
    }
    
    return output

def main():
    dataset = build_dataset()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    target_file = os.path.join(data_dir, "latest.json")
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Market data successfully written to {target_file}")
    print(f"Tracked: {dataset['metadata']['total_pairs_tracked']} pairs.")
    print(f"Top Arbitrage: {dataset['market_summary']['highest_arbitrage_spread']}")

if __name__ == "__main__":
    main()
