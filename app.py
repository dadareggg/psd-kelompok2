import os

import numpy as np
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

PINK, PURPLE, TEAL = "#E040A8", "#8E5CF0", "#2DD4BF"
AMBER, RED, GREEN = "#F59E0B", "#EF4444", "#22C55E"
MUTED, LINE = "#9AA0C3", "#2B2D4A"
BELI_COLORS = {"Yes": GREEN, "Maybe": AMBER, "No": RED}
DATA_DIR = "data"

TIPE = ["Kombinasi", "Berminyak", "Sensitif", "Kering", "Normal"]
KELUHAN = ["Kulit Kusam", "Jerawat", "Pori Besar", "Komedo",
           "Kantung Mata", "Flek", "Stretch Mark"]
LAMA_ORDER = ["< 1 minggu", "1 minggu - 1 bulan", "1-3 bulan",
              "3-6 bulan", "6 bulan - 1 tahun", "> 1 tahun"]
LAMA_ID = {
    "Less Than 1 Week": "< 1 minggu", "1 Week - 1 Month": "1 minggu - 1 bulan",
    "1 - 3 Months": "1-3 bulan", "3 - 6 Months": "3-6 bulan",
    "6 Months - 1 Year": "6 bulan - 1 tahun", "More Than 1 Year": "> 1 tahun",
}
SHORT = {"Kepuasan Konsumen": "Kepuasan", "Durasi Penggunaan": "Durasi pakai",
         "Rekomendasi Produk": "Rekomendasi",
         "Niat Pembelian Ulang": "Niat beli ulang"}

st.markdown(
    f"""
    <style>
    .block-container {{ padding-top: 1.6rem; max-width: 1180px; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 16px; border: 1px solid {LINE}; background: #17182F; }}
    .title {{ font-size: 2.1rem; font-weight: 800; line-height: 1.1;
             background: linear-gradient(90deg,{PINK},{PURPLE});
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .lead {{ font-size: 1.05rem; margin: 6px 0 2px 0; max-width: 860px; }}
    .lead b {{ color: {PINK}; }}
    .meta {{ color: {MUTED}; font-size: .8rem; }}
    .chips span {{ display:inline-block; margin: 6px 8px 0 0; padding: 4px 12px;
                  border-radius: 999px; background:#241B3D; color:#E9D5FF;
                  font-size:.8rem; }}
    .kpi {{ padding: 14px 16px; border-radius: 16px; background:#17182F;
           border: 1px solid {LINE}; }}
    .kpi .label {{ color:{MUTED}; font-size:.8rem; }}
    .kpi .value {{ font-size: 2rem; font-weight: 800; margin-top: 4px; }}
    .kpi .unit {{ font-size:.9rem; color:{MUTED}; margin-left:4px; }}
    .h {{ font-size: 1.15rem; font-weight: 700; margin: 34px 0 4px 0; }}
    .h b {{ color: {PINK}; }}
    .sub {{ color: {MUTED}; font-size: .85rem; margin-bottom: 10px; }}
    .flow {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; }}
    .flow .p {{ padding: 8px 14px; border-radius: 12px; background:#17182F;
               border: 1px solid {LINE}; font-size:.9rem; }}
    .flow .p.on {{ border-color:{PINK}; color:#fff; font-weight:700; }}
    .flow .s {{ color:{MUTED}; }}
    .cardt {{ font-weight: 700; font-size: 1rem; }}
    .cardd {{ color:{MUTED}; font-size:.8rem; margin-bottom: 6px; }}
    .res {{ font-size:.95rem; margin-top: 4px; }}
    .res b {{ color:{PINK}; }}
    .big {{ font-size: 2.2rem; font-weight: 800; color:{PINK}; line-height:1.1; }}
    .bigd {{ font-size: .95rem; margin-top: 6px; }}
    .bullets {{ margin: 0; padding-left: 1.1rem; }}
    .bullets li {{ margin-bottom: 8px; }}
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


def load_csv(name):
    p = os.path.join(DATA_DIR, name)
    return _read(p, os.path.getmtime(p)).copy() if os.path.exists(p) else None


def show(fig, height=260, legend=True):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font_color="#D7DAF0",
        margin=dict(l=4, r=4, t=8, b=4), legend_title_text="",
        showlegend=legend,
        legend=dict(orientation="h", y=1.12, x=0))
    fig.update_xaxes(gridcolor=LINE, zeroline=False)
    fig.update_yaxes(gridcolor=LINE, zeroline=False)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def table(d, **kw):
    try:
        st.dataframe(d, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(d, use_container_width=True, hide_index=True, **kw)


def kpi(col, label, value, unit=""):
    col.markdown(
        f'<div class="kpi"><div class="label">{label}</div>'
        f'<div class="value">{value}<span class="unit">{unit}</span></div></div>',
        unsafe_allow_html=True)


def heading(html, sub=""):
    st.markdown(f'<div class="h">{html}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="sub">{sub}</div>', unsafe_allow_html=True)


def card_head(title, desc):
    st.markdown(f'<div class="cardt">{title}</div><div class="cardd">{desc}</div>',
                unsafe_allow_html=True)


def result(html):
    st.markdown(f'<div class="res">{html}</div>', unsafe_allow_html=True)


def pct_yes(s):
    return (s == "Yes").mean() * 100


def efek_hubungan(d):
    """Kekuatan hubungan tiap peubah dengan beli_lagi (0 sampai 1).
    Angka: eta (akar rasio ragam antar kelompok). Kategori: Cramer's V."""
    y = d["beli_lagi"]
    rows = []
    for col, nama in [("rating", "Rating"),
                      ("sub_rating_efektivitas", "Efektivitas"),
                      ("sub_rating_kemasan", "Kemasan"),
                      ("sub_rating_tekstur", "Tekstur"),
                      ("sub_rating_kualitas_harga", "Kualitas harga"),
                      ("harga_min", "Harga minimum"),
                      ("harga_max", "Harga maksimum")]:
        x = d[col].astype(float)
        gm = x.mean()
        ssb = sum(len(v) * (v.mean() - gm) ** 2 for _, v in x.groupby(y))
        sst = ((x - gm) ** 2).sum()
        rows.append((nama, float(np.sqrt(ssb / sst)) if sst else 0.0))
    for col, nama in [("rekomendasi", "Rekomendasi"),
                      ("lama_penggunaan", "Lama pemakaian")]:
        ct = pd.crosstab(d[col], y).values.astype(float)
        n = ct.sum()
        exp = ct.sum(1, keepdims=True) * ct.sum(0, keepdims=True) / n
        chi2 = ((ct - exp) ** 2 / exp).sum()
        rows.append((nama, float(np.sqrt(chi2 / (n * (min(ct.shape) - 1))))))
    return pd.DataFrame(rows, columns=["Peubah", "Kekuatan"]).sort_values(
        "Kekuatan")


def load_klas():
    km, cmx, fim = (load_csv("klasifikasi_metrics.csv"),
                    load_csv("confusion_matrix.csv"),
                    load_csv("feature_importance.csv"))
    if km is None or cmx is None:
        return None, None, None
    km["Kelas"] = km["Kelas"].map(lambda v: LAMA_ID.get(v, v))
    for k in ["Prediksi", "Aktual"]:
        cmx[k] = cmx[k].map(lambda v: LAMA_ID.get(v, v))
    return km, cmx, fim


def klas_summary(km, cmx):
    rows = []
    for nama in km["Analisis"].unique():
        c_ = cmx[cmx["Analisis"] == nama]
        tot = c_["Jumlah"].sum()
        akt = c_.groupby("Aktual")["Jumlah"].sum()
        acc = c_.loc[c_["Prediksi"] == c_["Aktual"], "Jumlah"].sum() / tot
        rows.append(dict(analisis=nama, acc=acc * 100, nir=akt.max() / tot * 100))
    return pd.DataFrame(rows)


# ---------------- Data ----------------
df_all = load_csv("data_bersih.csv")
if df_all is None:
    st.error("File `data/data_bersih.csv` belum ada.")
    st.stop()

# ================= HERO: judul, latar belakang, tujuan =================
st.markdown('<div class="title">Beli Lagi atau Beralih?</div>',
            unsafe_allow_html=True)
st.markdown(
    f'<div class="lead">Cocok di kulit mereka, <b>belum tentu cocok di kulit '
    f'kita</b>. Dari {idn(len(df_all))} ulasan skincare Sociolla, apa yang '
    f'membuat orang membeli lagi?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="chips"><span>Kenali reviewer dan produk</span>'
    '<span>Temukan faktor pembelian ulang</span>'
    '<span>Bangun model dan beri rekomendasi</span></div>',
    unsafe_allow_html=True)
st.markdown('<div class="meta" style="margin-top:8px">Kelompok 2 (K1) | '
            'Pengantar Sains Data</div>', unsafe_allow_html=True)

st.write("")
f1, f2, f3 = st.columns([1, 1, 1.4])
pilih_tipe = f1.multiselect("Tipe kulit", TIPE, placeholder="Semua")
pilih_brand = f2.multiselect("Brand", sorted(df_all["brand"].unique()),
                             placeholder="Semua")
f3.markdown('<div class="meta" style="padding-top:30px">Filter memengaruhi '
            'angka dan grafik eksplorasi serta peta FAMD.</div>',
            unsafe_allow_html=True)

df = df_all
if pilih_tipe:
    df = df[df[[f"tipe_{t}" for t in pilih_tipe]].sum(axis=1) > 0]
if pilih_brand:
    df = df[df["brand"].isin(pilih_brand)]
if len(df) == 0:
    st.warning("Tidak ada ulasan yang cocok dengan filter.")
    st.stop()

kc = st.columns(4)
kpi(kc[0], "Ulasan", idn(len(df)))
kpi(kc[1], "Berniat beli lagi", fmt(pct_yes(df["beli_lagi"])), "%")
kpi(kc[2], "Rating rata-rata", fmt(df["rating"].mean(), 2), "/5")
kpi(kc[3], "Merekomendasikan", fmt(pct_yes(df["rekomendasi"])), "%")

# ================= DATA + PREPROCESSING =================
heading("Datanya dari <b>web scraping Sociolla</b>, lalu dibersihkan")
st.markdown(
    f'<div class="flow"><span class="p">Scraping review Sociolla</span>'
    f'<span class="s">›</span><span class="p">11.401 ulasan mentah</span>'
    f'<span class="s">›</span><span class="p">Pembersihan</span>'
    f'<span class="s">›</span><span class="p on">{idn(len(df_all))} ulasan '
    f'bersih, 11 peubah</span></div>', unsafe_allow_html=True)
st.write("")
a, b = st.columns([2, 3])
with a:
    st.markdown(
        '<ul class="bullets">'
        '<li>Data hasil scraping dibersihkan dan diperiksa (tanpa nilai '
        'kosong pada peubah analisis)</li>'  # CEK: sesuaikan dgn cleaning asli
        '<li>Tipe kulit dan keluhan dipecah dari satu kolom</li>'
        '<li>Teks ulasan dirapikan untuk sentimen dan kata kunci</li>'
        '<li>Peubah dipilih lewat uji ANOVA dan Chi-square</li></ul>',
        unsafe_allow_html=True)
with b:
    ef = efek_hubungan(df_all)
    ef["Jenis"] = np.where(ef["Peubah"].isin(["Rekomendasi", "Lama pemakaian"]),
                           "Kategori (Cramér's V)", "Angka (eta)")
    fig = px.bar(ef, x="Kekuatan", y="Peubah", orientation="h", color="Jenis",
                 color_discrete_sequence=[PINK, PURPLE])
    fig.update_xaxes(title="Kekuatan hubungan dengan beli lagi (0 sampai 1)",
                     range=[0, max(0.5, ef["Kekuatan"].max() * 1.1)])
    fig.update_yaxes(title=None)
    show(fig, 300)
with st.expander("Lihat contoh data dan kamus variabel"):
    kolom = ["brand", "nama_produk", "harga_min", "harga_max", "tipe_kulit",
             "rating", "rekomendasi", "lama_penggunaan", "beli_lagi"]
    table(df_all[kolom].head(50))
    st.caption("Target: beli_lagi (Yes, Maybe, No). Peubah lain: harga, tipe "
               "kulit, rating dan 4 sub-rating, rekomendasi, lama pemakaian.")

# ================= EDA =================
top_kel = None
heading("Siapa reviewernya dan <b>apa yang mereka rasakan</b>?")
c1, c2, c3 = st.columns(3)
with c1:
    card_head("Keluhan kulit", "Persen ulasan yang menyebutnya")
    kel = pd.DataFrame({
        "Keluhan": KELUHAN,
        "Persen": [df["keluhan_" + k.replace(" ", "_")].mean() * 100
                   for k in KELUHAN]}).sort_values("Persen")
    fig = px.bar(kel, x="Persen", y="Keluhan", orientation="h",
                 text=kel["Persen"].map(lambda v: f"{v:.0f}%"),
                 color_discrete_sequence=[PINK])
    fig.update_xaxes(visible=False, range=[0, kel["Persen"].max() * 1.25])
    fig.update_yaxes(title=None)
    fig.update_traces(textposition="outside", cliponaxis=False)
    show(fig, 270, legend=False)
with c2:
    card_head("Tipe kulit", "Satu reviewer bisa menyebut lebih dari satu")
    tk = pd.DataFrame({"Tipe": TIPE,
                       "Jumlah": [int(df[f"tipe_{t}"].sum()) for t in TIPE]})
    fig = px.pie(tk, names="Tipe", values="Jumlah", hole=0.6,
                 color_discrete_sequence=[PINK, PURPLE, "#F9A8D4", "#C4B5FD",
                                          TEAL])
    fig.update_traces(textinfo="percent")
    show(fig, 270)
with c3:
    card_head("Sentimen ulasan", "Lexicon sederhana")
    if "label_sentimen" in df.columns:
        sm = (df["label_sentimen"].value_counts(normalize=True) * 100
              ).reindex(["Positif", "Netral", "Negatif"]).fillna(0).reset_index()
        sm.columns = ["Sentimen", "Persen"]
        fig = px.bar(sm, x="Sentimen", y="Persen",
                     text=sm["Persen"].map(lambda v: f"{v:.0f}%"),
                     color="Sentimen",
                     color_discrete_map={"Positif": GREEN, "Netral": AMBER,
                                         "Negatif": RED})
        fig.update_yaxes(visible=False)
        fig.update_xaxes(title=None)
        fig.update_traces(textposition="outside", cliponaxis=False)
        show(fig, 270, legend=False)

d1, d2 = st.columns(2)
with d1:
    card_head("Rekomendasi dan niat beli ulang",
              "Persen niat beli lagi pada tiap kelompok")
    ct = (pd.crosstab(df["rekomendasi"], df["beli_lagi"], normalize="index")
          * 100).round(1)
    bl = ct.reset_index().melt(id_vars="rekomendasi", var_name="Beli lagi",
                               value_name="Persen")
    fig = px.bar(bl, x="rekomendasi", y="Persen", color="Beli lagi",
                 text=bl["Persen"].map(lambda v: f"{v:.0f}%" if v >= 4 else ""),
                 category_orders={"Beli lagi": ["No", "Maybe", "Yes"]},
                 color_discrete_map=BELI_COLORS)
    fig.update_xaxes(title="Merekomendasikan produk?")
    fig.update_yaxes(visible=False)
    show(fig, 280)
with d2:
    card_head("Lama pemakaian", "Persen yang berniat beli lagi (Yes)")
    urut = [x for x in LAMA_ORDER if x in set(df["lama_penggunaan"])]
    ll = (df.groupby("lama_penggunaan")["beli_lagi"].apply(pct_yes)
          .reindex(urut).reset_index())
    ll.columns = ["Lama", "Persen"]
    fig = px.bar(ll, x="Lama", y="Persen",
                 text=ll["Persen"].map(lambda v: f"{v:.0f}%"),
                 color_discrete_sequence=[PURPLE])
    fig.update_yaxes(visible=False, range=[0, 110])
    fig.update_xaxes(title=None)
    fig.update_traces(textposition="outside", cliponaxis=False)
    show(fig, 280, legend=False)

with st.expander("Eksplor lebih jauh: brand dan kata yang sering muncul"):
    e1, e2 = st.columns(2)
    with e1:
        br = df["brand"].value_counts().head(10).reset_index()
        br.columns = ["Brand", "Ulasan"]
        fig = px.bar(br.iloc[::-1], x="Ulasan", y="Brand", orientation="h",
                     color_discrete_sequence=[PURPLE])
        fig.update_yaxes(title=None)
        show(fig, 330, legend=False)
        st.caption("10 brand dengan ulasan terbanyak.")
    with e2:
        wc = os.path.join(DATA_DIR, "wordcloud.png")
        if os.path.exists(wc):
            st.image(wc)
            st.caption("Kata yang sering muncul di ulasan.")

# ================= MODELING (4 kartu ringkas) =================
heading("Empat metode, <b>satu pertanyaan</b>: apa yang menentukan beli ulang?",
        "Hasil dihitung dari seluruh data. Buka 'Detail' untuk grafik lengkap.")
km, cmx, fim = load_klas()
ev = load_csv("famd_eigen.csv")
kp = load_csv("famd_peubah.csv")
rules = load_csv("rules.csv")
cl = load_csv("cluster.csv")
if cl is not None:
    cl["cluster"] = "Klaster " + cl["cluster"].astype(str)

m1, m2 = st.columns(2)

# --- Klasifikasi ---
with m1:
    with st.container(border=True):
        card_head("Klasifikasi", "Menebak niat beli ulang dari data ulasan")
        if km is not None:
            ks = klas_summary(km, cmx)
            ks["Analisis"] = ks["analisis"].map(SHORT)
            lg = ks.melt(id_vars="Analisis", value_vars=["acc", "nir"],
                         var_name="Ukuran", value_name="Persen")
            lg["Ukuran"] = lg["Ukuran"].map({"acc": "Akurasi model",
                                             "nir": "Tebakan mayoritas"})
            fig = px.bar(lg, x="Analisis", y="Persen", color="Ukuran",
                         barmode="group",
                         color_discrete_sequence=[PINK, "#4B4F7A"])
            fig.update_yaxes(title=None, range=[0, 105])
            fig.update_xaxes(title=None)
            show(fig, 250)
            r4 = ks[ks["analisis"] == "Niat Pembelian Ulang"]
            if len(r4):
                r4 = r4.iloc[0]
                result(f"Niat beli ulang: akurasi <b>{fmt(r4['acc'])}%</b> "
                       f"hanya sedikit di atas tebakan mayoritas "
                       f"({fmt(r4['nir'])}%).")
            with st.expander("Detail"):
                k4 = cmx[cmx["Analisis"] == "Niat Pembelian Ulang"]
                pv = k4.pivot_table(index="Aktual", columns="Prediksi",
                                    values="Jumlah", aggfunc="sum",
                                    fill_value=0)
                kls = [x for x in ["No", "Maybe", "Yes"] if x in pv.index]
                pv = pv.reindex(index=kls, columns=kls, fill_value=0)
                norm = pv.div(pv.sum(axis=1).replace(0, 1), axis=0)
                fig = go.Figure(go.Heatmap(
                    z=norm.values, x=list(pv.columns), y=list(pv.index),
                    text=pv.values, texttemplate="%{text}",
                    colorscale="RdPu", showscale=False))
                fig.update_yaxes(autorange="reversed", title="Aktual")
                fig.update_xaxes(title="Prediksi")
                show(fig, 240, legend=False)
                st.caption("Niat beli ulang (Random Forest). Kelas No dan "
                           "Maybe jarang terdeteksi karena datanya jauh lebih "
                           "sedikit dari Yes.")
                if fim is not None:
                    f4 = fim[fim["Analisis"] == "Niat Pembelian Ulang"].copy()
                    f4["Variabel"] = f4["Variabel"].str.replace("_", " ")
                    fig = px.bar(f4.sort_values("Importance"), x="Importance",
                                 y="Variabel", orientation="h",
                                 color_discrete_sequence=[PINK])
                    fig.update_yaxes(title=None)
                    show(fig, 280, legend=False)
                    st.caption("Peubah terpenting.")

# --- FAMD ---
with m2:
    with st.container(border=True):
        card_head("FAMD", "Peta kemiripan ulasan dari peubah angka dan kategori")
        if "Dim1" in df.columns:
            pts = df if len(df) <= 2500 else df.sample(2500, random_state=1)
            fig = px.scatter(pts, x="Dim1_jitter", y="Dim2_jitter",
                             color="beli_lagi", opacity=0.45,
                             color_discrete_map=BELI_COLORS,
                             category_orders={"beli_lagi": ["No", "Maybe",
                                                            "Yes"]})
            fig.update_xaxes(title="Dim1: kepuasan")
            fig.update_yaxes(title="Dim2: niat beli ulang")
            show(fig, 250)
            if ev is not None:
                result(f"Dim1 (kepuasan) menjelaskan "
                       f"<b>{fmt(ev['persen_ragam'][0])}%</b> ragam. Dim2 "
                       f"dibentuk oleh niat beli ulang.")
            with st.expander("Detail"):
                if ev is not None:
                    fig = px.bar(ev, x=ev["dimensi"].astype(str),
                                 y="persen_ragam",
                                 color_discrete_sequence=[PURPLE])
                    fig.add_scatter(x=ev["dimensi"].astype(str),
                                    y=ev["persen_ragam_kumulatif"],
                                    mode="lines+markers", name="kumulatif",
                                    line_color=AMBER)
                    fig.update_xaxes(title="Dimensi")
                    fig.update_yaxes(title="% ragam")
                    show(fig, 220)
                if kp is not None:
                    dsel = st.radio("Kontribusi peubah pada dimensi",
                                    [1, 2, 3], horizontal=True, key="kpd")
                    k2 = kp[(kp["dimensi"] == dsel) & (kp["peran"] == "Aktif")]
                    fig = px.bar(k2.sort_values("kontribusi_persen"),
                                 x="kontribusi_persen", y="peubah",
                                 orientation="h",
                                 color_discrete_sequence=[PINK])
                    fig.update_xaxes(title="Kontribusi (%)")
                    fig.update_yaxes(title=None)
                    show(fig, 260, legend=False)
                    st.caption("Beli_lagi dan rekomendasi ikut sebagai "
                               "peubah aktif, jadi dimensi sebagian "
                               "mencerminkan niat beli ulang itu sendiri.")

m3, m4 = st.columns(2)

# --- Association ---
with m3:
    with st.container(border=True):
        card_head("Association rules",
                  "Kata yang sering muncul bersamaan dalam ulasan")
        if rules is not None and "lhs_label" in rules.columns:
            ra = rules[rules["analisis"] == "A_kata_bersamaan"].sort_values(
                "lift", ascending=False)
            t = ra.head(8).copy()
            t["Aturan"] = t["lhs_label"] + " + " + t["rhs_label"]
            fig = px.bar(t.iloc[::-1], x="lift", y="Aturan", orientation="h",
                         color_discrete_sequence=[PURPLE])
            fig.update_xaxes(title="Lift (makin tinggi makin sering bersama)")
            fig.update_yaxes(title=None)
            show(fig, 250, legend=False)
            t0 = ra.iloc[0]
            result(f"Paling kuat: <b>{t0['lhs_label']}</b> dan "
                   f"<b>{t0['rhs_label']}</b> (lift {fmt(t0['lift'])}).")
            with st.expander("Detail"):
                AN = {"A_kata_bersamaan": "Kata bersamaan",
                      "B_profil_kulit_kata": "Profil kulit ke kata",
                      "C_pemicu_ketidakpuasan": "Pemicu ketidakpuasan",
                      "D_tier_harga": "Tier harga ke kata"}
                pilih = st.radio("Analisis", list(AN),
                                 format_func=AN.get, key="an")
                r = rules[rules["analisis"] == pilih].sort_values(
                    "lift", ascending=False)
                table(r[["lhs_label", "rhs_label", "support", "confidence",
                         "lift"]].round(3).head(15))
                st.caption("Support kecil, jadi baca sebagai pola "
                           "eksploratif.")

# --- Clustering ---
with m4:
    with st.container(border=True):
        card_head("Clustering", "Mengelompokkan produk yang mirip (K-Means)")
        if cl is not None:
            fig = px.scatter(cl, x="rating_rata", y="beli_lagi_rate",
                             color="cluster", opacity=0.8,
                             hover_name="nama_produk",
                             hover_data=["brand", "n_review"],
                             color_discrete_sequence=[PINK, TEAL])
            fig.update_xaxes(title="Rating rata-rata produk")
            fig.update_yaxes(title="Proporsi beli lagi")
            show(fig, 250)
            g = cl.groupby("cluster").agg(n=("nama_produk", "size"),
                                          bl=("beli_lagi_rate", "mean"))
            if len(g) == 2:
                hi, lo = g["bl"].idxmax(), g["bl"].idxmin()
                result(f"2 kelompok produk: beli ulang "
                       f"<b>{fmt(g.loc[hi, 'bl'] * 100)}%</b> ({hi}) vs "
                       f"<b>{fmt(g.loc[lo, 'bl'] * 100)}%</b> ({lo}). "
                       "Pembedanya kepuasan, bukan harga.")
            with st.expander("Detail"):
                prof = cl.groupby("cluster").agg(
                    Produk=("nama_produk", "size"),
                    Harga=("harga_tengah", "mean"),
                    Rating=("rating_rata", "mean"),
                    Beli_lagi=("beli_lagi_rate", lambda s: s.mean() * 100),
                ).round(2).reset_index()
                prof["Harga"] = prof["Harga"].round(0).astype(int)
                table(prof)
                sil = load_csv("cluster_silhouette.csv")
                if sil is not None:
                    fig = px.bar(sil, x=sil["k"].astype(str), y="silhouette",
                                 text=sil["silhouette"].map(
                                     lambda v: f"{v:.3f}"),
                                 color_discrete_sequence=[PURPLE])
                    fig.update_xaxes(title="Jumlah klaster (k)")
                    fig.update_yaxes(visible=False)
                    show(fig, 200, legend=False)
                    st.caption("Silhouette k=2 sebesar 0,232: pemisahan "
                               "lemah, jadi ini segmentasi eksploratif.")

# ================= KEY INSIGHTS =================
heading("Tiga temuan utama")
rec_y = pct_yes(df_all.loc[df_all["rekomendasi"] == "Yes", "beli_lagi"])
rec_n = pct_yes(df_all.loc[df_all["rekomendasi"] == "No", "beli_lagi"])
lama_y = pct_yes(df_all.loc[df_all["lama_penggunaan"] == "> 1 tahun",
                            "beli_lagi"])
harga_eta = ef.loc[ef["Peubah"].str.startswith("Harga"), "Kekuatan"].max()
i1, i2, i3 = st.columns(3)
for col, big, desc in [
    (i1, f"{fmt(rec_y, 0)}% vs {fmt(rec_n, 0)}%",
     "berniat beli lagi pada yang merekomendasikan vs yang tidak. "
     "Rekomendasi adalah penanda loyalitas."),
    (i2, f"{fmt(lama_y, 0)}%",
     "pengguna lebih dari 1 tahun berniat beli lagi, tertinggi dari semua "
     "kelompok lama pemakaian."),
    (i3, f"η = {fmt(harga_eta, 2)}",
     "hubungan harga dengan niat beli ulang (skala 0 sampai 1). Harga "
     "hampir tidak berperan, kepuasan jauh lebih."),
]:
    with col:
        with st.container(border=True):
            st.markdown(f'<div style="min-height:150px"><div class="big">'
                        f'{big}</div><div class="bigd">{desc}</div></div>',
                        unsafe_allow_html=True)

# ================= KESIMPULAN + REKOMENDASI =================
heading("Kesimpulan dan rekomendasi")
k1, k2 = st.columns(2)
with k1:
    with st.container(border=True):
        card_head("Kesimpulan", "Menjawab tujuan proyek")
        acc4 = ""
        if km is not None:
            r4 = klas_summary(km, cmx)
            r4 = r4[r4["analisis"] == "Niat Pembelian Ulang"]
            if len(r4):
                acc4 = (f" Model klasifikasi hanya sedikit di atas tebakan "
                        f"mayoritas ({fmt(r4.iloc[0]['acc'])}% vs "
                        f"{fmt(r4.iloc[0]['nir'])}%).")
        st.markdown(
            '<ul class="bullets">'
            '<li>Faktor pembelian ulang: <b>rekomendasi, rating, dan lama '
            'pemakaian</b>. Harga tidak.</li>'
            f'<li>Produk terbagi dua kelompok menurut kepuasan.{acc4}</li>'
            '<li>Pola kata di ulasan membantu membaca keluhan, tapi '
            'kekuatannya terbatas.</li></ul>', unsafe_allow_html=True)
with k2:
    with st.container(border=True):
        card_head("Rekomendasi", "Untuk brand dan platform")
        st.markdown(
            '<ul class="bullets">'
            '<li><b>Brand:</b> dorong pelanggan memberi ulasan dan '
            'rekomendasi.</li>'
            '<li><b>Brand:</b> tinjau produk di kelompok dengan beli ulang '
            'lebih rendah.</li>'
            '<li><b>Sociolla:</b> tampilkan ulasan sesuai tipe kulit '
            'pembaca dan pantau keluhan lewat kata kunci.</li></ul>',
            unsafe_allow_html=True)

with st.expander("Batasan analisis"):
    baru = (df_all["lama_penggunaan"] == "< 1 minggu").mean() * 100
    st.markdown(
        f"- {fmt(baru, 0)}% ulasan dari pemakai kurang dari 1 minggu, dan "
        f"rating menumpuk di 4 sampai 5 (rata-rata "
        f"{fmt(df_all['rating'].mean(), 2)}).\n"
        "- Niat beli ulang tidak seimbang (Yes sekitar 85%), dan model "
        "klasifikasi belum menanganinya.\n"
        "- FAMD memakai beli_lagi sebagai peubah aktif.\n"
        "- Silhouette clustering 0,232 (lemah) dan support association "
        "rules kecil.\n"
        "- Sentimen memakai lexicon sederhana, dan data hanya dari satu "
        "platform.")

# ================= COBA SENDIRI =================
heading("Coba sendiri: cari produk")
pb = st.selectbox("Brand", sorted(df_all["brand"].unique()), key="pe",
                  label_visibility="collapsed")
d = df_all[df_all["brand"] == pb]
prod = (d.groupby("nama_produk").agg(
    Ulasan=("rating", "size"), Rating=("rating", "mean"),
    Beli_lagi=("beli_lagi", pct_yes)).reset_index()
    .sort_values("Ulasan", ascending=False))
prod["Rating"] = prod["Rating"].round(2)
prod["Beli_lagi"] = prod["Beli_lagi"].round(1)
try:
    table(prod, column_config={
        "Beli_lagi": st.column_config.ProgressColumn(
            "Beli lagi (%)", min_value=0, max_value=100, format="%.0f%%")})
except Exception:
    table(prod)

st.markdown('<div class="meta" style="margin:28px 0 8px 0">Sumber data: '
            'ulasan produk skincare di sociolla.com (web scraping).</div>',
            unsafe_allow_html=True)
