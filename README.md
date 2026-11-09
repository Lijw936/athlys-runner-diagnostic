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

## Optional commit-status mirror

To also display the result on the private Athlys2 commit, add an Actions secret named `ATHLYS_STATUS_TOKEN` to this repository. Use a fine-grained token scoped only to `Lijw936/Athlys2`, with **Commit statuses: read and write**. Do not use a broad account token. The mirror is optional; the quality workflow remains functional without it.

## Android build workflow

`.github/workflows/athlys-private-build.yml` builds the currently pinned Android feature branch and uploads the APK only to a private draft release in `Lijw936/Athlys2`. It does not publish source code or APK binaries to this public repository.
