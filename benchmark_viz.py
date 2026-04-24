"""
benchmark_viz.py

Generates a self-contained HTML visualization from a telemetry JSON file.

Three panels:
  1. Convergence Curve  — cosine similarity between consecutive turn outputs
                          rising from adversarial divergence → consensus
  2. Entropy Decay      — flag severity entropy falling from uncertainty → certainty
  3. Model Family Map   — color-coded turn-by-turn architecture assignment

The three panels together make the structural argument: this is not a routing
network sending tokens to a shared latent space. It is adversarial collision
between independent architectures converging on truth through mathematical pressure.

Saves the HTML file alongside the telemetry JSON.
Usage:
  from benchmark_viz import generate_visualization
  generate_visualization(Path("benchmark_results/telemetry/telemetry_....json"))
"""

import json
from pathlib import Path


def generate_visualization(telemetry_path: Path) -> Path:
    """
    Read the telemetry JSON at telemetry_path and write a matching .html file.
    Returns the HTML output path.
    """
    telemetry_path = Path(telemetry_path)
    data = json.loads(telemetry_path.read_text())

    html = _build_html(data)

    out_path = telemetry_path.with_suffix(".html")
    out_path.write_text(html, encoding="utf-8")
    print(f"    Visualization: {out_path}")
    return out_path


def _build_html(data: dict) -> str:
    scenario     = data.get("scenario_name", "unknown")
    verdict      = data.get("verdict", "?")
    turns_run    = data.get("turns_run", 0)
    generated_at = data.get("generated_at", "")
    run_health   = data.get("run_health", "")
    threat_hyp   = data.get("threat_hypothesis", "")

    family_map    = data.get("architecture_proof", {}).get("model_family_assignment_map", [])
    family_colors = data.get("architecture_proof", {}).get("family_colors", {})
    constraint    = data.get("architecture_proof", {}).get(
        "consecutive_same_family_constraint", {}
    )
    embed_info    = data.get("embeddings", {})
    conv_series   = data.get("convergence_series", [])
    entropy_series = data.get("entropy_series", [])
    gov_briefs    = data.get("governor_brief_log", [])
    turns         = data.get("turns", [])

    # Panel 1: Convergence curve data
    conv_labels = [str(p["turn"]) for p in conv_series]
    conv_values = [
        round(p["cosine_similarity"], 6) if p["cosine_similarity"] is not None else None
        for p in conv_series
    ]
    conv_available = embed_info.get("available", False)
    conv_note = embed_info.get("note", "")

    # Panel 2: Entropy decay data
    ent_labels  = [str(p["turn"]) for p in entropy_series]
    ent_values  = [p["severity_entropy"] for p in entropy_series]
    sev_values  = [p["normalized_severity"] for p in entropy_series]

    # Panel 3: Family map data
    fam_labels  = [f"T{t['turn_number']}" for t in family_map]
    fam_families = [t["model_family"] for t in family_map]
    fam_roles    = [t.get("role", "") for t in family_map]
    fam_verdicts = [t.get("verdict", "") for t in family_map]
    fam_colors   = [family_colors.get(f, "#b2bec3") for f in fam_families]

    # Governor brief table rows
    brief_rows = ""
    for b in gov_briefs:
        fam = b.get("driver_family", "")
        color = family_colors.get(fam, "#b2bec3")
        brief_text = (b.get("brief_output", "") or "")[:400]
        if len(b.get("brief_output", "") or "") > 400:
            brief_text += "…"
        brief_rows += f"""
        <tr>
          <td class="num">{b.get('for_turn', '?')}</td>
          <td><span class="badge" style="background:{color}">{fam}</span> {b.get('driver_model', '')}</td>
          <td>{b.get('convergence_level', '')}</td>
          <td class="brief-text">{brief_text}</td>
        </tr>"""

    # Turn detail rows
    turn_rows = ""
    for t in turns:
        fam   = t.get("model_family", "")
        color = family_colors.get(fam, "#b2bec3")
        flags = t.get("severity_flags", {})
        flag_html = " ".join(
            f'<span class="flag flag-{v.lower()}">{k[:3].upper()}:{v[0]}</span>'
            for k, v in flags.items()
        )
        sim = t.get("cosine_similarity_prev")
        sim_str = f"{sim:.4f}" if sim is not None else "—"
        ent = t.get("severity_entropy")
        ent_str = f"{ent:.4f}" if ent is not None else "—"
        turn_rows += f"""
        <tr>
          <td class="num">{t.get('turn_number', '?')}</td>
          <td><span class="badge" style="background:{color}">{fam}</span></td>
          <td>{t.get('model_name', '')}</td>
          <td>{t.get('role', '')}</td>
          <td class="verdict verdict-{(t.get('verdict') or '').lower()}">{t.get('verdict', '')}</td>
          <td class="num">{sim_str}</td>
          <td class="num">{ent_str}</td>
          <td>{flag_html}</td>
          <td class="num">{t.get('input_tokens', 0)} + {t.get('output_tokens', 0)}</td>
        </tr>"""

    constraint_badge = (
        '<span class="ok">✓ constraint satisfied</span>'
        if constraint.get("constraint_satisfied")
        else f'<span class="warn">⚠ {len(constraint.get("violations", []))} violation(s)</span>'
    )

    verdict_class = "escalate" if verdict == "ESCALATE" else "allow"

    js_conv_labels    = json.dumps(conv_labels)
    js_conv_values    = json.dumps(conv_values)
    js_ent_labels     = json.dumps(ent_labels)
    js_ent_values     = json.dumps(ent_values)
    js_sev_values     = json.dumps(sev_values)
    js_fam_labels     = json.dumps(fam_labels)
    js_fam_families   = json.dumps(fam_families)
    js_fam_roles      = json.dumps(fam_roles)
    js_fam_verdicts   = json.dumps(fam_verdicts)
    js_fam_colors     = json.dumps(fam_colors)
    js_family_colors  = json.dumps(family_colors)
    js_conv_available = json.dumps(conv_available)
    js_conv_note      = json.dumps(conv_note)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Holo Engine Telemetry — {scenario}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg:       #0d1117;
    --surface:  #161b22;
    --border:   #30363d;
    --text:     #e6edf3;
    --muted:    #8b949e;
    --openai:   #74b9ff;
    --anthropic:#a29bfe;
    --google:   #55efc4;
    --escalate: #ff7675;
    --allow:    #55efc4;
    --high:     #ff7675;
    --medium:   #fdcb6e;
    --low:      #74b9ff;
    --none:     #636e72;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', 'Fira Mono', monospace;
    font-size: 13px;
    line-height: 1.6;
    padding: 24px;
  }}
  h1 {{ font-size: 22px; font-weight: 700; margin-bottom: 4px; }}
  h2 {{ font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--muted); letter-spacing: .08em; text-transform: uppercase; }}
  h3 {{ font-size: 13px; font-weight: 600; margin-bottom: 8px; }}
  .meta {{ color: var(--muted); font-size: 12px; margin-bottom: 24px; }}
  .verdict-badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 14px;
    margin-left: 8px;
  }}
  .verdict-badge.escalate {{ background: rgba(255,118,117,.2); color: var(--escalate); border: 1px solid var(--escalate); }}
  .verdict-badge.allow    {{ background: rgba(85,239,196,.2); color: var(--allow);    border: 1px solid var(--allow); }}
  .section {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 20px;
  }}
  .panels {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }}
  .panel-full {{ grid-column: 1 / -1; }}
  canvas {{ max-height: 280px; }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 600;
    color: #0d1117;
  }}
  .ok   {{ color: var(--allow); }}
  .warn {{ color: #fdcb6e; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }}
  th {{
    text-align: left;
    color: var(--muted);
    padding: 6px 8px;
    border-bottom: 1px solid var(--border);
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
  }}
  td {{
    padding: 6px 8px;
    border-bottom: 1px solid rgba(48,54,61,.5);
    vertical-align: top;
  }}
  tr:last-child td {{ border-bottom: none; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .brief-text {{ color: var(--muted); max-width: 480px; word-break: break-word; }}
  .flag {{ display: inline-block; padding: 1px 5px; border-radius: 3px; font-size: 10px; font-weight: 700; margin-right: 3px; }}
  .flag-high   {{ background: rgba(255,118,117,.25); color: var(--high); }}
  .flag-medium {{ background: rgba(253,203,110,.2);  color: var(--medium); }}
  .flag-low    {{ background: rgba(116,185,255,.2);  color: var(--low); }}
  .flag-none   {{ background: rgba(99,110,114,.2);   color: var(--none); }}
  .verdict-escalate {{ color: var(--escalate); font-weight: 700; }}
  .verdict-allow    {{ color: var(--allow); }}
  .note {{ color: var(--muted); font-size: 11px; margin-top: 8px; font-style: italic; }}
  .threat-hyp {{ color: var(--muted); font-size: 12px; padding: 8px 12px; background: rgba(48,54,61,.5); border-left: 3px solid var(--border); border-radius: 0 4px 4px 0; margin-top: 8px; }}
  .no-data {{ color: var(--muted); text-align: center; padding: 40px 0; }}
</style>
</head>
<body>

<h1>
  Holo Engine Telemetry
  <span class="verdict-badge {verdict_class}">{verdict}</span>
</h1>
<p class="meta">
  Scenario: <strong>{scenario}</strong> &nbsp;|&nbsp;
  Turns: <strong>{turns_run}</strong> &nbsp;|&nbsp;
  Health: <strong>{run_health}</strong> &nbsp;|&nbsp;
  Generated: {generated_at}
</p>

{"<div class='threat-hyp'><strong>Wrangler threat hypothesis:</strong> " + threat_hyp + "</div>" if threat_hyp else ""}

<!-- ======================================================== -->
<!-- Three-panel architecture proof                           -->
<!-- ======================================================== -->

<div class="panels">

  <!-- Panel 1: Convergence Curve -->
  <div class="section">
    <h2>Panel 1 — Convergence Curve</h2>
    <h3>Cosine similarity between consecutive turn outputs</h3>
    {"<p class='no-data'>Embeddings unavailable — " + conv_note + "</p>" if not conv_available else ""}
    {"<canvas id='chartConv'></canvas>" if conv_available else ""}
    <p class="note">Expected shape: rising from low similarity (adversarial divergence) → high similarity (convergence at verdict).<br>Embeddings: {embed_info.get("model", "N/A")}. {conv_note if not conv_available else "Cross-architecture shared vector space."}</p>
  </div>

  <!-- Panel 2: Entropy Decay -->
  <div class="section">
    <h2>Panel 2 — Entropy Decay</h2>
    <h3>Flag severity entropy per turn (proxy for output uncertainty)</h3>
    <canvas id="chartEnt"></canvas>
    <p class="note">Expected shape: falling from high entropy (spread across NONE/LOW/MEDIUM/HIGH) → low entropy (converged severity distribution).<br>Source: Shannon entropy over flag severity ranks. Logprob entropy unavailable (Anthropic/Google APIs + OpenAI JSON mode suppress token-level probabilities).</p>
  </div>

  <!-- Panel 3: Model Family Map (full width) -->
  <div class="section panel-full">
    <h2>Panel 3 — Model Family Assignment Map</h2>
    <h3>Architecture: no two consecutive turns share the same model family &nbsp; {constraint_badge}</h3>
    <canvas id="chartFamily" style="max-height:160px"></canvas>
    <p class="note">Each bar = one turn. Color = model family. Proves that no single architecture dominated the session and the same-DNA-never-collide rule was enforced throughout.</p>
  </div>

</div>

<!-- ======================================================== -->
<!-- Turn-by-turn audit trail                                 -->
<!-- ======================================================== -->

<div class="section">
  <h2>Turn-by-Turn Trace</h2>
  <table>
    <thead>
      <tr>
        <th>Turn</th>
        <th>Family</th>
        <th>Model</th>
        <th>Role</th>
        <th>Verdict</th>
        <th>Cosine sim</th>
        <th>Entropy</th>
        <th>Severity flags</th>
        <th>Tokens in+out</th>
      </tr>
    </thead>
    <tbody>
      {turn_rows}
    </tbody>
  </table>
</div>

<!-- ======================================================== -->
<!-- Governor brief log                                       -->
<!-- ======================================================== -->

<div class="section">
  <h2>Governor Brief Log</h2>
  <table>
    <thead>
      <tr>
        <th>For turn</th>
        <th>Driver</th>
        <th>Conv. level</th>
        <th>Brief (truncated to 400 chars)</th>
      </tr>
    </thead>
    <tbody>
      {brief_rows if brief_rows else "<tr><td colspan='4' class='no-data'>No governor briefs recorded.</td></tr>"}
    </tbody>
  </table>
</div>

<script>
const CONV_LABELS    = {js_conv_labels};
const CONV_VALUES    = {js_conv_values};
const ENT_LABELS     = {js_ent_labels};
const ENT_VALUES     = {js_ent_values};
const SEV_VALUES     = {js_sev_values};
const FAM_LABELS     = {js_fam_labels};
const FAM_FAMILIES   = {js_fam_families};
const FAM_ROLES      = {js_fam_roles};
const FAM_VERDICTS   = {js_fam_verdicts};
const FAM_COLORS     = {js_fam_colors};
const FAMILY_COLORS  = {js_family_colors};
const CONV_AVAILABLE = {js_conv_available};

Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = '#30363d';

// ---- Panel 1: Convergence Curve ----------------------------------------
if (CONV_AVAILABLE) {{
  const ctx1 = document.getElementById('chartConv').getContext('2d');
  new Chart(ctx1, {{
    type: 'line',
    data: {{
      labels: CONV_LABELS,
      datasets: [{{
        label: 'Cosine similarity (consecutive turns)',
        data: CONV_VALUES,
        borderColor: '#74b9ff',
        backgroundColor: 'rgba(116,185,255,0.08)',
        borderWidth: 2,
        pointBackgroundColor: '#74b9ff',
        pointRadius: 5,
        tension: 0.35,
        fill: true,
        spanGaps: false,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: ctx => `sim = ${{ctx.parsed.y !== null ? ctx.parsed.y.toFixed(6) : 'N/A'}}`
          }}
        }}
      }},
      scales: {{
        x: {{ title: {{ display: true, text: 'Turn number' }} }},
        y: {{
          min: 0, max: 1,
          title: {{ display: true, text: 'Cosine similarity' }}
        }}
      }}
    }}
  }});
}}

// ---- Panel 2: Entropy Decay --------------------------------------------
const ctx2 = document.getElementById('chartEnt').getContext('2d');
new Chart(ctx2, {{
  type: 'line',
  data: {{
    labels: ENT_LABELS,
    datasets: [
      {{
        label: 'Flag severity entropy',
        data: ENT_VALUES,
        borderColor: '#a29bfe',
        backgroundColor: 'rgba(162,155,254,0.08)',
        borderWidth: 2,
        pointBackgroundColor: '#a29bfe',
        pointRadius: 5,
        tension: 0.35,
        fill: true,
        yAxisID: 'y',
      }},
      {{
        label: 'Normalized severity (rising = more HIGH)',
        data: SEV_VALUES,
        borderColor: '#ff7675',
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [4, 4],
        pointBackgroundColor: '#ff7675',
        pointRadius: 3,
        tension: 0.35,
        yAxisID: 'y',
      }}
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ display: true, position: 'top', labels: {{ boxWidth: 12, font: {{ size: 11 }} }} }},
      tooltip: {{
        callbacks: {{
          label: ctx => `${{ctx.dataset.label}}: ${{ctx.parsed.y.toFixed(6)}}`
        }}
      }}
    }},
    scales: {{
      x: {{ title: {{ display: true, text: 'Turn number' }} }},
      y: {{ min: 0, title: {{ display: true, text: 'Entropy / severity' }} }}
    }}
  }}
}});

// ---- Panel 3: Model Family Map -----------------------------------------
const ctx3 = document.getElementById('chartFamily').getContext('2d');
new Chart(ctx3, {{
  type: 'bar',
  data: {{
    labels: FAM_LABELS,
    datasets: [{{
      label: 'Model family',
      data: FAM_LABELS.map(() => 1),
      backgroundColor: FAM_COLORS,
      borderColor: FAM_COLORS.map(c => c),
      borderWidth: 1,
      borderRadius: 3,
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          title: (items) => `Turn ${{items[0].label}}`,
          label: (ctx) => [
            `Family: ${{FAM_FAMILIES[ctx.dataIndex]}}`,
            `Role: ${{FAM_ROLES[ctx.dataIndex]}}`,
            `Verdict: ${{FAM_VERDICTS[ctx.dataIndex]}}`,
          ]
        }}
      }}
    }},
    scales: {{
      x: {{ title: {{ display: false }} }},
      y: {{ display: false, min: 0, max: 1.2 }}
    }}
  }}
}});

// Legend for family colors
const legend = document.createElement('div');
legend.style.cssText = 'display:flex;gap:16px;margin-top:8px;font-size:11px;';
const seenFamilies = [...new Set(FAM_FAMILIES)];
seenFamilies.forEach(fam => {{
  const color = FAMILY_COLORS[fam] || '#b2bec3';
  const item = document.createElement('span');
  item.innerHTML = `<span style="display:inline-block;width:12px;height:12px;background:${{color}};border-radius:2px;margin-right:4px;vertical-align:middle"></span>${{fam}}`;
  legend.appendChild(item);
}});
document.getElementById('chartFamily').parentNode.insertBefore(legend, document.getElementById('chartFamily').nextSibling);
</script>
</body>
</html>"""
