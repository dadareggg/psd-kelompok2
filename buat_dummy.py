"""Buat data DUMMY di folder data/ supaya dashboard bisa dites.
Hapus file dummy dan ganti dengan hasil asli begitu modeler selesai.
Jalankan: python buat_dummy.py
"""
import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
os.makedirs("data", exist_ok=True)
n = 500

# data_bersih.csv
df = pd.DataFrame(
    {
        "harga_min": rng.integers(30000, 150000, n),
        "harga_max": rng.integers(150000, 400000, n),
        "tipe_kulit": rng.choice(
            ["Kombinasi", "Berminyak", "Sensitif", "Kering", "Normal"], n),
        "rating": rng.integers(1, 6, n),
        "efektivitas": rng.integers(1, 6, n),
        "kemasan": rng.integers(1, 6, n),
        "tekstur": rng.integers(1, 6, n),
        "kualitas_harga": rng.integers(1, 6, n),
        "rekomendasi": rng.choice(["Yes", "No"], n, p=[0.85, 0.15]),
        "lama_penggunaan": rng.choice(
            ["<1 minggu", "1-4 minggu", "1-3 bulan", ">3 bulan"], n),
    }
)
df["beli_lagi"] = np.where(
    df["rekomendasi"] == "Yes",
    rng.choice(["Yes", "Maybe", "No"], n, p=[0.88, 0.10, 0.02]),
    rng.choice(["Yes", "Maybe", "No"], n, p=[0.03, 0.37, 0.60]),
)
df.to_csv("data/data_bersih.csv", index=False)

# seleksi_peubah.csv
pd.DataFrame(
    {
        "peubah": ["sub rating tekstur", "sub rating kualitas harga",
                   "sub rating efektivitas", "rating", "sub rating kemasan",
                   "rekomendasi", "lama penggunaan"],
        "uji": ["ANOVA"] * 5 + ["Chi-square"] * 2,
        "pvalue": [1e-90, 1e-80, 1e-70, 1e-60, 0.03, 1e-140, 1e-14],
    }
).to_csv("data/seleksi_peubah.csv", index=False)

# klasifikasi
pd.DataFrame(
    {
        "model": ["Logistic Regression", "Random Forest", "XGBoost"],
        "akurasi": [0.86, 0.91, 0.92],
        "f1": [0.84, 0.90, 0.91],
    }
).to_csv("data/klasifikasi_metrics.csv", index=False)
pd.DataFrame(
    {
        "peubah": ["rekomendasi", "lama_penggunaan", "rating", "efektivitas",
                   "tekstur", "kualitas_harga", "kemasan"],
        "importance": [0.38, 0.17, 0.14, 0.11, 0.08, 0.07, 0.05],
    }
).to_csv("data/feature_importance.csv", index=False)

# famd
famd = pd.DataFrame(
    {"Dim1": rng.normal(0, 1, n), "Dim2": rng.normal(0, 1, n),
     "beli_lagi": df["beli_lagi"]}
)
famd.to_csv("data/famd_coords.csv", index=False)
pd.DataFrame(
    {"dimensi": [f"Dim{i}" for i in range(1, 7)],
     "persen_varians": [24, 16, 12, 10, 8, 6]}
).to_csv("data/famd_eigen.csv", index=False)

# rules
pd.DataFrame(
    {
        "antecedents": ["rekomendasi=Yes", "tipe=Kombinasi", "rating=5",
                        "rekomendasi=Yes, rating=5"],
        "consequents": ["beli_lagi=Yes", "keluhan=Berjerawat",
                        "beli_lagi=Yes", "beli_lagi=Yes"],
        "support": [0.45, 0.22, 0.30, 0.28],
        "confidence": [0.88, 0.70, 0.90, 0.95],
        "lift": [1.4, 1.1, 1.5, 1.6],
    }
).to_csv("data/rules.csv", index=False)

# cluster
clus = pd.DataFrame(
    {"Dim1": rng.normal(0, 1, n), "Dim2": rng.normal(0, 1, n),
     "cluster": rng.integers(1, 4, n)}
)
clus.loc[clus.cluster == 1, "Dim1"] += 2
clus.loc[clus.cluster == 2, "Dim2"] += 2
clus.to_csv("data/cluster.csv", index=False)
pd.DataFrame(
    {
        "cluster": [1, 2, 3],
        "ukuran": [180, 150, 170],
        "ciri": ["Puas dan loyal", "Sensitif harga", "Ragu beli ulang"],
    }
).to_csv("data/cluster_profile.csv", index=False)

print("Dummy data selesai di folder data/")
