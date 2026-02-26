#!/usr/bin/env python3
"""
Script untuk mendownload dan menggenerate gambar untuk Bab 2 Buku Ajar Logika Matematika.
Menjalankan: python scripts/download_figures_bab2.py
"""
import os
import sys

# Path relatif ke figures
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "buku_ajar_logika_matematika", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def download_from_url(url: str, filename: str) -> bool:
    """Download gambar dari URL ke folder figures."""
    try:
        import urllib.request
        filepath = os.path.join(FIGURES_DIR, filename)
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Download failed for {url}: {e}")
        return False


def generate_logic_gates() -> None:
    """Generate diagram gerbang logika dengan matplotlib."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon
        import numpy as np

        fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))

        # NOT gate
        ax = axes[0]
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_aspect('equal')
        ax.axis('off')
        # Triangle for NOT
        triangle = np.array([[0.3, 1], [1.5, 0.3], [1.5, 1.7]])
        ax.add_patch(plt.Polygon(triangle, fill=True, facecolor='lightgray', edgecolor='black'))
        circle = plt.Circle((1.65, 1), 0.15, fill=True, facecolor='white', edgecolor='black')
        ax.add_patch(circle)
        ax.plot(0.1, 1, 'ko', markersize=6)
        ax.plot(1.9, 1, 'ko', markersize=6)
        ax.text(0.05, 1, 'A', fontsize=12)
        ax.text(1.85, 1, 'Y', fontsize=12)
        ax.text(0.9, 1.4, 'NOT', fontsize=10)

        # AND gate
        ax = axes[1]
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_aspect('equal')
        ax.axis('off')
        # D-shaped AND
        arc = mpatches.Arc((1.2, 1), 1.2, 1.4, theta1=270, theta2=90, linewidth=2)
        ax.add_patch(arc)
        ax.plot([0.2, 0.6], [0.7, 0.7], 'k-', linewidth=1)
        ax.plot([0.2, 0.6], [1.3, 1.3], 'k-', linewidth=1)
        ax.plot([1.2, 1.9], [1, 1], 'k-', linewidth=1)
        ax.plot(0.2, 0.7, 'ko', markersize=6)
        ax.plot(0.2, 1.3, 'ko', markersize=6)
        ax.plot(1.9, 1, 'ko', markersize=6)
        ax.text(0.05, 0.65, 'A', fontsize=12)
        ax.text(0.05, 1.25, 'B', fontsize=12)
        ax.text(1.8, 1, 'Y', fontsize=12)
        ax.text(0.9, 1.2, 'AND', fontsize=10)

        # OR gate
        ax = axes[2]
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_aspect('equal')
        ax.axis('off')
        # Curved OR gate
        from matplotlib.patches import Arc, FancyArrowPatch
        arc1 = mpatches.Arc((0.8, 1), 0.8, 1.6, theta1=270, theta2=90, linewidth=2)
        ax.add_patch(arc1)
        ax.plot([0.1, 0.5], [0.65, 0.75], 'k-', linewidth=1)
        ax.plot([0.1, 0.5], [1.35, 1.25], 'k-', linewidth=1)
        ax.plot([1.4, 1.9], [1, 1], 'k-', linewidth=1)
        ax.plot(0.1, 0.65, 'ko', markersize=6)
        ax.plot(0.1, 1.35, 'ko', markersize=6)
        ax.plot(1.9, 1, 'ko', markersize=6)
        ax.text(0.02, 0.6, 'A', fontsize=12)
        ax.text(0.02, 1.3, 'B', fontsize=12)
        ax.text(1.82, 1, 'Y', fontsize=12)
        ax.text(1.0, 1.2, 'OR', fontsize=10)

        plt.tight_layout()
        filepath = os.path.join(FIGURES_DIR, "logic-gates.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"Generated: logic-gates.png")
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib")


def generate_timeline() -> None:
    """Generate timeline perkembangan logika dengan matplotlib."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime

        fig, ax = plt.subplots(figsize=(10, 4))
        events = [
            ("Aristoteles\n(384-322 SM)", -350),
            ("Stoik\n(Abad 3 SM)", -250),
            ("Boole\n(1854)", 1854),
            ("Frege\n(1879)", 1879),
            ("Wittgenstein\n(1921)", 1921),
        ]
        years = [e[1] for e in events]
        labels = [e[0] for e in events]

        ax.plot(years, [0] * len(years), 'k-', linewidth=2)
        for i, (label, year) in enumerate(events):
            ax.plot(year, 0, 'o', markersize=12, color='steelblue')
            ax.annotate(label, (year, 0), textcoords="offset points", xytext=(0, 15),
                        ha='center', fontsize=9)

        ax.set_xlim(-400, 2000)
        ax.set_ylim(-0.5, 0.5)
        ax.axis('off')
        ax.set_title("Timeline Perkembangan Logika Matematika", fontsize=12)
        plt.tight_layout()
        filepath = os.path.join(FIGURES_DIR, "timeline-logika.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"Generated: timeline-logika.png")
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib")


def main():
    print("=== Download/Generate Figures for Bab 2 ===\n")
    print(f"Output directory: {FIGURES_DIR}\n")

    # Download potret tokoh dari Wikimedia (public domain / CC)
    urls = [
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Aristotle_Altemps_Inv8575.jpg/220px-Aristotle_Altemps_Inv8575.jpg", "aristoteles.jpg"),
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/George_Boole_color.jpg/220px-George_Boole_color.jpg", "george-boole.jpg"),
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Gottlob_Frege_1891.jpg/220px-Gottlob_Frege_1891.jpg", "gottlob-frege.jpg"),
    ]
    for url, filename in urls:
        download_from_url(url, filename)

    # Generate diagrams
    generate_logic_gates()
    generate_timeline()

    print("\nDone.")


if __name__ == "__main__":
    main()
