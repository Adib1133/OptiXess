# OptiScaler XeSS GUI review — 2026-09-09

Historical pre-fix review. The original findings and outputs below are retained as evidence. Remediation status and current validation are recorded separately in `REMEDIATION.md`; the maintained regression suite is under `tests/`.

**Verdict: not ready for reliability or compatibility sign-off.** The existing suite passes, but independent acceptance tests reproduce serious file-restoration and configuration defects. No production source or executable was changed during this review. Added artifacts are the review, isolated test runners, acceptance tests, and results; test dependencies are in `.audit-deps`.

## What was actually tested

| Check | Result | Meaning |
|---|---|---|
| Existing tests, isolated storage and offline release fallback | 13/13 pass | Basic detection, config string generation, copying, GUI initialization/workflow, one simulated process crash |
| Independent acceptance suite | 1 passes, 22 fail; no test errors | Reproduced defects; failures intentionally remain visible for remediation |
| Installed v0.9.4 package deployment | 8 proxy names copied with matching SHA-256 | File deployment only; no DLL loading or game rendering |
| Package PE header inspection | Root DLLs have MZ/PE headers and AMD64 machine type | Basic format check, not authenticity, dependency, export, or compatibility certification |
| Preservation of installed assets | SHA-256 unchanged | Existing tests were prevented from overwriting the real package |
| GPU inventory | Intel UHD Graphics 730, driver 32.0.101.7088 | Intel Arc runtime validation unavailable on this host |

The application is a **per-game proxy file installer and launcher**. `apply_injection` copies files to disk and refuses a detected running game. The Python source does not implement remote-process DLL injection or perform DLSS/FSR translation itself; those behaviors depend on the external OptiScaler binary and the game's loader.

## Method coverage

| Method | GUI exposed | Hash-verified primary/plugin copying | Complete clean rollback | In-game interception |
|---|---|---|---|---|
| dxgi.dll | Yes | Pass | Fail: FakeNvapi INI left behind | Unverified |
| version.dll | Yes | Pass | Fail: same | Unverified |
| winmm.dll | Yes | Pass | Fail: same | Unverified |
| nvngx.dll | Yes | Pass | Fail: same | Unverified |
| d3d12.dll | No; backend accepts it | Pass | Fail: same | Unverified |
| dbghelp.dll | No; backend accepts it | Pass | Fail: same | Unverified |
| wininet.dll | No; backend accepts it | Pass | Fail: same | Unverified |
| winhttp.dll | No; backend accepts it | Pass | Fail: same | Unverified |
| FakeNvapi | Bundled with every method, not a separate hook selection | DLL hashes match | Fail: INI omitted from snapshot | NVAPI redirection and Reflex conversion unverified |

The extra four names appear in the installed package's `setup_windows.bat`. Acceptance by the Python backend does not establish implemented per-method validation: it also accepts `unsupported.dll`. All eight real-package cases omit `libxess_dx11.dll` and `OptiScaler.ini`. All non-nvngx methods additionally deploy a second OptiScaler copy as `nvngx.dll`; the review did not establish that dual loading is appropriate for each game.

## Reproduced findings

### 1. P1 — Snapshot failure can delete untouched original game files

`core/injector.py:260–268`, `core/safety.py:113–116,213–231`.

When snapshot copying raises a disk or I/O error before a manifest is written, injection unconditionally invokes rollback. With no manifest, rollback deletes recognized filenames without checking ownership. The acceptance test simulates disk-full at backup creation and confirms an original `dxgi.dll` disappears even though deployment never began. Manual revert without a manifest also deletes a native `libxess.dll`.

Remediation: stage and commit a complete snapshot before mutation; distinguish snapshot failure from deployment failure; never infer ownership from filenames alone.

### 2. P1 — Reapplying replaces the only original backup

`core/safety.py:41–87`.

Inject twice over an existing original `dxgi.dll`, then revert: the result is the injected proxy, not the original. Every snapshot overwrites the same `.orig` files and manifest. Changing hook, version, or settings through another injection risks losing the vanilla recovery point and leaving old hooks unmanaged.

Remediation: preserve the first snapshot, track subsequent deployments transactionally, and explicitly support update/hook-switch operations.

### 3. P1 — Failed restores are reported as successful and backups are discarded

`core/safety.py:158–174,198–210`.

With restoration forced to raise `PermissionError`, rollback returns success and removes its manifest/backup while the original is not restored. Retry helpers swallow failures; rollback counts restoration without verifying the result. Missing backup files are also silently skipped. The stored original hashes are not checked on restoration.

Remediation: return or raise definitive operation results, verify restored bytes, and retain all recovery material until every required operation succeeds.

### 4. P1 — Generated settings do not implement the advertised configuration

`core/config_generator.py:66–201`; compare installed `assets/versions/v0.9.4/OptiScaler.ini`.

The schema acceptance test lists generated section/key pairs absent from the installed template. Concrete mismatches include:

| Feature | GUI output | Installed package contract |
|---|---|---|
| XeSS FG selection | `Type=xess`, `FgMethod=xess` | `[FrameGen] FGInput` and `FGOutput`; XeSS output is `xefg` |
| DLSS/FSR inputs | `OverrideNvngx`, `OverrideFsr2`, `OverrideFsr3` | `EnableDlssInputs`, `EnableFsr2Inputs`, `EnableFsr3Inputs` |
| NVAPI redirection | `[FakeNvapi] Enabled/LibraryPath` | `[NvApi] OverrideNvapiDll`, paths under the template's path section |
| Network model | UI labels 1=DP4a, 2=XMX | Template labels network variants; 2 is Model 3, not an XMX hardware switch |
| Reflex/boost | Generated `[Reflex]` settings | Those section/key pairs are absent from the supplied OptiScaler template; bundled FakeNvapi has its own configuration |

The three `[Upscalers]` backend selectors do match the template, but that does not validate all other controls. The installer emits only `nvngx.ini`, while the supplied distribution and installation instructions use `OptiScaler.ini`. Legacy filename fallback and precedence were not tested by loading the DLL. A pre-existing `OptiScaler.ini` is not updated or backed up by this installer.

Remediation: build configuration against the selected release's actual parser/schema and test effective settings from runtime logs/overlay, not only generated string contents. Upstream corroboration: [configuration template](https://github.com/optiscaler/OptiScaler/blob/master/OptiScaler.ini), [manual installation](https://github.com/optiscaler/OptiScaler/wiki/Manual-Installation).

### 5. P1 — Incomplete and invalid releases pass preflight

`core/version_manager.py:64–82`, `core/injector.py:111–125,207–257`.

Independent cases show that deleting `libxess.dll` still yields full-suite success; a release validated through an alternative `dxgi.dll` name deploys no proxy because source resolution only requests `OptiScaler.dll`; arbitrary non-PE bytes above 100 KB are marked valid; and an explicitly selected missing release is silently substituted. The supplied package is a real PE-format package, but the application validator does not establish that.

Remediation: require architecture-compatible PE binaries and dependencies for selected features, resolve supported legacy names consistently, reject invalid explicit selections, and report only files actually deployed.

### 6. P1 — Native DX11 XeSS dependency is omitted

`core/injector.py:140–158`, `core/version_manager.py:410–419`.

The installed package contains `libxess_dx11.dll`; neither the deployment list nor nested-archive promotion list includes it. All eight real-package deployments confirm it is absent while the generated config chooses the native `xess` DX11 backend. Existing tests did not include this runtime.

Remediation: use release-aware dependency inventories, including the DX11 runtime and any required support directories; verify actual DX11 initialization on Arc.

### 7. P1 — Watchdog can trigger destructive rollback for a normal exit or unrelated crash

`core/safety.py:310–359`.

A clean exit code 0 before eight seconds is treated as a crash. Separately, a reporter targeting PID 1234 is considered a crash for PID 123 because matching uses substring search. Both paths are reproduced and call rollback. These mistakes compound the recovery defects above.

Remediation: treat clean exit separately from confirmed failure, identify reporter arguments structurally, and track process identity and descendants.

### 8. P2 — FakeNvapi settings are overwritten without backup; unrelated overlay settings are removed

`core/injector.py:140–158,242–243`, `core/safety.py:152–154`.

`fakenvapi.ini` is copied into every target but never included in the planned snapshot. Existing settings are lost; fresh installs leave the INI behind on revert. Rollback also deletes a pre-existing `imgui.ini` even though injection neither created nor backed it up. Both cases fail acceptance tests. FakeNvapi's documented deployment includes its INI next to OptiScaler: [upstream instructions](https://github.com/optiscaler/OptiScaler/wiki/Fakenvapi).

### 9. P2 — Process and target validation are incomplete

`core/injector.py:47–63,99–138`.

Reproductions show that an unrelated process with the same executable basename blocks injection; a process in a game subdirectory is missed; a missing game executable is accepted; and an unsupported hook filename is accepted. Additional target directories are not separately checked for active processes. Filename input also lacks basename/path containment validation.

### 10. P2 — Profiles and asynchronous GUI callbacks affect the wrong settings/game

`gui/config_tab.py:530–603,833–849`, `core/library.py:46–77`.

Loading a game does not restore its saved version, invert-depth, or jitter values. Re-adding a game reconstructs the profile and drops settings such as custom scale and version. A mocked GUI workflow launches A, selects B, then receives A's crash callback: the callback marks B as reverted because it references mutable `current_profile`. Each behavior is reproduced without launching games.

Remediation: round-trip every control; capture immutable launched-profile identity; marshal worker callbacks onto the UI thread; update state only after confirmed recovery.

## Additional source-review concerns (not runtime-certified)

- The handoff loop does not check the stop event or crash reporters, accepts any executable in the same directory, and treats child disappearance as a crash without its exit status. The crash path kills only the original Popen process and does not wait for confirmed exit before file operations.
- A watchdog timeout is announced as successful XeSS rendering without module, log, frame, or backend telemetry. GUI crash callbacks clear backup state and claim vanilla restoration even when rollback reports failure. Widgets and message boxes are touched directly from the watchdog worker.
- GUI version download allows overlapping requests, writes into the final installation directory, and can use pre-existing extracted files to satisfy extraction/validation checks. No transactional redownload or concurrent-install tests existed. Release sorting is lexicographic rather than semantic.
- Frozen builds bundle assets under PyInstaller's extraction directory, while `MainWindow` searches beside the executable. A truly standalone copy may not discover bundled assets. The existing EXE was not rebuilt or tested as a standalone distribution.
- Detector searches can select an Engine helper before the intended game and do not validate executable architecture. Shortcut paths are interpolated unescaped into PowerShell, so apostrophes can break resolution. These need targeted follow-up tests.
- Existing GUI test constructs the real default injector and writes mock DLLs into `assets/versions/v0.9.4`. The isolated baseline runner redirects that constructor before running it. Do not run the original suite unmodified against a valuable local installation.

## Reproduction and remaining validation

Use a Python environment with `psutil`, `customtkinter`, and Tk. The audit runners also search the workspace `.audit-deps` installed for this review. From the workspace, run `audit/run_baseline.py`, `audit/test_review.py`, and `audit/check_real_package.py` with Python. The acceptance runner returns nonzero while defects remain. The baseline runner forces release fetching offline; no live downloader claim follows from its passing release test. The real-package runner requires the existing v0.9.4 assets and only copies/hashes them.

Saved results: `baseline-test-results.txt`, `review-test-results.txt`, `real-package-results.json`. The 22 failures are acceptance checks, not 22 independent root causes.

Before compatibility sign-off, fix the file safety and configuration defects, rerun these tests, and validate on an Intel Arc host using game-specific installations for each applicable proxy. Record game/build, API, driver, OptiScaler version, loaded module paths, effective input/output settings, and logs. Exercise DX11/DX12 DLSS and FSR inputs; FG off/on with each supported input; Reflex off/on; launcher handoff; repeated launches; overlays; fullscreen/resolution changes; normal exit/crash; and hash-exact rollback with pre-existing mods. Check image correctness, frame pacing, latency, and actual XeSS/XeFG backend activation. A copy test or 25-second live process cannot substitute for those results.
