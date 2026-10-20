from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

candidates = [
    Path("artefacts.csv"),
    Path("../../documents_checker/artefacts.csv"),
]
art_path = next((p for p in candidates if p.exists()), None)
if art_path is None:
    raise FileNotFoundError("Не найден artefacts.csv")

COLS = ["FIO", "BirthDate", "BirthYear", "Document", "IssueYear", "Delta", "Source"]
df = pd.read_csv(art_path, sep=";", header=None, dtype=str)

if str(df.iloc[0, 0]).strip().upper() == "FIO":
    df = df.iloc[1:].reset_index(drop=True)
df.columns = COLS

df["Delta"] = pd.to_numeric(df["Delta"], errors="coerce")
art = df["Delta"].dropna().astype(int)

if art.empty:
    raise ValueError("В файле нет валидных значений Delta")

vc = art.value_counts()
peak_delta = int(vc.index[0])
peak_count = int(vc.iloc[0])

norm = None
raw_path = Path("../../resources/raw/BoardingData.csv")

if raw_path.exists():
    with raw_path.open(encoding="utf-8") as f:
        head = f.readline()
    sep = ";" if ";" in head else ("|" if "|" in head else ",")
    raw = pd.read_csv(raw_path, sep=sep, dtype=str, low_memory=False)

    doc_col = next((c for c in raw.columns if "Document" in c), None)
    birth_col = next((c for c in raw.columns if "BirthDate" in c), None)

    if doc_col and birth_col:
        passport_re = re.compile(r"^(\d{2})(\d{2})\s?(\d{6})$")
        values = []

        for doc, birth in zip(raw[doc_col].fillna(""), raw[birth_col].fillna("")):
            m = passport_re.match(str(doc).strip().upper())
            ym = re.search(r"(19|20)\d{2}", str(birth))
            if not m or not ym:
                continue

            birth_year = int(ym.group())
            yy = int(m.group(2))
            deltas = [1900 + yy - birth_year, 2000 + yy - birth_year]

            valid = [d for d in deltas if d in (14, 20, 45)]
            if valid:
                values.append(valid[0])

        if values:
            norm = pd.Series(values)

print(f"Артефактов: {len(art):,} | Уникальных паспортов: {df['Document'].nunique():,}")
print(f"Нормальных записей: {len(norm):,}" if norm is not None else "Норма: схематичная зона")
print(f"Пик артефактов: дельта {peak_delta} -> {peak_count} записей")

X_MIN, X_MAX = -80, 55
NORM_FROM, NORM_TO = 10, 50

plt.rcParams.update({"font.family": "sans-serif", "font.size": 11})

fig = plt.figure(figsize=(15, 8), facecolor="white")
ax = fig.add_axes([0.075, 0.13, 0.89, 0.60])

ax.set_xlim(X_MIN, X_MAX)
max_h = max(int(vc.max()), int(norm.value_counts().max()) if norm is not None else 0)
ax.set_ylim(0, max_h * 1.22)

ax.axvspan(NORM_FROM, NORM_TO, color="#2a9d8f", alpha=0.10, zorder=0)

if norm is not None:
    ax.hist(norm, bins=np.arange(10.5, 51.5, 1),
            color="#2a9d8f", edgecolor="white", linewidth=0.7, alpha=0.9)

ax.hist(art, bins=np.arange(int(art.min()) - 1, int(art.max()) + 2, 1),
        color="#e4572e", edgecolor="white", linewidth=0.6)

ax.axvline(0, color="#343a40", linestyle="--", linewidth=1.8, zorder=3)

ax.annotate(f"{peak_count} записей\nдельта {peak_delta}",
            xy=(peak_delta, peak_count),
            xytext=(peak_delta, max_h * 1.07),
            ha="center", va="bottom", fontsize=10, color="#b23a2a",
            arrowprops=dict(arrowstyle="->", color="#b23a2a", lw=1.2))

ax.text((NORM_FROM + NORM_TO) / 2, max_h * 1.07,
        "ЗОНА НОРМЫ\nдельта = 14 / 20 / 45 лет",
        ha="center", va="bottom", fontsize=10.5,
        fontweight="bold", color="#1b6b5e")

if norm is None:
    ax.text((NORM_FROM + NORM_TO) / 2, max_h * 0.45,
            "Корректные записи\nне попадают\nв файл артефактов",
            ha="center", va="center", fontsize=11, color="#1b6b5e")

fig.text(0.075, 0.955, "Качество данных: паспорт выдан раньше рождения",
         fontsize=17, fontweight="bold", color="#212529")

fig.text(0.075, 0.913,
         "Дельта = год выдачи паспорта - год рождения. Слева от нуля - физически невозможные записи.",
         fontsize=11.5, color="#495057")

top3 = " | ".join(f"{int(d)} лет -> {int(c)}" for d, c in vc.head(3).items())

fig.text(0.075, 0.858,
         f"АРТЕФАКТЫ: {len(art):,} записей | {df['Document'].nunique():,} уникальных паспортов\n"
         f"Топ-3 дельты (кол-во записей): {top3}",
         fontsize=10.5, va="top", color="#8a2b1b",
         bbox=dict(boxstyle="round,pad=0.55", facecolor="#fff0ed",
                   edgecolor="#e4572e", alpha=0.95))

norm_line = (f"НОРМА: {len(norm):,} записей из BoardingData"
             if norm is not None else "НОРМА: дельта в {14, 20, 45} лет")

fig.text(0.965, 0.858,
         f"{norm_line}\n"
         "Правило взято из documents_checker.py",
         fontsize=10.5, va="top", ha="right", color="#1b6b5e",
         bbox=dict(boxstyle="round,pad=0.55", facecolor="#eafaf5",
                   edgecolor="#2a9d8f", alpha=0.95))

ax.set_xlabel("Дельта (лет): год выдачи - год рождения", fontsize=12, labelpad=10)
ax.set_ylabel("Количество записей", fontsize=12, labelpad=10)
ax.set_xticks(range(X_MIN, X_MAX + 1, 10))
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)

fig.text(0.075, 0.045,
         f"Источник: {art_path.name} | Пунктир - граница невозможного (дельта = 0)",
         fontsize=9, color="#6c757d")

plt.savefig("artefacts_vs_norm.png", dpi=300, facecolor="white")
plt.show()