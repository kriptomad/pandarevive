# pandarevive

Trazendo a **black panda** da comma (STM32F413) de volta ao master atual
do [panda](https://github.com/commaai/panda) e do
[openpilot](https://github.com/commaai/openpilot).

[English](README.md)

## Situacao em um paragrafo

Existem duas branches em forks e as duas compilam: o firmware do panda em
[`kriptomad/panda` branch `revive-f4`](https://github.com/kriptomad/panda/tree/revive-f4)
e o lado do openpilot em
[`kriptomad/openpilot` branch `revive-f4`](https://github.com/kriptomad/openpilot/tree/revive-f4).
O firmware passa no CI do panda (build, MISRA, testes unitarios) e a
branch do openpilot roda no CI do openpilot em runners do GitHub.
**Nada foi executado em uma black panda real.** Nenhum pull request foi
aberto no upstream. Os hashes exatos e os links do CI estao em
[STATUS.md](STATUS.md).

## Por que

A commaai removeu a familia STM32F4 (white, grey, black panda e as placas
uno/dos) do firmware do panda em 2025:

- `3d272335` (2025-07-19): apagou `board/boards/black.h` e `white.h`.
- `1ce986f7` "bye bye f4" (2025-08-26): apagou `board/stm32f4/*`, o
  driver bxCAN, o alvo de build F4 e o suporte Python a `McuType.F4` /
  `HW_TYPE_BLACK`.

No openpilot, `96d1b876b` (2026-02-14) removeu o transporte libusb do
`pandad` (ficou so SPI) e `9aca13cf2` fixou o tipo de MCU em H7. A black
panda fala apenas USB e nao tem SPI escravo, entao o master atual do
openpilot nao a enxerga nem com firmware funcionando.

A black panda continua sendo um dispositivo util: tres barramentos
CAN 2.0 (dois pelos transceivers internos mais o barramento escolhido pelo
harness), USB e o mesmo codigo de safety (`opendbc/safety`) que a
red/tres panda roda. Para carros que nao precisam de CAN-FD (por exemplo
o Honda City G7 do projeto
[openpilot-honda-city-brasil](https://github.com/kriptomad/openpilot-honda-city-brasil))
e o caminho mais barato para rodar o openpilot atual em um PC.

## O que esta feito

### Firmware: `kriptomad/panda` branch `revive-f4`

Base: `commaai/panda` master `1305b78c` (2026-10-25). Commits, do mais
antigo para o mais novo:

| Commit | Assunto |
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

O que foi restaurado: `board/stm32f4/*` (clock, perifericos, linker
scripts, startup, bootstub, USB OTG FS, ADC, timers, entrada em DFU),
`board/boards/black.h`, o driver bxCAN adaptado a interface atual de
`can_common`, o alvo SCons `panda` ao lado de `panda_h7`, `McuType.F4`,
`HW_TYPE_BLACK` (hw type 3) e o serial DFU do F4 na biblioteca Python.
Builds debug e release compilam, cppcheck/MISRA sem achados nas variantes
F4 e H7, e o `test.sh` passa no CI do fork (ver no STATUS.md o run que
ainda falha em um passo pip/Python 3.14 pre-existente, sem relacao com a
branch).

### Lado do host: `kriptomad/openpilot` branch `revive-f4`

Base: `commaai/openpilot` master `0152aab4` (2026-10-25). Commits, do
mais antigo para o mais novo:

| Commit | Assunto |
|---|---|
| `45b12a352` | panda: point submodule to the revive-f4 fork |
| `92b862b5e` | pandad: restore USB comms for external pandas |
| `c1e41b44b` | pandad: flash an external panda through its own bootloader request |
| `941cab937` | pandad: cover the black panda in the host side tests |

Mapa do que o upstream removeu e do que a branch restaura:

| Mudanca no upstream | Restaurado em `revive-f4` |
|---|---|
| `96d1b876b` apagou `panda_comms.cc` (`PandaUsbHandle`), a classe base `PandaCommsHandle` e o libusb do build do pandad | `panda_comms.h` tem a classe base de novo, `usb.cc` e o antigo `panda_comms.cc`, `Panda` tenta USB primeiro e cai para SPI, `Panda::list()` junta os seriais USB e SPI; o libusb vem do pacote `comma-deps-libusb` que o cabana ja usa |
| `9aca13cf2` fixou `McuType.H7` no `pandad.py` | A biblioteca panda do fork resolve o tipo de MCU a partir do tipo de hardware; o `pandad.py` nao precisa saber |
| `d3f0aab96` reescreveu o loop de flash em torno das linhas de reset/BOOT0 do SoM (`HARDWARE.recover_internal_panda()`) | Em um PC (`COMMA_HARDWARE` falso) o `flash_panda()` pede ao firmware para entrar no bootstub e depois no bootloader da ST antes do `PandaDFU.recover()`; o caminho do dispositivo comma nao muda |
| `test_pandad_canprotocol.cc` so exercitava frames de dos e red panda | `blackPanda` entrou no loop de tipos de hardware; novo `test_pandad_flash.py` cobre os caminhos de flash externo e interno com mocks |
| `.gitmodules` apontava `panda` para `commaai/panda` | Aponta para `kriptomad/panda` branch `revive-f4` em `a8225ef3` |

Nao foi preciso mudar nada no `opendbc` (o codigo de safety e
compartilhado), na camada de hardware (`common/hardware`: uma black panda
em um PC e um dispositivo USB externo, `HardwarePc` serve como esta), no
cereal (`blackPanda @3` nunca saiu de `PandaState.hwType`) nem na
configuracao de processos.

## O que NAO esta feito

- Nada foi executado em hardware. Enumeracao USB, timing do bxCAN,
  deteccao de harness, entrada em DFU, self test do F4 e regioes da MPU
  estao todos sem exercicio. A lista completa esta na secao 6 do
  [documento de escopo](https://github.com/kriptomad/openpilot-honda-city-brasil/blob/main/hardware/research/pandarevive-scope.md).
- Nenhum pull request no upstream. A commaai removeu o F4 de proposito;
  este trabalho fica em forks.
- A base do firmware `1305b78c` esta dois commits (so firmware) atras do
  commit do panda que o master do openpilot fixava antes desta branch
  (`f38f504f`: checagem de registradores e telemetria de falhas do H7).
- O `import libusb` em `selfdrive/pandad/SConscript` so foi compilado no
  ambiente do CI do openpilot (que instala todos os extras). Nao foi
  compilado dentro de uma imagem de dispositivo comma.
- `selfdrive/pandad/tests/test_pandad_spi.py` ainda exige tres/cuatro; so
  roda em hardware comma e foi deixado como esta.
- O CI do openpilot nao pode rodar no proprio fork `kriptomad/openpilot`
  (o GitHub nao executa workflows nesse fork), entao o run ligado no
  STATUS.md foi feito em um snapshot da mesma arvore enviado para este
  repositorio (branches `ci/openpilot-base` e `ci/openpilot-revive-f4`).

## Como usar

```
git clone -b revive-f4 --recurse-submodules https://github.com/kriptomad/openpilot.git
```

O submodulo `panda` ja aponta para o fork do firmware. Compile o openpilot
como de costume (`scons`); isso tambem gera
`panda/board/obj/panda.bin.signed` para o F4. O `pandad` grava uma black
panda conectada ao PC quando o firmware dela nao bate com o compilado.

Gravar uma black panda manualmente (DFU, bootstub, firmware assinado) esta
descrito passo a passo em
[flash-black-panda-city-g7.md](https://github.com/kriptomad/openpilot-honda-city-brasil/blob/main/docs/flashing/flash-black-panda-city-g7.md)
(EN + pt-BR).

Submodulos deste repositorio:

- `panda`: `kriptomad/panda` branch `revive-f4`
- `openpilot`: `kriptomad/openpilot` branch `revive-f4`

## Projetos relacionados

- [openpilot-honda-city-brasil](https://github.com/kriptomad/openpilot-honda-city-brasil):
  port do Honda City G7 (Brasil), a razao deste trabalho. O arquivo
  `hardware/research/pandarevive-scope.md` e o documento detalhado de
  escopo e evidencias, e `firmware/` guarda os binarios compilados.
- Hybrid Panda: uma nova placa compativel com o panda (STM32H725,
  LQFP144) projetada no mesmo repositorio. O pandarevive e o caminho de
  software para quem ja tem uma black panda; a Hybrid Panda e o caminho
  de hardware para quem nao tem.

## Licenca

MIT, como o panda e o openpilot upstream. As fontes STM32F4 restauradas
sao codigo da commaai retirado do historico do panda anterior a
`1ce986f7`.

## Autor

Bruno Costa ([kriptomad](https://github.com/kriptomad)), 2026.
