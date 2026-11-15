# Benchmark publication

Source repositories: NuSTAR, NuExpansionHunter, NuTRF and NuMAFFT. Each maintains `benchmarks/published.json` on `main`; this directory is the initial validated snapshot. `scripts/benchmarks.py` defines the shared version-1 data contract. The renderer escapes text and links and computes ratios from measured values.

`Publish benchmark tables` fetches each main SHA, downloads that exact revision's data, validates all four files, builds the site and deploys it through GitHub Pages. A dispatch payload cannot select a repository, revision or executable. Concurrent publication runs are serialized and always read current main. Publication runs on repository dispatch, manual request and hourly fallback. It never executes benchmark programs.

The workflow uploads `benchmark-provenance` with the exact four source revisions and published records. Automated runs do not commit generated HTML back to main. For local preview, run `python3 scripts/sync_benchmarks.py` then `python3 build.py`; without fetching, the build uses the checked-in snapshot. Run `python3 -m unittest discover -s tests -v` before changing the publisher.

Only benchmark rows, table headers, captions, benchmark notes and Performance Improvement cells are generated. Project descriptions, Validation cells, upstream activity dates and the rest of the page remain in `template.html`.

Setup: choose **GitHub Actions** as this repository's Pages source. For immediate updates, configure organization secret `BENCHMARK_PUBLISH_TOKEN`, available to the four source repositories, with **Contents: write** permission on this website repository only. The token is used solely for `repository_dispatch`. Do not reuse a broad personal token. Without it, hourly polling still publishes valid updates. GitHub can delay scheduled runs.

A fetch, validation, build or deployment failure preserves the previous deployed website. Review the failed workflow before retrying; never relax the schema to accept incomplete results. Changes to timing scope, RSS scope, hardware or repetitions must also update captions/notes and pinned evidence. An index-construction row is separate from sample processing; do not combine its resources with sample measurements.
