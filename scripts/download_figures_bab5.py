#!/usr/bin/env python3
"""
Script untuk mendownload gambar eksternal (opsional) untuk Bab 5 Buku Ajar Logika Matematika.
Bab 5 saat ini menggunakan diagram TikZ; script ini berguna jika ingin menambah gambar
dari sumber eksternal (mis. diagram FOL dari Wikipedia/CC). Sumber dan lisensi harus
disebutkan di caption dan references.bib.

Menjalankan: python scripts/download_figures_bab5.py
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "buku_ajar_logika_matematika", "figures")
FIGURES_BAB05 = os.path.join(FIGURES_DIR, "bab-05")
os.makedirs(FIGURES_BAB05, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


def download_from_url(url: str, filename: str, subdir: str = "bab-05") -> bool:
    """Download gambar dari URL ke folder figures/subdir. Default: figures/bab-05/."""
    try:
        import urllib.request
        out_dir = os.path.join(FIGURES_DIR, subdir) if subdir else FIGURES_DIR
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, filename)
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded: {filename} -> {filepath}")
        return True
    except Exception as e:
        print(f"Download failed for {url}: {e}")
        return False


def main():
    print("=== Download Figures for Bab 5 (Logika Predikat) ===\n")
    print(f"Output directory: {FIGURES_DIR}\n")
    print("Bab 5 menggunakan diagram TikZ di LaTeX. Untuk menambah gambar eksternal,")
    print("edit daftar urls di script ini, lalu jalankan lagi. Sertakan sumber di caption dan references.bib.\n")

    # Contoh: URL gambar eksternal (opsional). Uncomment dan isi URL + nama file jika perlu.
    # urls = [
    #     ("https://example.com/predicate-logic-diagram.png", "predicate-logic-schema.png"),
    # ]
    # for url, filename in urls:
    #     download_from_url(url, filename)

    print("Done. (Tidak ada URL yang didownload; uncomment blok urls di script jika perlu.)")


if __name__ == "__main__":
    main()
