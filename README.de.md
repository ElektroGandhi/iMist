<p align="center">
  <img src="docs/images/logo.svg" width="112" alt="iMist-Logo">
</p>

<h1 align="center">iMist für Home Assistant</h1>

<p align="center">
  <b>Die App ist weg. Der Diffusor nicht.</b><br>
  Lokale Bluetooth-Steuerung ohne Cloud für den iMist-Aromadiffusor – mit echtem Zustand, Zeitplänen,<br>
  Ausschalt-Timer und einer schönen Seite in der Seitenleiste.
</p>

<p align="center"><a href="README.md">English</a></p>

<p align="center">
  <img src="docs/images/hero.png" alt="Die iMist-Seite auf drei Telefonen" width="100%">
</p>

## Warum es das gibt

Der iMist-Diffusor ist ein kleiner weißer, gerillter Zylinder mit zwei Tasten, **LIGHT** und **MIST**, und Bluetooth.
Seine iPhone-App ist aus dem App Store verschwunden – und damit jede Möglichkeit, ihn vom Telefon zu steuern.
Die Hardware funktioniert einwandfrei.

Diese Integration holt ihn zurück: in Home Assistant, ohne Cloud, Konto oder Hersteller-App. Das Protokoll
wurde am Gerät selbst abgelesen – Tasten drücken, Bluetooth-Meldungen mitlesen. Die ganze Geschichte samt
einem lehrreichen Irrweg steht in [docs/PROTOCOL.md](docs/PROTOCOL.md) (Englisch).

## Was sie kann

- 🎨 **Licht** – alle acht Farben des Geräts und aus. Eine beliebige Farbe in HA wird auf die nächste Gerätefarbe gerundet.
- 🌫️ **Nebel** – aus, Dauer oder Intervall.
- ⚡ **Echter Zustand statt Annahme** – das Gerät meldet sich zehnmal pro Sekunde. Wer am Gerät drückt, sieht es sofort in HA.
- 🗓️ **Zeitpläne** – je Wochentag mit Ein- und Ausschaltzeit, Farbe und Nebel; auch über Mitternacht.
- ⏲️ **Ausschalt-Timer** – 30 Min., 1, 2 oder 4 Std. Das Gerät hat keinen eigenen Timer; das übernimmt HA.
- 🖥️ **Optionale Seite in der Seitenleiste** – große Schaltflächen, telefontauglich, folgt Theme und Sprache von HA.
- 🔍 **Automatische Erkennung**, 🩺 **Diagnose** zum Kopieren, 🔁 **verbindet sich selbst neu**; Zeitpläne und Timer überstehen Neustarts.

## Läuft mein Diffusor?

Sehr wahrscheinlich, wenn alles zutrifft: weißer, gerillter Zylinder mit **LIGHT** und **MIST**; Bluetooth-Name
`AromaDiffuser`; Dienst `fff0` mit Kennwert `fff4` (lesen, schreiben, benachrichtigen).

Zum Prüfen mit **nRF Connect**: verbinden, Benachrichtigungen auf `fff4` einschalten, am Gerät **LIGHT** drücken –
es erscheinen drei Bytes wie `aa 00 18`.

> [!NOTE]
> Diffusoren, die zur Android-App **„Aroma Diffuser“** (`com.spark.imist.aroma`) gehören, sprechen ein **anderes**
> Protokoll (Dienst `f501`) und werden noch nicht unterstützt. Die Integration erfasst sie auch nicht versehentlich.

## Installation

**HACS:** HACS → ⋮ → **Benutzerdefinierte Repositories** → `https://github.com/ElektroGandhi/iMist`, Kategorie
**Integration** → **iMist Aroma Diffuser** installieren → HA neu starten.

**Von Hand:** `custom_components/imist` nach `config/custom_components/` kopieren, HA neu starten.

## Einrichten

1. HA braucht Bluetooth (eigener Adapter oder ESPHome-Bluetooth-Proxy).
2. Diffusor einschalten – er erscheint unter **Einstellungen → Geräte & Dienste → Entdeckt**.
3. Optional: **Konfigurieren** → *Seite „Diffusor“ in der Seitenleiste zeigen*.

## Entitäten

| Entität | Wirkung |
|---|---|
| `light.…_licht` | an/aus, 8 Farben als Effekte (`white`, `red`, `yellow`, `green`, `light_blue`, `dark_blue`, `pink`, `warm_white`) |
| `select.…_nebel` | `off` (Aus), `continuous` (Dauer), `interval` (Intervall) |

**Keine Helligkeit, kein Wasserstand** – beides gibt das Protokoll nicht her (Helligkeit am Gerät geprüft).

## Protokoll in 30 Sekunden

Alles läuft über `fff4`. Befehl und Zustandsmeldung sehen gleich aus: **`aa MM LL`** –
Nebel `00` aus · `20` Dauer · `40` Intervall; Licht `00` aus · `08` weiß · `18` rot · `30` gelb · `20` grün ·
`40` hellblau · `28` dunkelblau · `38` pink · `48` warmweiß. Ohne Prüfsumme, ohne Kopplung.

## Fehlersuche

- **Nicht erkannt:** Gerät an, kein Telefon verbunden; in HA unter **Einstellungen → Bluetooth** nach `AromaDiffuser` sehen.
- **Zeitweise nicht verfügbar:** Funkreichweite. Ab etwa −75 dBm reißt die Verbindung ab – näher heranstellen oder einen ESPHome-Bluetooth-Proxy in die Nähe.
- **„Service fff0 missing“ im Protokoll:** anderes Protokoll, siehe oben.
- **Sonst:** Seite → *Gerät und Diagnose* → **Diagnose kopieren** und an ein Issue hängen.

## Hinweis

Unabhängiges Gemeinschaftsprojekt, nicht verbunden mit dem Hersteller des Diffusors oder einer App.
Alle Marken gehören ihren Inhabern. Lizenz: [MIT](LICENSE).
