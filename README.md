<<<<<<< HEAD
# Deoro Wallet

Apple Wallet fidelity card for Deoro (coffee shop).

This `main` branch only receives merged ticket PRs.

- One branch per Exponential ticket (`deoro-N-…`)
- Branch from latest `main`
- Merge before starting a ticket that depends on it
- Never commit Pass Type ID certs or private keys

Product: https://www.exponential.im/w/personal-cmgwt550/products/deoro
=======
# Deoro Apple Wallet fidelity card

Greenfield PassKit source for Deoro. Tracked in Exponential product `deoro` (Mente Maestra Studio).

Ticket 1 is the source of truth: `pass/Deoro Loyalty.pass/` plus a browser preview of that same `pass.json`. Later tickets wrap these files. They do not invent a second card UI.

## Demo without an Apple Developer account

```bash
python3 scripts/generate-pass-images.py
python3 scripts/check-pass-source.py
python3 -m http.server 4173
```

Open http://localhost:4173/preview/

The preview fetches `pass/Deoro Loyalty.pass/pass.json` and draws the Wallet face (front + flip-side back fields). The QR payload is the member serial (`DEORO-10001`). Change stamps or the member name in `pass.json`, then refresh.

This is not a signed `.pkpass`. Wallet on a phone will refuse it until ticket 5 wires certificates. Do not commit Pass Type ID certs or private keys.

## Contracts

- Pass style: `storeCard`
- Pass Type ID: `pass.com.deoro.loyalty`
- Demo member: `DEORO-10001` (QR payload = that serial)
- Colors: espresso `rgb(42, 28, 20)`, cream `rgb(245, 230, 196)`, gold `rgb(212, 175, 106)`
- Stamp rule (V1): one stamp per visit; 10 stamps = free regular coffee

## Git flow

Repo: [blessedux/deoro-wallet](https://github.com/blessedux/deoro-wallet)

- `main` is the only integration branch. Do not commit ticket work straight to `main`.
- One git branch per Exponential ticket. Use the ticket `branchName` (`deoro-N-…`).
- Branch from the latest `main`. Merge that ticket to `main` before starting anything that depends on it.
- One open PR per ticket. No stacked PRs.
- After the PR exists, set the Exponential ticket to `QA` and `prUrl`.
- Never commit Pass Type ID certificates or private keys.

| Ticket | Branch |
|---|---|
| 1 Render Wallet face | `deoro-1-render-deoro-wallet-face-from-pass-source` |
| 2 Counter QR scan | `deoro-2-scan-deoro-member-qr-at-the-counter` |
| 3 Throwaway iPhone pass (HITL) | `deoro-3-throwaway-deoro-pass-on-real-iphone` |
| 4 Install URL / pkpass | `deoro-4-issue-downloadable-pkpass-install-url` |
| 5 Apple signing (HITL) | `deoro-5-wire-apple-pass-type-id-signing` |
| 6 Live stamp updates | `deoro-6-update-stamps-on-installed-pass` |

## Exponential

- Workspace: Mente Maestra Studio (`personal-cmgwt550`)
- Product: [Deoro](https://www.exponential.im/w/personal-cmgwt550/products/deoro)
- Feature: Apple Wallet Fidelity Card (`cmtq5xa1y0003ld04dqo5q57s`)
- Ticket 1: [Render the Deoro Wallet face from pass source](https://www.exponential.im/w/personal-cmgwt550/products/deoro/tickets/1)
>>>>>>> 28c4324 (Render Deoro Wallet face from pass.json source.)
