# ArcScaler 1.1.0 implementation record

Implemented the robustness and UI/UX plans in the existing native desktop app.

## Installation and recovery

- Durable manifest stages: backed up, deploying, verifying, complete, and restoring.
- Startup and profile health checks distinguish installed, modified, incomplete, unverified, and recovery-required states.
- Original backups survive interrupted operations; updates are blocked until recovery completes.
- Changed managed files are protected from silent replacement. User-confirmed recovery preserves copies and a path/hash index under `.optiscaler_backup/preserved`.
- Verification covers every deployment directory. SR+FG intent is recorded consistently in profiles and backup metadata.

## Detection and background work

- Evidence records include filenames, paths, origin and confidence. ArcScaler-deployed DLLs are not presented as native feature evidence.
- Generic FidelityFX/FSR DLLs no longer confirm FG support by themselves.
- One recommendation result supplies display text, applied settings, and its installation plan.
- Bounded workers support cooperative cancellation and suppress obsolete results. Scan exceptions become actionable UI errors.
- Downloads cancel before commit while retaining the previously installed package.

## Interface

- Suggested preset precedes SR and FG controls.
- Draft changes are distinguished from installed settings; the primary action changes between Install, Update installation and Up to date.
- Technical settings and detailed file evidence expand on demand. Each game retains panel and scroll state.
- The primary action bar contains Install/Update and Launch. More contains restore, force injection, diagnostics, rescanning, verification and folder access.
- Status-only game-list updates reuse widgets. Selection uses a short highlight transition, with a reduced-motion preference.
- Glass-inspired controls have visible keyboard focus and Enter/Space activation.
- Compact navigation and adjustable 100–200% sizing support narrower layouts.
- Diagnostic reports are previewed before local export and redact personal paths by default. Reports are not transmitted.

## Validation

- 102 tests passed, including real subprocess exits at every install stage, conflict preservation, secondary-directory verification, corrupt backups, combined SR+FG, stale callbacks, download cancellation, panel restoration, draft status and 100/125/150/200% control layout.
- Initial visual inspection identified excessive vertical space; the SR layout was compacted afterward and checked through real Tk layout tests. Desktop interaction was stopped when requested.
- `audit/release_gate.py` provides a repeatable regression → build → isolated packaged smoke-test workflow.
- Graphify's AST-only update succeeded outside the filesystem sandbox.
- Packaged build and smoke-test results are recorded separately in `arcscaler-build-result.json` and `packaged-smoke-result.json`.

Tests use fixture games and isolated storage. In-game feature activation remains a user/game-specific check in the overlay.
