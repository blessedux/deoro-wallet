## Problem

Deoro is a coffee shop that wants a fidelity (loyalty) card that lives in Apple Wallet — stamps, member number, and a counter-scannable code — without asking customers to download a Deoro app. There is no Apple Developer account yet, so a signed `.pkpass` cannot be added to a real iPhone today. The shop still needs a demoable card and a path that becomes a real Wallet pass the moment certificates exist.

## Goals

- A Deoro-branded store card the team can show: gold-on-espresso face, stamp count, member number, QR.
- The same QR can be scanned at the counter and resolves to one member.
- The PassKit source (`pass.json` + images) is the single source of truth; signing is a later wrap, not a redesign.
- After Apple enrollment, a member can tap an install URL and add a Deoro-signed pass to Wallet.
- After V2, recording a stamp updates the pass already in Wallet (same `passTypeIdentifier` + `serialNumber`).

## Non-goals

- A native iOS or Android Deoro app.
- NFC / Apple VAS (extra entitlement and hardware).
- Google Wallet (parallel format; later product if Android regulars need it).
- Live lock-screen geofence notifications in V1.
- Production customer PII, payments, or a full POS.
- Shipping customer-facing passes signed by a third-party builder (demo-only).

## Solution

Deoro issues one Apple Wallet **store card** per member. The card shows stamps (`7 / 10`), a member serial, and a QR whose payload is that serial. Staff scan the QR; the system looks up the member.

Until Deoro has a Pass Type ID certificate, we demo with:

1. A browser Wallet-face preview rendered from the same `pass.json`.
2. A counter scan of that QR.
3. An optional throwaway pass signed by a third-party tool, for a pitch on a real phone.

When certificates exist, the same source is packaged, signed, and served as `application/vnd.apple.pkpass` from an install URL. Stamp changes reissue or update that serial in place.

**Test seam:** the distributable pass package plus its install URL (and, before signing, the HTML preview of that same `pass.json`). One seam. Do not add a second abstraction for “card UI” that diverges from PassKit fields.

## Requirements

Canonical, checkable copies of these live as requirement rows on the feature.

- When a visitor opens the Deoro Wallet preview, the system shall render a store-card face with Deoro branding, stamp count, member number, and a QR encoding the member serial.
- When the QR on the preview or pass is scanned at the counter, the system shall display the matching member id and current stamp count.
- The system shall keep a PassKit source package (`pass.json` + required PNGs) that a later signing step can wrap without rewriting field layout.
- While no Apple Developer certificate is available, the system shall still allow a visual and barcode demo without requiring a signed `.pkpass`.
- When a member opens the Deoro install URL on iOS and signing credentials are present, the system shall serve a signed `.pkpass` with `Content-Type: application/vnd.apple.pkpass`.
- If the signing certificate is missing, the system shall refuse to emit a production `.pkpass` and shall report a clear error.
- The pass shall use style `storeCard`, `passTypeIdentifier` `pass.com.deoro.loyalty`, and a unique `serialNumber` per member.
- When a barista records a stamp for a member who already has the pass, the system shall update that pass in place so the visible stamp count increments.
- If a member reaches 10 stamps, the system shall present a redeemable free-drink state on the pass.

## Rollout

- **V1 — Demo without Apple account:** pass source, browser Wallet face, counter QR scan, optional throwaway third-party-signed phone demo.
- **V2 — Deoro-signed Wallet pass:** package builder, install URL, Pass Type ID + certificates, add-to-Wallet on a real device.
- **V3 — Live stamps:** in-place update of an installed pass when the counter records a stamp or a redeem.

## Open questions

- Exact Deoro logo, strip photography, and final gold/espresso hex values (design owner: Deoro).
- Stamp rule: one stamp per visit vs per drink (product; default in V1 is one per visit).
- Hosting for the install URL (Vercel vs existing Mentemaestra infra).
- Whether V3 uses full PassKit web service + APNs or a simpler “email a replacement pass with the same serial.”
