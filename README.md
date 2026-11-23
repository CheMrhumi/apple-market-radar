# 📱 Apple Market Radar MY

Dashboard analisis harga pasaran peranti Apple (iPhone & iPad) terpakai di Malaysia merentasi **CompAsia**, **Mudah.my**, dan **Carousell**.

📖 **Panduan Operasi Kedai:** Rujuk [USER_MANUAL.md](./USER_MANUAL.md) untuk penerangan penuh fungsi setiap tab dan istilah metrik.

## Ciri Utama
- **Semakan Harga Kedai:** Penanda aras Lantai C2C, Median 3 platform, cadangan harga jualan kedai, siling belian (*Max Buy-In*), serta pecahan gred kosmetik.
- **Matriks Semua Model:** Jadual perbandingan penuh mengikut model dan kapasiti storan.
- **Radar Stok C2C:** Penapis iklan aktif di bawah harga median pasaran mengikut peratusan diskaun dan negeri.
- **Kawalan Akses:** Dilindungi pagar kata laluan (`APP_PASSWORD`) sebelum memuatkan data dari Supabase.

## Konfigurasi Secrets (Streamlit Cloud / `.env`)
```toml
SUPABASE_URL = "[https://your-project.supabase.co](https://your-project.supabase.co)"
SUPABASE_KEY = "your-supabase-key"
APP_PASSWORD = "your-shop-password"
