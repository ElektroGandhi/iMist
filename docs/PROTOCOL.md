# The iMist Bluetooth protocol

This is how the diffuser talks, and how that was found out. Everything below was **measured on a real
device** in October 2026 – nothing is guessed.

## TL;DR

| | |
|---|---|
| Advertised name | `AromaDiffuser` |
| Service | `0000fff0-0000-1000-8000-00805f9b34fb` |
| Characteristic | `0000fff4-0000-1000-8000-00805f9b34fb` – read, write, notify |
| Command | write `aa MM LL` (with response) |
| State report | notification `aa MM LL`, about every 100 ms while connected |
| Pairing, checksum, handshake | none |

### Mist byte `MM`

| Byte | Mode | Seen as |
|---|---|---|
| `00` | off | |
| `20` | continuous | steady mist |
| `40` | interval | mist with pauses |

Pressing **MIST** on the device cycles `00 → 20 → 40 → 00`.

### Light byte `LL`

| Byte | Color |
|---|---|
| `00` | off |
| `08` | white |
| `18` | red |
| `30` | yellow |
| `20` | green |
| `40` | light blue |
| `28` | dark blue |
| `38` | pink |
| `48` | warm white |

Pressing **LIGHT** cycles through the colors in exactly this order, then off.

### Details worth knowing

- **Two reports can arrive glued together**: `aa 00 18 aa 00 30`. Parse in steps of three after each `aa`.
- **Reading** `fff4` returns 20 zero bytes. That is not a state – only notifications carry the state.
- **No brightness.** All color bytes are multiples of 8, so the low three bits looked like a brightness level.
  They are not: the device stores and echoes them (`aa 40 27`), but the light does not change.
  Tested by switching between `20` and `27` once per second while watching the device.
- **No timer and no water sensor** in the protocol. The integration implements the sleep timer and schedules in
  Home Assistant instead.
- The firmware is the unmodified **Texas Instruments CC254x example firmware**: the *Device Information* service
  contains placeholder strings (`"Serial Number"`, `"Model Number"`, …) and the PnP-ID says vendor `0x000D`
  (Texas Instruments). Do not expect anything useful there.

## How it was found

### Step 1 – the wrong turn

The original iPhone app had vanished, but an Android app called **“Aroma Diffuser”** (`com.spark.imist.aroma`,
versions 2.0 to 2.15) is still around and looked like the right one. Decompiling it gave a complete and very
plausible protocol: service `f501`, write `f502`, notify `f503`, a ten-byte mode frame starting with `0x12`,
timer values in minutes, an acknowledgement `0x91` and a water-level report `0x93`.

The first version of this integration was built on that. On the first connection the device answered:

```
Service 0000f501-… missing. Device offers: 180a, 1800, 1801, fff0
```

**None of the four app versions mentions `fff0` or `fff4` anywhere.** The app belongs to a different product
line that happens to use the same name. Lesson: an app that *looks* right proves nothing until the device
confirms it – check the GATT table first.

### Step 2 – listen before you talk

With the diffuser next to a laptop, the only thing done at first was subscribing to `fff4` and pressing the
buttons on the device. It reports its state about ten times per second:

```
 2.8– 45.2s  aa 00 08     ← start: white
45.3– 48.7s  aa 00 18     ← LIGHT pressed
48.7– 51.5s  aa 00 30     ← LIGHT pressed
…
79.5– 83.9s  aa 20 08     ← MIST pressed
86.6– 98.2s  aa 40 00     ← MIST pressed
```

The first byte never changed, the second followed **MIST**, the third followed **LIGHT**.

### Step 3 – only send what the device itself said

The first write was a state the device had already reported (`aa 00 18`: mist off, red). It switched the mist
off and reported exactly that state back. Then every color byte the device had reported was written once,
eight seconds each, while a person wrote down the color – that is where the color table comes from. The mist
modes were confirmed the same way (continuous vs. visible pauses).

Only then were unknown values tried (the brightness bits), with someone watching the device.

## Try it yourself

[`examples/control.py`](../examples/control.py) needs nothing but [bleak](https://github.com/hbldh/bleak):

```bash
pip install bleak
python examples/control.py                    # show the live state
python examples/control.py interval dark_blue # set mist and light
```

## Adding another diffuser

If your diffuser uses a different protocol, the same three steps work: read the GATT table, listen to
notifications while pressing buttons, then replay only what the device sent. Open an issue with the output of
`examples/control.py` and a photo – see [CONTRIBUTING.md](../CONTRIBUTING.md).
