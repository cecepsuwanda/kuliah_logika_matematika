#!/usr/bin/env python3
"""
Membangun format penilaian (Excel) dari berkas soal LaTeX.

Sumber soal:
  - tugas/tugas1.tex
  - tugas/tugas2.tex
  - UTS/uts.tex
  - UAS/uas.tex

Keluaran:
  format_penilaian/penilaian_<nama>.xlsx

Menjalankan:
  python scripts/format_penilaian.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError as exc:  # pragma: no cover
    print(
        "Paket openpyxl belum terpasang. Jalankan:\n"
        "  pip install openpyxl\n"
        f"Detail: {exc}",
        file=sys.stderr,
    )
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "format_penilaian"

# Jumlah baris kosong untuk isian mahasiswa pada lembar Daftar Nilai.
JUMLAH_BARIS_MAHASISWA = 50
NILAI_MAKSIMAL_TOTAL = 100

SUMBER_SOAL: list[tuple[str, Path]] = [
    ("tugas1", PROJECT_ROOT / "tugas" / "tugas1.tex"),
    ("tugas2", PROJECT_ROOT / "tugas" / "tugas2.tex"),
    ("uts", PROJECT_ROOT / "UTS" / "uts.tex"),
    ("uas", PROJECT_ROOT / "UAS" / "uas.tex"),
]


@dataclass
class ButirPenilaian:
    """Satu unit skor (soal utuh atau butir a/b/...)."""

    kode: str
    deskripsi: str
    bobot: int = 0


@dataclass
class Asesmen:
    """Metadata dan daftar butir dari satu berkas soal."""

    kunci: str
    judul: str
    nama_mk: str
    kode_mk: str
    path_sumber: Path
    butir: list[ButirPenilaian] = field(default_factory=list)

    @property
    def total_bobot(self) -> int:
        return sum(b.bobot for b in self.butir)


# ---------------------------------------------------------------------------
# Utilitas teks LaTeX
# ---------------------------------------------------------------------------

_RE_COMMAND = re.compile(
    r"\\(?:newcommand|renewcommand)\s*\{\\(?P<name>[A-Za-z]+)\}"
    r"\s*\{(?P<body>(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}",
)
_RE_BEGIN_SOAL = re.compile(r"\\begin\{soal\}(?:\[[^\]]*\])?")
_RE_END_SOAL = re.compile(r"\\end\{soal\}")
# Hindari menangkap \newcommand{\soaluts} / \newcommand{\soaluas}.
_RE_SOAL_MACRO = re.compile(r"(?<![{])\\soal(?:uts|uas)\b")
_RE_BEGIN_ENUM = re.compile(r"\\begin\{enumerate\}(?:\[[^\]]*\])?")
_RE_END_ENUM = re.compile(r"\\end\{enumerate\}")
_RE_ITEM = re.compile(r"\\item\b")


def baca_teks(path: Path) -> str:
    return hapus_komentar_latex(path.read_text(encoding="utf-8"))


def hapus_komentar_latex(teks: str) -> str:
    """Buang komentar `% ...` agar tidak mengganggu deteksi lingkungan soal."""
    return re.sub(r"(?<!\\)%[^\n]*", "", teks)


def ambil_newcommand(teks: str, nama: str, default: str = "") -> str:
    for match in _RE_COMMAND.finditer(teks):
        if match.group("name") == nama:
            return bersihkan_latex(match.group("body"))
    return default


def bersihkan_latex(teks: str, batas: int = 120) -> str:
    """Ringkas cuplikan soal agar layak ditampilkan di sel Excel."""
    teks = teks.replace("\n", " ")
    teks = re.sub(r"\\begin\{[^}]+\}(?:\[[^\]]*\])?", " ", teks)
    teks = re.sub(r"\\end\{[^}]+\}", " ", teks)
    teks = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", teks)
    teks = teks.replace("$", "")
    teks = teks.replace("\\(", "").replace("\\)", "")
    teks = teks.replace("\\[", "").replace("\\]", "")
    teks = teks.replace("{", " ").replace("}", " ")
    teks = teks.replace("&", " ")
    teks = teks.replace("~", " ")
    teks = re.sub(r"\s+", " ", teks).strip(" .;:")
    if len(teks) > batas:
        return teks[: batas - 1].rstrip() + "…"
    return teks


def label_abjad(indeks: int) -> str:
    """1 -> a, 26 -> z, 27 -> aa, ..."""
    if indeks < 1:
        raise ValueError("indeks harus >= 1")
    hasil = ""
    n = indeks
    while n > 0:
        n, sisa = divmod(n - 1, 26)
        hasil = chr(ord("a") + sisa) + hasil
    return hasil


def label_romawi(indeks: int) -> str:
    tabel = [
        (1000, "m"),
        (900, "cm"),
        (500, "d"),
        (400, "cd"),
        (100, "c"),
        (90, "xc"),
        (50, "l"),
        (40, "xl"),
        (10, "x"),
        (9, "ix"),
        (5, "v"),
        (4, "iv"),
        (1, "i"),
    ]
    n = indeks
    parts: list[str] = []
    for nilai, simbol in tabel:
        while n >= nilai:
            parts.append(simbol)
            n -= nilai
    return "".join(parts)


def alokasi_bobot(jumlah: int, total: int = NILAI_MAKSIMAL_TOTAL) -> list[int]:
    """Bagagi total skor secara merata (metode largest remainder)."""
    if jumlah <= 0:
        return []
    dasar = total // jumlah
    sisa = total - dasar * jumlah
    bobot = [dasar] * jumlah
    for i in range(sisa):
        bobot[i] += 1
    return bobot


# ---------------------------------------------------------------------------
# Parser struktur enumerate bersarang
# ---------------------------------------------------------------------------

@dataclass
class _ItemEnum:
    teks: str
    anak: list["_ItemEnum"] = field(default_factory=list)


def _potong_hingga_seimbang(
    teks: str,
    mulai: int,
    pola_buka: re.Pattern[str],
    pola_tutup: re.Pattern[str],
) -> tuple[str, int]:
    """Ambil isi lingkungan mulai setelah token buka di posisi `mulai`."""
    kedalaman = 1
    pos = mulai
    while pos < len(teks) and kedalaman > 0:
        m_buka = pola_buka.search(teks, pos)
        m_tutup = pola_tutup.search(teks, pos)
        if m_tutup is None:
            raise ValueError("Lingkungan LaTeX tidak seimbang (akhir tidak ditemukan).")
        if m_buka is not None and m_buka.start() < m_tutup.start():
            kedalaman += 1
            pos = m_buka.end()
        else:
            kedalaman -= 1
            if kedalaman == 0:
                return teks[mulai : m_tutup.start()], m_tutup.end()
            pos = m_tutup.end()
    raise ValueError("Lingkungan LaTeX tidak seimbang.")


def parse_enumerate(teks: str) -> list[_ItemEnum]:
    """Urai `\begin{enumerate}...\end{enumerate}` terluar pertama (jika ada)."""
    m_buka = _RE_BEGIN_ENUM.search(teks)
    if m_buka is None:
        return []
    isi, _ = _potong_hingga_seimbang(
        teks, m_buka.end(), _RE_BEGIN_ENUM, _RE_END_ENUM
    )
    return _parse_isi_enumerate(isi)


_RE_BEGIN_ITEMIZE = re.compile(r"\\begin\{itemize\}(?:\[[^\]]*\])?")
_RE_END_ITEMIZE = re.compile(r"\\end\{itemize\}")


def _cari_item_satu_tingkat(isi: str, mulai: int) -> re.Match[str] | None:
    """Cari `\\item` berikutnya yang tidak berada di dalam enumerate/itemize bersarang."""
    kedalaman = 0
    pos = mulai
    while pos < len(isi):
        kandidat = [
            (_RE_BEGIN_ENUM.search(isi, pos), 1),
            (_RE_BEGIN_ITEMIZE.search(isi, pos), 1),
            (_RE_END_ENUM.search(isi, pos), -1),
            (_RE_END_ITEMIZE.search(isi, pos), -1),
            (_RE_ITEM.search(isi, pos), 0),
        ]
        kandidat = [(m, delta) for m, delta in kandidat if m is not None]
        if not kandidat:
            return None
        m, delta = min(kandidat, key=lambda x: x[0].start())
        if delta == 0 and kedalaman == 0:
            return m
        kedalaman += delta
        if kedalaman < 0:
            kedalaman = 0
        pos = m.end()
    return None


def _parse_isi_enumerate(isi: str) -> list[_ItemEnum]:
    items: list[_ItemEnum] = []
    pos = 0
    while True:
        m_item = _cari_item_satu_tingkat(isi, pos)
        if m_item is None:
            break
        start_konten = m_item.end()
        m_next = _cari_item_satu_tingkat(isi, start_konten)
        end_konten = m_next.start() if m_next else len(isi)
        potongan = isi[start_konten:end_konten]

        anak: list[_ItemEnum] = []
        # Ambil semua enumerate langsung di bawah butir (bukan hanya yang pertama).
        sisa = potongan
        teks_bagian: list[str] = []
        while True:
            m_nested = _RE_BEGIN_ENUM.search(sisa)
            if m_nested is None:
                teks_bagian.append(sisa)
                break
            teks_bagian.append(sisa[: m_nested.start()])
            nested_isi, nested_end = _potong_hingga_seimbang(
                sisa, m_nested.end(), _RE_BEGIN_ENUM, _RE_END_ENUM
            )
            anak.extend(_parse_isi_enumerate(nested_isi))
            sisa = sisa[nested_end:]
        teks_item = " ".join(bagian.strip() for bagian in teks_bagian if bagian.strip())

        items.append(_ItemEnum(teks=teks_item.strip(), anak=anak))
        pos = end_konten
    return items


def parse_semua_enumerate_terluar(teks: str) -> list[_ItemEnum]:
    """Urai semua lingkungan enumerate pada tingkat terluar (termasuk `[resume]`)."""
    semua: list[_ItemEnum] = []
    pos = 0
    kedalaman = 0
    while pos < len(teks):
        m_buka = _RE_BEGIN_ENUM.search(teks, pos)
        m_tutup = _RE_END_ENUM.search(teks, pos)
        if m_buka is None and m_tutup is None:
            break
        if m_buka is not None and (m_tutup is None or m_buka.start() < m_tutup.start()):
            if kedalaman == 0:
                isi, akhir = _potong_hingga_seimbang(
                    teks, m_buka.end(), _RE_BEGIN_ENUM, _RE_END_ENUM
                )
                semua.extend(_parse_isi_enumerate(isi))
                pos = akhir
                continue
            kedalaman += 1
            pos = m_buka.end()
        else:
            kedalaman = max(0, kedalaman - 1)
            pos = m_tutup.end() if m_tutup else len(teks)
    return semua


def butir_dari_items(
    nomor_soal: int,
    items: list[_ItemEnum],
    label_bahasan: str = "",
) -> list[ButirPenilaian]:
    """Ubah pohon enumerate menjadi daftar butir penilaian."""
    awalan = f"{nomor_soal}"
    if not items:
        deskripsi = label_bahasan or f"Soal {nomor_soal}"
        return [ButirPenilaian(kode=awalan, deskripsi=deskripsi)]

    hasil: list[ButirPenilaian] = []
    for i, item in enumerate(items, start=1):
        lab = label_abjad(i)
        kode_induk = f"{awalan}{lab}"
        if item.anak:
            for j, anak in enumerate(item.anak, start=1):
                kode = f"{kode_induk}.{label_romawi(j)}"
                desk = bersihkan_latex(anak.teks) or f"Soal {nomor_soal} butir {lab}.{label_romawi(j)}"
                hasil.append(ButirPenilaian(kode=kode, deskripsi=desk))
        else:
            desk = bersihkan_latex(item.teks) or f"Soal {nomor_soal} butir {lab}"
            if label_bahasan and i == 1 and len(items) == 1:
                desk = f"{label_bahasan}: {desk}"
            hasil.append(ButirPenilaian(kode=kode_induk, deskripsi=desk))
    return hasil


# ---------------------------------------------------------------------------
# Ekstraksi soal dari berkas
# ---------------------------------------------------------------------------

def ekstrak_blok_soal_theorem(teks: str) -> list[str]:
    blok: list[str] = []
    pos = 0
    while True:
        m_buka = _RE_BEGIN_SOAL.search(teks, pos)
        if m_buka is None:
            break
        isi, akhir = _potong_hingga_seimbang(
            teks, m_buka.end(), _RE_BEGIN_SOAL, _RE_END_SOAL
        )
        blok.append(isi)
        pos = akhir
    return blok


def ekstrak_blok_soal_macro(teks: str) -> list[str]:
    matches = list(_RE_SOAL_MACRO.finditer(teks))
    if not matches:
        return []
    blok: list[str] = []
    for i, m in enumerate(matches):
        mulai = m.end()
        selesai = matches[i + 1].start() if i + 1 < len(matches) else len(teks)
        potongan = teks[mulai:selesai]
        # Potong sebelum penutup dokumen / ucapan selamat.
        potongan = re.split(
            r"\\vspace\{1em\}|\\end\{document\}|---\s*Selamat",
            potongan,
            maxsplit=1,
        )[0]
        blok.append(potongan)
    return blok


def ambil_label_bahasan(blok: str) -> str:
    """Ambil label cetak miring di awal soal UTS/UAS, mis. (Pengertian Proposisi)."""
    m = re.search(r"\\textit\{", blok)
    if m is None:
        return ""
    isi, _ = _ambil_argumen_kurung_kurawal(blok, m.end())
    isi = isi.strip()
    if isi.startswith("(") and isi.endswith(")"):
        return bersihkan_latex(isi[1:-1], batas=80)
    return ""


def _ambil_argumen_kurung_kurawal(teks: str, mulai: int) -> tuple[str, int]:
    """Ambil isi `{...}` dengan memperhitungkan nested braces; `mulai` tepat setelah `{`."""
    kedalaman = 1
    pos = mulai
    while pos < len(teks) and kedalaman > 0:
        ch = teks[pos]
        if ch == "{":
            kedalaman += 1
        elif ch == "}":
            kedalaman -= 1
            if kedalaman == 0:
                return teks[mulai:pos], pos + 1
        elif ch == "\\" and pos + 1 < len(teks):
            pos += 1  # lewati karakter yang di-escape
        pos += 1
    raise ValueError("Argumen {...} tidak seimbang.")


def bangun_asesmen(kunci: str, path: Path) -> Asesmen:
    if not path.is_file():
        raise FileNotFoundError(f"Berkas soal tidak ditemukan: {path}")

    teks = baca_teks(path)
    judul = ambil_newcommand(teks, "JudulTugas") or ambil_newcommand(
        teks, "JudulUjian", kunci.upper()
    )
    nama_mk = ambil_newcommand(teks, "NamaMK", "Logika Matematika")
    kode_mk = ambil_newcommand(teks, "KodeMK", "")

    if kunci in {"tugas1", "tugas2"}:
        blok_soal = ekstrak_blok_soal_theorem(teks)
    else:
        blok_soal = ekstrak_blok_soal_macro(teks)

    # Buang blok kosong (sisa artefak parsing).
    blok_soal = [b for b in blok_soal if bersihkan_latex(b, batas=20)]

    if not blok_soal:
        raise ValueError(f"Tidak ada soal terdeteksi di {path}")

    butir: list[ButirPenilaian] = []
    for idx, blok in enumerate(blok_soal, start=1):
        label = ambil_label_bahasan(blok)
        # Ambil semua enumerate tingkat terluar (termasuk `\begin{enumerate}[resume]`).
        items = parse_semua_enumerate_terluar(blok)
        butir.extend(butir_dari_items(idx, items, label_bahasan=label))

    bobot_list = alokasi_bobot(len(butir), NILAI_MAKSIMAL_TOTAL)
    for b, bobot in zip(butir, bobot_list):
        b.bobot = bobot

    return Asesmen(
        kunci=kunci,
        judul=judul,
        nama_mk=nama_mk,
        kode_mk=kode_mk,
        path_sumber=path,
        butir=butir,
    )


# ---------------------------------------------------------------------------
# Penulisan Excel
# ---------------------------------------------------------------------------

_THIN = Border(
    left=Side(style="thin", color="B0B0B0"),
    right=Side(style="thin", color="B0B0B0"),
    top=Side(style="thin", color="B0B0B0"),
    bottom=Side(style="thin", color="B0B0B0"),
)
_FILL_HEADER = PatternFill("solid", fgColor="1F4E79")
_FILL_SUBHEADER = PatternFill("solid", fgColor="D6E3F0")
_FILL_TOTAL = PatternFill("solid", fgColor="FFF2CC")
_FILL_INFO_LABEL = PatternFill("solid", fgColor="E7E6E6")
_FONT_HEADER = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
_FONT_BOLD = Font(bold=True, name="Calibri", size=11)
_FONT_NORMAL = Font(name="Calibri", size=11)
_ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
_ALIGN_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)


def _style_header_cell(cell, fill=_FILL_HEADER, font=_FONT_HEADER) -> None:
    cell.fill = fill
    cell.font = font
    cell.alignment = _ALIGN_CENTER
    cell.border = _THIN


def tulis_lembar_info(wb: Workbook, asesmen: Asesmen) -> None:
    ws = wb.create_sheet("Info", 0)
    ws["A1"] = "FORMAT PENILAIAN"
    ws["A1"].font = Font(bold=True, size=14, name="Calibri", color="1F4E79")
    ws.merge_cells("A1:B1")

    baris_info = [
        ("Judul asesmen", asesmen.judul),
        ("Mata kuliah", asesmen.nama_mk),
        ("Kode mata kuliah", asesmen.kode_mk),
        ("Berkas sumber", str(asesmen.path_sumber.relative_to(PROJECT_ROOT))),
        ("Jumlah soal (blok utama)", _hitung_jumlah_soal(asesmen)),
        ("Jumlah butir penilaian", len(asesmen.butir)),
        ("Nilai maksimal total", NILAI_MAKSIMAL_TOTAL),
        ("Jumlah baris mahasiswa (template)", JUMLAH_BARIS_MAHASISWA),
        (
            "Catatan",
            "Bobot per butir dibagi merata hingga berjumlah 100. "
            "Dosen dapat mengubah kolom Bobot pada lembar Bobot Soal; "
            "sesuaikan juga baris bobot pada lembar Daftar Nilai.",
        ),
    ]
    for i, (label, nilai) in enumerate(baris_info, start=3):
        cell_l = ws.cell(row=i, column=1, value=label)
        cell_v = ws.cell(row=i, column=2, value=nilai)
        cell_l.fill = _FILL_INFO_LABEL
        cell_l.font = _FONT_BOLD
        cell_l.border = _THIN
        cell_v.font = _FONT_NORMAL
        cell_v.border = _THIN
        cell_v.alignment = _ALIGN_LEFT

    ws.column_dimensions["A"].width = 36
    ws.column_dimensions["B"].width = 80


def _hitung_jumlah_soal(asesmen: Asesmen) -> int:
    nomor = set()
    for b in asesmen.butir:
        m = re.match(r"(\d+)", b.kode)
        if m:
            nomor.add(int(m.group(1)))
    return len(nomor)


def tulis_lembar_bobot(wb: Workbook, asesmen: Asesmen) -> None:
    ws = wb.create_sheet("Bobot Soal", 1)
    headers = ["No", "Kode Butir", "Deskripsi Singkat", "Bobot Maksimal"]
    for col, judul in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=judul)
        _style_header_cell(cell)

    for i, butir in enumerate(asesmen.butir, start=1):
        row = i + 1
        ws.cell(row=row, column=1, value=i).alignment = _ALIGN_CENTER
        ws.cell(row=row, column=2, value=butir.kode).alignment = _ALIGN_CENTER
        ws.cell(row=row, column=3, value=butir.deskripsi).alignment = _ALIGN_LEFT
        cell_bobot = ws.cell(row=row, column=4, value=butir.bobot)
        cell_bobot.alignment = _ALIGN_CENTER
        for col in range(1, 5):
            ws.cell(row=row, column=col).border = _THIN
            ws.cell(row=row, column=col).font = _FONT_NORMAL

    total_row = len(asesmen.butir) + 2
    ws.cell(row=total_row, column=3, value="TOTAL").font = _FONT_BOLD
    cell_total = ws.cell(
        row=total_row,
        column=4,
        value=f"=SUM(D2:D{total_row - 1})",
    )
    cell_total.font = _FONT_BOLD
    cell_total.fill = _FILL_TOTAL
    cell_total.alignment = _ALIGN_CENTER
    for col in range(3, 5):
        ws.cell(row=total_row, column=col).border = _THIN

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 70
    ws.column_dimensions["D"].width = 16
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:D{total_row - 1}"


def tulis_lembar_daftar_nilai(wb: Workbook, asesmen: Asesmen) -> None:
    ws = wb.create_sheet("Daftar Nilai", 2)

    identitas = ["No", "NIM", "Nama Mahasiswa", "Kelas"]
    kode_butir = [b.kode for b in asesmen.butir]
    headers = identitas + kode_butir + ["Total", "Keterangan"]

    # Baris 1: header kolom
    for col, judul in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=judul)
        _style_header_cell(cell)

    # Baris 2: bobot maksimal per kolom skor
    ws.cell(row=2, column=1, value="").border = _THIN
    ws.cell(row=2, column=2, value="").border = _THIN
    ws.cell(row=2, column=3, value="Bobot maksimal →").font = _FONT_BOLD
    ws.cell(row=2, column=3).fill = _FILL_SUBHEADER
    ws.cell(row=2, column=3).border = _THIN
    ws.cell(row=2, column=4, value="").border = _THIN
    ws.cell(row=2, column=4).fill = _FILL_SUBHEADER

    col0_skor = len(identitas) + 1
    for i, butir in enumerate(asesmen.butir):
        col = col0_skor + i
        cell = ws.cell(row=2, column=col, value=butir.bobot)
        cell.fill = _FILL_SUBHEADER
        cell.font = _FONT_BOLD
        cell.alignment = _ALIGN_CENTER
        cell.border = _THIN

    col_total = col0_skor + len(asesmen.butir)
    cell_total_bobot = ws.cell(row=2, column=col_total, value=f"=SUM({get_column_letter(col0_skor)}2:{get_column_letter(col_total - 1)}2)")
    cell_total_bobot.fill = _FILL_TOTAL
    cell_total_bobot.font = _FONT_BOLD
    cell_total_bobot.alignment = _ALIGN_CENTER
    cell_total_bobot.border = _THIN

    ws.cell(row=2, column=col_total + 1, value="").fill = _FILL_SUBHEADER
    ws.cell(row=2, column=col_total + 1).border = _THIN

    # Baris data mahasiswa
    first_data_row = 3
    last_data_row = first_data_row + JUMLAH_BARIS_MAHASISWA - 1
    huruf_awal_skor = get_column_letter(col0_skor)
    huruf_akhir_skor = get_column_letter(col_total - 1)
    huruf_total = get_column_letter(col_total)

    for offset in range(JUMLAH_BARIS_MAHASISWA):
        row = first_data_row + offset
        ws.cell(row=row, column=1, value=offset + 1).alignment = _ALIGN_CENTER
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=row, column=col)
            cell.border = _THIN
            cell.font = _FONT_NORMAL
            if col >= col0_skor and col < col_total:
                cell.alignment = _ALIGN_CENTER
        # Rumus total per mahasiswa
        cell_sum = ws.cell(
            row=row,
            column=col_total,
            value=f"=IF(COUNTA({huruf_awal_skor}{row}:{huruf_akhir_skor}{row})=0,\"\",SUM({huruf_awal_skor}{row}:{huruf_akhir_skor}{row}))",
        )
        cell_sum.fill = _FILL_TOTAL
        cell_sum.alignment = _ALIGN_CENTER
        cell_sum.border = _THIN

    # Validasi angka: skor tidak melebihi bobot pada baris 2 (peringatan lunak via validasi per kolom)
    for i, butir in enumerate(asesmen.butir):
        col = col0_skor + i
        huruf = get_column_letter(col)
        dv = DataValidation(
            type="decimal",
            operator="between",
            formula1="0",
            formula2=str(butir.bobot),
            allow_blank=True,
            showErrorMessage=True,
            errorTitle="Skor di luar rentang",
            error=f"Masukkan skor antara 0 dan {butir.bobot}.",
        )
        dv.add(f"{huruf}{first_data_row}:{huruf}{last_data_row}")
        ws.add_data_validation(dv)

    # Baris ringkasan rata-rata
    ringkas_row = last_data_row + 2
    ws.cell(row=ringkas_row, column=3, value="Rata-rata kelas").font = _FONT_BOLD
    for i in range(len(asesmen.butir)):
        col = col0_skor + i
        huruf = get_column_letter(col)
        cell = ws.cell(
            row=ringkas_row,
            column=col,
            value=f"=IFERROR(AVERAGE({huruf}{first_data_row}:{huruf}{last_data_row}),\"\")",
        )
        cell.font = _FONT_BOLD
        cell.alignment = _ALIGN_CENTER
        cell.border = _THIN
    cell_avg_total = ws.cell(
        row=ringkas_row,
        column=col_total,
        value=f"=IFERROR(AVERAGE({huruf_total}{first_data_row}:{huruf_total}{last_data_row}),\"\")",
    )
    cell_avg_total.font = _FONT_BOLD
    cell_avg_total.fill = _FILL_TOTAL
    cell_avg_total.alignment = _ALIGN_CENTER
    cell_avg_total.border = _THIN

    # Lebar kolom
    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 28
    ws.column_dimensions["D"].width = 12
    for col in range(col0_skor, col_total):
        ws.column_dimensions[get_column_letter(col)].width = max(6, len(kode_butir[col - col0_skor]) + 2)
    ws.column_dimensions[huruf_total].width = 8
    ws.column_dimensions[get_column_letter(col_total + 1)].width = 22

    ws.freeze_panes = "E3"
    ws.row_dimensions[1].height = 30


def buat_workbook(asesmen: Asesmen, path_keluaran: Path) -> Path:
    wb = Workbook()
    # Hapus sheet default; lembar dibuat eksplisit.
    default = wb.active
    wb.remove(default)

    tulis_lembar_info(wb, asesmen)
    tulis_lembar_bobot(wb, asesmen)
    tulis_lembar_daftar_nilai(wb, asesmen)

    path_keluaran.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path_keluaran)
    return path_keluaran


def generate_semua(sumber: Iterable[tuple[str, Path]] = SUMBER_SOAL) -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    hasil: list[Path] = []
    for kunci, path in sumber:
        print(f"Memproses {path.relative_to(PROJECT_ROOT)} ...")
        asesmen = bangun_asesmen(kunci, path)
        keluar = OUTPUT_DIR / f"penilaian_{kunci}.xlsx"
        buat_workbook(asesmen, keluar)
        print(
            f"  -> {keluar.relative_to(PROJECT_ROOT)} "
            f"({_hitung_jumlah_soal(asesmen)} soal, {len(asesmen.butir)} butir, "
            f"total bobot {asesmen.total_bobot})"
        )
        hasil.append(keluar)
    return hasil


def main() -> int:
    try:
        berkas = generate_semua()
    except Exception as exc:
        print(f"Gagal membuat format penilaian: {exc}", file=sys.stderr)
        return 1
    print(f"Selesai. {len(berkas)} berkas Excel disimpan di {OUTPUT_DIR.relative_to(PROJECT_ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
