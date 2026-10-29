# Changelog

## 0.4.0 – first public release

- English code, English and German translations; light colors and mist modes are translatable keys
  (`dark_blue`, `interval`, …). Schedules stored by earlier versions are migrated automatically.
- Sidebar panel follows the Home Assistant language (English, German).
- HACS support (`hacs.json`), CI with hassfest, HACS validation and tests.

## 0.3.1

- Fix: the panel status lost the entity IDs while the device was disconnected.

## 0.3.0

- Optional sidebar panel: control, sleep timer, weekly schedules, diagnostics.
- Sleep timer and schedules run in Home Assistant and survive restarts.
- The integration loads even when the diffuser is out of range.
- Discovery requires service `fff0`, so diffusers with the `f501` protocol are not picked up by mistake.

## 0.2.0

- Rewritten on the protocol measured on the device (`aa MM LL` on `fff4`). Real state via notifications.

## 0.1.0

- First attempt, based on the Android app “Aroma Diffuser”. Did not work: that app belongs to a different
  product line (service `f501`). See [docs/PROTOCOL.md](docs/PROTOCOL.md).
