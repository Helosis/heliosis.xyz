/**
 * HELIOSIS TERMINAL - CONFIGURATION & AFFILIATE SETTINGS
 * Update your referral codes and links below. 
 * All buttons and links across the site will automatically update.
 */

window.HELIOSIS_CONFIG = {
  brandName: "Heliosis Terminal",
  domain: "heliosis.xyz",
  tagline: "Autonomous Crypto Funding & Basis Yield Terminal",
  
  // ==========================================
  // AFFILIATE / MONETIZATION SETTINGS
  // Replace these with your actual referral links / codes
  // ==========================================
  affiliates: {
    bybit: {
      name: "Bybit",
      enabled: true,
      tagline: "VIP 0% Maker Fees + Up to $30,000 Deposit Bonus",
      badge: "Highest Liquidity",
      referralCode: "HELIOSIS",
      // Replace with your full affiliate link:
      url: "https://www.bybit.com/register?affiliate_id=HELIOSIS"
    },
    binance: {
      name: "Binance",
      enabled: true,
      tagline: "20% Lifetime Fee Rebate + Spot & Futures",
      badge: "World #1 Volume",
      referralCode: "HELIOSIS",
      // Replace with your full affiliate link:
      url: "https://accounts.binance.com/register?ref=HELIOSIS"
    },
    okx: {
      name: "OKX",
      enabled: true,
      tagline: "Mystery Box up to $50 USDT + Ultra-low Spreads",
      badge: "Best Execution",
      referralCode: "HELIOSIS",
      // Replace with your full affiliate link:
      url: "https://www.okx.com/join/HELIOSIS"
    },
    tradingview: {
      name: "TradingView",
      enabled: true,
      tagline: "Get $15 Off Pro Charting & Alerts",
      url: "https://www.tradingview.com/?aff_id=heliosis"
    }
  },

  // ==========================================
  // COMMUNITY / LEAD GENERATION
  // ==========================================
  community: {
    telegramUrl: "https://t.me/heliosis_quant", // Your Telegram Group / Channel
    twitterUrl: "https://x.com/heliosis_xyz",
    tipJarAddress: "0x742d35Cc6634C0532925a3b844Bc454e4438f44e" // USDT / ETH / SOL address
  }
};
