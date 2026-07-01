# VeSync Cosori TurboBlaze Copywriter Exercise Staging

Status: staged fixture with one preserved local live lane. Do not rerun from this
folder without explicit approval.

This folder packages the VeSync copywriting exercise for a future HoloBuild-style creative loop and matching solo controls. It keeps the research packet, initial draft, and comparison protocol separate so the generation lanes can receive identical visible inputs.

## Files

- `00_input_brief.json`: assignment brief and user-specified constraints.
- `01_research_packet_seed.json`: evidence-leveled packet seed for the chosen product.
- `02_initial_draft.md`: starting creative draft to improve.
- `02_initial_draft.json`: starting creative draft normalized into the required output schema.
- `03_holobuild_run_plan.json`: six-turn HoloBuild loop plan with convergence enabled.
- `04_comparison_protocol.md`: solo single-shot, solo multi-shot, and HoloBuild comparison design.
- `05_output_schema.json`: exact JSON output template supplied by the user.
- `06_product_lane_strategy.json`: TurboBlaze live-research strategy and wellness-linkage requirements.
- `validate_vesync_output.py`: strict schema and email word-count validator for generated artifacts.
- `manifest.json`: package index and source-material references.

## Important Boundary

The current local `holo_builder/` runtime is shaped around AP/BEC benchmark packet construction. This staged project is a creative-assignment fixture. It should not be run through the existing AP/BEC Builder without a creative HoloBuild adapter or prompt surface.

Provider/model calls are not included in the fixture staging step. The preserved
`runs/live_lane-01_hb_creative_20260626T222600Z/` directory records a prior
approved local live lane and Gemini-only accepted judge tally. Live web research
is allowed only during an approved generation run, and every live finding must
be saved with source metadata before it can support copy. The active product
focus is Cosori TurboBlaze Air Fryer only.

This fixture inherits the HoloBuild architecture contract in `../../ARCHITECTURE.md`, including lossless canonical-thread access across turns and a 20-second live web-research cap per turn.
