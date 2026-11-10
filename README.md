# Athlys independent CI runner

This repository contains CI workflow definitions only. It does not store or publish the private Athlys application source.

## Private-source quality validation

`.github/workflows/athlys-private-quality.yml`:

- checks out `Lijw936/Athlys2@main` using the `ATHLYS_READ_TOKEN` Actions secret;
- requires only read access to the private source repository;
- sets `persist-credentials: false`, so the checkout credential is removed before tests run;
- runs the vitrine, mobile, remote-AI, static JavaScript, JSON-manifest and service-worker checks;
- polls every 15 minutes and can also be started manually;
- caches a successful result by exact source commit SHA, so an unchanged revision is not needlessly retested.

The public runner's Actions result is the authoritative CI result while native Actions dispatch in the private source repository is unavailable.

## Neural Mesh feature-branch verification

`.github/workflows/athlys-neural-mesh-pr-verify.yml` independently validates the private Neural Mesh feature branch while native Actions dispatch in Athlys2 is returning startup failures:

- Checks out `Lijw936/Athlys2@feat/032-athlys-neural-mesh` by default; manual dispatch accepts another private ref.
- Uses the read-only `ATHLYS_READ_TOKEN` and `persist-credentials: false`; no source or checkout credentials are published.
- Runs the root release contract and browser-bundle build, Node 22 syntax and gateway tests, targeted Neural Mesh tests, Deno 2 Edge Function type-checking, Python learning-factory tests, Docker image build, and feature-branch web/privacy/PWA regression checks.
- Polls every 15 minutes and caches successful results by exact source SHA and workflow definition hash, so changing the validation gates forces a fresh run.
- Latest successful run: https://github.com/Lijw936/athlys-runner-diagnostic/actions/runs/42735872662
- Validated private source SHA: `17c62061a6ba6e4821e33d618a5615d657847c61`.

This is the active CI authority for the feature branch until the native private-repository Actions dispatcher is repaired. It does not deploy to production or activate external inference.

## Optional commit-status mirror

To also display the result on the private Athlys2 commit, add an Actions secret named `ATHLYS_STATUS_TOKEN` to this repository. Use a fine-grained token scoped only to `Lijw936/Athlys2`, with **Commit statuses: read and write**. Do not use a broad account token. The mirror is optional; the quality workflow remains functional without it.

## Android build workflow

`.github/workflows/athlys-private-build.yml` builds the currently pinned Android feature branch and uploads the APK only to a private draft release in `Lijw936/Athlys2`. It does not publish source code or APK binaries to this public repository.


## Private Desktop packaging validation

`.github/workflows/athlys-desktop-private-packages.yml` builds the selected private Athlys2 ref on independent Linux, Windows and macOS runners:

- Linux: server-only Quantum contract tests and Electron shell syntax checks. Rust/Scala server modules will be added to this job when Feature 031 implements them; no compute runtime is installed in Desktop.
- Windows: Electron NSIS installer and portable x64 executable; both must be present and at most 250 MiB.
- macOS: Electron ARM64 and x64 DMG + ZIP; all four outputs must be present and at most 250 MiB.
- The workflow is triggered when its definition changes on this repository's `main` branch and can be manually dispatched with a source ref.
- Only non-sensitive size/SHA-256 manifests are uploaded to this public runner. Application binaries are never uploaded here.
- If `ATHLYS_PRIVATE_UPLOAD_TOKEN` is configured with Contents: Write limited to `Lijw936/Athlys2`, each platform's binaries are uploaded to a **private draft release** in Athlys2. Without that optional secret, the builds and checks still run, but the binaries remain temporary on the runner.
- `ATHLYS_READ_TOKEN` must remain read-only (Contents: Read) on the private source repository. Checkout credentials are not persisted.
