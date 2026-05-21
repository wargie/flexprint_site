from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = [
    "Круговая этикетка",
    "Офсет",
    "Самоклеящаяся этикетка",
    "Термобилеты",
    "Упаковка",
]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
CATALOG_DIR = ROOT / "assets" / "catalog"
MAX_SIZE = (1200, 900)

TRANSLIT = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "c",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
)


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def slugify(value: str) -> str:
    value = value.lower().translate(TRANSLIT)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def title_from_stem(stem: str) -> str:
    title = stem.replace("_", " ").strip()
    title = re.sub(r"\s+", " ", title)
    return title


def unique_path(path: Path, used: set[Path]) -> Path:
    if path not in used:
        used.add(path)
        return path
    base = path.with_suffix("")
    suffix = path.suffix
    index = 2
    while True:
        candidate = Path(f"{base}-{index}{suffix}")
        if candidate not in used:
            used.add(candidate)
            return candidate
        index += 1


def convert_image(src: Path, dst: Path) -> tuple[int, int, int]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as image:
        image.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", image.size, "#ffffff")
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            canvas.paste(rgba, mask=rgba.getchannel("A"))
        else:
            canvas = image.convert("RGB")
        canvas.save(dst, "JPEG", quality=86, optimize=True, progressive=True)
        width, height = canvas.size
    return width, height, dst.stat().st_size


def discover_sources() -> list[Path]:
    files: list[Path] = []
    for dirname in SOURCE_DIRS:
        base = ROOT / dirname
        if not base.exists():
            continue
        files.extend(path for path in base.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
    return sorted(files, key=lambda path: [natural_key(part) for part in path.relative_to(ROOT).parts])


def build() -> None:
    files = discover_sources()
    used_paths: set[Path] = set()
    items = []
    index_rows = []

    for src in files:
        rel = src.relative_to(ROOT)
        category = rel.parts[0]
        subcategory = rel.parts[1] if len(rel.parts) > 2 else ""
        target_parts = [slugify(category)]
        if subcategory:
            target_parts.append(slugify(subcategory))
        dst_dir = CATALOG_DIR.joinpath(*target_parts)
        dst = unique_path(dst_dir / f"{slugify(src.stem)}.jpg", used_paths)
        width, height, bytes_size = convert_image(src, dst)
        dst_rel = dst.relative_to(ROOT).as_posix()
        items.append(
            {
                "category": category,
                "subcategory": subcategory,
                "title": title_from_stem(src.stem),
                "src": dst_rel,
                "source": rel.as_posix(),
            }
        )
        index_rows.append((category, subcategory, rel.as_posix(), dst_rel, width, height, round(bytes_size / 1024)))

    js = "const catalogItems = "
    js += json.dumps(items, ensure_ascii=False, indent=2)
    js += ";\n"
    (ROOT / "assets" / "catalog-items.js").write_text(js, encoding="utf-8")

    counts = Counter(item["category"] for item in items)
    subcounts = Counter((item["category"], item["subcategory"]) for item in items if item["subcategory"])
    grouped: dict[tuple[str, str], list[tuple[str, str, int, int, int]]] = defaultdict(list)
    for category, subcategory, source, target, width, height, kb in index_rows:
        grouped[(category, subcategory)].append((source, target, width, height, kb))

    lines = [
        "# Индекс материалов",
        "",
        f"Дата повторной индексации: {date.today().isoformat()}",
        "",
        "## Сводка",
        "",
        f"Всего рабочих изображений: {len(items)} без учета `logo.png`.",
        f"Оптимизированных изображений для сайта: {len(items)} JPG в `assets/catalog`.",
        "",
    ]
    for dirname in SOURCE_DIRS:
        lines.append(f"- {dirname}: {counts[dirname]}")
        for (category, subcategory), count in sorted(subcounts.items(), key=lambda pair: natural_key(pair[0][1])):
            if category == dirname:
                lines.append(f"  - {subcategory}: {count}")
    lines.append("- Логотип: 1")

    for dirname in SOURCE_DIRS:
        lines.extend(["", f"## {dirname}"])
        category_subs = sorted({sub for cat, sub in grouped if cat == dirname}, key=natural_key)
        if category_subs == [""]:
            for source, target, width, height, kb in grouped[(dirname, "")]:
                lines.append(f"- `{source}` -> `{target}` ({width}x{height}, {kb} KB)")
            continue
        for subcategory in category_subs:
            if subcategory:
                lines.extend(["", f"### {subcategory}"])
            for source, target, width, height, kb in grouped[(dirname, subcategory)]:
                lines.append(f"- `{source}` -> `{target}` ({width}x{height}, {kb} KB)")

    (ROOT / "MATERIALS_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        import build_catalog_pages

        build_catalog_pages.build()
    except Exception as error:
        print(f"catalog_pages_error={error}")
    print(f"indexed={len(items)}")


if __name__ == "__main__":
    build()
