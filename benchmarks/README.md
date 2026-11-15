# Benchmark publication

Source repositories: NuSTAR, NuExpansionHunter, NuTRF and NuMAFFT. Each maintains `benchmarks/published.json` on `main`; this directory is the initial validated snapshot. `scripts/benchmarks.py` defines the shared version-1 data contract. The renderer escapes text and links and computes ratios from measured values.

`Publish benchmark tables` fetches each main SHA, downloads that exact revision's data, validates all four files, builds the site and deploys it through GitHub Pages. A dispatch payload cannot select a repository, revision or executable. Concurrent publication runs are serialized and always read current main. Publication runs on repository dispatch, manual request and hourly fallback. It never executes benchmark programs.

The workflow uploads `benchmark-provenance` with the exact four source revisions and published records. Automated runs do not commit generated HTML back to main. For local preview, run `python3 scripts/sync_benchmarks.py` then `python3 build.py`; without fetching, the build uses the checked-in snapshot. Run `python3 -m unittest discover -s tests -v` before changing the publisher.

Only benchmark rows, table headers, captions, benchmark notes and Performance Improvement cells are generated. Project descriptions, Validation cells, upstream activity dates and the rest of the page remain in `template.html`.

The Pages source is **GitHub Actions**. Each of the four source repositories has the `BENCHMARK_PUBLISH_TOKEN` Actions Secret configured for immediate dispatch. The organization administrator maintains these secrets centrally; project maintainers do not need personal publishing credentials. An hourly poll remains a fallback.

To rotate the credential, create a fine-grained token limited to this website repository with **Contents: write** (required by `repository_dispatch`). Replace the secret in all four source repositories, run each **Published benchmark** workflow manually, and confirm a successful **Publish benchmark tables** deployment. Revoke the previous token after all four checks pass. Never copy an administrator's broad login token into Actions. If organization-level secret management becomes available, the same secret name can be shared with only these four repositories instead of storing four copies.

For maintainer handover, keep project-level review within each source repository and transfer publisher administration separately. No workflow depends on an individual maintainer's name. Review schema changes against all four existing data files before deploying them. A successful notification means the website accepted the request; the deployment workflow is the authority for whether it went live.

A fetch, validation, build or deployment failure preserves the previous deployed website. Review the failed workflow before retrying; never relax the schema to accept incomplete results. Changes to timing scope, RSS scope, hardware or repetitions must also update captions/notes and pinned evidence. An index-construction row is separate from sample processing; do not combine its resources with sample measurements.
