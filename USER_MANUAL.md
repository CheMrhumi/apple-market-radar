# 📱 Manual Pengguna: Radar Harga Apple Terpakai MY

Aplikasi ini mengumpul dan menganalisis harga semasa **iPhone & iPad terpakai di Malaysia** secara automatik setiap hari (jam **6:00 pagi**) daripada tiga sumber utama: **CompAsia**, **Mudah.my**, dan **Carousell**.

---

## 1. Cara Akses & Pasang di Telefon (Macam App)

1. Buka pautan dashboard di pelayar telefon (**Safari** untuk iPhone / **Chrome** untuk Android).
2. Masukkan **Kata Laluan Kedai** dan tekan **Buka Dashboard**.
3. **Jadikan Ikon di Skrin Utama:**
   * **iPhone (Safari):** Tekan ikon **Share** (petak anak panah ke atas) → pilih **Add to Home Screen**.
   * **Android (Chrome):** Tekan ikon **Menu (⋮)** di bucu kanan atas → pilih **Add to Home Screen / Install App**.
4. **Butang `🔄 Refresh Data`:** Data disimpan dalam *cache* selama 1 jam supaya laju dibuka. Tekan butang ini jika mahu menarik data terkini dari pelayan serta-merta.

---

## 2. Maksud Istilah Utama (*Glossary*)

| Istilah | Maksud & Fungsi dalam Operasi Kedai |
| :--- | :--- |
| **C2C** (*Consumer-to-Consumer*) | Pasaran terbuka daripada penjual individu & kedai kecil di **Mudah.my** dan **Carousell**. |
| **B2C** (*Business-to-Consumer*) | Pasaran runcit syarikat korporat berwaranti seperti **CompAsia**. Bertindak sebagai **harga siling** pasaran terpakai. |
| **Median** | **Harga tengah** pasaran (50% iklan lebih murah daripadanya, 50% lebih mahal). Digunakan menggantikan *purata* supaya harga tidak terherot akibat satu iklan yang terlalu mahal atau terlalu murah. |
| **Lantai C2C (Termurah)** | Harga iklan aktif paling rendah yang ditemui di Mudah.my atau Carousell bagi model tersebut. Berguna sebagai rujukan harga paling bawah apabila pelanggan cuba tawar-menawar. |
| **Unit (CA / MD / CR)** | Bilangan iklan aktif yang berjaya ditapis dalam 48 jam terakhir mengikut platform: **CA** (CompAsia), **MD** (Mudah.my), **CR** (Carousell). |
| **Keyakinan (`Tinggi` / `Sederhana` / `Rendah`)** | Tahap ketepatan data berdasarkan jumlah iklan C2C yang wujud:<br>• **Tinggi:** 8 unit ke atas (sangat tepat)<br>• **Sederhana:** 3 hingga 7 unit (boleh dipercayai)<br>• **Rendah:** Bawah 3 unit (sampel kecil — rujuk harga CompAsia sebagai panduan utama) |

---

## 3. Panduan Penggunaan 3 Tab Utama

### Tab 1: 🏪 Semak Harga Kedai (Untuk Pelanggan *Walk-In* & *Trade-In*)
Gunakan tab ini di kaunter apabila pelanggan bertanya harga jualan atau mahu *trade-in* peranti.

1. Pilih **Kategori** (`iPhone` / `iPad`), **Model**, dan **Storan**.
2. **Bahagian 1 — Penanda Aras Pasaran Semasa:**
   * Memaparkan 4 angka rujukan pantas: **Lantai C2C**, **Median Mudah.my**, **Median Carousell**, dan **Median CompAsia**.
   * *Nota:* Harga di Carousell biasanya sedikit tinggi berbanding Mudah.my kerana penjual individu meletakkan ruang untuk *nego*.
3. **Bahagian 2 — Panduan Harga Kedai & Trade-In:**
   * **🏷️ Cadangan Harga Jual Kedai:** Dikira sekitar **4% di bawah Median CompAsia** (dibundarkan ke RM 10 terdekat). Tujuannya supaya harga kedai lebih menarik berbanding CompAsia, tetapi masih lebih tinggi daripada penjual individu kerana kedai menawarkan pemeriksaan & waranti.
   * **🤝 Siling Belian / Trade-In (Max Buy-In):** Harga maksimum yang disyorkan untuk membeli atau mengambil *trade-in* daripada pelanggan (dikira pada **85% Median C2C** atau sekurang-kurangnya **RM 350 di bawah Cadangan Harga Jual**). Ini melindungi margin untung kedai untuk menampung kos aksesori, servis, dan waranti.
4. **Bahagian 3 — Rujukan Gred Kosmetik (CompAsia):**
   * Memecahkan harga CompAsia mengikut keadaan fizikal unit (*Excellent*, *Good*, *Fair*). Gunakan jadual ini untuk menolak harga *trade-in* jika keadaan fizikal peranti pelanggan bercalar teruk atau kemek.

---

### Tab 2: 📊 Jadual Semua Model (Matriks Keseluruhan)
Gunakan tab ini untuk melihat perbandingan harga keseluruhan model dalam satu skrin.
* Taip kata kunci di kotak **Cari model** (contoh: `15 Pro`, `14 Pro Max`, `iPad Air`) untuk menapis senarai serta-merta.
* Boleh tekan pada mana-mana tajuk kolum untuk menyusun harga dari paling rendah ke paling tinggi.

---

### Tab 3: 🔥 Lubuk Stok C2C (Cari Unit Murah untuk *Restock*)
Gunakan tab ini untuk memburu unit bawah harga pasaran di Mudah.my dan Carousell bagi menambah stok kedai.

1. **Diskaun minimum bawah Median C2C (%):** Laraskan *slider* (lalai: **12%**) untuk menapis iklan yang dijual jauh lebih murah daripada harga tengah pasaran semasa. *(Hanya model dengan sekurang-kurangnya 3 iklan C2C dipaparkan bagi mengelakkan ralat).*
2. **Tapis Lokasi / Negeri:** Pilih negeri berhampiran kedai (contoh: `Selangor`, `Kuala Lumpur`) untuk memudahkan urusan COD (*Cash on Delivery*) dan pemeriksaan fizikal.
3. **Tekan `Lihat ↗`:** Membuka terus halaman iklan di Carousell atau Mudah.my supaya anda boleh terus menghubungi penjual sebelum disambar pembeli lain.

---

## 4. Perkara Penting Semasa Menggunakan Data Ini

* **Iklan Rosak Sudah Ditapis Secara Automatik:** Sistem secara automatik membuang iklan *rosak, bypass, iCloud/MDM lock, telco lock, green line, LCD pecah*, serta iklan aksesori/kotak sahaja. Stok yang sudah terjual atau melebihi 48 jam juga ditanda tidak aktif secara automatik.
* **Semakan Fizikal Tetap Wajib:** Harga dalam dashboard ini adalah penanda aras pasaran bagi unit berfungsi normal. Sebelum memuktamadkan harga *trade-in* atau pembelian stok C2C, pastikan anda tetap menyemak:
  1. Peratusan **Battery Health (BH)** (unit bawah 80% perlu ditolak kos tukar bateri).
  2. Status **True Tone**, **Face ID**, dan paparan mesej *Unknown Part* dalam *Settings → General → About*.
  3. Bebas daripada **iCloud Lock**, **MDM**, atau sekatan telco (*Telco Lock*).
