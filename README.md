# Kuliah Logika Matematika

Repositori ini berisi seluruh materi pengajaran, dokumen pendukung, dan kode sumber untuk mata kuliah **Logika Matematika**. Seluruh dokumen utama ditulis menggunakan LaTeX dan disusun dengan pendekatan *Outcome-Based Education* (OBE).

## 📂 Struktur Repositori

Repositori ini terbagi menjadi beberapa direktori utama:

- **`buku_ajar/`**: Berisi *source code* LaTeX untuk Buku Ajar Logika Matematika. Terdiri dari 15 bab (dari pengantar proposisi hingga pembuktian dan aplikasi logika), *frontmatter*, lampiran, dan daftar pustaka. Terdapat *batch script* (`compile_main.bat`, `compile_bab.bat`) untuk mempermudah kompilasi buku menjadi PDF.
- **`kontrak_kuliah/`**: Berisi dokumen kesepakatan studi (*Kontrak Kuliah*) antara dosen dan mahasiswa dalam format LaTeX beserta skrip kompilasinya.
- **`silabus/`**: Berisi dokumen Silabus mata kuliah berdasarkan standar OBE dalam format LaTeX beserta skrip kompilasinya.
- **`ppt/`**: Berisi bahan tayang atau presentasi (*slides*) untuk materi perkuliahan, seperti Logika Proposisi dan Logika Predikat (format LaTeX/Beamer).
- **`docs/`**: Berisi dokumentasi panduan penyusunan materi, format struktur bab OBE, daftar Capaian Pembelajaran (CPL & CPMK), sumber referensi terbuka, dan *prompt* untuk pengembangan materi secara otomatis.
- **`scripts/`**: Kumpulan skrip Python dan Batch. Skrip Python (`download_figures_*.py`, `generate_figures_*.py`, dll) digunakan untuk mengunduh atau menghasilkan gambar/grafik (menggunakan matplotlib) yang disisipkan ke dalam buku ajar. Terdapat juga skrip untuk membersihkan *file temp* hasil kompilasi LaTeX (`clean_all.bat`).

## 🎯 Capaian Pembelajaran

Mata kuliah ini dirancang untuk mencapai *Course Learning Outcomes* (CPMK) berikut:
1. **CPMK 1**: Menganalisis argumen dan komputasi dasar dengan logika proposisional.
2. **CPMK 2**: Memodelkan persoalan menggunakan logika predikat (kuantor universal dan eksistensial).
3. **CPMK 3**: Menerapkan Aljabar Boolean dan menyederhanakan fungsi ke gerbang logika.
4. **CPMK 4**: Merancang argumen matematis dan membuktikan kebenaran algoritma menggunakan teknik pembuktian formal (deduksi, induksi, dll).

## 🛠️ Prasyarat (*Prerequisites*)

Untuk menyusun atau mengubah dokumen di repositori ini, pastikan sistem Anda telah terpasang:
- **Distribusi LaTeX** (seperti TeX Live, MiKTeX, atau MacTeX) untuk melakukan kompilasi file `.tex` menjadi `.pdf`. Disarankan yang mendukung `pdflatex` dan `biber` (untuk manajemen daftar pustaka).
- **Python 3.x** untuk menjalankan skrip pembuatan grafik/gambar.
- Ketergantungan Python: Anda bisa menginstal *library* yang dibutuhkan dengan perintah:
  ```bash
  pip install -r requirements.txt
  ```

## 🚀 Cara Penggunaan

1. **Mengompilasi Dokumen LaTeX**: 
   Anda dapat masuk ke masing-masing direktori (`buku_ajar`, `kontrak_kuliah`, atau `silabus`) dan menjalankan *batch file* yang tersedia (misal: `compile_main.bat`).
2. **Men-generate Gambar Buku**:
   Buka terminal/command prompt, arahkan ke direktori `scripts/`, lalu jalankan skrip Python yang sesuai, misalnya:
   ```bash
   python generate_figures_bab3.py
   ```
3. **Membersihkan File Temporary**:
   Setelah kompilasi, Anda dapat menggunakan `clean_all.bat` pada folder `scripts/` atau batch terkait jika tersedia untuk menghapus file sisa seperti `.aux`, `.log`, `.out`, `.toc`, dll.

---
*Proyek ini dirancang sebagai panduan lengkap, interaktif, dan terstruktur untuk mendukung pembelajaran komputasi logis berbasis luaran (OBE).*
