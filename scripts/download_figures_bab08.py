#!/usr/bin/env python3
"""
Script untuk mendownload gambar eksternal (opsional) untuk Bab 8 Buku Ajar Logika Matematika.
Bab 8 (Prolog) menggunakan diagram TikZ di LaTeX; script ini berguna jika ingin menambah
gambar dari sumber eksternal (mis. logo SWI-Prolog). Sumber dan lisensi harus disebutkan
di caption dan references.bib (sitasi swi_prolog).

Sumber: SWI-Prolog (https://swi-prolog.org/) - logo/ikon untuk keperluan pendidikan.
Menjalankan: python scripts/download_figures_bab08.py
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "buku_ajar_logika_matematika", "figures")
FIGURES_BAB08 = os.path.join(FIGURES_DIR, "bab-08")
os.makedirs(FIGURES_BAB08, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


def download_from_url(url: str, filename: str, subdir: str = "bab-08") -> bool:
    """Download gambar dari URL ke folder figures/subdir. Default: figures/bab-08/."""
    try:
        import urllib.request
        out_dir = os.path.join(FIGURES_DIR, subdir) if subdir else FIGURES_DIR
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, filename)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Buku Ajar Logika Matematika)"})
        with urllib.request.urlopen(req) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        print(f"Downloaded: {filename} -> {filepath}")
        return True
    except Exception as e:
        print(f"Download failed for {url}: {e}")
        return False


def main():
    print("=== Download Figures for Bab 8 (Prolog) ===\n")
    print(f"Output directory: {FIGURES_DIR}\n")

    # URL gambar eksternal (opsional). SWI-Prolog logo dari situs resmi.
    # Jika URL berubah atau tidak tersedia, script tetap membuat folder figures/bab-08.
    urls = [
        ("https://www.swi-prolog.org/icons/swi-prolog-icon.svg", "swi-prolog-icon.svg"),
    ]
    success = 0
    for url, filename in urls:
        if download_from_url(url, filename):
            success += 1

    if success == 0:
        print("Tidak ada file yang berhasil didownload. Folder figures/bab-08 sudah dibuat.")
        print("Untuk memasukkan logo di LaTeX, gunakan \\includegraphics dengan file dari figures/bab-08/.")
    print("\nDone.")


if __name__ == "__main__":
    main()
