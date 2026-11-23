import os
from datetime import datetime, timedelta, timezone
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

st.set_page_config(
    page_title="Radar Harga Pasaran Apple MY",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_supabase_credentials():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except Exception:
            pass
    return url, key


@st.cache_data(ttl=3600, show_spinner="Menarik data terkini 3 platform...")
def load_active_listings() -> pd.DataFrame:
    url, key = get_supabase_credentials()
    if not url or not key:
        st.error("SUPABASE_URL atau SUPABASE_KEY tidak ditemui dalam .env atau Streamlit Secrets.")
        st.stop()

    client = create_client(url, key)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()

    # Tarik secara berperingkat (1,000 baris setiap halaman) supaya semua ~1,650+ rekod masuk
    all_rows = []
    batch_size = 1000
    offset = 0

    while True:
        resp = (
            client.table("market_iphone_listings")
            .select(
                "source_platform,model,storage_gb,grade,sale_price_sen,listing_url,scraped_at,metadata"
            )
            .eq("is_available", True)
            .gte("scraped_at", cutoff)
            .range(offset, offset + batch_size - 1)
            .execute()
        )
        rows = resp.data or []
        all_rows.extend(rows)
        if len(rows) < batch_size:
            break
        offset += batch_size

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["price_rm"] = df["sale_price_sen"] / 100.0
    df["region"] = df["metadata"].apply(
        lambda m: (m or {}).get("region") if isinstance(m, dict) else None
    )
    df["subject"] = df["metadata"].apply(
        lambda m: (m or {}).get("subject") if isinstance(m, dict) else None
    )
    return df


def format_rm(val) -> str:
    if val is None or pd.isna(val):
        return "—"
    return f"RM {val:,.0f}"


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for (model, storage), grp in df.groupby(["model", "storage_gb"]):
        ca = grp[grp["source_platform"] == "compasia"]["price_rm"]
        md = grp[grp["source_platform"] == "mudah"]["price_rm"]
        cr = grp[grp["source_platform"] == "carousell"]["price_rm"]
        c2c = grp[grp["source_platform"].isin(["mudah", "carousell"])]["price_rm"]

        c2c_count = len(c2c)
        confidence = "Tinggi" if c2c_count >= 8 else ("Sederhana" if c2c_count >= 3 else "Rendah")

        records.append(
            {
                "Model": model,
                "Storan (GB)": int(storage),
                "Unit (CA/MD/CR)": f"{len(ca)} / {len(md)} / {len(cr)}",
                "Lantai C2C (RM)": float(c2c.min()) if c2c_count > 0 else None,
                "Median Mudah (RM)": float(md.median()) if len(md) > 0 else None,
                "Median Carousell (RM)": float(cr.median()) if len(cr) > 0 else None,
                "Median C2C (RM)": float(c2c.median()) if c2c_count > 0 else None,
                "Median CompAsia (RM)": float(ca.median()) if len(ca) > 0 else None,
                "Sampel C2C": c2c_count,
                "Keyakinan": confidence,
            }
        )

    summary = pd.DataFrame(records)
    if not summary.empty:
        summary = summary.sort_values(by=["Model", "Storan (GB)"], ascending=[False, True])
    return summary


import hmac

def require_auth():
    if st.session_state.get("authenticated"):
        return

    expected_pw = os.getenv("APP_PASSWORD")
    if not expected_pw:
        try:
            expected_pw = st.secrets["APP_PASSWORD"]
        except Exception:
            expected_pw = None

    if not expected_pw:
        st.error("Konfigurasi keselamatan tidak lengkap: APP_PASSWORD belum ditetapkan.")
        st.stop()

    st.markdown("### 🔒 Akses Terhad — Radar Harga Apple MY")
    st.caption("Masukkan kata laluan kedai untuk melihat data pasaran semasa.")

    with st.form("login_form"):
        entered_pw = st.text_input("Kata Laluan", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Buka Dashboard", use_container_width=True)

    if submitted:
        if hmac.compare_digest(entered_pw.encode("utf-8"), str(expected_pw).encode("utf-8")):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Kata laluan salah. Akses ditolak.")

    st.stop()


require_auth()

# --- HEADER UTAMA ---
st.title("📱 Radar Harga Apple Terpakai MY")

col_info, col_refresh = st.columns([4, 1])
with col_refresh:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

df = load_active_listings()

if df.empty:
    st.warning("Tiada data aktif dalam 48 jam terakhir. Sila jalankan scraper terlebih dahulu.")
    st.stop()

latest_sync = pd.to_datetime(df["scraped_at"]).max().tz_convert("Asia/Kuala_Lumpur")
with col_info:
    st.caption(
        f"Data aktif: **{len(df):,} unit** (CompAsia, Mudah.my & Carousell) • "
        f"Kemas kini terakhir: **{latest_sync.strftime('%d %b %Y, %I:%M %p')}**"
    )

tab_shop, tab_matrix, tab_deals = st.tabs(
    ["🏪 Semak Harga Kedai", "📊 Jadual Semua Model", "🔥 Lubuk Stok C2C"]
)

# ==============================================================================
# TAB 1: SEMAKAN PANTAS UNTUK KEDAI (MOBILE-FIRST)
# ==============================================================================
with tab_shop:
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        device_type = st.selectbox("Kategori", ["Semua", "iPhone", "iPad"])
    filtered_df = df if device_type == "Semua" else df[df["model"].str.startswith(device_type)]

    models = sorted(filtered_df["model"].unique(), reverse=True)
    with c2:
        selected_model = st.selectbox("Pilih Model", models)

    storages = sorted(filtered_df[filtered_df["model"] == selected_model]["storage_gb"].unique())
    with c3:
        selected_storage = st.selectbox(
            "Storan",
            storages,
            format_func=lambda s: f"{s // 1024}TB" if s >= 1024 else f"{s}GB",
        )

    sub = filtered_df[
        (filtered_df["model"] == selected_model) & (filtered_df["storage_gb"] == selected_storage)
    ]

    ca_prices = sub[sub["source_platform"] == "compasia"]["price_rm"]
    md_prices = sub[sub["source_platform"] == "mudah"]["price_rm"]
    cr_prices = sub[sub["source_platform"] == "carousell"]["price_rm"]
    c2c_prices = sub[sub["source_platform"].isin(["mudah", "carousell"])]["price_rm"]

    ca_med = ca_prices.median() if not ca_prices.empty else None
    c2c_med = c2c_prices.median() if not c2c_prices.empty else None
    c2c_min = c2c_prices.min() if not c2c_prices.empty else None

    if len(c2c_prices) < 3:
        st.warning(
            f"⚠️ Sampel C2C rendah ({len(c2c_prices)} iklan sahaja). "
            "Gunakan harga CompAsia sebagai rujukan utama."
        )

    st.subheader("1. Penanda Aras Pasaran Semasa")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lantai C2C (Termurah)", format_rm(c2c_min), f"{len(c2c_prices)} iklan C2C")
    m2.metric(
        "Median Mudah.my",
        format_rm(md_prices.median() if not md_prices.empty else None),
        f"{len(md_prices)} iklan",
    )
    m3.metric(
        "Median Carousell",
        format_rm(cr_prices.median() if not cr_prices.empty else None),
        f"{len(cr_prices)} iklan",
    )
    m4.metric(
        "Median CompAsia (B2C)",
        format_rm(ca_med),
        f"{len(ca_prices)} varian",
    )

    st.subheader("2. Panduan Harga Kedai & Trade-In")
    # Cadangan harga jualan kedai: 3% - 5% di bawah median CompAsia (lebih murah dari B2C besar, tapi ada jaminan kedai)
    # Jika tiada CompAsia, guna +8% atas median C2C
    if ca_med and not pd.isna(ca_med):
        suggested_retail = round((ca_med * 0.96) / 10) * 10
    elif c2c_med and not pd.isna(c2c_med):
        suggested_retail = round((c2c_med * 1.08) / 10) * 10
    else:
        suggested_retail = None

    # Cadangan max buy-in / trade-in: 85% daripada median C2C (atau tolak RM 350 daripada harga jualan kedai)
    if c2c_med and not pd.isna(c2c_med) and suggested_retail:
        max_buy_in = round(min(c2c_med * 0.85, suggested_retail - 350) / 10) * 10
    elif suggested_retail:
        max_buy_in = round((suggested_retail * 0.78) / 10) * 10
    else:
        max_buy_in = None

    g1, g2 = st.columns(2)
    g1.info(
        f"**🏷️ Cadangan Harga Jual Kedai:** `{format_rm(suggested_retail)}`\n\n"
        "Kompetitif di bawah harga runcit CompAsia sambil kekal atas paras peniaga individu."
    )
    g2.success(
        f"**🤝 Siling Belian / Trade-In (Max Buy-In):** `{format_rm(max_buy_in)}`\n\n"
        "Memberi ruang margin selamat selepas kos pemeriksaan, aksesori, atau waranti kedai."
    )

    # Pecahan mengikut gred kosmetik CompAsia (sangat berguna untuk nilai keadaan fizikal unit)
    ca_sub = sub[sub["source_platform"] == "compasia"]
    if not ca_sub.empty:
        st.subheader("3. Rujukan Gred Kosmetik (CompAsia)")
        grade_df = (
            ca_sub.groupby("grade")["price_rm"]
            .agg(Unit="count", Minimum="min", Median="median", Maksimum="max")
            .reset_index()
            .rename(columns={"grade": "Gred Kosmetik"})
            .sort_values(by="Median", ascending=False)
        )
        st.dataframe(
            grade_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Minimum": st.column_config.NumberColumn(format="RM %.0f"),
                "Median": st.column_config.NumberColumn(format="RM %.0f"),
                "Maksimum": st.column_config.NumberColumn(format="RM %.0f"),
            },
        )

# ==============================================================================
# TAB 2: MATRIKS HARGA SEMUA MODEL
# ==============================================================================
with tab_matrix:
    st.subheader("Perbandingan Median Harga 3 Platform")
    search_txt = st.text_input("Cari model (cth: 15 Pro, 14 Pro Max, iPad Air)", "")
    summary_df = build_summary_table(df)
    if search_txt.strip():
        summary_df = summary_df[
            summary_df["Model"].str.contains(search_txt.strip(), case=False, na=False)
        ]

    st.dataframe(
        summary_df.drop(columns=["Sampel C2C"]),
        hide_index=True,
        use_container_width=True,
        height=550,
        column_config={
            "Lantai C2C (RM)": st.column_config.NumberColumn(format="RM %.0f"),
            "Median Mudah (RM)": st.column_config.NumberColumn(format="RM %.0f"),
            "Median Carousell (RM)": st.column_config.NumberColumn(format="RM %.0f"),
            "Median C2C (RM)": st.column_config.NumberColumn(format="RM %.0f"),
            "Median CompAsia (RM)": st.column_config.NumberColumn(format="RM %.0f"),
        },
    )

# ==============================================================================
# TAB 3: RADAR STOK MURAH (SOURCING UNTUK KEDAI)
# ==============================================================================
with tab_deals:
    st.subheader("Iklan C2C Bawah Harga Median Pasaran")
    st.caption("Tapis iklan aktif Mudah.my & Carousell untuk restock kedai pada harga bawah pasaran.")

    d1, d2 = st.columns(2)
    with d1:
        min_discount_pct = st.slider("Diskaun minimum bawah Median C2C (%)", 5, 40, 12)
    with d2:
        regions = sorted(df["region"].dropna().unique())
        selected_regions = st.multiselect("Tapis Lokasi / Negeri (pilihan)", regions)

    # Kira median C2C bagi setiap (model, storage_gb) yang mempunyai >= 3 iklan C2C
    c2c_all = df[df["source_platform"].isin(["mudah", "carousell"])].copy()
    c2c_stats = (
        c2c_all.groupby(["model", "storage_gb"])["price_rm"]
        .agg(c2c_median="median", c2c_count="count")
        .reset_index()
    )
    c2c_stats = c2c_stats[c2c_stats["c2c_count"] >= 3]

    deals = c2c_all.merge(c2c_stats, on=["model", "storage_gb"], how="inner")
    deals["jimat_rm"] = deals["c2c_median"] - deals["price_rm"]
    deals["diskaun_pct"] = (deals["jimat_rm"] / deals["c2c_median"]) * 100.0

    deals = deals[deals["diskaun_pct"] >= min_discount_pct]
    if selected_regions:
        deals = deals[deals["region"].isin(selected_regions)]

    deals = deals.sort_values(by="diskaun_pct", ascending=False)

    if deals.empty:
        st.info("Tiada iklan yang melepasi penapis diskaun/lokasi semasa.")
    else:
        display_deals = deals[
            [
                "source_platform",
                "model",
                "storage_gb",
                "price_rm",
                "c2c_median",
                "diskaun_pct",
                "region",
                "subject",
                "listing_url",
            ]
        ].rename(
            columns={
                "source_platform": "Platform",
                "model": "Model",
                "storage_gb": "GB",
                "price_rm": "Harga Iklan",
                "c2c_median": "Median C2C",
                "diskaun_pct": "Bawah Median",
                "region": "Lokasi",
                "subject": "Tajuk Iklan",
                "listing_url": "Pautan",
            }
        )
        display_deals["Platform"] = display_deals["Platform"].str.capitalize()

        st.dataframe(
            display_deals,
            hide_index=True,
            use_container_width=True,
            height=550,
            column_config={
                "Harga Iklan": st.column_config.NumberColumn(format="RM %.0f"),
                "Median C2C": st.column_config.NumberColumn(format="RM %.0f"),
                "Bawah Median": st.column_config.NumberColumn(format="%.1f%%"),
                "Pautan": st.column_config.LinkColumn("Buka Iklan", display_text="Lihat ↗"),
            },
        )
