from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATEGORY_PAGES = {
    "Круговая этикетка": "catalog-krugovaya-etiketka.html",
    "Офсет": "catalog-ofset.html",
    "Самоклеящаяся этикетка": "catalog-samokleyaschayasya-etiketka.html",
    "Термобилеты": "catalog-termobilety.html",
    "Упаковка": "catalog-upakovka.html",
}
CATEGORY_DESCRIPTIONS = {
    "Круговая этикетка": "Этикетки для PET-тары, напитков, воды и лимонадной продукции.",
    "Офсет": "Листовая полиграфия, визитки, папки, флайеры и офсетные упаковочные решения.",
    "Самоклеящаяся этикетка": "Этикетки для пищевой продукции, напитков, косметики, бытовой химии и электроники.",
    "Термобилеты": "Билетная продукция и термоматериалы для событий, проходов и учёта.",
    "Упаковка": "Коробки, обечайки, BOPP-материалы и упаковка для разных товарных групп.",
}
SITE_URL = "https://wargie.github.io/flexprint_site"
SITE_NAME = "Флекспринт"
KEYWORDS = {
    "Круговая этикетка": "круговая этикетка, этикетка для PET, этикетки для напитков, печать этикеток Калининград",
    "Офсет": "офсетная печать Калининград, визитки, папки, флайеры, листовая полиграфия",
    "Самоклеящаяся этикетка": "самоклеящиеся этикетки, печать самоклеящихся этикеток, этикетки для продуктов, этикетки Калининград",
    "Термобилеты": "термобилеты, печать билетов, билетная продукция, термоматериалы Калининград",
    "Упаковка": "печать упаковки, картонная упаковка, обечайки, BOPP упаковка, упаковка Калининград",
}


def load_items() -> list[dict[str, str]]:
    source = (ROOT / "assets" / "catalog-items.js").read_text(encoding="utf-8")
    payload = source[source.index("[") : source.rindex("]") + 1]
    return json.loads(payload)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render_card(item: dict[str, str]) -> str:
    alt = f"{item['category']}{', ' + item['subcategory'] if item['subcategory'] else ''}: {item['title']}"
    return f"""
          <button class="work-card" type="button" data-lightbox-src="{esc(item['src'])}" data-lightbox-alt="{esc(alt)}">
            <img class="work-card__image" src="{esc(item['src'])}" alt="{esc(alt)}" loading="lazy" />
          </button>"""


def render_groups(category: str, items: list[dict[str, str]]) -> str:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in items:
        groups[item["subcategory"] or ""].append(item)

    parts: list[str] = []
    for subcategory, grouped_items in groups.items():
        heading = ""
        if subcategory:
            heading = f"""
        <h2 class="subcategory-title">{esc(subcategory)}</h2>"""
        cards = "".join(render_card(item) for item in grouped_items)
        parts.append(
            f"""{heading}
        <div class="portfolio-grid">{cards}
        </div>"""
        )
    return "\n".join(parts)


def render_page(category: str, items: list[dict[str, str]]) -> str:
    title = esc(category)
    description = esc(CATEGORY_DESCRIPTIONS[category])
    page_title = esc(f"{category} - примеры работ Флекспринт в Калининграде")
    page_url = f"{SITE_URL}/{CATEGORY_PAGES[category]}"
    keywords = esc(KEYWORDS[category])
    structured_data = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "CollectionPage",
                    "@id": f"{page_url}#webpage",
                    "url": page_url,
                    "name": f"{category} - примеры работ Флекспринт в Калининграде",
                    "description": CATEGORY_DESCRIPTIONS[category],
                    "isPartOf": {
                        "@type": "WebSite",
                        "@id": f"{SITE_URL}/#website",
                        "name": SITE_NAME,
                        "url": f"{SITE_URL}/",
                    },
                    "about": {
                        "@type": "Service",
                        "name": category,
                        "provider": {
                            "@type": "LocalBusiness",
                            "@id": f"{SITE_URL}/#organization",
                            "name": SITE_NAME,
                        },
                    },
                    "mainEntity": {
                        "@type": "ItemList",
                        "numberOfItems": len(items),
                        "itemListElement": [
                            {
                                "@type": "ListItem",
                                "position": index,
                                "name": item["title"],
                                "url": f"{SITE_URL}/{item['src']}",
                            }
                            for index, item in enumerate(items, start=1)
                        ],
                    },
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "Главная",
                            "item": f"{SITE_URL}/",
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": category,
                            "item": page_url,
                        },
                    ],
                },
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    groups = render_groups(category, items)
    body_class = "catalog-page catalog-page--termobilety" if category == "Термобилеты" else "catalog-page"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <meta name="description" content="{description}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="robots" content="index, follow" />
  <meta name="author" content="{SITE_NAME}" />
  <meta name="theme-color" content="#111827" />
  <link rel="canonical" href="{page_url}" />
  <link rel="icon" href="{SITE_URL}/favicon.ico" type="image/x-icon" />
  <link rel="icon" href="{SITE_URL}/favicon.png" type="image/png" sizes="120x120" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="ru_RU" />
  <meta property="og:site_name" content="{SITE_NAME}" />
  <meta property="og:title" content="{page_title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:image" content="{SITE_URL}/assets/hero-business.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{page_title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{SITE_URL}/assets/hero-business.jpg" />
  <script type="application/ld+json">
{structured_data}
  </script>
  <style>
    :root {{
      --bg: #eef1f5;
      --text: #111827;
      --muted: #5b6472;
      --line: #d9dde3;
      --dark: #1f2937;
      --container: 1180px;
      --radius: 4px;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--text);
      background-color: var(--bg);
      background-image:
        radial-gradient(circle at 12% 18%, rgba(0, 151, 167, 0.16) 0 120px, transparent 310px),
        radial-gradient(circle at 86% 12%, rgba(220, 38, 38, 0.11) 0 90px, transparent 270px),
        radial-gradient(circle at 78% 76%, rgba(245, 158, 11, 0.14) 0 130px, transparent 330px),
        repeating-linear-gradient(120deg, rgba(31, 41, 55, 0.06) 0, rgba(31, 41, 55, 0.06) 1px, transparent 1px, transparent 132px),
        linear-gradient(180deg, #f8fafc 0%, #e8edf3 44%, #f7f9fb 100%);
      background-attachment: fixed;
      line-height: 1.55;
    }}

    a {{ color: inherit; text-decoration: none; }}

    .container {{
      width: min(100% - 40px, var(--container));
      margin: 0 auto;
    }}

    .header {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(255, 255, 255, 0.94);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(14px);
    }}

    .header__inner {{
      min-height: 118px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }}

    .logo__image {{
      display: block;
      width: auto;
      max-width: 310px;
      max-height: 116px;
      object-fit: contain;
    }}

    .nav {{
      display: flex;
      align-items: center;
      gap: 22px;
      color: var(--dark);
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}

    .btn {{
      min-height: 44px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 22px;
      border: 1px solid var(--dark);
      border-radius: var(--radius);
      background: var(--dark);
      color: #ffffff;
      font-weight: 700;
    }}

    .hero {{
      padding: 82px 0 48px;
      border-bottom: 1px solid rgba(217, 221, 227, 0.72);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.58), rgba(255, 255, 255, 0.24));
    }}

    .label {{
      display: inline-block;
      margin-bottom: 18px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1, h2, h3 {{ margin: 0; line-height: 1.15; }}

    h1 {{
      max-width: 820px;
      font-size: clamp(38px, 5vw, 62px);
      letter-spacing: -0.035em;
    }}

    .hero p {{
      max-width: 760px;
      margin: 24px 0 0;
      color: var(--muted);
      font-size: 19px;
    }}

    .catalog {{
      padding: 62px 0 86px;
    }}

    .subcategory-title {{
      margin: 48px 0 18px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .portfolio-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 16px;
    }}

    .work-card {{
      min-width: 0;
      padding: 0;
      cursor: zoom-in;
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--line);
      box-shadow: 0 18px 42px rgba(31, 41, 55, 0.055);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .work-card:hover {{
      transform: translateY(-3px);
      border-color: rgba(31, 41, 55, 0.34);
    }}

    .work-card__image {{
      width: 100%;
      aspect-ratio: 4 / 3;
      display: block;
      object-fit: cover;
      background: #f9fafb;
    }}

    .catalog-page--termobilety .portfolio-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 28px;
      align-items: start;
    }}

    .catalog-page--termobilety .work-card {{
      padding: 18px;
      background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(242, 245, 248, 0.9));
      border-color: rgba(31, 41, 55, 0.14);
      box-shadow: 0 24px 58px rgba(31, 41, 55, 0.1);
    }}

    .catalog-page--termobilety .work-card__image {{
      aspect-ratio: 16 / 7;
      object-fit: contain;
      padding: 10px;
      background:
        linear-gradient(180deg, #ffffff 0%, #f5f7fa 100%);
      border: 1px solid rgba(31, 41, 55, 0.08);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.75);
    }}

    .lightbox {{
      position: fixed;
      inset: 0;
      z-index: 100;
      display: grid;
      grid-template-columns: 72px minmax(0, 1fr) 72px;
      align-items: center;
      gap: 18px;
      padding: 34px;
      background: rgba(15, 23, 42, 0.88);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.18s ease;
    }}

    .lightbox.is-open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .lightbox__stage {{
      min-width: 0;
      display: grid;
      justify-items: center;
    }}

    .lightbox__image {{
      max-width: 100%;
      max-height: calc(100vh - 68px);
      display: block;
      object-fit: contain;
      background: #ffffff;
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.42);
    }}

    .lightbox__button,
    .lightbox__close {{
      width: 52px;
      height: 52px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid rgba(255, 255, 255, 0.34);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.12);
      color: #ffffff;
      font-size: 30px;
      line-height: 1;
      cursor: pointer;
    }}

    .lightbox__button:hover,
    .lightbox__close:hover {{
      background: rgba(255, 255, 255, 0.22);
    }}

    .lightbox__close {{
      position: absolute;
      top: 22px;
      right: 22px;
      font-size: 24px;
    }}

    .footer {{
      background: rgba(255, 255, 255, 0.92);
      border-top: 1px solid var(--line);
      padding: 30px 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .footer__inner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
    }}

    @media (max-width: 1040px) {{
      .portfolio-grid {{ grid-template-columns: repeat(3, 1fr); }}
      .catalog-page--termobilety .portfolio-grid {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 720px) {{
      .container {{ width: min(100% - 28px, var(--container)); }}
      .header__inner {{ min-height: 88px; }}
      .logo__image {{ max-width: 245px; max-height: 86px; }}
      .nav {{ gap: 14px; font-size: 12px; }}
      .portfolio-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .catalog-page--termobilety .portfolio-grid {{ grid-template-columns: 1fr; gap: 18px; }}
      .catalog-page--termobilety .work-card {{ padding: 10px; }}
      .lightbox {{
        grid-template-columns: 1fr;
        gap: 12px;
        padding: 18px;
      }}
      .lightbox__button {{
        position: absolute;
        bottom: 18px;
      }}
      .lightbox__button--prev {{ left: 18px; }}
      .lightbox__button--next {{ right: 18px; }}
      .lightbox__image {{ max-height: calc(100vh - 116px); }}
    }}

    @media (max-width: 480px) {{
      .portfolio-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body class="{body_class}">
  <header class="header">
    <div class="container header__inner">
      <a class="logo" href="index.html" aria-label="Флекспринт">
        <img class="logo__image" src="logo.png" alt="Флекспринт" />
      </a>

      <nav class="nav" aria-label="Основная навигация">
        <a href="index.html#portfolio">Работы</a>
        <a href="index.html#services">Услуги</a>
        <a href="index.html#contacts">Контакты</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="container">
        <span class="label">Примеры работ</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </section>

    <section class="catalog">
      <div class="container">
        <a class="btn" href="index.html#portfolio">Назад к направлениям</a>
{groups}
      </div>
    </section>
  </main>

  <div class="lightbox" id="lightbox" aria-hidden="true" role="dialog" aria-label="Просмотр изображения">
    <button class="lightbox__close" type="button" aria-label="Закрыть">×</button>
    <button class="lightbox__button lightbox__button--prev" type="button" aria-label="Предыдущее изображение">‹</button>
    <div class="lightbox__stage">
      <img class="lightbox__image" id="lightboxImage" src="" alt="" />
    </div>
    <button class="lightbox__button lightbox__button--next" type="button" aria-label="Следующее изображение">›</button>
  </div>

  <footer class="footer">
    <div class="container footer__inner">
      <div><strong>Флекспринт</strong> · ПРОМЫШЛЕННАЯ УПАКОВКА И ПОЛИГРАФИЯ В КАЛИНИНГРАДЕ</div>
      <div><a href="mailto:zakaz@flexprintkld.ru">zakaz@flexprintkld.ru</a> · <a href="tel:+74012355476">8 (4012) 35-54-76</a></div>
    </div>
  </footer>

  <script>
    const cards = Array.from(document.querySelectorAll("[data-lightbox-src]"));
    const lightbox = document.getElementById("lightbox");
    const lightboxImage = document.getElementById("lightboxImage");
    const closeButton = document.querySelector(".lightbox__close");
    const prevButton = document.querySelector(".lightbox__button--prev");
    const nextButton = document.querySelector(".lightbox__button--next");
    let currentIndex = 0;

    function showImage(index) {{
      currentIndex = (index + cards.length) % cards.length;
      const card = cards[currentIndex];
      lightboxImage.src = card.dataset.lightboxSrc;
      lightboxImage.alt = card.dataset.lightboxAlt || "";
    }}

    function openLightbox(index) {{
      showImage(index);
      lightbox.classList.add("is-open");
      lightbox.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      closeButton.focus();
    }}

    function closeLightbox() {{
      lightbox.classList.remove("is-open");
      lightbox.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      lightboxImage.src = "";
    }}

    cards.forEach((card, index) => {{
      card.addEventListener("click", () => openLightbox(index));
    }});

    closeButton.addEventListener("click", closeLightbox);
    prevButton.addEventListener("click", () => showImage(currentIndex - 1));
    nextButton.addEventListener("click", () => showImage(currentIndex + 1));

    lightbox.addEventListener("click", (event) => {{
      if (event.target === lightbox) {{
        closeLightbox();
      }}
    }});

    document.addEventListener("keydown", (event) => {{
      if (!lightbox.classList.contains("is-open")) {{
        return;
      }}

      if (event.key === "Escape") closeLightbox();
      if (event.key === "ArrowLeft") showImage(currentIndex - 1);
      if (event.key === "ArrowRight") showImage(currentIndex + 1);
    }});
  </script>
</body>
</html>
"""


def build() -> None:
    items = load_items()
    by_category: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in items:
        by_category[item["category"]].append(item)

    for category, filename in CATEGORY_PAGES.items():
        page = render_page(category, by_category[category])
        (ROOT / filename).write_text(page, encoding="utf-8")
        print(f"{filename}: {len(by_category[category])}")


if __name__ == "__main__":
    build()
