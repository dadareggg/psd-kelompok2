import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Beli Lagi atau Beralih?", page_icon="💜", layout="wide")

PINK = "#D6249F"
PURPLE = "#5B2A86"
PALETTE = ["#D6249F", "#8E44AD", "#F39AD0", "#5B2A86", "#C9A0DC"]
DATA_DIR = "data"

st.markdown(
    f"""
    <style>
    h1, h2, h3 {{ color: {PURPLE}; }}
    [data-testid="stMetricValue"] {{ color: {PINK}; }}
    .insight {{ background:#F5E8FB; border-left:6px solid {PINK};
               padding:12px 16px; border-radius:8px; margin-bottom:10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def load_csv(name):
    """Baca CSV hasil modeler. Return None kalau belum ada."""
    path = os.path.join(DATA_DIR, name)
    return pd.read_csv(path) if os.path.exists(path) else None


def waiting(name, who):
    st.info(f"Menunggu file `{DATA_DIR}/{name}` dari {who}.")


# ---------------- Data ringkasan dari infografis ----------------
keluhan = pd.DataFrame(
    {
        "Keluhan": ["Kulit Kusam", "Berjerawat", "Pori Besar", "Komedo",
                    "Kantung Mata", "Flek", "Stretch Mark"],
        "Persen": [97.75, 95.50, 88.57, 72.42, 55.50, 41.27, 39.30],
    }
)
tipe_kulit = pd.DataFrame(
    {"Tipe": ["Kombinasi", "Berminyak", "Sensitif", "Kering", "Normal"],
     "Persen": [33.4, 21.8, 19.3, 16.3, 9.2]}
)
sentimen = pd.DataFrame(
    {"Sentimen": ["Positif", "Netral", "Negatif"], "Persen": [60.4, 30.5, 9.1]}
)
brand = ["Skintific", "COSRX", "Skin1004", "Medheal", "Glad2Glow",
         "Npure", "Becoming", "Derma Angle", "Round Lab", "Carasun"]
variabel = pd.DataFrame(
    {
        "Kode": ["Y"] + [f"X{i}" for i in range(1, 11)],
        "Variabel": ["Pembelian Ulang", "Harga Minimum", "Harga Maksimum",
                     "Tipe Kulit", "Rating", "Efektivitas", "Kemasan",
                     "Tekstur", "Kualitas Harga", "Rekomendasi",
                     "Lama Penggunaan"],
    }
)
beli_ulang = pd.DataFrame(
    {
        "Rekomendasi": ["No"] * 3 + ["Yes"] * 3,
        "Beli Lagi": ["No", "Maybe", "Yes"] * 2,
        "Proporsi": [60.2, 37.3, 2.5, 1.8, 10.1, 88.1],
    }
)

# ---------------- Sidebar ----------------
st.sidebar.title("💜 Dashboard")
st.sidebar.caption("Pengantar Sains Data | Kelompok 2 (K1)")
PAGES = [
    "1. Project Overview",
    "2. Data Overview",
    "3. Exploratory Data Analysis",
    "4. Data Preprocessing",
    "5. Modeling",
    "6. Key Insights",
    "7. Kesimpulan dan Rekomendasi",
]
page = st.sidebar.radio("Menu", PAGES)

# ---------------- 1. Project Overview ----------------
if page == PAGES[0]:
    st.title("Beli Lagi atau Beralih?")
    st.subheader("Analisis Faktor Pembelian Ulang Produk Skincare di Sociolla")

    c1, c2, c3 = st.columns(3)
    c1.metric("Data Bersih", "9.119")
    c2.metric("Peubah", "11")
    c3.metric("Rekomendasi → Beli Lagi", "88,1%")

    st.markdown("### Latar Belakang")
    st.write(
        "Setiap orang punya jenis dan masalah kulit berbeda. Produk yang cocok "
        "di kulit orang lain belum tentu cocok di kulit kita. Ribuan ulasan "
        "konsumen bisa diolah untuk melihat pengalaman, persepsi, dan faktor "
        "yang berkaitan dengan kecocokan serta pembelian ulang."
    )
    st.markdown("### Tujuan")
    st.markdown(
        "- Mengeksplorasi karakteristik reviewer dan produk skincare\n"
        "- Mengidentifikasi faktor yang berkaitan dengan pembelian ulang\n"
        "- Memodelkan pembelian ulang (klasifikasi) dan menemukan pola "
        "(FAMD, clustering, association)\n"
        "- Memberi rekomendasi bagi brand dan platform"
    )

# ---------------- 2. Data Overview ----------------
elif page == PAGES[1]:
    st.title("Data Overview")
    st.markdown("### Sumber Data")
    st.write("Website resmi Sociolla, diambil dengan web scraping.")
    st.markdown(
        "**Alur:** Setup Driver & Target → Ambil Daftar Produk → Buka Tab "
        "Review → Scrapping → Looping Halaman & Produk → Ekspor Data"
    )

    c1, c2 = st.columns(2)
    c1.metric("Data Kotor", "11.401")
    c2.metric("Data Bersih", "9.119")

    st.markdown("### Variabel")
    st.dataframe(variabel, use_container_width=True, hide_index=True)

    st.markdown("### Preview Data")
    df = load_csv("data_bersih.csv")
    if df is not None:
        st.dataframe(df.head(100), use_container_width=True)
        st.caption(f"{df.shape[0]:,} baris, {df.shape[1]} kolom")
    else:
        waiting("data_bersih.csv", "tim dashboard")

# ---------------- 3. EDA ----------------
elif page == PAGES[2]:
    st.title("Exploratory Data Analysis")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(keluhan.sort_values("Persen"), x="Persen", y="Keluhan",
                     orientation="h", text="Persen",
                     color_discrete_sequence=[PINK],
                     title="Keluhan kulit reviewer (%)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(tipe_kulit, names="Tipe", values="Persen", hole=0.5,
                     color_discrete_sequence=PALETTE,
                     title="Tipe kulit reviewer")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(sentimen, x="Sentimen", y="Persen", text="Persen",
                     color="Sentimen",
                     color_discrete_map={"Positif": "#2ECC71",
                                         "Netral": "#F1C40F",
                                         "Negatif": "#E74C3C"},
                     title="Distribusi sentimen (lexicon-based)")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.markdown("#### 10 Brand Direkomendasikan")
        for i, b in enumerate(brand, 1):
            st.write(f"**{i}.** {b}")

    fig = px.bar(beli_ulang, x="Rekomendasi", y="Proporsi", color="Beli Lagi",
                 barmode="stack", text="Proporsi",
                 color_discrete_map={"No": "#E74C3C", "Maybe": "#F39C12",
                                     "Yes": "#27AE60"},
                 title="Niat beli lagi menurut rekomendasi produk (%)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Wordcloud")
    if os.path.exists(os.path.join(DATA_DIR, "wordcloud.png")):
        st.image(os.path.join(DATA_DIR, "wordcloud.png"))
    else:
        waiting("wordcloud.png", "Darell")

# ---------------- 4. Preprocessing ----------------
elif page == PAGES[3]:
    st.title("Data Preprocessing")

    st.markdown("### Langkah Cleaning")
    st.markdown(
        "1. Hapus duplikat dan baris kosong (11.401 → 9.119)\n"
        "2. Tangani missing value\n"
        "3. Standarisasi format (harga, lama penggunaan)\n"
        "4. Encoding variabel kategorik\n"
        "5. Seleksi peubah (ANOVA dan Chi-square)\n\n"
        "*Sesuaikan daftar ini dengan proses yang benar-benar dilakukan.*"
    )

    c1, c2 = st.columns(2)
    c1.metric("Sebelum", "11.401")
    c2.metric("Sesudah", "9.119", delta="-2.282")

    st.markdown("### Seleksi Peubah")
    st.write("Kriteria: p-value < 0,05 dipertahankan. "
             "ANOVA untuk peubah numerik, Chi-square untuk kategorik.")
    sel = load_csv("seleksi_peubah.csv")
    if sel is not None:
        st.dataframe(sel, use_container_width=True, hide_index=True)
        if {"peubah", "pvalue"} <= set(sel.columns):
            sel["-log10(p)"] = -(sel["pvalue"].clip(lower=1e-300)).apply(
                lambda p: __import__("math").log10(p))
            fig = px.bar(sel.sort_values("-log10(p)"), x="-log10(p)",
                         y="peubah", orientation="h",
                         color_discrete_sequence=[PINK])
            st.plotly_chart(fig, use_container_width=True)
    else:
        waiting("seleksi_peubah.csv (kolom: peubah, uji, pvalue)", "tim dashboard")

# ---------------- 5. Modeling ----------------
elif page == PAGES[4]:
    st.title("Modeling")
    t1, t2, t3, t4 = st.tabs(
        ["Klasifikasi", "FAMD", "Association Rules", "Clustering"]
    )

    with t1:
        st.subheader("Supervised: Klasifikasi Pembelian Ulang")
        st.caption("PIC: Abit")
        m = load_csv("klasifikasi_metrics.csv")
        if m is not None:
            st.dataframe(m, use_container_width=True, hide_index=True)
        else:
            waiting("klasifikasi_metrics.csv (model, akurasi, f1, ...)", "Abit")
        if os.path.exists(os.path.join(DATA_DIR, "confusion_matrix.png")):
            st.image(os.path.join(DATA_DIR, "confusion_matrix.png"))
        fi = load_csv("feature_importance.csv")
        if fi is not None:
            fig = px.bar(fi.sort_values(fi.columns[1]), x=fi.columns[1],
                         y=fi.columns[0], orientation="h",
                         color_discrete_sequence=[PINK],
                         title="Feature importance")
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.subheader("Unsupervised: FAMD")
        st.caption("PIC: Jua")
        f = load_csv("famd_coords.csv")
        if f is not None:
            cols = list(f.columns)
            color = "beli_lagi" if "beli_lagi" in cols else None
            fig = px.scatter(f, x=cols[0], y=cols[1], color=color,
                             color_discrete_sequence=PALETTE,
                             title="Plot individu pada Dim1 vs Dim2")
            st.plotly_chart(fig, use_container_width=True)
        else:
            waiting("famd_coords.csv (Dim1, Dim2, beli_lagi)", "Jua")
        ev = load_csv("famd_eigen.csv")
        if ev is not None:
            fig = px.bar(ev, x=ev.columns[0], y=ev.columns[1],
                         color_discrete_sequence=[PURPLE],
                         title="Scree plot")
            st.plotly_chart(fig, use_container_width=True)

    with t3:
        st.subheader("Unsupervised: Association Rules")
        st.caption("PIC: Restu")
        r = load_csv("rules.csv")
        if r is not None:
            st.dataframe(r.sort_values("lift", ascending=False)
                         if "lift" in r.columns else r,
                         use_container_width=True, hide_index=True)
            if {"support", "confidence", "lift"} <= set(r.columns):
                fig = px.scatter(r, x="support", y="confidence", color="lift",
                                 color_continuous_scale="Purples",
                                 title="Support vs Confidence (warna = lift)")
                st.plotly_chart(fig, use_container_width=True)
        else:
            waiting("rules.csv (antecedents, consequents, support, confidence, lift)", "Restu")

    with t4:
        st.subheader("Unsupervised: Clustering")
        st.caption("PIC: El")
        c = load_csv("cluster.csv")
        if c is not None:
            cols = list(c.columns)
            if "cluster" in cols:
                c["cluster"] = c["cluster"].astype(str)
                fig = px.scatter(c, x=cols[0], y=cols[1], color="cluster",
                                 color_discrete_sequence=PALETTE,
                                 title="Hasil clustering")
                st.plotly_chart(fig, use_container_width=True)
        else:
            waiting("cluster.csv (Dim1, Dim2, cluster)", "El")
        prof = load_csv("cluster_profile.csv")
        if prof is not None:
            st.markdown("#### Profil Cluster")
            st.dataframe(prof, use_container_width=True, hide_index=True)

# ---------------- 6. Key Insights ----------------
elif page == PAGES[5]:
    st.title("Key Insights")
    insights = [
        "**Rekomendasi = loyalitas.** 88,1% konsumen yang merekomendasikan "
        "produk berniat beli lagi, hanya 2,5% pada yang tidak.",
        "**7 dari 9 peubah signifikan** terhadap beli lagi (p-value < 0,05).",
        "**Sentimen dominan positif** (60,4%), negatif hanya 9,1%.",
        "**Tipe kulit terbanyak: kombinasi** (33,4%), keluhan utama kulit "
        "kusam dan jerawat.",
        "ISI: temuan dari klasifikasi, FAMD, clustering, association.",
    ]
    for t in insights:
        st.markdown(f'<div class="insight">{t}</div>', unsafe_allow_html=True)

# ---------------- 7. Kesimpulan ----------------
elif page == PAGES[6]:
    st.title("Kesimpulan dan Rekomendasi")
    st.markdown("### Kesimpulan")
    st.markdown(
        "- ISI: jawab tujuan proyek satu per satu\n"
        "- Faktor utama pembelian ulang: rekomendasi dan lama penggunaan\n"
        "- Model terbaik: ISI nama model dan skor"
    )
    st.markdown("### Rekomendasi")
    st.markdown(
        "- **Brand:** dorong ulasan dan rekomendasi pelanggan\n"
        "- **Sociolla:** personalisasi produk berdasarkan tipe kulit\n"
        "- ISI: rekomendasi dari cluster dan association rules"
    )
    st.markdown("### Keterbatasan")
    st.markdown(
        "- Sentimen pakai lexicon sederhana\n"
        "- Data hanya dari satu platform"
    )
