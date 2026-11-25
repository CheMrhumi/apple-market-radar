# GEMINI.md — Konteks Seni Bina Projek (`apple-market-radar`)

> **Repositori pasangan:** `../iphone-market-pipeline` (Private ETL Pipeline)
> **Peranan repositori ini:** Public / Shop-facing Streamlit Dashboard (antaramuka bacaan sahaja yang dilindungi kata laluan untuk kegunaan kedai).

---

## 1. Gambaran Keseluruhan Seni Bina

Sistem **Apple Market Radar MY** dibina menggunakan seni bina terpisah (*decoupled two-repo architecture*) merentasi dua repositori yang berkomunikasi secara tidak langsung melalui satu pangkalan data **Supabase (PostgreSQL)**:

```text
[ iphone-market-pipeline (Private ETL) ]
   ├── GitHub Actions Cron (6:00 AM MYT / 22:00 UTC)
   ├── src/scrapers/{compasia,mudah,carousell}.py
   ├── src/utils.py (Normalisasi model, storan GB, harga sen)
   └── src/db.py (Batch UPSERT & auto-bersih stok basi)
            │
            ▼  (Tulis/Kemas kini jadual `market_iphone_listings`)
   [ Supabase PostgreSQL ]
            ▲  (Baca rekod aktif `is_available=true` <= 48 jam)
            │
[ apple-market-radar (Streamlit Dashboard) ]
   ├── dashboard.py (Pagar `APP_PASSWORD`, cache 1 jam, paginasi 1,000 baris)
   └── requirements.txt (Ringan: streamlit, pandas, supabase, python-dotenv)
```

- **`apple-market-radar` (Repositori ini):** Dashboard Streamlit mudah alih (*mobile-first*) yang direka untuk semakan harga kaunter kedai, anggaran siling *trade-in* (*Max Buy-In*), dan carian stok C2C bawah pasaran. Ia hanya membaca data daripada Supabase dan tidak mengandungi sebarang kod pengikis (*scraper*).
- **`iphone-market-pipeline` (Repositori pasangan):** Pipeline ETL harian di GitHub Actions yang mengikis CompAsia (B2C), Mudah.my (C2C), dan Carousell (C2C) serta menulis ke Supabase.

---

## 2. Skema & Kontrak Data Supabase (`market_iphone_listings`)

Dashboard di `dashboard.py` bergantung kepada kontrak data berikut daripada jadual `market_iphone_listings` di Supabase.

### 2.1 Lajur yang Ditarik oleh `dashboard.py`

Dalam `load_active_listings()`, dashboard menapis `.eq("is_available", True)` dan `.gte("scraped_at", cutoff)` (48 jam terakhir dalam UTC), serta menarik secara berperingkat (`batch_size = 1000`):

| Lajur | Jenis | Format daripada Pipeline | Bagaimana `dashboard.py` Memprosesnya |
| :--- | :--- | :--- | :--- |
| `source_platform` | `TEXT` | `'compasia'`, `'mudah'`, `'carousell'` | B2C (`compasia`) vs C2C (`mudah`, `carousell`); `str.capitalize()` dalam jadual Tab 3 |
| `model` | `TEXT` | Nama standard hasil `normalize_device_model()` (cth: `iPhone 15 Pro`, `iPad Air 11" M2`) | Penapis kategori `startswith("iPhone")` / `startswith("iPad")`, dropdown & carian teks |
| `storage_gb` | `INT` | Integer GB (`64`, `128`, `256`, `512`, `1024`, `2048`) | Dropdown storan (`>= 1024` dipapar sebagai `TB`) & kunci pengelompokan `(model, storage_gb)` |
| `grade` | `TEXT` | Gred kosmetik CompAsia (`Fair`, `Good`, `Excellent`, `Standard`) / kondisi C2C | Jadual `Rujukan Gred Kosmetik (CompAsia)` dalam Tab 1 |
| `sale_price_sen` | `BIGINT` | **Integer sen** (`RM 1,499.00` = `149900`) | Ditukar kepada RM melalui `df["price_rm"] = df["sale_price_sen"] / 100.0` |
| `listing_url` | `TEXT` | Pautan terus ke iklan/produk | Kolum pautan `Lihat ↗` (`st.column_config.LinkColumn`) dalam Tab 3 |
| `scraped_at` | `TIMESTAMPTZ` | Cap masa UTC ISO-8601 | Penapis tetingkap 48 jam & paparan `latest_sync` dalam zon waktu `Asia/Kuala_Lumpur` |
| `metadata` | `JSONB` | Objek JSON tambahan mengikut platform | Mengekstrak `region` dan `subject` dengan selamat untuk `dict` atau `None` |

### 2.2 Kontrak Medan JSONB `metadata`

**Struktur sebenar yang wujud dalam kod semasa:**
- **Diekstrak oleh `dashboard.py` (baris 67–72):**
  - `region`: Negeri/lokasi iklan (penapis `Tapis Lokasi / Negeri` dan kolum `Lokasi` dalam Tab 3).
  - `subject`: Tajuk asal iklan (kolum `Tajuk Iklan` dalam Tab 3).
- **Dihantar oleh pengikis di `iphone-market-pipeline`:**
  - `carousell.py`: `subject`, `description`, `region`, `seller_username`
  - `mudah.py`: `subject`, `region`, `subarea`, `is_company`, `warranty`, `posted_at`
  - `compasia.py`: Tidak menghantar `metadata` (`None` di Supabase)

> [!NOTE]
> **Status ciri terancang (Belum Diimplementasi):** Modul `src/enrichment.py` di `iphone-market-pipeline` serta kunci `metadata` iaitu `battery_health`, `set_type`, dan `is_fullset` **belum wujud** dalam kod sumber semasa di kedua-dua repositori. Apabila ciri pengayaan (*enrichment*) ditambah ke pipeline pada masa hadapan, `dashboard.py` mesti dikemas kini selari untuk membaca kunci `battery_health`, `set_type`, dan `is_fullset` daripada lajur `metadata` dengan pengendalian nilai `None` yang selamat.

---

## 3. Aliran Kerja & Peta Fail Utama

### 3.1 Peta Fail (`apple-market-radar`)

| Fail | Peranan Sebenar dalam Kod Sumber |
| :--- | :--- |
| [`dashboard.py`](dashboard.py) | Aplikasi Streamlit utama. Mengandungi pengawal akses `require_auth()`, pembacaan kredensial `get_supabase_credentials()`, pemuat data berpaginasi `load_active_listings()`, pembina jadual `build_summary_table()`, serta 3 tab UI (`🏪 Semak Harga Kedai`, `📊 Jadual Semua Model`, `🔥 Lubuk Stok C2C`). |
| [`requirements.txt`](requirements.txt) | Senarai kebergantungan ringan untuk Streamlit Cloud: `streamlit>=1.40.0`, `pandas>=2.2.0`, `supabase>=2.4.0`, `python-dotenv>=1.0.1`. |
| [`USER_MANUAL.md`](USER_MANUAL.md) | Panduan pengguna kedai: cara pasang sebagai pintasan telefon, glosari istilah (`C2C`, `B2C`, `Median`, `Lantai C2C`, `Keyakinan`), dan SOP penggunaan 3 tab serta semakan fizikal unit. |
| [`README.md`](README.md) | Gambaran ringkas repositori dan format konfigurasi `SUPABASE_URL`, `SUPABASE_KEY`, `APP_PASSWORD`. |
| [`.gitignore`](.gitignore) | Mengecualikan `.env`, `.streamlit/`, `__pycache__/`, `*.pyc`. |

### 3.2 Mekanisme Kawalan Akses (`APP_PASSWORD`) & Logik Harga

- **Kawalan Akses (`require_auth()` dalam `dashboard.py`):**
  1. Semak `st.session_state.get("authenticated")` — teruskan jika sudah sah.
  2. Dapatkan `APP_PASSWORD` daripada `os.getenv("APP_PASSWORD")`, atau jatuh balik ke `st.secrets["APP_PASSWORD"]`. Jika tiada, papar ralat dan hentikan aplikasi (`st.stop()`).
  3. Papar borang log masuk (`st.form("login_form")`) dan sahkan input menggunakan perbandingan masa tetap `hmac.compare_digest(...)` sebelum menetapkan `st.session_state["authenticated"] = True` dan memanggil `st.rerun()`.
- **Formula Harga Kedai (Tab 1 dalam `dashboard.py`):**
  - **Cadangan Harga Jual Kedai:** `round((ca_med * 0.96) / 10) * 10` (4% di bawah median CompAsia, dibundar ke RM 10 terdekat), atau jatuh balik ke `round((c2c_med * 1.08) / 10) * 10` jika tiada data CompAsia.
  - **Siling Belian / Trade-In (`max_buy_in`):** `round(min(c2c_med * 0.85, suggested_retail - 350) / 10) * 10`, atau `round((suggested_retail * 0.78) / 10) * 10` jika tiada sampel C2C.
- **Penunjuk Keyakinan & Tab 3 (`Lubuk Stok C2C`):**
  - Tahap keyakinan berdasarkan `c2c_count`: `Tinggi` (`>= 8`), `Sederhana` (`>= 3`), `Rendah` (`< 3`).
  - Tab 3 hanya menyertakan model/storan yang mempunyai `c2c_count >= 3` dan menapis iklan dengan peratusan diskaun di bawah median C2C `>= min_discount_pct` (lalai `12%`).

### 3.3 Ringkasan Aliran ETL Pasangan (`iphone-market-pipeline`)

- [`../iphone-market-pipeline/.github/workflows/scraper.yml`](../iphone-market-pipeline/.github/workflows/scraper.yml): Berjalan harian pada `0 22 * * *` UTC (**6:00 AM MYT**) dengan `python -m src.run --platform all --category all`.
- [`../iphone-market-pipeline/src/run.py`](../iphone-market-pipeline/src/run.py), [`src/db.py`](../iphone-market-pipeline/src/db.py), [`src/utils.py`](../iphone-market-pipeline/src/utils.py), [`src/scrapers/`](../iphone-market-pipeline/src/scrapers/): Menyeragamkan model/storan/harga kepada sen, melakukan UPSERT pada `(source_platform, listing_id)`, dan menanda stok basi sebagai `is_available = False`.

---

## 4. Peraturan & Kekangan Pembangunan (Guardrails)

1. **Kekalkan Kebergantungan Ringan (`requirements.txt`):**
   - `apple-market-radar/requirements.txt` **MESTI kekal ringan** (hanya `streamlit`, `pandas`, `supabase`, `python-dotenv`). **DILARANG** menambah `scrapling`, `patchright`, `playwright`, `httpx`, atau kebergantungan pelayar/pengikis ke repositori ini agar deployment Streamlit Cloud kekal pantas dan bersih.
2. **Keselamatan Kunci Rahsia & Kata Laluan:**
   - **JANGAN SESEKALI** memasukkan nilai tetap (*hardcoded*) atau mendedahkan kandungan `.env`, `.streamlit/secrets.toml`, `SUPABASE_URL`, `SUPABASE_KEY`, atau `APP_PASSWORD` ke dalam kod sumber atau repositori Git.
   - Sentiasa kekalkan panggilan `require_auth()` sebelum `load_active_listings()` dan sahkan kata laluan dengan `hmac.compare_digest`.
3. **Penyegerakan Kontrak `metadata` & Skema Supabase:**
   - Sebarang perubahan pada kunci `metadata` di `iphone-market-pipeline` (cth: penambahan `src/enrichment.py` dengan medan `battery_health`, `set_type`, `is_fullset`, atau perubahan pada `region`/`subject`) **MESTI** diselaraskan dengan logik pengekstrakan dataframe dan paparan UI di `dashboard.py`.
   - Sentiasa pastikan pengekstrakan `metadata` di `dashboard.py` mengendalikan kes `None` atau kunci yang tiada (kerana rekod `compasia` tidak mempunyai `metadata`).
4. **Konsistensi Unit & Tetingkap Masa:**
   - Kekalkan pembahagian `sale_price_sen / 100.0` (jangan ubah kontrak unit integer sen di pangkalan data).
   - Sebarang perubahan kepada nama `source_platform` (`compasia`, `mudah`, `carousell`), awalan `model` (`iPhone`, `iPad`), atau kekerapan jadual cron di `scraper.yml` mesti dinilai kesannya terhadap penapis 48 jam dan pengiraan median di `dashboard.py`.
