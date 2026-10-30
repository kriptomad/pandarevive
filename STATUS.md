# STATUS

Last update: 2026-10-30. Nothing below has been executed on hardware.

## Commits

| Component | Repository / branch | Commit | Base |
|---|---|---|---|
| panda firmware | [kriptomad/panda `revive-f4`](https://github.com/kriptomad/panda/tree/revive-f4) | `a8225ef3aebff61ce73c7d4f5ad317e0f56a8165` | commaai/panda master `1305b78c9dca91169a94456439a7daf3184b13d5` (2026-10-25) |
| openpilot host side | [kriptomad/openpilot `revive-f4`](https://github.com/kriptomad/openpilot/tree/revive-f4) | `941cab937eb2a35ef1d8cd5020adf7161506b9e5` | commaai/openpilot master `0152aab4` (2026-10-25) |
| opendbc | unchanged | pinned by openpilot (`1bce882`) | - |

The `panda` submodule inside the openpilot branch points to `a8225ef3`.
The submodules of this repository point to the two commits above.

## openpilot CI

GitHub does not run workflows on the `kriptomad/openpilot` fork
("Workflows are not currently being run on this fork due to the scale of
GitHub Actions usage"), and `workflow_dispatch` is rejected there. The
fork-internal PR https://github.com/kriptomad/openpilot/pull/2
(`revive-f4` -> `revive-f4-base`, a copy of `0152aab4`) therefore has no
checks.

To run the openpilot workflows on GitHub-hosted runners, the exact trees
of `0152aab4` and `941cab937` were pushed to this repository as
`ci/openpilot-base` and `ci/openpilot-revive-f4` (history-less snapshots
on top of `main`) and a CI-only PR was opened:
https://github.com/kriptomad/pandarevive/pull/2 (not to be merged).

Run: https://github.com/kriptomad/pandarevive/actions/runs/41112766789
(workflow `tests`, event `pull_request`, head `508f0307` = tree of
`941cab937`).

| Job | Result | Notes |
|---|---|---|
| build release | success | `release/build_release.sh` on ubuntu-24.04; the `check-submodules` step is gated to `commaai/openpilot` and does not run here |
| build macOS | success | `pandad` is not built on Darwin (upstream SConscript guard), but the SConscript still imports `libusb` |
| static analysis | success | ruff, ty, codespell, dependency checks (`scripts/lint/lint.sh`) |
| unit tests | success | 1034 collected, 957 passed, 49 skipped, 1 xfailed. Includes `test_pandad_flash.py` (new) and the native `test_pandad_canprotocol` binary via `test_native.py`. `usb.o` compiled and `pandad` linked; `panda/board/obj/panda.bin.signed` (F4) built |
| process replay | success | - |
| Create UI Report | success | artifact push to `ci-artifacts` is gated to commaai and skipped |
| simulator driving | skipped | gated to `commaai/openpilot` |

Workflow `docs` on the same PR: success. Jobs that only exist for
`commaai/openpilot` (self-hosted runners, secrets, `ci-artifacts`
pushes) are not applicable to this fork.

Not covered by any CI job: `selfdrive/pandad/tests/test_pandad.py`,
`test_pandad_loopback.py` and `test_pandad_spi.py` require comma hardware
(`COMMA_HARDWARE_TEST`) and are skipped on PC runners.

## panda CI

Fork run on `a8225ef3`: https://github.com/kriptomad/panda/actions/runs/40712103722

| Job | Result | Notes |
|---|---|---|
| ./test.sh (ubuntu-latest) | success | scons for all targets including the F4, ruff, unit tests (51, 42 HITL skipped), MISRA mutation test for the F4 and H7 variants, `test_comms` with libpanda |
| windows pip package test | success | - |
| build | failure | pre-existing: the "Test python package installer" step uses the system pip on the ubuntu-26.04 image with Python 3.14 and `pandacan` requires `<3.13,>=3.12.3`. Same failure on an unmodified upstream tree with that image; not caused by this branch. The release build of the same job was done locally (see the scope document) |
| ./test.sh (macos-latest) | cancelled | cancelled by the `build` failure before a macOS runner was available |

## Local checks on Windows (openpilot branch)

- `ruff check openpilot/selfdrive/pandad`: all checks passed.
- `python -m pytest openpilot/selfdrive/pandad/tests/test_pandad_flash.py`:
  cannot be collected on Windows (`openpilot.common.hardware` imports
  `fcntl`); covered by the CI job above.
- No Linux toolchain or Docker available, so the C++ side was only
  compiled in CI.

## Known gaps

- No execution on a black panda (USB enumeration, bxCAN timing, harness
  detection, DFU entry through `Panda.reset(enter_bootstub)` /
  `reset(enter_bootloader)`, F4 self test, MPU regions).
- `import libusb` in `openpilot/selfdrive/pandad/SConscript` depends on
  the `comma-deps-libusb` package (`tools` extra). Not built inside a
  comma device image.
- Firmware base `1305b78c` is two firmware-only commits behind the panda
  commit openpilot master pinned before this branch (`f38f504f`).
- `test_pandad_spi.py` still asserts tres/cuatro hardware types
  (device-only test, untouched).
- No upstream pull request.
