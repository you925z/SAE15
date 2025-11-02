# === SAE15 : Traitement de donnée ===
# Version pédagogique : Python standard + csv uniquement

import csv

CSV_FILE = "enquete-police-municipal.csv"

# ---------------------- Helpers (simples) ----------------------

def read_csv_rows(path: str):
    """Lit le CSV et renvoie la liste de lignes (dictionnaires)."""
    with open(path, "r", encoding="utf-8") as f:
        head = f.read(4096)
        sep = ";" if head.count(";") >= head.count(",") else ","
        f.seek(0)
        reader = csv.DictReader(f, delimiter=sep)
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]

def to_num(x):
    """Convertit texte -> nombre (gère la virgule)."""
    try:
        return float(str(x).replace(",", "."))
    except:
        return 0.0

def fmt_int(n):
    """Affiche un entier avec des espaces pour les milliers."""
    try:
        return f"{int(round(n)):,}".replace(",", " ").replace("\u202f", " ")
    except:
        return str(n)

def fmt_float(x, nd=2):
    """Affiche un flottant avec n décimales (virgule)."""
    try:
        return f"{float(x):.{nd}f}".replace(".", ",")
    except:
        return str(x)

def esc(s: str) -> str:
    """Échappe un texte pour l’HTML."""
    s = "" if s is None else str(s)
    return (s.replace("&","&amp;")
             .replace("<","&lt;")
             .replace(">","&gt;")
             .replace('"',"&quot;")
             .replace("'","&#39;"))

# ---------------------- Modèle de données ----------------------

SPECIALITES = [
    ("agents_police",     "Agents de police"),
    ("asvp",              "ASVP"),
    ("gardes_champetres", "Gardes champêtres"),
    ("maitre_chien",      "Maîtres-chiens"),
    ("chien_police",      "Chiens de police"),
]

COULEURS = ["#4BC0C0", "#36A2EB", "#9966FF", "#FF6384", "#FF9F40"]  # pour donut + légende

# ---------------------- Agrégations ----------------------

def compute_aggregations(rows):
    """Calcule les totaux, valeurs par département, population…"""
    totaux = {k: 0.0 for k, _ in SPECIALITES}
    pop_dep = {}
    val_dep = {k: {} for k, _ in SPECIALITES}

    for r in rows:
        dep = r.get("departement", "")
        pop_dep[dep] = pop_dep.get(dep, 0.0) + to_num(r.get("habitants"))
        for cle, _ in SPECIALITES:
            v = to_num(r.get(cle))
            totaux[cle] += v
            val_dep[cle][dep] = val_dep[cle].get(dep, 0.0) + v

    dep_list = sorted(pop_dep.keys(), key=lambda x: (x is None, x))
    total_general = sum(totaux.values()) or 1.0
    total_pop = sum(pop_dep.values()) or 0.0
    nb_dep = len(dep_list)
    moyenne_dep = total_general / nb_dep if nb_dep else 0.0
    taux_10k = (total_general / total_pop * 10000.0) if total_pop > 0 else 0.0

    # totaux par département (toutes spécialités)
    total_dep = {d: sum(val_dep[k].get(d, 0.0) for k, _ in SPECIALITES) for d in dep_list}

    return {
        "totaux": totaux,
        "pop_dep": pop_dep,
        "val_dep": val_dep,
        "dep_list": dep_list,
        "total_general": total_general,
        "total_pop": total_pop,
        "nb_dep": nb_dep,
        "moyenne_dep": moyenne_dep,
        "taux_10k": taux_10k,
        "total_dep": total_dep
    }

# ---------------------- Donut CSS ----------------------

def build_donut_css(totaux):
    """Construit les stops du conic-gradient pour le donut."""
    total = sum(totaux.values()) or 1.0
    stops = []
    acc = 0.0
    couleurs = []
    labels = []
    values = []
    for i, (cle, nom) in enumerate(SPECIALITES):
        part = totaux[cle] / total * 100.0
        start = acc
        end = acc + part
        color = COULEURS[i % len(COULEURS)]
        stops.append(f"{color} {start:.4f}% {end:.4f}%")
        acc = end
        couleurs.append(color)
        labels.append(nom)
        values.append(totaux[cle])
    return ", ".join(stops), labels, values, couleurs

# ---------------------- Tables HTML ----------------------

def table_totaux(totaux, total_general):
    rows = []
    for cle, nom in SPECIALITES:
        val = totaux[cle]
        part = val / total_general * 100.0 if total_general > 0 else 0.0
        rows.append(f"<tr><td>{esc(nom)}</td><td class='num'>{fmt_int(val)}</td><td class='num'>{fmt_float(part,1)}%</td></tr>")
    return (
        "<div class='table-wrap'><table>"
        "<thead><tr><th>Spécialité</th><th>Total</th><th>Part (%)</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )

def table_top10_abs(total_dep):
    top10 = sorted(total_dep.items(), key=lambda kv: kv[1], reverse=True)[:10]
    rows = [f"<tr><td>{esc(dep)}</td><td class='num'>{fmt_int(val)}</td></tr>" for dep, val in top10]
    return (
        "<div class='table-wrap'><table>"
        "<thead><tr><th>Département</th><th>Total (toutes spécialités)</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )

def table_top10_rate(total_dep, pop_dep):
    rate = []
    for dep, val in total_dep.items():
        pop = pop_dep.get(dep, 0.0)
        r = (val / pop * 10000.0) if pop > 0 else 0.0
        rate.append((dep, r, val, pop))
    rate.sort(key=lambda x: x[1], reverse=True)
    top10 = rate[:10]
    rows = [
        f"<tr><td>{esc(dep)}</td><td class='num'>{fmt_float(r,2)}</td><td class='num'>{fmt_int(v)}</td><td class='num'>{fmt_int(p)}</td></tr>"
        for dep, r, v, p in top10
    ]
    return (
        "<div class='table-wrap'><table>"
        "<thead><tr><th>Département</th><th>Taux / 10 000</th><th>Total</th><th>Population</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )

def table_par_departement(dep_list, val_dep):
    head = "<th>Département</th>" + "".join(f"<th>{esc(nom)}</th>" for _, nom in SPECIALITES) + "<th>Total</th>"
    rows = []
    for d in dep_list:
        cells = []
        total_d = 0.0
        for cle, _ in SPECIALITES:
            v = val_dep[cle].get(d, 0.0)
            cells.append(f"<td class='num'>{fmt_int(v)}</td>")
            total_d += v
        rows.append(f"<tr><td>{esc(d)}</td>{''.join(cells)}<td class='num'>{fmt_int(total_d)}</td></tr>")
    return (
        "<div class='table-wrap'><table>"
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )

# ---------------------- Page HTML ----------------------

def build_page(data):
    donut_stops, labels, values, colors = build_donut_css(data["totaux"])
    # Légende (couleur + nom + valeur)
    legend_items = [
        f"<li><span class='dot' style='background:{colors[i]}'></span>{esc(labels[i])}"
        f"<span class='num'>{fmt_int(values[i])}</span></li>"
        for i in range(len(labels))
    ]
    legend_html = "<ul class='legend'>" + "".join(legend_items) + "</ul>"

    kpis = f"""
    <div class="kpis">
      <div class="kpi"><div class="label">Départements</div><div class="value">{data['nb_dep']}</div></div>
      <div class="kpi"><div class="label">Population totale</div><div class="value">{fmt_int(data['total_pop'])}</div></div>
      <div class="kpi"><div class="label">Total général</div><div class="value">{fmt_int(data['total_general'])}</div></div>
      <div class="kpi"><div class="label">Moyenne / département</div><div class="value">{fmt_int(data['moyenne_dep'])}</div></div>
      <div class="kpi"><div class="label">Taux global / 10 000</div><div class="value">{fmt_float(data['taux_10k'],2)}</div></div>
    </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>SAE15 : Traitement de donnée</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <header class="page-head">
    <h1>SAE15 : Traitement de donnée</h1>
    <p>Analyse du fichier <b>{esc(CSV_FILE)}</b> — visualisation simple et tableaux lisibles.</p>
    {kpis}
  </header>

  <section class="card" id="donut">
    <h2>Répartition des spécialités</h2>
    <div class="donut-wrap">
      <div class="donut" style="--conic: {donut_stops}">
        <div class="center">{fmt_int(data['total_general'])}</div>
      </div>
      {legend_html}
    </div>
  </section>

  <section class="card" id="totaux">
    <h2>Tableau 1 — Totaux par spécialité</h2>
    {table_totaux(data['totaux'], data['total_general'])}
  </section>

  <section class="card" id="top10">
    <h2>Tableau 2 — Top 10 départements (total)</h2>
    {table_top10_abs(data['total_dep'])}
  </section>

  <section class="card" id="taux10k">
    <h2>Tableau 3 — Classement par taux / 10 000 habitants</h2>
    {table_top10_rate(data['total_dep'], data['pop_dep'])}
  </section>

  <section class="card" id="par-dep">
    <h2>Tableau 4 — Par département (spécialités en colonnes)</h2>
    {table_par_departement(data['dep_list'], data['val_dep'])}
  </section>

  <footer class="foot">
    Projet SAE15 — BUT Info 1ère année.
  </footer>
</body>
</html>
"""
    return html

# ---------------------- main ----------------------

def main():
    rows = read_csv_rows(CSV_FILE)
    data = compute_aggregations(rows)
    page = build_page(data)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(page)
    print("✅ index.html généré (tableaux simples + donut coloré).")

if __name__ == "__main__":
    main()