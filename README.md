# Dashboard Beli Lagi atau Beralih? (Kelompok 2 K1)

## Jalankan
```
pip install -r requirements.txt
streamlit run app.py
```

## Folder data/
Taruh file hasil tiap anggota di folder `data/`. App otomatis membacanya.

| File | Dari | Kolom |
|---|---|---|
| data_bersih.csv | Dashboard | semua variabel |
| wordcloud.png | Darell | gambar |
| seleksi_peubah.csv | Dashboard | peubah, uji, pvalue |
| klasifikasi_metrics.csv | Abit | model, akurasi, f1 |
| confusion_matrix.png | Abit | gambar |
| feature_importance.csv | Abit | peubah, importance |
| famd_coords.csv | Jua | Dim1, Dim2, beli_lagi |
| famd_eigen.csv | Jua | dimensi, eigenvalue |
| rules.csv | Restu | antecedents, consequents, support, confidence, lift |
| cluster.csv | El | Dim1, Dim2, cluster |
| cluster_profile.csv | El | cluster, ringkasan tiap variabel |

## Pembagian halaman
- Dapu: halaman 1 dan 2
- Bob: halaman 3 dan 4
- Darell: halaman 6, 7, integrasi halaman 5
