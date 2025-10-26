## build_site.py
# Multi-pages : index (donut global interactif) + 5 pages par spécialité (barres PNG)
# CSV attendu : departement, habitants, agents_police, asvp, gardes_champetres, maitre_chien, chien_police, ...

from pathlib import Path
from collections import defaultdict, Counter
import csv, html, io, base64, json

# ===== Thème/couleurs du site =====
SITE_BG_DARK   = "#0f1b24"
SITE_TEXT      = "#dfe9e9"
SITE_TEAL      = "#3aa59f"   # couleur principale pour les barres
SITE_TEAL_DARK = "#2f7a76"

# Palette pour ECharts (du clair au foncé)
ECHARTS_PALETTE = [
    "#7fd8d0", "#62c9c0", "#49b8af", "#3aa59f", "#2f8f89",
    "#2a7a75", "#256864", "#1f5856", "#174746", "#113a3a"
]

# ===== Matplotlib pour les graphiques (pages spécialités) =====
_has_mpl = True
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Style sombre/assorti
    matplotlib.rcParams.update({
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "savefig.transparent": True,
        "text.color": SITE_TEXT,
        "axes.edgecolor": SITE_TEXT,
        "axes.labelcolor": SITE_TEXT,
        "xtick.color": SITE_TEXT,
        "ytick.color": SITE_TEXT,
        "grid.color": "#24424a",
    })
except Exception:
    _has_mpl = False

ROOT = Path(".")
CSV_PATH = ROOT / "enquete-police-municipal.csv"

# ---------- Lecture CSV ----------
def _detect_delimiter(sample: str) -> str:
    return ";" if sample.count(";") > sample.count(",") else ","

def read_rows(csv_path: Path):
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        s = f.read(4096)
        d = _detect_delimiter(s)
        f.seek(0)
        reader = csv.DictReader(f, delimiter=d)
        for r in reader:
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items()}

def to_num(v) -> float:
    if not v:
        return 0.0
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return 0.0

# ---------- Graphiques base64 (Matplotlib) ----------
def fig_to_b64():
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150, transparent=True)
    plt.close()
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode("ascii")

def bar_chart(labels, values, title, rotation=0):
    plt.figure(figsize=(9, 4.8))
    bars = plt.bar(range(len(labels)), values, color=SITE_TEAL, edgecolor=SITE_TEAL_DARK)
    plt.title(title)
    plt.xticks(range(len(labels)), labels, rotation=rotation,
               ha="right" if rotation else "center")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    return fig_to_b64()

# ---------- Donut interactif (ECharts) ----------
def echarts_donut_html(labels, values, title, elem_id="donut_global"):
    """
    Retourne le HTML + script ECharts (donut interactif) prêt à insérer dans la page.
    - labels/values : listes Python -> injectées en JSON
    - échappement des templates JS `\${...}` pour éviter l'interprétation par Python
    """
    data_labels = json.dumps(labels, ensure_ascii=False)
    data_values = json.dumps(values)
    palette     = json.dumps(ECHARTS_PALETTE)
    # NB: on échappe bien les ${...} pour JS avec \$
    return f"""
<div id="{elem_id}" class="chart" style="width:100%;min-height:420px;"></div>
<script>
(function(){{
  const el = document.getElementById("{elem_id}");
  const chart = echarts.init(el, null, {{ renderer: 'canvas' }});

  const labels = {data_labels};
  const values = {data_values};
  const total  = values.reduce((a,b)=>a+b, 0) || 1;
  const data   = labels.map((name,i)=>({{ name, value: values[i] }}));

  const option = {{
    backgroundColor: 'transparent',
    tooltip: {{
      trigger: 'item',
      formatter: (p) => {{
        const pct = Math.round((p.value/total)*1000)/10;
        return `\\${{p.name}} : <b>\\${{p.value}}</b> (\\${{pct}}%)`;
      }}
    }},
    legend: {{
      type: 'scroll',
      bottom: 0,
      textStyle: {{ color: '{SITE_TEXT}' }},
      itemWidth: 18, itemHeight: 12
    }},
    series: [{{
      name: '{html.escape(title)}',
      type: 'pie',
      radius: ['45%','70%'],
      center: ['50%','45%'],
      avoidLabelOverlap: true,
      itemStyle: {{
        borderRadius: 2,
        borderColor: '{SITE_BG_DARK}',
        borderWidth: 1
      }},
      label: {{ show: false }},
      emphasis: {{ label: {{ show: true, fontWeight: 'bold', color: '{SITE_TEXT}' }} }},
      data: data,
      color: {palette}
    }}]
  }};

  chart.setOption(option);
  window.addEventListener('resize', ()=>chart.resize());
}})();
</script>
"""

# ---------- Config des spécialités ----------
SPECIALITES = [
    ("agents_police",     "Agents de police",      "agents"),
    ("asvp",              "ASVP",                  "asvp"),
    ("gardes_champetres", "Gardes champêtres",     "gardes"),
    ("maitre_chien",      "Maîtres-chiens",        "maitres"),
    ("chien_police",      "Chiens de police",      "chiens"),
]

# ---------- Navigation commune ----------
def nav_links(active_slug=""):
    items = [
        ("index.html", "Accueil / Donut", "index"),
        *[(f"{slug}.html", label, slug) for _, label, slug in SPECIALITES]
    ]
    links = "\n".join(
        f'<a class="{"active" if active_slug == slug else ""}" href="{href}">{label}</a>'
        for href, label, slug in items
    )
    return f"""
<header class="topbar">
  <div class="brand">
    <button class="burger" onclick="toggleMenu()">&#9776;</button>
    <h1>Police Municipale</h1>
  </div>
  <nav class="quick">{links}</nav>
</header>
<nav class="subnav">
  <a href="index.html">Tableau de bord</a>
  <a href="#">Nous informer</a>
  <a href="#">Nous rejoindre</a>
</nav>
<div class="overlay" id="overlay" onclick="closeMenu()"></div>
<aside class="menu" id="menu">{links}</aside>
"""

# ---------- Squelette HTML ----------
def page_wrap(title, active_slug, body_html):
    """
    Injecte aussi ECharts via CDN + petit style pour s'accorder au thème.
    """
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="style.css" />
  <!-- ECharts (pour le donut interactif de l'index) -->
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    body {{ background:{SITE_BG_DARK}; color:{SITE_TEXT}; }}
    .chart-img {{ max-width:100%; height:auto; display:block; }}
    .card {{ background:rgba(255,255,255,0.03); border:1px solid #16333a; border-radius:10px; padding:12px; }}
    .bloc {{ margin: 18px 0; }}
    .table-wrap table.counts th, .table-wrap table.counts td {{ border-color:#24424a; }}
    .topbar, .subnav, .footer {{ background:rgba(255,255,255,0.02); border-top:1px solid #16333a; border-bottom:1px solid #16333a; }}
    a {{ color:{SITE_TEAL}; }}
    .quick a.active {{ color:#fff; background:{SITE_TEAL_DARK}; padding:3px 8px; border-radius:8px; }}
  </style>
</head>
<body>
  {nav_links(active_slug)}
  <main class="content">
    {body_html}
  </main>
  <footer class="footer">© Tableau multi-pages généré automatiquement.</footer>
  <script>
    function toggleMenu(){{
      document.getElementById('menu').classList.toggle('open');
      document.getElementById('overlay').classList.toggle('show');
    }}
    function closeMenu(){{
      document.getElementById('menu').classList.remove('open');
      document.getElementById('overlay').classList.remove('show');
    }}
  </script>
</body>
</html>"""

# ---------- Génération des pages ----------
def build_all():
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV introuvable: {CSV_PATH.resolve()}")

    rows = list(read_rows(CSV_PATH))
    if not rows:
        raise SystemExit("CSV vide.")

    # Agrégations
    total_by_spec = Counter({k: 0.0 for k, _, _ in SPECIALITES})
    dep_hab = defaultdict(float)
    dep_values = {k: defaultdict(float) for k, _, _ in SPECIALITES}

    for r in rows:
        dep = r.get("departement", "")
        dep_hab[dep] += to_num(r.get("habitants"))
        for key, _, _ in SPECIALITES:
            val = to_num(r.get(key))
            total_by_spec[key] += val
            dep_values[key][dep] += val

    # ---------- index.html : donut global (INTERACTIF) ----------
    donut_html = echarts_donut_html(
        [lbl for _, lbl, _ in SPECIALITES],
        [total_by_spec[key] for key, _, _ in SPECIALITES],
        "Répartition des spécialités (100%)",
        elem_id="donut_global"
    )

    index_body = f"""
<section class="bloc">
  <h3>Donut global des spécialités (interactif)</h3>
  <p class="muted">Survolez pour voir la valeur et le pourcentage.</p>
  <div class="grid"><figure class="card"><figcaption>Répartition</figcaption>{donut_html}</figure></div>
  <noscript><p>Activez JavaScript pour voir le graphique interactif.</p></noscript>
</section>
<section class="bloc">
  <h3>Totaux globaux</h3>
  <div class="table-wrap">
    <table class="counts">
      <thead><tr><th>Spécialité</th><th>Total</th></tr></thead>
      <tbody>
        {"".join(f"<tr><td>{html.escape(lbl)}</td><td>{int(total_by_spec[key])}</td></tr>" for key, lbl, _ in SPECIALITES)}
      </tbody>
    </table>
  </div>
</section>
"""
    (ROOT / "index.html").write_text(page_wrap("PM - Donut global", "index", index_body), encoding="utf-8")

    # ---------- Pages par spécialité ----------
    for key, label, slug in SPECIALITES:
        # Table : nombre par département
        rows_dep = sorted(dep_values[key].items(), key=lambda x:x[0])
        table_rows = "\n".join(f"<tr><td>{html.escape(dep)}</td><td>{int(val)}</td></tr>" for dep, val in rows_dep)
        table_html = f"""
<div class="table-wrap">
  <table class="counts">
    <thead><tr><th>Département</th><th>{html.escape(label)}</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
</div>"""

        # Moyenne pour 10k habitants
        total_val = sum(dep_values[key].values())
        total_hab = sum(dep_hab.values()) or 1.0
        rate_global = round((total_val / total_hab) * 10000.0, 2)

        # Graphiques (Top 15 absolu + Taux/10k) — couleurs assorties
        if _has_mpl:
            dep_sorted_abs = sorted(dep_values[key].items(), key=lambda x: x[1], reverse=True)
            labels_abs = [d for d,_ in dep_sorted_abs[:15]]
            values_abs = [v for _,v in dep_sorted_abs[:15]]
            img_abs = bar_chart(labels_abs, values_abs, f"Top 15 {label} (absolu)", rotation=45)

            rates = []
            for d in dep_values[key]:
                hab = dep_hab[d]
                if hab > 0:
                    rates.append((d, (dep_values[key][d] / hab) * 10000.0))
            rates.sort(key=lambda x:x[1], reverse=True)
            lab_rate = [d for d,_ in rates[:15]]
            val_rate = [round(v,2) for _,v in rates[:15]]
            img_rate = bar_chart(lab_rate, val_rate, f"Taux par département (pour 10 000) - {label}", rotation=45)
        else:
            img_abs = img_rate = ""

        body = f"""
<section class="bloc">
  <h3>{html.escape(label)}</h3>
  <p class="muted">Navigation : {", ".join(f"<a href='{s}.html'>{html.escape(l)}</a>" for _, l, s in SPECIALITES if s!=slug)}</p>
</section>

<section class="bloc">
  <h3>Nombre par département</h3>
  <div class="grid">
    <div class="card">
      <figcaption>Table</figcaption>
      {table_html}
    </div>
    <div class="card">
      <figcaption>Barres (absolu)</figcaption>
      {("<img class='chart-img' src='"+img_abs+"' alt='Top 15 absolu'/>") if img_abs else "<p class='muted'>Matplotlib non installé.</p>"}
    </div>
  </div>
</section>

<section class="bloc">
  <h3>Moyenne pour 10 000 habitants</h3>
  <p class="muted">Valeur globale (toutes communes) : <strong>{rate_global}</strong></p>
  <div class="card">
    <figcaption>Taux par département (Top 15)</figcaption>
    {("<img class='chart-img' src='"+img_rate+"' alt='Taux 10k'/>") if img_rate else "<p class='muted'>Matplotlib non installé.</p>"}
  </div>
</section>
"""
        (ROOT / f"{slug}.html").write_text(page_wrap(f"PM - {label}", slug, body), encoding="utf-8")

    print("✅ Pages générées : index.html + 5 pages spécialités")

if __name__ == "__main__":
    build_all()