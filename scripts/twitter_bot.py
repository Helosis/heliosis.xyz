#!/usr/bin/env python3
"""
Heliosis Terminal - Autonomous Twitter (X) Bot Engine
Posts high-yield basis arbitrage alerts and funding spikes to Twitter (X).
Uses standard library OAuth 1.0a for zero external dependencies.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Load .env if present
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Environment variables for Twitter API keys (with defaults)
API_KEY = os.environ.get("TWITTER_API_KEY", "hRZAUWTityj7TXqAdrwos8CIE").strip()
API_SECRET = os.environ.get("TWITTER_API_SECRET", "HZec2M2Qf9yaB86XFe8pqc8u1y3s8zTskOqsfJnqGUGIoe0L6s").strip()
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "2096014984878710785-aePUpWgva6X29N8ytksIGbZw5zbf9u").strip()
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "XxW0lwxcIKQfFb1negZ0tuxeZd1a0JxqN5K82NusRoH5U").strip()

# Site & Referral Constants
SITE_URL = "https://heliosis.xyz"
BYBIT_INVITE = "https://www.bybit.com/invite?ref=71XNO1"
BYBIT_CODE = "71XNO1"
BINANCE_CODE = "CPA_00M822DCVK"

def generate_oauth_header(method, url, params=None):
    """Generate OAuth 1.0a Authorization header using only standard library."""
    if not (API_KEY and API_SECRET and ACCESS_TOKEN and ACCESS_TOKEN_SECRET):
        return None

    oauth_params = {
        "oauth_consumer_key": API_KEY,
        "oauth_nonce": base64.b64encode(os.urandom(16)).decode("utf-8").replace("=", "").replace("+", "").replace("/", ""),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ACCESS_TOKEN,
        "oauth_version": "1.0"
    }

    all_params = oauth_params.copy()
    if params:
        all_params.update(params)

    # Sort and encode params
    param_str = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(all_params[k]), safe='')}"
        for k in sorted(all_params.keys())
    )

    base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_str, safe='')}"
    signing_key = f"{urllib.parse.quote(API_SECRET, safe='')}&{urllib.parse.quote(ACCESS_TOKEN_SECRET, safe='')}"

    hashed = hmac.new(signing_key.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode("utf-8")
    oauth_params["oauth_signature"] = signature

    header_val = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(oauth_params[k], safe="")}"'
        for k in sorted(oauth_params.keys())
    )
    return header_val

def post_tweet(tweet_text):
    """Post tweet using Twitter API v2 (POST /2/tweets)."""
    if not (API_KEY and API_SECRET and ACCESS_TOKEN and ACCESS_TOKEN_SECRET):
        print("[DRY-RUN] Twitter API keys not configured. Simulating tweet post:")
        print("--------------------------------------------------")
        print(tweet_text)
        print("--------------------------------------------------")
        print(f"Tweet length: {len(tweet_text)} chars")
        return True

    url = "https://api.twitter.com/2/tweets"

    # Prefer requests_oauthlib if available
    try:
        import requests
        from requests_oauthlib import OAuth1
        auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        resp = requests.post(url, auth=auth, json={"text": tweet_text}, timeout=15)
        if resp.status_code == 201:
            data = resp.json()
            print(f"[SUCCESS] Tweet posted! ID: {data.get('data', {}).get('id')}")
            return True
        else:
            print(f"[ERROR] Twitter API returned status {resp.status_code}: {resp.text}", file=sys.stderr)
            return False
    except ImportError:
        pass

    # Fallback to standard library
    payload = json.dumps({"text": tweet_text}).encode("utf-8")
    auth_header = generate_oauth_header("POST", url)

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "User-Agent": "HeliosisBot/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] Tweet posted! ID: {data.get('data', {}).get('id')}")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to post tweet: {e}", file=sys.stderr)
        if hasattr(e, "read"):
            try:
                print(f"[ERROR DETAILS] {e.read().decode('utf-8')}", file=sys.stderr)
            except Exception:
                pass
        return False


def format_arbitrage_tweet(opp):
    """Construct an engaging high-converting crypto tweet (<280 chars)."""
    sym = opp.get("symbol", "CRYPTO").replace("USDT", "")
    spread_apr = opp.get("spread_apr_pct", 0)
    b_rate = opp.get("binance_rate_pct", 0)
    y_rate = opp.get("bybit_rate_pct", 0)
    strategy = opp.get("strategy", "Delta-Neutral Arbitrage")

    # Keep concise & within 280 characters
    tweet = (
        f"⚡ ARBITRAGE ALERT: ${sym}\n\n"
        f"📈 Spread APR: +{spread_apr:,.1f}%\n"
        f"🔹 Binance: {b_rate:+.4f}%\n"
        f"🔹 Bybit: {y_rate:+.4f}%\n"
        f"💡 {strategy}\n\n"
        f"📊 Live Screener: {SITE_URL}\n"
        f"🎁 Bybit $6,135 Bonus: {BYBIT_INVITE}\n\n"
        f"#{sym} #CryptoArbitrage #Binance #Bybit $BTC"
    )

    # If length exceeds 280, trim hashtags
    if len(tweet) > 280:
        tweet = (
            f"⚡ ARBITRAGE ALERT: ${sym}\n\n"
            f"📈 Spread APR: +{spread_apr:,.1f}%\n"
            f"🔹 Binance: {b_rate:+.4f}%\n"
            f"🔹 Bybit: {y_rate:+.4f}%\n"
            f"💡 {strategy}\n\n"
            f"📊 Terminal: {SITE_URL}\n"
            f"🎁 0% Fees: {BYBIT_INVITE}\n"
            f"#{sym} #Arbitrage"
        )
    return tweet

def format_cash_carry_tweet(item):
    """Construct a Cash & Carry basis yield tweet."""
    sym = item.get("base_asset", "CRYPTO")
    apr = item.get("apr_pct", 0)
    rate = item.get("avg_rate_8h_pct", 0)

    tweet = (
        f"🌾 CASH & CARRY YIELD: ${sym}\n\n"
        f"🔥 Annualized APR: +{apr:,.1f}%\n"
        f"⏱️ 8h Rate: {rate:+.4f}%\n"
        f"🛡️ Strategy: Spot Long + 1x Perp Short (Delta-Neutral)\n\n"
        f"📊 Screener: {SITE_URL}\n"
        f"🎁 Claim $6,135 Bonus: {BYBIT_INVITE}\n\n"
        f"#{sym} #DeltaNeutral #CryptoYield $SOL $BTC"
    )

    if len(tweet) > 280:
        tweet = (
            f"🌾 BASIS YIELD: ${sym}\n\n"
            f"🔥 APR: +{apr:,.1f}%\n"
            f"🛡️ 100% Delta-Neutral\n\n"
            f"📊 Live Screener: {SITE_URL}\n"
            f"🎁 Trade on Bybit: {BYBIT_INVITE}\n"
            f"#{sym} #CryptoYield"
        )
    return tweet

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_file = os.path.join(project_root, "data", "latest.json")

    if not os.path.exists(data_file):
        print(f"[ERROR] Data file not found: {data_file}", file=sys.stderr)
        sys.exit(1)

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    arbs = data.get("top_arbitrage_spreads", [])
    cash = data.get("top_cash_and_carry", [])

    # Pick the best opportunity
    tweet_text = None
    if arbs and arbs[0].get("spread_apr_pct", 0) >= 15.0:
        # Prioritize high cross-exchange spreads
        tweet_text = format_arbitrage_tweet(arbs[0])
    elif cash and cash[0].get("apr_pct", 0) >= 10.0:
        # Fallback to high cash & carry yield
        tweet_text = format_cash_carry_tweet(cash[0])
    elif arbs:
        tweet_text = format_arbitrage_tweet(arbs[0])
    else:
        print("[INFO] No suitable market opportunity to tweet right now.")
        return

    post_tweet(tweet_text)

if __name__ == "__main__":
    main()
