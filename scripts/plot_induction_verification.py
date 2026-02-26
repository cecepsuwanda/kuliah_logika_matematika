#!/usr/bin/env python3
"""
Generate grafik verifikasi numerik untuk Bab 7 (Induksi Matematika).
Plot: S_n = 1+2+...+n vs n(n+1)/2 untuk n=1..N.
Menjalankan: python scripts/plot_induction_verification.py
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FIGURES_BAB07 = os.path.join(
    PROJECT_ROOT, "buku_ajar_logika_matematika", "figures", "bab-07"
)
os.makedirs(FIGURES_BAB07, exist_ok=True)


def generate_verifikasi_jumlah():
    """Plot S_n = 1+2+...+n vs n(n+1)/2 untuk verifikasi rumus induksi."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        n_vals = np.arange(1, 21, dtype=int)
        S_n = np.array([sum(range(1, k + 1)) for k in n_vals])
        formula = n_vals * (n_vals + 1) // 2

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(n_vals, S_n, "o-", color="steelblue", linewidth=2, markersize=6, label=r"$S_n = 1+2+\cdots+n$")
        ax.plot(n_vals, formula, "s--", color="darkorange", linewidth=1.5, markersize=5, label=r"$n(n+1)/2$")
        ax.set_xlabel(r"$n$", fontsize=11)
        ax.set_ylabel("Nilai", fontsize=11)
        ax.set_title(r"Verifikasi numerik: $1+2+\cdots+n = n(n+1)/2$", fontsize=12)
        ax.legend(loc="upper left", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.set_xticks(n_vals[::2])
        plt.tight_layout()

        for ext in ["pdf", "png"]:
            filepath = os.path.join(FIGURES_BAB07, f"verifikasi-jumlah-n.{ext}")
            plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="white")
            print(f"Generated: {filepath}")
        plt.close()
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib numpy")


def main():
    print("=== Generate Figures for Bab 7 (Induksi Matematika) ===\n")
    print(f"Output directory: {FIGURES_BAB07}\n")
    generate_verifikasi_jumlah()
    print("\nDone.")


if __name__ == "__main__":
    main()
