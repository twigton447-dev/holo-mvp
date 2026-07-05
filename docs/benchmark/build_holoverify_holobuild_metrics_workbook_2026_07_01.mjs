#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "/Users/taylorwigton/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), "../..");
const compiledDir = path.join(repoRoot, "docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01");
const packagePath = path.join(compiledDir, "compiled_metrics_package.json");
const outputDir = path.join(repoRoot, "outputs/holoverify_holobuild_metrics_2026_07_01");
const workbookPath = path.join(outputDir, "HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx");
const previewPath = path.join(outputDir, "dashboard_preview.png");

function asValue(value) {
  if (value === undefined || value === null) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return value;
}

function rowsToMatrix(rows, preferredHeaders = null) {
  const headers = preferredHeaders ?? Array.from(
    rows.reduce((set, row) => {
      Object.keys(row).forEach((key) => set.add(key));
      return set;
    }, new Set()),
  );
  return [headers, ...rows.map((row) => headers.map((header) => asValue(row[header])))];
}

function writeSheet(workbook, name, rows, preferredHeaders = null) {
  const sheet = workbook.worksheets.add(name);
  const matrix = rowsToMatrix(rows, preferredHeaders);
  const range = sheet.getRangeByIndexes(0, 0, matrix.length, matrix[0].length);
  range.values = matrix;
  try {
    sheet.freezePanes.freezeRows(1);
    sheet.getRangeByIndexes(0, 0, 1, matrix[0].length).format.fill.color = "#172033";
    sheet.getRangeByIndexes(0, 0, 1, matrix[0].length).format.font.color = "#FFFFFF";
    sheet.getRangeByIndexes(0, 0, 1, matrix[0].length).format.font.bold = true;
    range.format.wrapText = true;
    range.format.autofitColumns();
    range.format.autofitRows();
  } catch (error) {
    console.warn(`format warning for ${name}: ${error.message}`);
  }
  return sheet;
}

function num(value) {
  if (value === "" || value === undefined || value === null) return "";
  const n = Number(value);
  return Number.isFinite(n) ? n : value;
}

function pct(value) {
  if (value === "" || value === undefined || value === null) return "";
  const n = Number(value);
  return Number.isFinite(n) ? `${(n * 100).toFixed(1)}%` : value;
}

function dashboardRows(data) {
  const rows = [];
  const metrics = data.metric_summary.filter((row) =>
    row.model === "ALL_MODELS_OR_ROSTER" &&
    row.metric_scope === "audit_grade_knew_or_admissible" &&
    !row.evidence_tier.includes("nonholo_aggregate") &&
    (String(row.system).startsWith("Holo") ||
      String(row.system).startsWith("Full Holo") ||
      String(row.system).startsWith("Holo registry"))
  );
  const order = [
    "Kit A / Accounts Payable-BEC Registry",
    "Kit B / Agentic Commerce v1 Registry",
    "Clinical Activation Boundary Controls / Kit C",
    "Vendor-Master Payment Controls / AP Replication",
    "Wave 2 / HR-Data Privacy-Finance Targeted Holo Runs",
    "Agentic Commerce / Order Execution Replication",
    "Agentic Commerce / All-Six Collapse Canary",
    "IT Access / Permission Change Replication",
    "Hard ALLOW FP 5-Pair Precursor",
  ];
  for (const family of order) {
    for (const row of metrics.filter((r) => r.evidence_family === family)) {
      rows.push({
        family: row.evidence_family,
        system: row.system,
        evidence_tier: row.evidence_tier,
        rows: num(row.total_rows),
        binary_n: num(row.binary_n),
        TP: num(row.TP),
        TN: num(row.TN),
        FP: num(row.FP),
        FN: num(row.FN),
        OTHER: num(row.OTHER),
        FPR: pct(row.FPR),
        FNR: pct(row.FNR),
        TPR: pct(row.TPR_recall),
        TNR: pct(row.TNR_specificity),
        operational_success: pct(row.operational_success_rate_all_rows),
        caveat: caveatFor(row),
      });
    }
  }
  return rows;
}

function caveatFor(row) {
  const tier = row.evidence_tier;
  if (tier === "public_registry_summary") return "Public registry summary row; packet-level traces not expanded here.";
  if (tier === "frozen_complete_run" || tier === "committed_evidence_package") return "Strongest HoloVerify package evidence.";
  if (tier === "wave2_selected_target_batches_complete") return "Selected-target Wave2 Holo evidence across HR, data privacy, and finance; not full-family statistical proof.";
  if (tier === "wave2_selected_target_solo_triage_exact_roster") return "Selected packets from Wave2 solo triage; same three model families as the Wave2 Holo roster.";
  if (tier === "batched_full_family_complete") return "Complete via locked batches; consolidated public package now exists.";
  if (tier === "replacement_family_rollup_needs_consolidated_lock") return "IT includes replacement pair 015R1; replacement rollup package now exists.";
  if (tier === "roster_matched_solo_baseline") return "Solo used the exact same three models used inside the matching Holo run.";
  if (tier === "solo_triage_same_packet_bank_openai_4o_mini") return "Same packet bank seam triage; xAI and MiniMax match Holo, but OpenAI solo is gpt-4o-mini while Holo W2 is gpt-5.4-mini.";
  if (tier === "lock_rooted_canary") return "Canary-sized, not full-family proof.";
  if (tier === "frozen_pending_judge_not_benchmark_locked") return "Frozen precursor pending full-gated judge.";
  return "";
}

function definitionsRows() {
  return [
    { term: "Positive class", definition: "ESCALATE is treated as positive for TP/FN/TPR/FNR." },
    { term: "TP", definition: "Truth ESCALATE and verdict ESCALATE." },
    { term: "FN", definition: "Truth ESCALATE and verdict ALLOW." },
    { term: "TN", definition: "Truth ALLOW and verdict ALLOW." },
    { term: "FP", definition: "Truth ALLOW and verdict ESCALATE." },
    { term: "OTHER", definition: "Missing/non-binary verdict, parse/content/provider failure, or non-admissible result in the audit-grade view." },
    { term: "Binary view", definition: "Counts a verdict when a parseable ALLOW/ESCALATE verdict exists, even if the answer was not audit-grade." },
    { term: "Audit-grade view", definition: "Counts TP/TN only when the artifact was KNEW/admissible; otherwise rows become OTHER." },
    { term: "Roster-matched solo", definition: "A solo baseline where the solo one-shots use the exact same three models used inside the matching Holo run." },
    { term: "Same-packet-bank solo triage", definition: "A solo triage run over the same frozen packets where one or more model slots may differ; use for seam discovery, not exact roster-matched claims." },
    { term: "AP roster", definition: "AP Holo and AP solo roster-matched baseline used xai/grok-3-mini, openai/gpt-5.4-mini, and minimax/MiniMax-M2.5-highspeed." },
    { term: "Commerce/IT triage roster", definition: "Commerce and IT solo triage used xai/grok-3-mini, openai/gpt-4o-mini, and minimax/MiniMax-M2.5-highspeed; the Holo OpenAI-W2 slot used openai/gpt-5.4-mini." },
    { term: "Wave2 selected-target evidence", definition: "Wave2 target batches count selected pairs from the HR, data privacy, and finance packet bank; they are not full-family or per-domain statistical proof." },
    { term: "FPR", definition: "FP / (FP + TN). False escalation rate on ALLOW truth." },
    { term: "FNR", definition: "FN / (FN + TP). False allow rate on ESCALATE truth." },
    { term: "TPR", definition: "TP / (TP + FN). Escalation recall." },
    { term: "TNR", definition: "TN / (TN + FP). Allow specificity." },
    { term: "Rule of three", definition: "With zero observed errors, about 60 samples per class are needed for a 95% upper error bound below 5%, 150 for below 2%, and 300 for below 1%." },
    { term: "Claim boundary", definition: "This workbook compiles current repo-backed evidence; it does not claim universal model superiority or production reliability." },
  ];
}

async function main() {
  const data = JSON.parse(await fs.readFile(packagePath, "utf8"));
  await fs.mkdir(outputDir, { recursive: true });

  const workbook = Workbook.create();

  const dashboard = writeSheet(workbook, "Dashboard", dashboardRows(data), [
    "family",
    "system",
    "evidence_tier",
    "rows",
    "binary_n",
    "TP",
    "TN",
    "FP",
    "FN",
    "OTHER",
    "FPR",
    "FNR",
    "TPR",
    "TNR",
    "operational_success",
    "caveat",
  ]);
  try {
    dashboard.getRange("A1:P1").format.fill.color = "#0B1220";
    dashboard.getRange("A1:P1").format.font.color = "#FFFFFF";
  } catch {}

  writeSheet(workbook, "HV Metrics", data.metric_summary);
  writeSheet(workbook, "HV Packet Rows", data.packet_rows);
  writeSheet(workbook, "HV Runs", data.run_summaries);
  writeSheet(workbook, "HoloBuild", data.holo_build_rows);
  writeSheet(workbook, "Significance", data.significance_planner);
  writeSheet(workbook, "Source Audit", data.source_audit);
  writeSheet(workbook, "Lock Inventory", data.lock_inventory);
  writeSheet(workbook, "Definitions", definitionsRows());

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(workbookPath);

  let previewStatus = "not_rendered";
  try {
    const preview = await workbook.render({ sheetName: "Dashboard", autoCrop: "all", scale: 1, format: "png" });
    const previewBytes = new Uint8Array(await preview.arrayBuffer());
    await fs.writeFile(previewPath, previewBytes);
    previewStatus = "rendered";
  } catch (error) {
    previewStatus = `render_failed:${error.message}`;
  }

  const manifest = {
    classification: "HOLOVERIFY_HOLOBUILD_METRICS_WORKBOOK",
    workbook_path: path.relative(repoRoot, workbookPath),
    dashboard_preview_path: path.relative(repoRoot, previewPath),
    preview_status: previewStatus,
    sheets: [
      "Dashboard",
      "HV Metrics",
      "HV Packet Rows",
      "HV Runs",
      "HoloBuild",
      "Significance",
      "Source Audit",
      "Lock Inventory",
      "Definitions",
    ],
    source_package: path.relative(repoRoot, packagePath),
    generated_without_provider_calls: true,
    packet_rows: data.packet_rows.length,
    metric_rows: data.metric_summary.length,
    run_rows: data.run_summaries.length,
    holobuild_rows: data.holo_build_rows.length,
    source_audit_rows: data.source_audit.length,
    lock_inventory_rows: data.lock_inventory.length,
  };
  const manifestPath = path.join(outputDir, "workbook_manifest.json");
  await fs.writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  console.log(JSON.stringify(manifest, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
