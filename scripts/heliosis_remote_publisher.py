#!/usr/bin/env python3
"""
Heliosis Terminal - Autonomous Playwright X Publisher
Connects live market funding & arbitrage data from heliosis.xyz directly to Twitter (X).
Uses existing authenticated session cookies on Mini PC (192.168.1.143).
"""

import asyncio
import os
import sys
import json
import urllib.request
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "245e01bd4a10b981afc2447bf778681288db579d").strip()
CT0 = os.getenv("CT0", "954e75ce434c723980f318c560bee18f589a880d10fefa4dd5efb2dbbbd548ee5c0dc18413183d17de5e96b977ef545755e921b0d625a4990087eb9199f6f845dd214880a5b91008320a8f2c9a5e211d").strip()
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

API_URL = "https://heliosis.xyz/data/latest.json"
SITE_URL = "https://heliosis.xyz"
BYBIT_INVITE = "https://www.bybit.com/invite?ref=71XNO1"

def fetch_heliosis_data():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0 (HeliosisBot/1.0)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def generate_tweet(data):
    arbs = data.get("top_arbitrage_spreads", [])
    cash = data.get("top_cash_and_carry", [])
    
    if arbs and arbs[0].get("spread_apr_pct", 0) >= 15.0:
        top = arbs[0]
        sym = top.get("base_asset", "CRYPTO")
        spread_apr = top.get("spread_apr_pct", 0)
        b_rate = top.get("binance_rate_pct", 0)
        y_rate = top.get("bybit_rate_pct", 0)
        strat = top.get("strategy", "Delta-Neutral Spread")
        
        tweet = (
            f"⚡ HELIOSIS QUANT ARBITRAGE ALERT ⚡\n\n"
            f"Asset: ${sym}\n"
            f"📈 Spread APR: +{spread_apr:,.1f}%\n"
            f"🔹 Binance: {b_rate:+.4f}%\n"
            f"🔹 Bybit: {y_rate:+.4f}%\n"
            f"💡 Strategy: {strat}\n\n"
            f"📊 Live Screener: {SITE_URL}\n"
            f"🎁 Bybit $6,135 Bonus: {BYBIT_INVITE}\n\n"
            f"#{sym} #CryptoArbitrage #Binance #Bybit $BTC"
        )
    elif cash and cash[0].get("apr_pct", 0) >= 10.0:
        top = cash[0]
        sym = top.get("base_asset", "CRYPTO")
        apr = top.get("apr_pct", 0)
        rate = top.get("avg_rate_8h_pct", 0)
        
        tweet = (
            f"🌾 CASH & CARRY BASIS YIELD: ${sym}\n\n"
            f"🔥 Annualized APR: +{apr:,.1f}%\n"
            f"⏱️ 8h Funding Rate: {rate:+.4f}%\n"
            f"🛡️ Strategy: Spot Long + 1x Perp Short (Delta-Neutral)\n\n"
            f"📊 Screener: {SITE_URL}\n"
            f"🎁 Claim $6,135 Bonus: {BYBIT_INVITE}\n\n"
            f"#{sym} #DeltaNeutral #CryptoYield $SOL $BTC"
        )
    else:
        tweet = (
            f"⚡ HELIOSIS QUANT TERMINAL ⚡\n\n"
            f"Autonomous Crypto Funding & Basis Yield Screener.\n"
            f"Live 950+ Perpetual Pairs on Binance & Bybit.\n\n"
            f"📊 Screener: {SITE_URL}\n"
            f"🎁 Bybit $6,135 Bonus: {BYBIT_INVITE}\n\n"
            f"#CryptoArbitrage #Binance #Bybit $BTC"
        )
    return tweet

async def post_to_x(text, image_path=None):
    print("🌐 Headless Chromium başlatılıyor...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ]
        )
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800},
            locale="tr-TR"
        )
        
        # Inject Cookies
        cookies = [
            {"name": "auth_token", "value": AUTH_TOKEN, "domain": ".x.com", "path": "/", "secure": True, "httpOnly": True},
            {"name": "ct0", "value": CT0, "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False}
        ]
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        print("🔗 https://x.com/home adresine gidiliyor...")
        await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=35000)
        await asyncio.sleep(5)
        
        if "login" in page.url or "i/flow/login" in page.url:
            print("❌ Oturum açılamadı, çerezler geçersiz!")
            await browser.close()
            return False
            
        print("✅ Oturum doğrulandı!")
        
        # Turkish & English X Selectors
        selectors = [
            'div[aria-label="Gönderi metni"]',
            'div[aria-label="Post text"]',
            'div[aria-label="Tweet metni"]',
            '[data-testid="tweetTextarea_0"]',
            'div[role="textbox"][contenteditable="true"]',
            'div:has-text("Neler oluyor?")'
        ]
        
        tweet_box = None
        for sel in selectors:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=2000):
                    tweet_box = el
                    print(f"🎯 Metin kutusu bulundu: {sel}")
                    break
            except:
                continue
                
        # If not found directly, click "Gönderi yayınla" button on left sidebar to open compose modal
        if not tweet_box:
            print("💡 Kenar çubuğundaki 'Gönderi yayınla' butonuna tıklanıyor...")
            try:
                side_btn = page.locator('a[data-testid="SideNav_NewTweet_Button"], button:has-text("Gönderi yayınla")').first
                if await side_btn.is_visible(timeout=3000):
                    await side_btn.click()
                    await asyncio.sleep(2)
                    for sel in selectors:
                        el = page.locator(sel).first
                        if await el.is_visible(timeout=2000):
                            tweet_box = el
                            print(f"🎯 Modal kutusu bulundu: {sel}")
                            break
            except Exception as e_btn:
                print(f"Kenar butonu denemesi: {e_btn}")
                
        if not tweet_box:
            print("⚠️ Compose URL deneniyor...")
            await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
            for sel in selectors:
                try:
                    el = page.locator(sel).first
                    if await el.is_visible(timeout=2000):
                        tweet_box = el
                        break
                except:
                    continue
                    
        if not tweet_box:
            print("❌ Tweet yazma alanı bulunamadı!")
            await page.screenshot(path=os.path.join(BASE_DIR, "box_not_found.png"))
            await browser.close()
            return False
            
        print("✍️ Tweet metni giriliyor...")
        await tweet_box.click()
        await asyncio.sleep(0.5)
        await tweet_box.fill(text)
        await asyncio.sleep(1.5)
        
        if image_path and os.path.exists(image_path):
            print(f"📸 Görsel ekleniyor: {image_path}")
            try:
                file_input = page.locator('input[data-testid="fileInput"]').first
                if await file_input.count() > 0:
                    await file_input.set_input_files(image_path)
                await asyncio.sleep(4)
            except Exception as e_img:
                print(f"⚠️ Görsel yüklenirken hata: {e_img}")
                
        print("🚀 Tweet gönderiliyor...")
        # 1. Native shortcut
        await page.keyboard.press("Control+Enter")
        await asyncio.sleep(3)
        
        # 2. Button fallback
        btn_selectors = [
            '[data-testid="tweetButtonInline"]',
            '[data-testid="tweetButton"]',
            'button:has-text("Gönderi yayınla")',
            'button:has-text("Post")',
            'button:has-text("Gönder")'
        ]
        for b_sel in btn_selectors:
            try:
                b = page.locator(b_sel).first
                if await b.is_visible(timeout=2000):
                    await b.click(force=True, timeout=4000)
                    print(f"✅ Gönder butonuna tıklandı: {b_sel}")
                    await asyncio.sleep(4)
                    break
            except:
                continue
                
        await page.screenshot(path=os.path.join(BASE_DIR, "heliosis_tweet_posted.png"))
        await browser.close()
        print("🎉 Tweet X üzerinde başarıyla yayınlandı!")
        return True

async def main():
    print(f"\n==========================================")
    print(f"⚡ Heliosis Terminal X Bot Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==========================================")
    
    try:
        data = fetch_heliosis_data()
        tweet_text = generate_tweet(data)
        print("📌 Hazırlanan Tweet Metni:\n")
        print(tweet_text)
        print("------------------------------------------")
        
        success = await post_to_x(tweet_text)
        if success:
            print("🎉 İşlem başarıyla tamamlandı!")
        else:
            print("❌ Paylaşım başarısız.")
    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
