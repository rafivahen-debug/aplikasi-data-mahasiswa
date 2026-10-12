# Aplikasi Pengelolaan Data Mahasiswa

Aplikasi CRUD sederhana menggunakan Python, Flask, SQLite, HTML, dan CSS.

## Fitur
- Menambah, melihat daftar/detail, mengubah, dan menghapus data mahasiswa.
- Validasi NIM unik, kolom wajib, angkatan berupa bilangan bulat, dan IPK 0.00–4.00.
- Lama studi dihitung otomatis: tahun sekarang dikurangi angkatan.
- Data disimpan di database SQLite (`mahasiswa.db`) sehingga tetap ada setelah aplikasi dihentikan.
- Pesan sukses dan kesalahan ditampilkan di halaman.

## Persyaratan
- Python 3.10 atau lebih baru
- pip

## Menjalankan aplikasi di Windows (VS Code)
1. Ekstrak folder proyek lalu buka folder `aplikasi_data_mahasiswa` di VS Code.
2. Buka Terminal → New Terminal.
3. Buat virtual environment (disarankan):
   ```bash
   py -m venv .venv
   ```
4. Aktifkan virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
   Jika perintah `py` tidak tersedia, coba `python`.
5. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```
6. Jalankan aplikasi:
   ```bash
   python app.py
   ```
7. Buka alamat `http://127.0.0.1:5000` di browser.

Tabel database dibuat otomatis saat `app.py` dijalankan pertama kali. Jangan menghapus `mahasiswa.db` jika ingin mempertahankan data.

## Struktur folder
```text
aplikasi_data_mahasiswa/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── mahasiswa.db       # dibuat otomatis saat aplikasi berjalan
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── form.html
│   ├── detail.html
│   └── 404.html
└── static/
    └── style.css
```

## Rute aplikasi
- `GET /` — daftar mahasiswa
- `GET /mahasiswa/tambah` — formulir tambah
- `POST /mahasiswa/tambah` — memvalidasi dan menyimpan data
- `GET /mahasiswa/<nim>` — detail mahasiswa
- `GET /mahasiswa/<nim>/edit` — formulir edit
- `POST /mahasiswa/<nim>/edit` — memvalidasi dan memperbarui data
- `POST /mahasiswa/<nim>/hapus` — menghapus data

## Pengujian sebelum direkam
1. Tambahkan satu mahasiswa dengan data valid.
2. Pastikan data muncul pada tabel dan halaman detail.
3. Coba menambahkan NIM yang sama; sistem seharusnya menolak.
4. Coba IPK `4.5`; sistem seharusnya menolak.
5. Coba mengosongkan nama atau program studi; sistem seharusnya menolak.
6. Edit data mahasiswa dan pastikan perubahan tersimpan.
7. Hapus data uji.
8. Tambahkan data lalu hentikan dan jalankan ulang aplikasi; pastikan data masih ada.

## GitHub: target minimal 4 commit
Lakukan commit secara bertahap saat mengerjakan, bukan hanya membuat empat commit kosong. Contoh:
1. `buat struktur awal aplikasi Flask`
2. `tambah database SQLite dan validasi data`
3. `tambah fitur CRUD mahasiswa`
4. `rapikan tampilan HTML dan CSS`
5. `tambah panduan penggunaan dan pengujian`

Buat repository GitHub, lalu hubungkan repository lokal dan push. Jangan mengunggah virtual environment atau file database berisi data pribadi.
