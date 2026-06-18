current_best_state:
  summary: >
    The strongest draft now recommends not signing the full two-year reserved AI
    infrastructure contract immediately, but instead using a structured six-month
    validation window with explicit gates and triggers. It materially improved by:
    quantifying the expected six-month waiting premium at about $1.68M at expected
    utilization, explicitly acknowledging that later reservation availability/pricing
    are unknown, framing the reliability-to-capacity link as unverified, and stating
    a default no-commit posture if gates are not met at month six.
  retained_strengths:
    - "Clear recommendation with board/CFO audience fit."
    - "Uses only provided numbers: $31M cash, $42M ARR, 18% growth, GM 73% to 66%, $9.6M/year reserved, 1.35x on-demand, $6M at-risk pipeline, runway 24 to 15 months if growth slows."
    - "Avoids pure cost framing by integrating revenue defense, enterprise requirements, and margin."
    - "Explicitly addresses two-year lock-in and runway compression."
    - "Includes staged decision logic via prerequisite gates and supporting triggers."
    - "Adds default action if evidence is inconclusive: continue on-demand rather than force commitment."
  likely_final_direction: >
    Final artifact should preserve the recommendation to wait six months rather than
    commit now, but tighten synthesis so it reads as a decisive board memo rather than
    an analytical notebook.

new_learnings_from_prior_turns:
  - >
    The biggest prior weakness was not the recommendation itself but failure to justify
    the six-month interval. The current draft now argues six months is the minimum
    credible period to complete root-cause diagnosis, deal-level pipeline validation,
    and margin stabilization assessment.
  - >
    Quantifying the cost of waiting is mandatory. The expected-utilization premium of
    waiting six months is approximately $1.68M, derived from $9.6M/year reserved versus
    $12.96M/year on-demand.
  - >
    "Preserve optionality" must be qualified: it is not a guaranteed future option,
    because future reservation availability and pricing are unknown.
  - >
    Trigger frameworks need operational discipline. Vague phrases like "root cause
    confirmed" must be tied to evidence standards, not management discretion.
  - >
    The final memo must define the default month-six posture if evidence is unresolved;
    otherwise the board may drift into a pressured commitment.
  - >
    The context does not support invented hybrid commercial structures. If mentioning
    staged options, they must be framed as decision stages or information-gathering
    stages, not as assumed partial-contract alternatives.

highest_value_flaw:
  flaw: >
    The current best draft may still be too long and process-heavy for a final board
    document, risking dilution of the core recommendation. It can still read as if the
    company is optimizing an evaluation framework rather than making a crisp strategic
    choice under uncertainty.
  why_it_matters: >
    Turn 6 is the final artifact, not another critique. The final document must
    synthesize pressure into a concise, executive-grade recommendation that balances:
    runway risk, commercial reliability pressure, margin deterioration, and lock-in.
    If the memo over-indexes on methodology, the board may miss the central judgment:
    paying an estimated $1.68M premium over six months is preferable to taking on a
    $19.2M two-year fixed obligation before the company proves capacity is the binding
    constraint and that downside runway remains acceptable.
  repair_priority:
    - "Compress repetitive caveats."
    - "Lead with recommendation and rationale hierarchy."
    - "Keep trigger thresholds, but present them as a practical decision rule."
    - "Ensure the staged options are framed as now / six-month validation / commit only if gates met."

source_context_anchors:
  facts:
    - "31M cash and no debt."
    - "ARR is 42M and growing 18 percent year over year."
    - "Gross margin fell from 73 percent to 66 percent over three quarters because inference usage increased faster than pricing changes."
    - "Reserved accelerator capacity costs 9.6M per year for two years."
    - "On-demand capacity costs roughly 1.35x reserved price at expected utilization, but demand is volatile."
    - "Enterprise customers are asking for data residency, audit logs, and latency commitments."
    - "Sales attributes 6M of at-risk expansion pipeline to AI feature reliability."
    - "Finance warns a full commitment could reduce runway from 24 months to 15 months if growth slows."
  derived_numbers_allowed:
    - "$19.2M total two-year reserved obligation."
    - "~46% of cash."
    - "$12.96M annual on-demand cost at expected utilization."
    - "$3.36M annual premium for on-demand versus reserved at expected utilization."
    - "~$1.68M six-month premium at expected utilization."
  mandatory_contextual tensions:
    - "Reliability may defend revenue but creates fixed cost."
    - "Waiting preserves cash but may weaken expansion pipeline."
  hidden_traps_to_avoid:
    - "Pure cost framing."
    - "Ignoring two-year lock-in."
    - "No trigger thresholds."

next_role_objective:
  primary_goal: >
    Produce the final board-facing document that makes a clear recommendation on whether
    to commit now or preserve optionality for six months, with disciplined synthesis and
    no meta-commentary.
  execution_focus:
    - "Deliver a polished final artifact, not a critique."
    - "Make the recommendation explicit in the opening."
    - "Show the board the trade: ~$1.68M expected six-month premium versus $19.2M two-year lock-in and runway risk."
    - "Integrate commercial stakes: $6M at-risk expansion pipeline and enterprise requirements."
    - "Use staged options and trigger thresholds as required by the brief."
    - "State the default if triggers are not met at month six."
  ideal_shape:
    - "Executive memo format."
    - "Short recommendation section."
    - "Decision rationale section."
    - "Staged options / trigger framework."
    - "Near-term actions and month-six default."

constraints_and_do_not_do:
  - "Do not write another mission packet."
  - "Do not critique prior drafts or mention turn history."
  - "Do not judge the benchmark."
  - "Do not invent market forecasts, customer names, or unprovided operational metrics."
  - "Use only the given numbers and clearly derived arithmetic."
  - "Do not assume partial reservations, shorter terms, or hybrid contracts exist unless explicitly framed as unavailable