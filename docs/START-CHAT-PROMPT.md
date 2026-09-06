# Starter prompt — Deoro Wallet (paste into a new chat)

Copy everything inside the fence below.

````
You are starting Deoro's Apple Wallet fidelity card from the Exponential plan. Do not re-litigate the product. Fetch the plan, then implement tickets in dependency order, starting with Ticket 1.

## Goal

Deoro (coffee shop) issues one Apple Wallet store card per member: stamps, member serial, counter-scannable QR. Demoable before any Apple Developer account. Signed `.pkpass` only after certificates exist.

## Exponential (source of truth)

Auth if needed:

```bash
export PATH="$HOME/.local/bin:$PATH"
exponential auth status
# if not authenticated:
# exponential auth login --token "$expo_jwt" --api-url https://www.exponential.im
exponential workspaces set-default personal-cmgwt550
```

Then fetch, in this order:

```bash
exponential features get cmtq5xa1y0003ld04dqo5q57s --json
exponential pages get cmtq5yijp000jld04o48r80as
exponential tickets get cmtq5zelm0013ld0414fgdea9 --json
exponential tickets list --product cmtq5x0ly0001ld04vqazjhcy --feature cmtq5xa1y0003ld04dqo5q57s --json
```

| Thing | Value |
|---|---|
| Workspace | Mente Maestra Studio · `personal-cmgwt550` · `cmjzyn1b3001lrze706vmtgku` |
| Product | Deoro · `deoro` · `cmtq5x0ly0001ld04vqazjhcy` |
| Feature | Apple Wallet Fidelity Card · `cmtq5xa1y0003ld04dqo5q57s` |
| PRD page | `cmtq5yijp000jld04o48r80as` |
| App | https://www.exponential.im/w/personal-cmgwt550/products/deoro |

If `/start-ticket` / `/ship-ticket` (positonic/skills `to-expo` siblings) are installed, use them. Otherwise: `exponential tickets update --id <cuid> --status IN_PROGRESS`, work on the ticket's `branchName`, then move to `QA` only after a PR exists.

## Test seam

One seam: the PassKit package + its install URL. Before certificates, the HTML preview of the same `pass.json` is that seam. Do not invent a second card UI that diverges from PassKit fields.

## Tickets (dependency order)

| # | CUID | Title | Type | Status | HITL/AFK | Blocked by | Branch |
|---|------|-------|------|--------|----------|------------|--------|
| 1 | `cmtq5zelm0013ld0414fgdea9` | Render the Deoro Wallet face from pass source | FEATURE | READY_TO_PLAN | AFK | — | `deoro-1-render-deoro-wallet-face-from-pass-source` |
| 2 | `cmtq5zgye0017ld049pl0riwk` | Scan the Deoro member QR at the counter | FEATURE | READY_TO_PLAN | AFK | #1 | `deoro-2-scan-deoro-member-qr-at-the-counter` |
| 3 | `cmtq5zilb001bld04o3lfx8sb` | Put a throwaway Deoro pass on a real iPhone | FEATURE | NEEDS_REFINEMENT | HITL | #1 | `deoro-3-throwaway-deoro-pass-on-real-iphone` |
| 4 | `cmtq5zk31001fld0420ddyqcx` | Issue a downloadable pkpass from an install URL | FEATURE | READY_TO_PLAN | AFK | #1 | `deoro-4-issue-downloadable-pkpass-install-url` |
| 5 | `cmtq5zlkg001jld04nxmpelo8` | Wire Apple Pass Type ID signing so Wallet accepts the pass | CHORE | NEEDS_REFINEMENT | HITL | #4 | `deoro-5-wire-apple-pass-type-id-signing` |
| 6 | `cmtq5zn2p001nld042dskxory` | Update stamps on an already-installed pass | FEATURE | READY_TO_PLAN | AFK | #5, #2 | `deoro-6-update-stamps-on-installed-pass` |

Links: https://www.exponential.im/w/personal-cmgwt550/products/deoro/tickets/1 (same path, tickets/2 … /6).

## How to work

0. If a git repo exists: `git checkout <featureBase>` (default `main`) `&& git pull`. Never start from an unmerged feature branch.
1. Fetch the ticket: `exponential tickets get <cuid> --json`. Read body + acceptance criteria. Transition to `IN_PROGRESS`.
2. Implement that one vertical slice end-to-end. Verify acceptance locally.
3. Commit on the ticket `branchName`. Open/update a PR. Set ticket to `QA` and `prUrl`.
4. **Merge to `main` before starting any ticket that depends on it.** `QA` is not enough.
5. Independent tickets with no shared open blocker may proceed in parallel off `main`.
6. **Stop on HITL / `NEEDS_REFINEMENT`.** Surface the open question. Do not guess Apple Team IDs, do not pick a third-party signer for the user, do not commit certs.
7. If the ticket contradicts the code, comment with `exponential tickets comment add --id <cuid> -m "<question>"` and pause.

Do not create a stack of PRs. Either merge-between tickets, or keep a tightly-coupled chain on ONE branch / ONE PR.

## Already on disk (do not start from zero)

Scaffold lives at `deoro-wallet/` (or `/agent/deoro-wallet` in the previous cloud session):

- `pass/Deoro Loyalty.pass/pass.json` — `storeCard`, serial `DEORO-10001`, stamps `7 / 10`, `passTypeIdentifier` `pass.com.deoro.loyalty`, `teamIdentifier` `PENDING`
- icon / logo / strip PNGs at 1x, 2x, 3x (`python3 scripts/generate-pass-images.py`)
- `preview/index.html` — Wallet-face mock that **fetches** `pass.json` (changing JSON must change the preview)
- IDs: `.exponential/ids.json`
- PRD copy: `docs/PRD-apple-wallet-fidelity.md`

Demo without Apple:

```bash
python3 scripts/generate-pass-images.py
python3 -m http.server 4173
# open http://localhost:4173/preview/
```

Finish Ticket 1 against its acceptance criteria before starting Ticket 2. Ticket 1 is the source of truth; later signing wraps these files.

## Contracts (do not change without a ticket comment)

- Pass style: `storeCard`
- Pass Type ID: `pass.com.deoro.loyalty`
- Demo member: `DEORO-10001` (QR payload = that serial)
- Colors: espresso `rgb(42, 28, 20)`, cream `rgb(245, 230, 196)`, gold `rgb(212, 175, 106)`
- Stamp rule (V1 default): one stamp per visit; 10 stamps = free regular coffee
- No native iOS/Android app, no NFC, no Google Wallet in this feature
- No third-party-signed pass as the production issuer
- Never commit Pass Type ID certs or private keys

## First actions this chat

1. Confirm Exponential auth + fetch feature + Ticket 1.
2. Put Ticket 1 `IN_PROGRESS` and check out `deoro-1-render-deoro-wallet-face-from-pass-source`.
3. Close Ticket 1 acceptance: pass.json + images + preview that flips to back fields, QR encodes `DEORO-10001`, preview updates when `pass.json` changes.
4. Report what is demoable and what is still open. Then wait for merge before Ticket 2, unless the user says continue in-place.
````
