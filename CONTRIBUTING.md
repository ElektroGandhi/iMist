# Contributing

Thanks for helping! Three kinds of contributions are especially welcome.

## 1. Bug reports

Open the panel → *Device and diagnostics* → **Copy diagnostics** (or download diagnostics from the device page)
and attach it to a [bug report](https://github.com/ElektroGandhi/iMist/issues/new?template=bug_report.yml).
The Bluetooth address is shortened automatically.

## 2. Other diffusers

If your diffuser is not recognized, please open a
[device report](https://github.com/ElektroGandhi/iMist/issues/new?template=device_report.yml) with:

- a photo of the device,
- its Bluetooth name and advertised service UUIDs (e.g. from nRF Connect),
- the output of `python examples/control.py` while you press the buttons on the device.

The method that worked for the iMist is described in [docs/PROTOCOL.md](docs/PROTOCOL.md):
read the GATT table, listen while pressing buttons, then replay only what the device reported.

## 3. Code and translations

```bash
pip install pytest
pytest -q
```

The tests cover the protocol and the schedule rules and run without Home Assistant. CI additionally runs
`hassfest` and the HACS validation.

- Keep `protocol.py` and `schedule.py` free of Home Assistant imports so they stay testable.
- New user-facing text goes into `strings.json`, `translations/*.json` and the `TEXT` table in
  `frontend/imist-panel.js`.
- The panel has no build step and no dependencies – please keep it that way.
- Touch targets in the panel are at least 44 px; check new UI at 375 px width, light and dark.
