# ⚡ Heliosis Terminal (heliosis.xyz)

> **Autonomous Crypto Funding & Basis Yield Screener**  
> 100% Free Hosting (Cloudflare Pages), 100% Autonomous (GitHub Actions), Zero Maintenance, Passive Income Ready.

---

## 🎯 Ne Yapar ve Nasıl Pasif Gelir Sağlar?

1. **Otonom Piyasa Taraması:**
   - Binance Futures ve Bybit Linear vadeli işlem piyasalarındaki **1000'e yakın çifti** canlı tarar.
   - 8 saatlik fonlama oranlarını (Funding Rates), yıllıklandırılmış **APR** ve bileşik **APY** oranlarını hesaplar.
   - **Cash & Carry Arbitrajı:** Delta-nötr (fiyat dalgalanmalarından etkilenmeyen) pozisyonlar için en yüksek faiz veren coinleri listeler.
   - **Borsalar Arası Arbitraj:** Binance ile Bybit arasındaki fonlama makasını (spread) tespit ederek Long/Short stratejisi önerir.

2. **Pasif Gelir Modelleri:**
   - **Borsa Partner Linkleri (Affiliate):** Bybit (%0 maker komisyonu + $30.000 bonus), Binance (%20 komisyon iadesi) ve OKX referans butonları. Siteyi kullanan traderlar kayıt oldukça borsa komisyonlarından ömür boyu **%20 - %40 arası pasif komisyon payı** alırsınız.
   - **Telegram VIP / Lead Yakalama:** Yüksek spread alarmları için Telegram topluluğu toplama.

---

## ⚙️ Kendi Referans Linklerinizi Nasıl Tanımlarsınız?

Tek bir dosyayı düzenlemeniz yeterlidir: **`config.js`**

```javascript
window.HELIOSIS_CONFIG = {
  affiliates: {
    bybit: {
      referralCode: "SİZİN_KODUNUZ",
      url: "https://www.bybit.com/register?affiliate_id=SİZİN_KODUNUZ"
    },
    binance: {
      referralCode: "SİZİN_KODUNUZ",
      url: "https://accounts.binance.com/register?ref=SİZİN_KODUNUZ"
    },
    okx: {
      referralCode: "SİZİN_KODUNUZ",
      url: "https://www.okx.com/join/SİZİN_KODUNUZ"
    }
  },
  community: {
    telegramUrl: "https://t.me/kanal_adresiniz"
  }
};
```
Dosyadaki linkleri güncellediğinizde sitedeki tüm butonlar, tablolar ve hesap makinesi otomatik olarak sizin linklerinizi kullanır.

---

## 🚀 3 Adımda Canlıya Alma ve Domain Bağlama (Sıfır Maliyet)

### 1. Adım: Projeyi GitHub'a Yükleyin
GitHub hesabınızda yeni bir repo oluşturun (örneğin `heliosis.xyz`):
```bash
git init
git add .
git commit -m "Initial Heliosis Terminal"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/heliosis.xyz.git
git push -u origin main
```

### 2. Adım: GitHub Actions İzinlerini Açın (Otonom Güncelleme İçin)
Repo sayfanızda:
1. **Settings** -> **Actions** -> **General** bölümüne gidin.
2. **Workflow permissions** kısmında **"Read and write permissions"** seçeneğini işaretleyip **Save** butonuna tıklayın.
*(Bu sayede `.github/workflows/auto_update.yml` her saat başı piyasa verilerini çekip repoyu otonom olarak güncelleyebilecektir).*

### 3. Adım: Cloudflare Pages'e Bağlayın ($0 Hosting & Sınırsız Trafik)
1. [Cloudflare Dashboard](https://dash.cloudflare.com)'a ücretsiz giriş yapın.
2. Sol menüden **Workers & Pages** -> **Create application** -> **Pages** -> **Connect to Git** seçin.
3. GitHub reponuzu (`heliosis.xyz`) seçin.
4. **Build settings:**
   - **Framework preset:** `None`
   - **Build command:** *(Boş bırakın)*
   - **Build output directory:** `.` *(Nokta koyun veya boş bırakın)*
5. **Save and Deploy** butonuna tıklayın. 10 saniye içinde siteniz `*.pages.dev` üzerinde canlıya geçer!

### 4. Adım: `heliosis.xyz` Domainini Bağlama
1. Oluşturduğunuz Cloudflare Pages projesinin içinde **Custom domains** sekmesine gelin.
2. **Set up a custom domain** butonuna basıp `heliosis.xyz` yazın.
3. Cloudflare DNS otomatik olarak yönlendirmeyi yapacak ve **ücretsiz SSL sertifikasını** anında tanımlayacaktır.

---

## 💻 Yerel Test (Bilgisayarınızda Önizleme)

Tarayıcıda anında test etmek için terminalde proje klasöründe şu komutu çalıştırabilirsiniz:
```bash
python -m http.server 8080
```
Ardından tarayıcınızda `http://localhost:8080` adresini açarak terminali inceleyebilirsiniz.
