# pandarevive

Bringing the comma **black panda** (STM32F413) back to current
[panda](https://github.com/commaai/panda) and
[openpilot](https://github.com/commaai/openpilot) master.

[Portugues (Brasil)](README.pt-BR.md)

## Status in one paragraph

Two fork branches exist and compile: panda firmware
[`kriptomad/panda` branch `revive-f4`](https://github.com/kriptomad/panda/tree/revive-f4)
and openpilot host side
[`kriptomad/openpilot` branch `revive-f4`](https://github.com/kriptomad/openpilot/tree/revive-f4).
The firmware passes the panda CI (build, MISRA, unit tests) and the
openpilot branch is run through the openpilot CI on GitHub-hosted runners.
**Nothing has been executed on a real black panda.** No pull request has
been opened upstream. Exact commit hashes and CI links are in
[STATUS.md](STATUS.md).

## Why

commaai removed the STM32F4 family (white, grey, black panda and the
uno/dos boards) from the panda firmware in 2025:

- `3d272335` (2025-07-19): deleted `board/boards/black.h` and `white.h`.
- `1ce986f7` "bye bye f4" (2025-08-26): deleted `board/stm32f4/*`, the
  bxCAN driver, the F4 build target and the Python `McuType.F4` /
  `HW_TYPE_BLACK` support.

On the openpilot side, `96d1b876b` (2026-02-14) removed the libusb
transport from `pandad` (SPI only), and `9aca13cf2` hardcoded the MCU
type to H7. A black panda talks USB only and has no SPI slave, so current
openpilot master cannot see it even with working firmware.

The black panda is still a usable device: three CAN 2.0 buses (two via the
built-in transceivers plus the harness-selected bus), USB, and the same
safety model code (`opendbc/safety`) that the red/tres panda runs. For
cars that do not need CAN-FD (for example the Honda City G7 used in the
[openpilot-honda-city-brasil](https://github.com/kriptomad/openpilot-honda-city-brasil)
project) it is the cheapest way to run current openpilot on a PC.

## What is done

### Firmware: `kriptomad/panda` branch `revive-f4`

Base: `commaai/panda` master `1305b78c` (2026-10-25). Commits, oldest first:

| Commit | Subject |
|---|---|
| `967f6359` | board: restore STM32F4 / black panda sources verbatim |
| `ed13efa9` | board: adapt STM32F4 port to current driver/sys structure |
| `87270986` | bxcan: port to the current can_common / fdcan.h structure |
| `a56ee038` | build: add the STM32F4 panda target |
| `611b2d50` | python: restore STM32F4 / black panda support |
| `ee3ba954` | misra: check the STM32F4 variant again |
| `9ed2fd36` | README: mention the black panda (STM32F413) target |
| `e78c41e6` | misra: clean the STM32F4 variant and the H7 self test findings |
| `6e2ee01a` | docs: step by step flashing guide for a black panda used with the Honda City G7 port (EN + pt-BR) |
| `a8225ef3` | docs: quick path for the flowpilot option in the black panda flashing guide |

What it restores: `board/stm32f4/*` (clock, peripherals, linker scripts,
startup, bootstub, USB OTG FS, ADC, timers, DFU entry),
`board/boards/black.h`, the bxCAN driver adapted to the current
`can_common` interface, the `panda` SCons target next to `panda_h7`,
`McuType.F4`, `HW_TYPE_BLACK` (hw type 3) and the F4 DFU serial in the
Python library. Debug and release builds compile, cppcheck/MISRA is clean
for the F4 and H7 variants, and `test.sh` passes in the fork CI
(see STATUS.md for the run that still fails on a pre-existing
Python 3.14 pip step unrelated to this branch).

### Host side: `kriptomad/openpilot` branch `revive-f4`

Base: `commaai/openpilot` master `0152aab4` (2026-10-25). Commits, oldest first:

| Commit | Subject |
|---|---|
| `45b12a352` | panda: point submodule to the revive-f4 fork |
| `92b862b5e` | pandad: restore USB comms for external pandas |
| `c1e41b44b` | pandad: flash an external panda through its own bootloader request |
| `941cab937` | pandad: cover the black panda in the host side tests |

Mapping of what upstream removed and what the branch restores:

| Upstream change | Restored in `revive-f4` |
|---|---|
| `96d1b876b` deleted `panda_comms.cc` (`PandaUsbHandle`), the `PandaCommsHandle` base class and libusb from the pandad build | `panda_comms.h` has the base class again, `usb.cc` is the old `panda_comms.cc`, `Panda` tries USB first and falls back to SPI, `Panda::list()` merges USB and SPI serials; libusb comes from the `comma-deps-libusb` package already used by cabana |
| `9aca13cf2` hardcoded `McuType.H7` in `pandad.py` | The panda library from the fork resolves the MCU type from the hardware type; `pandad.py` does not need to know |
| `d3f0aab96` rewrote the flashing loop around the SoM reset/BOOT0 lines (`HARDWARE.recover_internal_panda()`) | On a PC (`COMMA_HARDWARE` false) `flash_panda()` asks the firmware to enter the bootstub and then the ST bootloader before `PandaDFU.recover()`; the comma-device path is unchanged |
| `test_pandad_canprotocol.cc` only exercised dos and red panda frames | `blackPanda` added to the hardware type loop; new `test_pandad_flash.py` covers the external and internal flashing paths with mocks |
| `.gitmodules` pointed `panda` to `commaai/panda` | Points to `kriptomad/panda` branch `revive-f4` at `a8225ef3` |

No change was needed in `opendbc` (the safety code is shared), in the
hardware layer (`common/hardware`: a black panda on a PC is an external
USB device, `HardwarePc` is used as is), in cereal (`blackPanda @3` was
never removed from `PandaState.hwType`) or in the process config.

## What is NOT done

- Nothing has been executed on hardware. USB enumeration, bxCAN timing,
  harness detection, DFU entry, the F4 self test and the MPU regions are
  all unexercised. See section 6 of the
  [scope document](https://github.com/kriptomad/openpilot-honda-city-brasil/blob/main/hardware/research/pandarevive-scope.md)
  for the full list.
- No upstream pull request. commaai removed F4 on purpose; this work is
  kept in forks.
- The fork firmware base `1305b78c` is two firmware-only commits behind the
  panda commit openpilot master pinned before this branch (`f38f504f`:
  register checks and fault telemetry for the H7).
- The `import libusb` in `selfdrive/pandad/SConscript` was only built in
  the openpilot CI environment (which installs all extras). It was not
  built inside a comma device image.
- `selfdrive/pandad/tests/test_pandad_spi.py` still asserts tres/cuatro;
  it only runs on comma hardware and was left alone.
- The openpilot CI could not be run on the `kriptomad/openpilot` fork
  itself (GitHub does not run workflows on that fork), so the run linked
  in STATUS.md was done on a snapshot of the same tree pushed to this
  repository (branches `ci/openpilot-base` and `ci/openpilot-revive-f4`).

## How to use

```
git clone -b revive-f4 --recurse-submodules https://github.com/kriptomad/openpilot.git
```

The `panda` submodule already points to the firmware fork. Build openpilot
as usual (`scons`), which also builds `panda/board/obj/panda.bin.signed`
for the F4. `pandad` flashes a connected black panda from the PC when its
firmware does not match the built one.

Flashing a black panda by hand (DFU, bootstub, signed firmware) is
described step by step in
[flash-black-panda-city-g7.md](https://github.com/kriptomad/openpilot-honda-city-brasil/blob/main/docs/flashing/flash-black-panda-city-g7.md)
(EN + pt-BR).

Submodules of this repository:

- `panda`: `kriptomad/panda` branch `revive-f4`
- `openpilot`: `kriptomad/openpilot` branch `revive-f4`

## Related projects

- [openpilot-honda-city-brasil](https://github.com/kriptomad/openpilot-honda-city-brasil):
  Honda City G7 (Brazil) port, the reason this work exists. Its
  `hardware/research/pandarevive-scope.md` is the detailed scope and
  evidence document, and `firmware/` holds the built binaries.
- Hybrid Panda: a new panda-compatible board (STM32H725, LQFP144) designed
  in the same repository. pandarevive is the software path for people who
  already own a black panda; the Hybrid Panda is the hardware path for
  people who do not.

## License

MIT, like upstream panda and openpilot. The restored STM32F4 sources are
commaai's code taken from the panda history before `1ce986f7`.

## Author

Bruno Costa ([kriptomad](https://github.com/kriptomad)), 2026.
