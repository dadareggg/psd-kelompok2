import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Beli Lagi atau Beralih?",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PINK = "#E040A8"
PURPLE = "#8E5CF0"
TEAL = "#2DD4BF"
AMBER = "#F59E0B"
RED = "#EF4444"
GREEN = "#22C55E"
PALETTE = [PINK, PURPLE, "#F9A8D4", "#C4B5FD", TEAL]
BELI_COLORS = {"No": RED, "Maybe": AMBER, "Yes": GREEN}
DATA_DIR = "data"
DUMMY_DIR = os.path.join(DATA_DIR, "dummy")

TIPE = ["Kombinasi", "Berminyak", "Sensitif", "Kering", "Normal"]
KELUHAN = ["Kulit Kusam", "Jerawat", "Pori Besar", "Komedo",
           "Kantung Mata", "Flek", "Stretch Mark"]
LAMA_ORDER = ["< 1 minggu", "1 minggu - 1 bulan", "1-3 bulan",
              "3-6 bulan", "6 bulan - 1 tahun", "> 1 tahun"]
SUBRATING = ["sub_rating_efektivitas", "sub_rating_kemasan",
             "sub_rating_tekstur", "sub_rating_kualitas_harga"]

# ---------------- Style ----------------
st.markdown(
    f"""
    <style>
    .block-container {{ padding-top: 1.2rem; max-width: 1400px; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 16px; border: 1px solid #2B2D4A;
        background: #17182F;
    }}
    .title {{ font-size: 1.6rem; font-weight: 800; line-height: 1.15;
             background: linear-gradient(90deg,{PINK},{PURPLE});
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .subtitle {{ color:#9AA0C3; font-size:.8rem; margin-top:4px; }}
    .card-title {{ color:#9AA0C3; font-size:.75rem; font-weight:700;
                  letter-spacing:.08em; text-transform:uppercase; }}
    .dummy {{ background:#3B2A06; color:{AMBER}; font-size:.65rem;
             padding:1px 7px; border-radius:8px; margin-left:8px;
             letter-spacing:.05em; }}
    .headline {{ font-size:1.05rem; font-weight:600; margin:2px 0 8px 0; }}
    .headline b {{ color:{PINK}; }}
    .kpi {{ padding:14px 16px; border-radius:16px; background:#17182F;
           border:1px solid #2B2D4A; }}
    .kpi .label {{ color:#9AA0C3; font-size:.8rem; }}
    .kpi .value {{ font-size:2rem; font-weight:800; margin-top:6px; }}
    .kpi .unit {{ font-size:.9rem; color:#9AA0C3; margin-left:4px; }}
    .kpi .chip {{ float:right; font-size:.72rem; padding:2px 8px;
                 border-radius:8px; background:#2B1F3F; color:{PINK}; }}
    .insight {{ background:#1F1A38; border-left:5px solid {PINK};
               padding:12px 16px; border-radius:10px; margin-bottom:10px; }}
    .insight.todo {{ border-left-color:{AMBER}; opacity:.85; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Helpers ----------------
def fmt(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def idn(n):
    return f"{int(n):,}".replace(",", ".")


@st.cache_data(show_spinner=False)
def _read(path, mtime):
    return pd.read_csv(path)


def _path(name):
    """Pakai file asli di data/. Kalau belum ada, pakai dummy di data/dummy/."""
    real = os.path.join(DATA_DIR, name)
    if os.path.exists(real):
        return real, False
    dummy = os.path.join(DUMMY_DIR, name)
    if os.path.exists(dummy):
        return dummy, True
    return None, False


def load_csv(name):
    p, _ = _path(name)
    return _read(p, os.path.getmtime(p)).copy() if p else None


def is_dummy(name):
    return _path(name)[1]


def waiting(name, who):
    st.info(f"Menunggu file `{DATA_DIR}/{name}` dari {who}.")


def show(fig, height=320):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#D7DAF0",
        margin=dict(l=10, r=10, t=30, b=10),
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor="#2B2D4A")
    fig.update_yaxes(gridcolor="#2B2D4A")
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def table(d):
    try:
        st.dataframe(d, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(d, use_container_width=True, hide_index=True)


def kpi(col, label, value, unit="", chip=""):
    chip_html = f'<span class="chip">{chip}</span>' if chip else ""
    col.markdown(
        f'<div class="kpi">{chip_html}<div class="label">{label}</div>'
        f'<div class="value">{value}<span class="unit">{unit}</span></div></div>',
        unsafe_allow_html=True,
    )


def card_title(text, file=None):
    tag = '<span class="dummy">DUMMY</span>' if file and is_dummy(file) else ""
    st.markdown(f'<div class="card-title">{text}{tag}</div>',
                unsafe_allow_html=True)


def headline(html):
    st.markdown(f'<div class="headline">{html}</div>', unsafe_allow_html=True)


def insight(html, todo=False):
    cls = "insight todo" if todo else "insight"
    st.markdown(f'<div class="{cls}">{html}</div>', unsafe_allow_html=True)


def pct_yes(s):
    return (s == "Yes").mean() * 100


LAMA_ID = {
    "Less Than 1 Week": "< 1 minggu",
    "1 Week - 1 Month": "1 minggu - 1 bulan",
    "1 - 3 Months": "1-3 bulan",
    "3 - 6 Months": "3-6 bulan",
    "6 Months - 1 Year": "6 bulan - 1 tahun",
    "More Than 1 Year": "> 1 tahun",
}
KLAS_ORDER = LAMA_ORDER + ["Belum_Puas", "Puas", "No", "Maybe", "Yes"]
KLAS_INFO = {
    "Kepuasan Konsumen": {
        "model": "Decision Tree (rpart)",
        "target": "Puas bila rating 4 atau lebih, selain itu Belum_Puas",
        "prediktor": "harga min, harga max, brand, tipe kulit utama, "
                     "lama penggunaan"},
    "Durasi Penggunaan": {
        "model": "Naive Bayes",
        "target": "lama penggunaan (6 kelas)",
        "prediktor": "rating, 4 sub-rating, harga min, harga max, brand, "
                     "tipe kulit utama"},
    "Rekomendasi Produk": {
        "model": "Random Forest (300 pohon)",
        "target": "rekomendasi (Yes/No)",
        "prediktor": "harga min, harga max, brand, tipe kulit utama, "
                     "lama penggunaan"},
    "Niat Pembelian Ulang": {
        "model": "Random Forest (300 pohon)",
        "target": "beli lagi (Yes/Maybe/No)",
        "prediktor": "rating, 4 sub-rating, harga min, harga max, brand, "
                     "tipe kulit utama, lama penggunaan"},
}


def load_klas():
    km, cmx, fim = (load_csv("klasifikasi_metrics.csv"),
                    load_csv("confusion_matrix.csv"),
                    load_csv("feature_importance.csv"))
    if km is None or cmx is None or "Analisis" not in km.columns \
            or "Analisis" not in cmx.columns:
        return None, None, None
    km["Kelas"] = km["Kelas"].map(lambda v: LAMA_ID.get(v, v))
    for k in ["Prediksi", "Aktual"]:
        cmx[k] = cmx[k].map(lambda v: LAMA_ID.get(v, v))
    return km, cmx, fim


def klas_summary(km, cmx):
    rows = []
    for nama in km["Analisis"].unique():
        c_ = cmx[cmx["Analisis"] == nama]
        k_ = km[km["Analisis"] == nama]
        tot = c_["Jumlah"].sum()
        acc = c_.loc[c_["Prediksi"] == c_["Aktual"], "Jumlah"].sum() / tot
        akt = c_.groupby("Aktual")["Jumlah"].sum()
        kel_min = akt.idxmin()
        rec = k_.loc[k_["Kelas"] == kel_min, "Recall"]
        rows.append(dict(
            analisis=nama, n=int(tot), acc=acc, nir=akt.max() / tot,
            kappa=k_["Kappa"].iloc[0], f1=k_["Macro_F1"].iloc[0],
            kelas_min=kel_min,
            rec_min=float(rec.iloc[0]) if len(rec) else float("nan")))
    return pd.DataFrame(rows)


# ---------------- Data ----------------
df_all = load_csv("data_bersih.csv")
if df_all is None:
    st.error("File `data/data_bersih.csv` belum ada. Jalankan dulu: "
             "`python siapkan_data.py`")
    st.stop()

sel_df = load_csv("seleksi_peubah.csv")

sentimen = pd.DataFrame(
    {"Sentimen": ["Positif", "Netral", "Negatif"],
     "Persen": [60.4, 30.5, 9.1]}
)  # hasil lexicon-based kelompok (dari infografis)

variabel = pd.DataFrame(
    {
        "Kode": ["Y", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8", "X9",
                 "X10"],
        "Kolom": ["beli_lagi", "harga_min", "harga_max",
                  "reviewer_skin_types", "rating", "sub_rating_efektivitas",
                  "sub_rating_kemasan", "sub_rating_tekstur",
                  "sub_rating_kualitas_harga", "rekomendasi",
                  "lama_penggunaan"],
        "Keterangan": ["Pembelian ulang (Yes/Maybe/No)", "Harga minimum",
                       "Harga maksimum", "Tipe kulit dan keluhan reviewer",
                       "Rating 1-5", "Efektivitas", "Kemasan", "Tekstur",
                       "Kualitas harga", "Rekomendasi (Yes/No)",
                       "Lama penggunaan (6 kategori)"],
    }
)

# ---------------- Header: judul + filter ----------------
st.markdown('<div class="title">Beli Lagi atau Beralih?</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Pengantar Sains Data | Kelompok 2 (K1) | '
    'Faktor Pembelian Ulang Skincare Sociolla</div>',
    unsafe_allow_html=True,
)

f1, f2, f3, f4 = st.columns(4)
pilih_tipe = f1.multiselect("Tipe kulit", TIPE, placeholder="Semua")
pilih_brand = f2.multiselect("Brand", sorted(df_all["brand"].unique()),
                             placeholder="Semua")
pilih_lama = f3.multiselect(
    "Lama pemakaian",
    [x for x in LAMA_ORDER if x in set(df_all["lama_penggunaan"])],
    placeholder="Semua")
pilih_rek = f4.multiselect("Rekomendasi", ["Yes", "No"], placeholder="Semua")

df = df_all
if pilih_tipe:
    df = df[df[[f"tipe_{t}" for t in pilih_tipe]].sum(axis=1) > 0]
if pilih_brand:
    df = df[df["brand"].isin(pilih_brand)]
if pilih_lama:
    df = df[df["lama_penggunaan"].isin(pilih_lama)]
if pilih_rek:
    df = df[df["rekomendasi"].isin(pilih_rek)]

if len(df) == 0:
    st.warning("Tidak ada ulasan yang cocok dengan filter. Kurangi filter.")
    st.stop()

# ---------------- KPI row ----------------
kc = st.columns(5)
kpi(kc[0], "Jumlah Ulasan", idn(len(df)), "",
    "terfilter" if len(df) != len(df_all) else "bersih")
kpi(kc[1], "Berniat Beli Lagi", fmt(pct_yes(df["beli_lagi"])), "%", "Yes")
kpi(kc[2], "Rata-rata Rating", fmt(df["rating"].mean(), 2), "/5")
kpi(kc[3], "Merekomendasikan", fmt(pct_yes(df["rekomendasi"])), "%", "Yes")
kpi(kc[4], "Brand | Produk",
    f'{df["brand"].nunique()} | {df["nama_produk"].nunique()}')

st.write("")

# ---------------- Navigasi 7 bagian ----------------
tabs = st.tabs([
    "1 Overview", "2 Data", "3 EDA", "4 Preprocessing",
    "5 Modeling", "6 Insights", "7 Kesimpulan",
])

# ===== 1. Project Overview =====
with tabs[0]:
    a, b = st.columns([3, 2])
    with a:
        with st.container(border=True):
            card_title("Latar Belakang")
            headline("Cocok di kulit mereka, <b>belum tentu cocok</b> di kulit kita.")
            st.write(
                "Setiap orang punya jenis dan masalah kulit berbeda. Ribuan "
                "ulasan konsumen bisa diolah untuk melihat pengalaman, "
                "persepsi, dan faktor yang berkaitan dengan kecocokan serta "
                "pembelian ulang produk skincare."
            )
    with b:
        with st.container(border=True):
            card_title("Tujuan Proyek")
            st.markdown(
                "- Mengeksplorasi karakteristik reviewer dan produk\n"
                "- Mengidentifikasi faktor pembelian ulang\n"
                "- Memodelkan pembelian ulang dan menemukan pola\n"
                "- Memberi rekomendasi untuk brand dan platform"
            )
    with st.container(border=True):
        card_title("Cara Membaca Dashboard")
        st.markdown(
            "Pakai **filter di atas** (tipe kulit, brand, lama pemakaian, "
            "rekomendasi). Angka KPI, EDA, dan Product Explorer ikut berubah. "
            "Buka tab **5 Modeling** untuk hasil klasifikasi, FAMD, "
            "association rules, clustering, dan simulasi."
        )

# ===== 2. Data Overview =====
with tabs[1]:
    a, b = st.columns([2, 3])
    with a:
        with st.container(border=True):
            card_title("Sumber dan Alur Data")
            st.write("Website resmi Sociolla, diambil dengan web scraping.")
            st.markdown(
                "1. Setup driver dan target\n"
                "2. Ambil daftar produk\n"
                "3. Buka tab review\n"
                "4. Scraping\n"
                "5. Looping halaman dan produk\n"
                "6. Ekspor data"
            )
            c1, c2 = st.columns(2)
            c1.metric("Data kotor", "11.401")
            c2.metric("Data bersih", idn(len(df_all)))
            st.caption(f"Missing value pada data bersih: "
                       f"{int(df_all[variabel['Kolom'].tolist()].isna().sum().sum())}")
    with b:
        with st.container(border=True):
            card_title("Variabel yang Digunakan")
            table(variabel)
    c, d = st.columns([2, 3])
    with c:
        with st.container(border=True):
            card_title("Distribusi Target (beli_lagi)")
            tg = df["beli_lagi"].value_counts().reset_index()
            tg.columns = ["Beli Lagi", "Jumlah"]
            headline("Kelas <b>tidak seimbang</b>: "
                     f"Yes {fmt(pct_yes(df['beli_lagi']))}%.")
            fig = px.pie(tg, names="Beli Lagi", values="Jumlah", hole=0.55,
                         color="Beli Lagi", color_discrete_map=BELI_COLORS)
            show(fig, 280)
    with d:
        with st.container(border=True):
            card_title("Preview Data")
            kolom = ["brand", "nama_produk", "harga_min", "harga_max",
                     "tipe_kulit", "keluhan", "rating"] + SUBRATING + [
                "rekomendasi", "lama_penggunaan", "beli_lagi"]
            table(df[kolom].head(100))
            st.caption(f"Menampilkan 100 dari {idn(len(df))} baris (sesuai filter)")

# ===== 3. EDA =====
with tabs[2]:
    r1a, r1b = st.columns(2)
    with r1a:
        with st.container(border=True):
            card_title("Keluhan Kulit Reviewer")
            kel = pd.DataFrame({
                "Keluhan": KELUHAN,
                "Persen": [df["keluhan_" + k.replace(" ", "_")].mean() * 100
                           for k in KELUHAN],
            }).sort_values("Persen")
            top = kel.iloc[-1]
            headline(f"<b>{top['Keluhan']}</b> keluhan paling banyak "
                     f"({fmt(top['Persen'])}% ulasan).")
            fig = px.bar(kel, x="Persen", y="Keluhan", orientation="h",
                         text=kel["Persen"].map(lambda v: f"{v:.1f}%"),
                         color_discrete_sequence=[PINK])
            fig.update_xaxes(title=None)
            fig.update_yaxes(title=None)
            show(fig)
    with r1b:
        with st.container(border=True):
            card_title("Tipe Kulit Reviewer")
            tk = pd.DataFrame({
                "tipe_kulit": TIPE,
                "Jumlah": [int(df[f"tipe_{t}"].sum()) for t in TIPE],
            })
            top = tk.sort_values("Jumlah", ascending=False).iloc[0]
            share = top["Jumlah"] / tk["Jumlah"].sum() * 100
            headline(f"Tipe <b>{top['tipe_kulit']}</b> terbanyak "
                     f"({fmt(share)}% dari seluruh sebutan tipe kulit).")
            fig = px.pie(tk, names="tipe_kulit", values="Jumlah", hole=0.55,
                         color_discrete_sequence=PALETTE)
            show(fig)

    r2a, r2b = st.columns(2)
    with r2a:
        with st.container(border=True):
            card_title("Distribusi Sentimen Ulasan")
            if "label_sentimen" in df.columns:
                sm = (df["label_sentimen"].value_counts(normalize=True) * 100
                      ).reindex(["Positif", "Netral", "Negatif"]).fillna(0)
                sm = sm.round(1).reset_index()
                sm.columns = ["Sentimen", "Persen"]
                cap = "Lexicon-based sederhana (dari analisis FAMD), ikut filter."
            else:
                sm = sentimen
                cap = "Hasil analisis sentimen kelompok, tidak ikut filter."
            headline(f"<b>{fmt(sm.iloc[0]['Persen'])}%</b> ulasan bernada "
                     "positif (lexicon-based).")
            fig = px.bar(sm, x="Sentimen", y="Persen",
                         text=sm["Persen"].map(lambda v: f"{v}%"),
                         color="Sentimen",
                         color_discrete_map={"Positif": GREEN,
                                             "Netral": AMBER, "Negatif": RED})
            fig.update_xaxes(title=None)
            fig.update_yaxes(title=None)
            show(fig)
            st.caption(cap)
    with r2b:
        with st.container(border=True):
            card_title("Niat Beli Lagi menurut Rekomendasi")
            ct = (pd.crosstab(df["rekomendasi"], df["beli_lagi"],
                              normalize="index") * 100).round(1)
            bl = ct.reset_index().melt(id_vars="rekomendasi",
                                       var_name="Beli Lagi",
                                       value_name="Persen")
            bl = bl.rename(columns={"rekomendasi": "Rekomendasi"})
            headline("Yang <b>merekomendasikan</b> hampir semuanya "
                     "berniat beli lagi.")
            fig = px.bar(bl, x="Rekomendasi", y="Persen", color="Beli Lagi",
                         barmode="stack", text="Persen",
                         color_discrete_map=BELI_COLORS)
            show(fig)

    r3a, r3b = st.columns(2)
    with r3a:
        with st.container(border=True):
            card_title("10 Brand dengan Ulasan Terbanyak")
            br = df["brand"].value_counts().head(10).reset_index()
            br.columns = ["Brand", "Ulasan"]
            fig = px.bar(br.iloc[::-1], x="Ulasan", y="Brand",
                         orientation="h", text="Ulasan",
                         color_discrete_sequence=[PURPLE])
            fig.update_yaxes(title=None)
            show(fig, 360)
    with r3b:
        with st.container(border=True):
            card_title("Beli Lagi menurut Lama Pemakaian")
            urut = [x for x in LAMA_ORDER if x in set(df["lama_penggunaan"])]
            ll = (df.groupby("lama_penggunaan")["beli_lagi"]
                  .apply(pct_yes).reindex(urut).reset_index())
            ll.columns = ["Lama Pemakaian", "Persen Yes"]
            headline("Pengguna <b>lebih dari 1 tahun</b> paling setia "
                     "beli lagi.")
            fig = px.bar(ll, x="Lama Pemakaian", y="Persen Yes",
                         text=ll["Persen Yes"].map(lambda v: f"{v:.1f}%"),
                         color_discrete_sequence=[PINK])
            fig.update_yaxes(range=[0, 100], title="% beli lagi (Yes)")
            fig.update_xaxes(title=None)
            show(fig, 360)

    r4a, r4b, r4c = st.columns([2, 2, 3])
    with r4a:
        with st.container(border=True):
            card_title("Sebaran Rating")
            rc = df["rating"].round().astype(int).value_counts().sort_index()
            rc = rc.reset_index()
            rc.columns = ["Rating", "Ulasan"]
            fig = px.bar(rc, x="Rating", y="Ulasan", text="Ulasan",
                         color_discrete_sequence=[PURPLE])
            show(fig, 300)
    with r4b:
        with st.container(border=True):
            card_title("Korelasi Rating dan Harga")
            kk = ["rating"] + SUBRATING + ["harga_min", "harga_max"]
            corr = df[kk].corr().round(2)
            corr.columns = ["rating", "efektivitas", "kemasan", "tekstur",
                            "kual. harga", "harga min", "harga max"]
            corr.index = corr.columns
            fig = px.imshow(corr, text_auto=True,
                            color_continuous_scale="Purples")
            fig.update_coloraxes(showscale=False)
            show(fig, 300)
    with r4c:
        with st.container(border=True):
            card_title("Wordcloud Ulasan")
            wc = os.path.join(DATA_DIR, "wordcloud.png")
            if os.path.exists(wc):
                st.image(wc)
            else:
                waiting("wordcloud.png", "siapkan_data.py")

    with st.container(border=True):
        card_title("Product Explorer")
        brands = sorted(df["brand"].unique())
        pe_brand = st.selectbox("Pilih brand", brands, key="pe_brand")
        d = df[df["brand"] == pe_brand]
        prod = (d.groupby("nama_produk")
                .agg(Ulasan=("rating", "size"),
                     Rating=("rating", "mean"),
                     Persen_Beli_Lagi=("beli_lagi", pct_yes),
                     Harga_Min=("harga_min", "first"),
                     Harga_Max=("harga_max", "first"))
                .reset_index()
                .sort_values("Ulasan", ascending=False))
        prod["Rating"] = prod["Rating"].round(2)
        prod["Persen_Beli_Lagi"] = prod["Persen_Beli_Lagi"].round(1)
        table(prod)
        pe_prod = st.selectbox("Lihat contoh ulasan produk",
                               prod["nama_produk"].tolist(), key="pe_prod")
        dd = d[d["nama_produk"] == pe_prod]
        m1, m2, m3 = st.columns(3)
        m1.metric("Ulasan", idn(len(dd)))
        m2.metric("Rating rata-rata", fmt(dd["rating"].mean(), 2))
        m3.metric("Berniat beli lagi", f"{fmt(pct_yes(dd['beli_lagi']))}%")
        for t in dd["review_final"].head(3):
            st.caption(f"\"{t}\"")

# ===== 4. Preprocessing =====
with tabs[3]:
    a, b = st.columns([2, 3])
    with a:
        with st.container(border=True):
            card_title("Langkah Preprocessing")
            st.markdown(
                "1. Pembersihan data hasil scraping\n"
                "2. Pecah `reviewer_skin_types` menjadi tipe kulit dan keluhan\n"
                "3. Rapikan label lama pemakaian (6 kategori berurutan)\n"
                "4. Teks ulasan dibersihkan (`review_final`)\n"
                "5. Seleksi peubah (ANOVA dan Chi-square)"
            )
            st.caption("ISI: sesuaikan dengan proses cleaning kelompok "
                       "(11.401 menjadi 9.119).")
            c1, c2 = st.columns(2)
            c1.metric("Sebelum", "11.401")
            c2.metric("Sesudah", idn(len(df_all)),
                      delta=f"-{idn(11401 - len(df_all))}")
    with b:
        with st.container(border=True):
            card_title("Seleksi Peubah (p-value < 0,05 dipertahankan)")
            if sel_df is not None:
                s = sel_df.copy()
                s["-log10(p)"] = s["pvalue"].clip(lower=1e-300).apply(
                    lambda p: -1 * __import__("math").log10(p))
                fig = px.bar(s.sort_values("-log10(p)"), x="-log10(p)",
                             y="peubah", orientation="h", color="uji",
                             color_discrete_sequence=[PINK, PURPLE])
                fig.add_vline(x=1.301, line_dash="dash", line_color=AMBER,
                              annotation_text="p = 0,05")
                fig.update_yaxes(title=None)
                show(fig)
                n_sig = int((s["pvalue"] < 0.05).sum())
                st.caption(f"{n_sig} dari {len(s)} peubah signifikan. "
                           "ANOVA untuk numerik, Chi-square untuk kategorik.")
                with st.expander("Lihat tabel"):
                    table(s.drop(columns="-log10(p)"))
            else:
                waiting("seleksi_peubah.csv", "siapkan_data.py")

# ===== 5. Modeling =====
with tabs[4]:
    sub = st.tabs(["Klasifikasi", "FAMD", "Association Rules", "Clustering",
                   "Simulasi"])

    with sub[0]:
        km, cmx, fim = load_klas()
        if km is None:
            waiting("klasifikasi_metrics.csv dan confusion_matrix.csv", "Abit")
        else:
            ks = klas_summary(km, cmx)
            with st.container(border=True):
                card_title("Ringkasan 4 Analisis Klasifikasi (PIC: Abit)")
                headline("Akurasi tinggi pada kelas yang timpang "
                         "<b>menipu</b>: bandingkan dengan tebakan mayoritas.")
                tbl = pd.DataFrame({
                    "Analisis": ks["analisis"],
                    "Model": ks["analisis"].map(lambda n: KLAS_INFO[n]["model"]),
                    "Akurasi (%)": (ks["acc"] * 100).round(1),
                    "Tebakan mayoritas (%)": (ks["nir"] * 100).round(1),
                    "Kappa": ks["kappa"].round(3),
                    "Macro-F1": ks["f1"].round(3),
                    "Recall kelas terkecil (%)": (ks["rec_min"] * 100).round(1),
                })
                table(tbl)
                st.caption(
                    "Tebakan mayoritas = akurasi bila semua ulasan ditebak "
                    "kelas terbanyak. Macro-F1 sesuai file Abit (rata-rata F1 "
                    "tanpa kelas yang tak pernah ditebak).")

            urut = list(ks["analisis"])
            pil = st.radio("Lihat detail analisis", urut,
                           index=urut.index("Niat Pembelian Ulang")
                           if "Niat Pembelian Ulang" in urut else 0,
                           horizontal=True, key="klas_pil")
            r_ = ks[ks["analisis"] == pil].iloc[0]
            info = KLAS_INFO[pil]
            kc_ = st.columns(4)
            kpi(kc_[0], "Akurasi", fmt(r_["acc"] * 100), "%")
            kpi(kc_[1], "Tebakan mayoritas", fmt(r_["nir"] * 100), "%")
            kpi(kc_[2], "Kappa", fmt(r_["kappa"], 3))
            kpi(kc_[3], "Macro-F1", fmt(r_["f1"], 3))
            st.write("")
            selisih = (r_["acc"] - r_["nir"]) * 100
            if selisih <= 0.5:
                headline("Model <b>tidak lebih baik</b> dari menebak kelas "
                         f"mayoritas ({fmt(selisih)} poin).")
            else:
                headline(f"Model hanya <b>{fmt(selisih)} poin</b> di atas "
                         "tebakan mayoritas.")

            a, b = st.columns(2)
            with a:
                with st.container(border=True):
                    card_title("Confusion Matrix")
                    c_ = cmx[cmx["Analisis"] == pil]
                    pv = c_.pivot_table(index="Aktual", columns="Prediksi",
                                        values="Jumlah", aggfunc="sum",
                                        fill_value=0)
                    kls = [x for x in KLAS_ORDER if x in pv.index]
                    kls += [x for x in pv.index if x not in kls]
                    pv = pv.reindex(index=kls, columns=kls, fill_value=0)
                    norm = pv.div(pv.sum(axis=1).replace(0, 1), axis=0)
                    fig = go.Figure(go.Heatmap(
                        z=norm.values, x=list(pv.columns), y=list(pv.index),
                        text=pv.values, texttemplate="%{text}",
                        colorscale="RdPu", showscale=False,
                        hovertemplate="Aktual %{y}<br>Prediksi %{x}"
                                      "<br>Jumlah %{text}<extra></extra>"))
                    fig.update_yaxes(autorange="reversed", title="Aktual")
                    fig.update_xaxes(title="Prediksi")
                    show(fig, 380)
                    st.caption("Angka = jumlah ulasan uji. Warna = proporsi "
                               "per baris Aktual (makin gelap makin sering).")
            with b:
                with st.container(border=True):
                    card_title("Recall dan F1 per Kelas")
                    k_ = km[km["Analisis"] == pil].copy()
                    k_["F1"] = k_["F1"].fillna(0)
                    lg = k_.melt(id_vars="Kelas", value_vars=["Recall", "F1"],
                                 var_name="Ukuran", value_name="Nilai")
                    fig = px.bar(lg, x="Kelas", y="Nilai", color="Ukuran",
                                 barmode="group",
                                 category_orders={"Kelas": kls},
                                 color_discrete_sequence=[PINK, PURPLE])
                    fig.update_yaxes(range=[0, 1.05])
                    fig.update_xaxes(title=None)
                    show(fig, 380)
                    st.caption("F1 kosong (kelas tak pernah ditebak) "
                               "ditampilkan sebagai 0.")

            with st.container(border=True):
                card_title("Peubah Terpenting")
                if fim is not None and pil in set(fim["Analisis"]):
                    f_ = fim[fim["Analisis"] == pil].copy()
                    f_["Variabel"] = f_["Variabel"].str.replace("_", " ")
                    f_ = f_.sort_values("Importance")
                    fig = px.bar(f_, x="Importance", y="Variabel",
                                 orientation="h",
                                 color_discrete_sequence=[PINK])
                    fig.update_yaxes(title=None)
                    show(fig, 320)
                    st.caption("Random Forest. Ukuran importance sesuai "
                               "file Abit (relatif antar peubah).")
                else:
                    st.info("Importance tidak tersedia untuk model ini "
                            f"({info['model']}).")
            with st.expander("Detail model"):
                st.markdown(
                    f"- **Model:** {info['model']}\n"
                    f"- **Target:** {info['target']}\n"
                    f"- **Prediktor:** {info['prediktor']}\n"
                    "- **Pembagian data:** 80% latih, 20% uji (seed 123), "
                    f"{idn(r_['n'])} ulasan uji\n"
                    "- Belum ada penanganan kelas tidak seimbang "
                    "(class weight atau resampling).")

    with sub[1]:
        if "Dim1" not in df.columns:
            waiting("data_bersih.csv (kolom Dim1..Dim3)",
                    "Jua, lalu jalankan integrasi_hasil.py")
        else:
            DIM_NAMA = {"Dim1": "Dim1 (kepuasan)",
                        "Dim2": "Dim2 (tegas tidak beli lagi vs ragu)",
                        "Dim3": "Dim3 (lama pemakaian)"}
            a, b = st.columns([3, 2])
            with a:
                with st.container(border=True):
                    card_title("Plot Individu FAMD (PIC: Jua)")
                    c1, c2, c3 = st.columns(3)
                    sx = c1.selectbox("Sumbu X", list(DIM_NAMA), 0,
                                      format_func=DIM_NAMA.get, key="fx")
                    sy = c2.selectbox("Sumbu Y", list(DIM_NAMA), 1,
                                      format_func=DIM_NAMA.get, key="fy")
                    warna = c3.selectbox(
                        "Warna",
                        ["beli_lagi", "rekomendasi", "lama_penggunaan",
                         "label_sentimen"], key="fc")
                    pts = df if len(df) <= 4000 else df.sample(
                        4000, random_state=1)
                    cmap = {**BELI_COLORS, "Positif": GREEN, "Netral": AMBER,
                            "Negatif": RED}
                    if warna == "lama_penggunaan":
                        fig = px.scatter(
                            pts, x=sx + "_jitter", y=sy + "_jitter",
                            color=warna, opacity=0.45,
                            category_orders={warna: LAMA_ORDER},
                            color_discrete_sequence=[
                                TEAL, "#60A5FA", PURPLE, PINK, AMBER,
                                "#F9A8D4"])
                    else:
                        fig = px.scatter(
                            pts, x=sx + "_jitter", y=sy + "_jitter",
                            color=warna, opacity=0.45,
                            color_discrete_map=cmap)
                    fig.update_xaxes(title=DIM_NAMA[sx])
                    fig.update_yaxes(title=DIM_NAMA[sy])
                    show(fig, 420)
                    st.caption(
                        f"Menampilkan {idn(len(pts))} dari {idn(len(df))} "
                        "ulasan (sesuai filter). Titik diberi simpangan acak "
                        "kecil (jitter) agar tidak menumpuk.")
            with b:
                with st.container(border=True):
                    card_title("Ragam yang Dijelaskan (Scree Plot)")
                    ev = load_csv("famd_eigen.csv")
                    if ev is not None:
                        headline(
                            f"Dim1 <b>{fmt(ev['persen_ragam'][0])}%</b>, dua "
                            "dimensi pertama "
                            f"<b>{fmt(ev['persen_ragam_kumulatif'][1])}%</b>.")
                        fig = px.bar(ev, x=ev["dimensi"].astype(str),
                                     y="persen_ragam",
                                     color_discrete_sequence=[PURPLE])
                        fig.add_scatter(
                            x=ev["dimensi"].astype(str),
                            y=ev["persen_ragam_kumulatif"],
                            mode="lines+markers", name="kumulatif",
                            line_color=AMBER)
                        fig.update_xaxes(title="Dimensi")
                        fig.update_yaxes(title="% ragam")
                        show(fig, 300)
                        st.caption("Tidak ada siku yang tegas: dimensi 4 ke "
                                   "atas hampir datar (eigenvalue sekitar 1), "
                                   "wajar pada data dengan banyak kategori.")
                    else:
                        waiting("famd_eigen.csv", "Jua")

            a, b = st.columns(2)
            with a:
                with st.container(border=True):
                    card_title("Kontribusi Peubah per Dimensi")
                    kp = load_csv("famd_peubah.csv")
                    if kp is not None:
                        dsel = st.radio("Dimensi", [1, 2, 3], horizontal=True,
                                        key="kp_dim")
                        k2 = kp[(kp["dimensi"] == dsel)
                                & (kp["peran"] == "Aktif")]
                        k2 = k2.sort_values("kontribusi_persen")
                        fig = px.bar(k2, x="kontribusi_persen", y="peubah",
                                     orientation="h",
                                     color_discrete_sequence=[PINK])
                        fig.update_xaxes(title="Kontribusi (%)")
                        fig.update_yaxes(title=None)
                        show(fig, 300)
                        st.caption("Hanya peubah aktif. Harga dan sentimen "
                                   "dipakai sebagai peubah suplementer.")
                    else:
                        waiting("famd_peubah.csv", "Jua")
            with b:
                with st.container(border=True):
                    card_title("Peta Kategori")
                    kk = load_csv("famd_kategori.csv")
                    if kk is not None:
                        fig = px.scatter(
                            kk, x="Dim1", y="Dim2", color="peubah",
                            size="n_ulasan", text="kategori", size_max=30,
                            color_discrete_sequence=[PINK, PURPLE, TEAL])
                        fig.update_traces(textposition="top center")
                        fig.update_xaxes(title=DIM_NAMA["Dim1"])
                        fig.update_yaxes(title=DIM_NAMA["Dim2"])
                        show(fig, 340)
                    else:
                        waiting("famd_kategori.csv", "Jua")

            with st.container(border=True):
                card_title("Brand pada Dimensi Kepuasan")
                fb = load_csv("famd_brand.csv")
                if fb is not None:
                    fig = px.scatter(
                        fb, x="rata_Dim1", y="persen_beli_lagi_yes",
                        size="n_ulasan", hover_name="brand",
                        text=fb["brand"].where(fb["n_ulasan"] >= 400, ""),
                        size_max=35, color_discrete_sequence=[PINK])
                    fig.update_traces(textposition="top center")
                    fig.update_xaxes(title="Rata-rata Dim1 (kepuasan)")
                    fig.update_yaxes(title="% beli lagi (Yes)")
                    show(fig, 360)
                    st.caption("Seluruh data (tidak ikut filter). Ukuran titik "
                               "= jumlah ulasan.")
            st.caption(
                "Catatan: `beli_lagi` dan `rekomendasi` ikut sebagai peubah "
                "aktif, jadi dimensi FAMD sebagian besar mencerminkan niat "
                "beli ulang itu sendiri (Dim2: 63,7% kontribusi dari "
                "beli_lagi).")

    with sub[2]:
        r_all = load_csv("rules.csv")
        AN = {
            "A_kata_bersamaan": (
                "A. Kata bersamaan",
                "Kata yang sering muncul bersamaan dalam satu ulasan."),
            "B_profil_kulit_kata": (
                "B. Profil kulit ke kata",
                "Kata yang berkaitan dengan tipe atau masalah kulit reviewer."),
            "C_pemicu_ketidakpuasan": (
                "C. Pemicu ketidakpuasan",
                "Kata yang berkaitan dengan label ketidakpuasan "
                "(Kemasan, Harga, Efektivitas, No, Ya)."),
            "D_tier_harga": (
                "D. Tier harga ke kata",
                "Kata yang khas pada produk Murah, Menengah, atau Mahal."),
        }
        with st.container(border=True):
            card_title("Aturan Asosiasi (PIC: Restu)")
            if r_all is None or "lhs_label" not in r_all.columns:
                waiting("rules.csv", "Restu, lalu jalankan integrasi_hasil.py")
            else:
                pilih = st.radio("Analisis", list(AN),
                                 format_func=lambda k: AN[k][0],
                                 horizontal=True)
                st.caption(AN[pilih][1])
                r = r_all[r_all["analisis"] == pilih].copy()
                lo, hi = float(r["lift"].min()), float(r["lift"].max())
                s1, s2, s3 = st.columns(3)
                min_lift = s1.slider("Lift minimum", round(lo, 2),
                                     round(hi, 2), round(lo, 2), 0.05) \
                    if hi > lo else lo
                min_conf = s2.slider("Confidence minimum", 0.0,
                                     round(float(r["confidence"].max()), 2),
                                     0.0, 0.01)
                top_n = s3.slider("Tampilkan N teratas", 5, 30, 15)
                r = r[(r["lift"] >= min_lift)
                      & (r["confidence"] >= min_conf)]
                r = r.sort_values("lift", ascending=False)
                r["aturan"] = r["lhs_label"] + " → " + r["rhs_label"]
                a, b = st.columns([3, 2])
                with a:
                    if len(r) == 0:
                        st.info("Tidak ada aturan yang lolos. Longgarkan "
                                "slider.")
                    else:
                        t = r.head(top_n).iloc[::-1]
                        fig = px.bar(
                            t, x="lift", y="aturan", orientation="h",
                            hover_data=["support", "confidence", "count"],
                            color_discrete_sequence=[PURPLE])
                        fig.update_yaxes(title=None)
                        show(fig, max(280, 24 * len(t) + 80))
                with b:
                    table(r[["lhs_label", "rhs_label", "support",
                             "confidence", "lift", "count"]]
                          .round(3).reset_index(drop=True))
                    st.caption(f"{len(r)} aturan lolos filter.")
                par = load_csv("parameter_analisis.csv")
                if par is not None:
                    pr = par[par["analisis"] == pilih[0]]
                    if len(pr):
                        st.caption("Parameter analisis: "
                                   + pr["parameter"].iloc[0])
                st.caption("Support kecil (kurang dari 3% ulasan), jadi lift "
                           "tinggi sering berasal dari kata yang jarang. "
                           "Baca sebagai pola eksploratif.")

                if pilih == "D_tier_harga":
                    d2 = load_csv("assoc_D2_harga_tipe_kulit.csv")
                    if d2 is not None:
                        st.markdown("**Tier harga dan tipe kulit reviewer** "
                                    "(lift 1 = tidak ada kaitan)")
                        pv = d2.pivot(index="tier_harga", columns="tipe",
                                      values="lift").reindex(
                            ["Murah", "Menengah", "Mahal"])
                        fig = px.imshow(pv, text_auto=".2f", aspect="auto",
                                        color_continuous_scale="RdPu",
                                        color_continuous_midpoint=1)
                        fig.update_coloraxes(showscale=False)
                        show(fig, 240)
                        st.caption(
                            f"Lift antara {fmt(d2['lift'].min(), 2)} dan "
                            f"{fmt(d2['lift'].max(), 2)}: tier harga hampir "
                            "tidak terkait dengan tipe kulit reviewer.")

    with sub[3]:
        c_all = load_csv("cluster.csv")
        if c_all is None or "cluster" not in c_all.columns:
            waiting("cluster.csv", "El, lalu jalankan integrasi_hasil.py")
        else:
            c_all["cluster"] = "Cluster " + c_all["cluster"].astype(str)
            c = c_all[c_all["brand"].isin(pilih_brand)] \
                if pilih_brand else c_all
            AXES = {"harga_tengah": "Harga tengah (Rp)",
                    "rating_rata": "Rating rata-rata",
                    "beli_lagi_rate": "Proporsi beli lagi",
                    "rekomendasi_rate": "Proporsi rekomendasi",
                    "PC1": "PC1", "PC2": "PC2"}
            a, b = st.columns([3, 2])
            with a:
                with st.container(border=True):
                    card_title("Hasil K-Means pada Produk (PIC: El)")
                    s1, s2 = st.columns(2)
                    cx = s1.selectbox("Sumbu X", list(AXES), 0,
                                      format_func=AXES.get, key="cx")
                    cy = s2.selectbox("Sumbu Y", list(AXES), 1,
                                      format_func=AXES.get, key="cy")
                    fig = px.scatter(
                        c, x=cx, y=cy, color="cluster", opacity=0.8,
                        hover_name="nama_produk",
                        hover_data=["brand", "n_review"],
                        color_discrete_sequence=[PINK, TEAL])
                    fig.update_xaxes(title=AXES[cx])
                    fig.update_yaxes(title=AXES[cy])
                    show(fig, 400)
                    st.caption(
                        f"{len(c)} produk (filter brand berlaku). Unit "
                        "analisis adalah produk, bukan ulasan. PC1 dan PC2 "
                        "adalah proyeksi PCA dari semua variabel klaster.")
            with b:
                with st.container(border=True):
                    card_title("Profil Cluster")
                    prof = c_all.groupby("cluster").agg(
                        Produk=("nama_produk", "size"),
                        Harga=("harga_tengah", "mean"),
                        Rating=("rating_rata", "mean"),
                        Rek_pct=("rekomendasi_rate",
                                         lambda s: s.mean() * 100),
                        Beli_pct=("beli_lagi_rate",
                                       lambda s: s.mean() * 100),
                        Komb_pct=("prop_kombinasi",
                                       lambda s: s.mean() * 100),
                        Berm_pct=("prop_berminyak",
                                       lambda s: s.mean() * 100),
                    ).round(2).reset_index()
                    prof["Harga"] = prof["Harga"].round(0).astype(int)
                    table(prof)
                    sil = load_csv("cluster_silhouette.csv")
                    if sil is not None:
                        s_best = sil.sort_values("silhouette").iloc[-1]
                        headline(f"Silhouette k={int(s_best['k'])}: "
                                 f"<b>{fmt(s_best['silhouette'], 3)}</b> "
                                 "(pemisahan lemah).")
                        fig = px.bar(sil, x=sil["k"].astype(str),
                                     y="silhouette",
                                     text=sil["silhouette"].map(
                                         lambda v: f"{v:.3f}"),
                                     color_discrete_sequence=[PURPLE])
                        fig.update_xaxes(title="Jumlah cluster (k)")
                        show(fig, 240)
            a, b = st.columns(2)
            with a:
                with st.container(border=True):
                    card_title("Brand per Cluster (8 brand terbanyak)")
                    top8 = c_all["brand"].value_counts().head(8).index
                    bc = (c_all[c_all["brand"].isin(top8)]
                          .groupby(["brand", "cluster"]).size()
                          .reset_index(name="Produk"))
                    fig = px.bar(bc, x="brand", y="Produk", color="cluster",
                                 barmode="stack",
                                 color_discrete_sequence=[PINK, TEAL])
                    fig.update_xaxes(title=None)
                    show(fig, 300)
            with b:
                with st.container(border=True):
                    card_title("Daftar Produk")
                    pc = st.multiselect("Cluster", sorted(c_all["cluster"]
                                                          .unique()),
                                        default=sorted(c_all["cluster"]
                                                       .unique()))
                    lp = c[c["cluster"].isin(pc)][[
                        "nama_produk", "brand", "cluster", "harga_tengah",
                        "rating_rata", "beli_lagi_rate", "n_review"]]
                    table(lp.sort_values("beli_lagi_rate", ascending=False)
                          .round(3))
            st.caption(
                "Silhouette 0,232 menunjukkan klaster belum terpisah tegas, "
                "jadi hasil ini segmentasi eksploratif. Label klaster 1 dan 2 "
                "bersifat teknis, bukan peringkat kualitas.")

    with sub[4]:
        with st.container(border=True):
            card_title("Simulasi Peluang Beli Lagi")
            st.caption("Dihitung dari frekuensi data historis (seluruh "
                       "ulasan), bukan dari model klasifikasi.")
            s1, s2, s3 = st.columns(3)
            sim_rek = s1.selectbox("Rekomendasi", ["Yes", "No"])
            sim_lama = s2.selectbox("Lama pemakaian", LAMA_ORDER, index=2)
            sim_rating = s3.select_slider("Rating", options=[1, 2, 3, 4, 5],
                                          value=5)
            cocok = df_all[(df_all["rekomendasi"] == sim_rek)
                           & (df_all["lama_penggunaan"] == sim_lama)
                           & (df_all["rating"].round() == sim_rating)]
            if len(cocok) == 0:
                st.info("Tidak ada ulasan dengan kombinasi ini.")
            else:
                dist = (cocok["beli_lagi"].value_counts(normalize=True) * 100
                        ).reindex(["Yes", "Maybe", "No"]).fillna(0).round(1)
                dist = dist.reset_index()
                dist.columns = ["Beli Lagi", "Persen"]
                headline(f"Dari <b>{idn(len(cocok))}</b> ulasan serupa, "
                         f"<b>{fmt(dist.iloc[0]['Persen'])}%</b> berniat "
                         "beli lagi.")
                if len(cocok) < 30:
                    st.warning("Contoh kurang dari 30 ulasan, hasil kurang "
                               "andal.")
                fig = px.bar(dist, x="Beli Lagi", y="Persen",
                             text=dist["Persen"].map(lambda v: f"{v}%"),
                             color="Beli Lagi",
                             color_discrete_map=BELI_COLORS)
                fig.update_yaxes(range=[0, 100])
                show(fig, 280)

# ===== 6. Key Insights =====
with tabs[5]:
    rec_y = pct_yes(df_all.loc[df_all["rekomendasi"] == "Yes", "beli_lagi"])
    rec_n = pct_yes(df_all.loc[df_all["rekomendasi"] == "No", "beli_lagi"])
    lama_y = pct_yes(df_all.loc[df_all["lama_penggunaan"] == "> 1 tahun",
                                "beli_lagi"])
    lama_n = pct_yes(df_all.loc[df_all["lama_penggunaan"] == "< 1 minggu",
                                "beli_lagi"])
    r_yes = df_all.loc[df_all["beli_lagi"] == "Yes", "rating"].mean()
    r_no = df_all.loc[df_all["beli_lagi"] == "No", "rating"].mean()

    st.markdown("##### Eksplorasi dan seleksi peubah")
    insight(f"<b>Rekomendasi = loyalitas.</b> {fmt(rec_y)}% yang "
            f"merekomendasikan produk berniat beli lagi, hanya "
            f"{fmt(rec_n)}% pada yang tidak.")
    insight(f"<b>Pengguna jangka panjang paling setia.</b> {fmt(lama_y)}% "
            f"pengguna lebih dari 1 tahun berniat beli lagi, dibanding "
            f"{fmt(lama_n)}% pada pengguna kurang dari 1 minggu.")
    insight(f"<b>Rating membedakan.</b> Rata-rata rating kelompok beli lagi "
            f"Yes {fmt(r_yes, 2)} vs No {fmt(r_no, 2)}.")
    if sel_df is not None:
        n_sig = int((sel_df["pvalue"] < 0.05).sum())
        tdk = ", ".join(sel_df.loc[sel_df["pvalue"] >= 0.05, "peubah"])
        insight(f"<b>{n_sig} dari {len(sel_df)} peubah signifikan</b> "
                f"terhadap beli lagi (p < 0,05)."
                + (f" Tidak signifikan: {tdk}." if tdk else ""))
    if "label_sentimen" in df_all.columns:
        sp = (df_all["label_sentimen"] == "Positif").mean() * 100
        sn = (df_all["label_sentimen"] == "Negatif").mean() * 100
        insight(f"<b>Sentimen dominan positif</b> ({fmt(sp)}%), negatif "
                f"hanya {fmt(sn)}%.")
    big = df_all.groupby("brand").filter(lambda g: len(g) >= 200)
    if len(big):
        bp = big.groupby("brand")["beli_lagi"].apply(pct_yes).sort_values()
        insight(f"<b>Brand dengan 200 ulasan atau lebih:</b> niat beli lagi "
                f"tertinggi {bp.index[-1]} ({fmt(bp.iloc[-1])}%), "
                f"terendah {bp.index[0]} ({fmt(bp.iloc[0])}%).")

    st.markdown("##### Hasil pemodelan")
    ev_i = load_csv("famd_eigen.csv")
    kp_i = load_csv("famd_peubah.csv")
    if ev_i is not None:
        txt = (f"<b>FAMD.</b> Dim1 (kepuasan keseluruhan) menjelaskan "
               f"{fmt(ev_i['persen_ragam'][0])}% ragam; dua dimensi pertama "
               f"{fmt(ev_i['persen_ragam_kumulatif'][1])}%, jadi peta 2D "
               "hanya penyederhanaan.")
        if kp_i is not None:
            v = kp_i[(kp_i["dimensi"] == 2) & (kp_i["peubah"] == "beli_lagi")]
            if len(v):
                txt += (f" Dim2 hampir seluruhnya dibentuk niat beli ulang "
                        f"({fmt(v['kontribusi_persen'].iloc[0])}% "
                        "kontribusi).")
        insight(txt)
    c_i = load_csv("cluster.csv")
    if c_i is not None and "cluster" in c_i.columns:
        g = c_i.groupby("cluster").agg(
            n=("nama_produk", "size"), harga=("harga_tengah", "mean"),
            bl=("beli_lagi_rate", "mean"), rt=("rating_rata", "mean"))
        if len(g) == 2:
            a_, b_ = g.index[0], g.index[1]
            insight(
                f"<b>Clustering.</b> K-Means membagi {int(g['n'].sum())} "
                f"produk menjadi 2 klaster. Klaster {a_}: {int(g.loc[a_, 'n'])} "
                f"produk, beli lagi {fmt(g.loc[a_, 'bl'] * 100)}%, rating "
                f"{fmt(g.loc[a_, 'rt'], 2)}. Klaster {b_}: "
                f"{int(g.loc[b_, 'n'])} produk, beli lagi "
                f"{fmt(g.loc[b_, 'bl'] * 100)}%, rating "
                f"{fmt(g.loc[b_, 'rt'], 2)}. Pembeda utama adalah kepuasan, "
                "bukan harga. Silhouette 0,232 (pemisahan lemah).")
    r_i = load_csv("rules.csv")
    d2_i = load_csv("assoc_D2_harga_tipe_kulit.csv")
    if r_i is not None and "lhs_label" in r_i.columns:
        ra = r_i[r_i["analisis"] == "A_kata_bersamaan"].sort_values(
            "lift", ascending=False)
        if len(ra):
            t0 = ra.iloc[0]
            insight(f"<b>Association rules.</b> Pasangan kata terkuat: "
                    f"\"{t0['lhs_label']}\" dan \"{t0['rhs_label']}\" "
                    f"(lift {fmt(t0['lift'])}, confidence "
                    f"{fmt(t0['confidence'] * 100, 0)}%).")
    if d2_i is not None:
        insight(f"<b>Harga tidak terkait tipe kulit.</b> Lift tier harga "
                f"terhadap tipe kulit reviewer hanya "
                f"{fmt(d2_i['lift'].min(), 2)} sampai "
                f"{fmt(d2_i['lift'].max(), 2)} (1 = tidak ada kaitan).")
    km_i, cmx_i, fim_i = load_klas()
    if km_i is not None:
        ks_i = klas_summary(km_i, cmx_i)
        a4 = ks_i[ks_i["analisis"] == "Niat Pembelian Ulang"]
        if len(a4):
            a4 = a4.iloc[0]
            k4 = km_i[km_i["Analisis"] == "Niat Pembelian Ulang"]
            rc = dict(zip(k4["Kelas"], k4["Recall"]))
            txt = (f"<b>Klasifikasi niat beli ulang.</b> Random Forest "
                   f"akurasi {fmt(a4['acc'] * 100)}%, hanya "
                   f"{fmt((a4['acc'] - a4['nir']) * 100)} poin di atas "
                   f"tebakan mayoritas ({fmt(a4['nir'] * 100)}%), kappa "
                   f"{fmt(a4['kappa'], 2)}. Recall kelas No "
                   f"{fmt(rc.get('No', 0) * 100)}% dan Maybe "
                   f"{fmt(rc.get('Maybe', 0) * 100)}%.")
            if fim_i is not None:
                f4 = fim_i[fim_i["Analisis"] == "Niat Pembelian Ulang"] \
                    .sort_values("Importance", ascending=False).head(3)
                if len(f4):
                    txt += (" Peubah terpenting: " + ", ".join(
                        f4["Variabel"].str.replace("_", " ")) + ".")
            insight(txt)
        lemah = ks_i[(ks_i["acc"] - ks_i["nir"]) * 100 <= 0.5]
        if len(lemah):
            item = [f"{r['analisis'].lower()} (akurasi {fmt(r['acc'] * 100)}%, "
                    f"tebakan mayoritas {fmt(r['nir'] * 100)}%, recall kelas "
                    f"terkecil {fmt(r['rec_min'] * 100, 0)}%)"
                    for _, r in lemah.iterrows()]
            insight("<b>Tidak mengalahkan tebakan mayoritas.</b> "
                    + "; ".join(item) + ". Akurasi saja tidak cukup.")
    else:
        insight("ISI: hasil klasifikasi (Abit).", todo=True)

# ===== 7. Kesimpulan =====
with tabs[6]:
    baru = (df_all["lama_penggunaan"] == "< 1 minggu").mean() * 100
    a, b, c = st.columns(3)
    with a:
        with st.container(border=True):
            card_title("Kesimpulan")
            st.markdown(
                "- Faktor utama pembelian ulang: rekomendasi, lama "
                "pemakaian, dan rating. Harga tidak signifikan.\n"
                "- FAMD: dimensi utama adalah kepuasan keseluruhan, dimensi "
                "kedua memisahkan yang tegas tidak beli lagi dari yang ragu.\n"
                "- Clustering: 2 kelompok produk dibedakan oleh kepuasan "
                "dan niat beli ulang, bukan harga.\n"
                "- Klasifikasi niat beli ulang (Random Forest): akurasi "
                "86,2%, hanya sedikit di atas tebakan mayoritas (85,1%). "
                "Kelas No dan Maybe sulit diprediksi."
            )
    with b:
        with st.container(border=True):
            card_title("Rekomendasi")
            st.markdown(
                "- **Brand:** dorong pelanggan memberi ulasan dan "
                "rekomendasi, karena itu penanda loyalitas\n"
                "- **Brand:** tinjau produk di klaster dengan beli ulang "
                "lebih rendah\n"
                "- **Sociolla:** keluhan kemasan, harga, dan efektivitas "
                "perlu dipantau lewat kata kunci ulasan (analisis C)\n"
                "- **Sociolla:** rekomendasi tidak perlu dibedakan menurut "
                "tier harga, karena tier tidak terkait tipe kulit"
            )
    with c:
        with st.container(border=True):
            card_title("Keterbatasan")
            st.markdown(
                f"- {fmt(baru, 0)}% ulasan dari pemakai kurang dari 1 minggu\n"
                f"- Rating sangat condong tinggi (rata-rata "
                f"{fmt(df_all['rating'].mean(), 2)})\n"
                "- Kelas beli_lagi tidak seimbang, model klasifikasi belum "
                "menanganinya\n"
                "- Sentimen pakai lexicon sederhana\n"
                "- Silhouette clustering 0,232 (pemisahan lemah)\n"
                "- FAMD memakai beli_lagi sebagai peubah aktif\n"
                "- Support association rules kecil\n"
                "- Data hanya dari satu platform"
            )
