#!/usr/bin/env python3
"""
Generate gambar untuk Bab 3 Buku Ajar Logika Matematika.
Grafik: banyak baris tabel kebenaran 2^n vs n variabel.
Menjalankan: python scripts/generate_figures_bab3.py
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "buku_ajar_logika_matematika", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def generate_baris_tabel_kebenaran():
    """Grafik 2^n (banyak baris tabel kebenaran) vs n (banyak variabel)."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        n = np.arange(1, 11)
        rows = 2**n

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(n, rows, "o-", color="steelblue", linewidth=2, markersize=8)
        ax.set_xlabel("Banyak variabel proposisional ($n$)", fontsize=11)
        ax.set_ylabel("Banyak baris ($2^n$)", fontsize=11)
        ax.set_title("Pertumbuhan baris tabel kebenaran: $2^n$ untuk $n$ variabel", fontsize=12)
        ax.set_xticks(n)
        ax.grid(True, linestyle="--", alpha=0.7)
        for i, (ni, r) in enumerate(zip(n, rows)):
            ax.annotate(str(int(r)), (ni, r), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
        plt.tight_layout()
        filepath = os.path.join(FIGURES_DIR, "baris-tabel-kebenaran.png")
        plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()
        print(f"Generated: {filepath}")
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib numpy")


def main():
    print("=== Generate Figures for Bab 3 ===\n")
    print(f"Output directory: {FIGURES_DIR}\n")
    generate_baris_tabel_kebenaran()
    print("\nDone.")


if __name__ == "__main__":
    main()
