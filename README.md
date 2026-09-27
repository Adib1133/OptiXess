# ArcScaler

A native Windows desktop manager for per-game OptiScaler and Intel XeSS configuration.

## Run

Launch **ArcScaler.exe**. The app stores profiles, downloaded releases, cached game icons and logs in `%LOCALAPPDATA%\ArcScaler`.

Existing `%LOCALAPPDATA%\OptiScalerXeSS` and `%APPDATA%\OptiScalerXeSS` data is copied on first launch. Existing ArcScaler records win conflicts; the conflicting originals remain in `migration-originals`, and legacy folders are never deleted. Super Resolution and Frame Generation can be enabled together.

For development, install `requirements.txt` and run `python main.py`. Set `ARCSCALER_DATA_DIR` to isolate development or tests. The legacy environment variable is accepted for migration compatibility.

## Library

Add an executable, Windows shortcut or game folder, or scan Steam and Epic libraries. Select a game in the middle rail to edit it. Icons are extracted from the real executable in background workers and cached on disk; games without resources receive a name-based placeholder.

- **Super Resolution** and **Frame Generation** are independent. Both may be off, which disables installation. Inactive options are disabled, including keyboard traversal.
- **Suggested preset** explains the proposed settings; applying it changes the saved draft. Only installation changes game files. **Changes not installed**, **Update installation**, and **Up to date** distinguish the draft from the installed configuration.
- **Advanced settings** expands install mode, release, proxy, network model and overrides. Hardware selection is automatic: the XeSS runtime chooses XMX or DP4a; the network control selects a model variant.
- **Install to game** first shows the complete plan and reasons. Confirmation applies that plan only if the file set, settings and package hashes still match.
- **Force inject**, under **More**, requires confirmation and a separate risk acknowledgement. It cannot bypass malformed files, path containment, running-game protection, recovery conflicts or the DirectX 12 requirement for Frame Generation.
- **Restore original files** restores original bytes and removes files ArcScaler created. Changed files are blocked from replacement until the user chooses to preserve separate copies. Preserved copies and an index remain in `.optiscaler_backup/preserved`. Recovery uses the original snapshot across updates.
- **Launch** observes startup failures; verified installed files are not proof of runtime activation. Check the game's overlay.
- **More** contains folder access, rescanning, verification, restoration, diagnostics, force injection and library removal.
- **Runtime evidence** distinguishes game/unmanaged files, ArcScaler files and original backups. Generic FSR/FidelityFX files indicate uncertain FG support, not confirmed FG support.
- Per-game expansion and scroll state are retained. Narrow windows use compact navigation. **App settings** provides 100–200% interface sizing and reduced motion.

Installation stages are journaled before deployment and verification. Startup identifies interrupted operations, missing files, externally modified files and damaged backups. Choose recovery before installing again; incomplete recovery retains the backup.

## Automatic decisions

Auto mode resolves shipping executables, inspects PE imports and local graphics modules, detects native upscaler/FG runtimes, and selects a collision-free proxy. Local compatibility entries take precedence, followed by imported utility DLLs and generic fallbacks. Existing proxies are preserved; load success still requires verification in the game. Unknown or ambiguous APIs do not enable FG. Anti-cheat detection blocks Auto mode.

`assets/compatibility.json` contains local entries keyed by Steam appid and executable name. Use **App settings → Edit compatibility overrides** to create `%LOCALAPPDATA%\ArcScaler\compatibility.json`:

```json
{"steam":{},"exe":{"example.exe":{"hook":"winmm.dll","input":"DLSS","notes":"User-reviewed offline setup","ini_overrides":{"InitFlags":{"DepthInverted":"true"}}}}}
```

Overrides permit depth, jitter and spoofing values. Invalid entries stop planning. DLL presence provides evidence, not proof of a game's active rendering API. Unsupported or ambiguous games require manual verification.

Deployment discovers supported XeSS/FakeNvapi runtime variants from the selected release. It excludes unrelated upscalers, scripts, executables and optional runtime folders. Required dependencies, PE structure and available package hashes are checked before mutation. OptiScaler's upstream filenames and legacy recovery markers remain unchanged for compatibility.

## Other screens

**Downloads:** browse official release metadata, filter downloaded releases, download, validate, select a release, delete it, or open the package folder. Downloads can be cancelled before commit; the previous release is retained. Existing checksum mismatches are reported rather than silently trusted.

**Hardware:** re-detect the GPU, copy diagnostics, and apply recommended settings to the selected game.

**Log:** filter all activity, warnings or errors, then copy or clear the visible log.

**App settings:** open app data, edit local compatibility overrides or preview a diagnostic report. Reports include evidence, effective settings, health and recent activity, with personal paths redacted by default. Nothing is uploaded. Preferences and per-game drafts are saved automatically.

## Build and test

Install `requirements-build.txt`, then run `python build.py`. This creates `dist/ArcScaler.exe` with the supplied icon at all seven Windows sizes and ArcScaler version metadata. `ArcScaler.iss` is an optional Inno Setup 6 installer recipe using the same icon. No installer compiler was bundled with this project.

Run `python audit/run_checks.py` for isolated tests. `python audit/preview_arcscaler.py` renders all five screens with temporary fixture games and saves screenshots. The test executables are structural PE fixtures and are never executed as games.

Run `python audit/release_gate.py` to run regressions, rebuild, and smoke-test the distributed executable with a temporary data directory. Regression coverage includes process termination at transaction stages, changed-file preservation, corrupt backups, cancelled downloads, stale task results, combined SR+FG, and control layout at 100–200% scale.

See `audit/ARCSCALER_CHANGE_REPORT.md` for the requirement checklist, changed-file inventory, line counts, validation results and deliberate template differences.
