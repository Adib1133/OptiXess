# Remediation and release validation — 2026-09-09

The reviewed application has been repaired and its Windows executable rebuilt. All 51 maintained regression tests pass. Actual v0.9.4 package deployment and restoration pass for all eight supported proxy names. The standalone executable passes an isolated startup/shutdown smoke test.

This is a hardened release candidate, not an Intel Arc/game compatibility certification. This host has Intel UHD Graphics 730, not Arc. No test here establishes successful in-game API interception, rendered XeSS output, XeFG output, image quality, or performance.

## Delivered executable

- `../OptiScalerXeSS.exe`: rebuilt single-file Windows executable, including the v0.9.4 package and GUI resources.
- Size: 180,393,080 bytes.
- SHA-256: `3a601fcc1fd5b361a6eeab7f1d7e997780ec33f78df4e766624f60360e7ea67c`.
- Build: Python 3.12.14, PyInstaller 6.16.0; pinned dependencies in `../requirements*.txt`.
- Previous executable preserved as `OptiScalerXeSS.before-fixes.exe` for historical comparison. Do not use it as the repaired release.
- Writable application data, packages, profiles, and rotating diagnostics are separated from bundled resources under `%LOCALAPPDATA%/OptiScalerXeSS`.

## Original findings addressed

| Original finding | Implemented correction | Verification |
|---|---|---|
| Snapshot failure deletes originals | Complete snapshot before deployment; no rollback/deletion without an owned manifest | Injected backup failure and manifest-free recovery tests |
| Reapply destroys original backup | Preserve the first snapshot across settings updates and hook changes | Repeated deployment, hook switching, and exact restoration |
| Failed restore loses recovery data | Hash-check originals and restored bytes; retain manifest and backups on failure | Restore failure/retry, corrupted backup, missing target tests |
| Configuration uses incorrect keys | Generate from selected release schema; correct input, FG, scaling, sharpness, depth/jitter and FakeNvapi settings | Schema contract, reciprocal scaling, invalid input and GUI persistence tests |
| Invalid/incomplete releases accepted | Validate AMD64 PE files and required runtimes; reject missing explicit release; stage downloads and verify available checksums | Corrupt packages, interrupted updates, bad digest, traversal, ZIP and actual 7z tests |
| DX11 XeSS runtime missing | Include and validate `libxess_dx11.dll` | Fixture and real-package deployment checks |
| Watchdog mistakes clean exits/unrelated crashes for failure | Track process identity/descendants, exact reporter PID and nonzero exits; no heuristic force-kill; retain backups while a game is active | Clean exit, unrelated reporter, active process, stop and real nonzero subprocess tests |
| FakeNvapi INI not backed up; unrelated files deleted | Snapshot FakeNvapi configuration; restore only tracked files | All eight method round trips; unmanaged overlay file preservation |
| Process/target checks incomplete | Actual executable validation, path containment, game process checks and operation locks | PE/path, descendant, same-name process and concurrent operation tests |
| Profile/UI callbacks target wrong game/settings | Atomic synchronized profiles, captured game identity and main-thread callback queue | Real Tk workflow, profile switching, crash callback and dispatcher tests |

Additional corrections include exposing all eight supported proxy choices, deploying exactly one selected OptiScaler proxy, preserving legacy recovery data, safe release-cache behavior offline, explicit FG input selection, FG disabled by default, and distinguishing configuration previews from observed runtime activation. Network model selection no longer claims to control XMX/DP4a. Unsupported Reflex Boost controls were removed.

## Final checks

| Check | Result | Evidence |
|---|---|---|
| Maintained regression suite | 51 passed in 16.383 seconds | `regression-results.txt` |
| Real v0.9.4 DLL package | All 8 methods passed export-presence, deployment hash and original-file restoration checks | `real-package-fixed-results.json` |
| Reference package preservation | Source DLLs unchanged | Real-package report and regression runner |
| Windows build | Succeeded | `build-result.json`, `build-log.txt` |
| EXE alone in a temporary folder | Exit 0 in 10.72 seconds; no stderr or unhandled application error | `standalone-smoke-result.json` |
| Bundled resources with fresh user data | Package seeded; OptiScaler hash matched; no sibling assets folder | Standalone smoke report |

The GUI workflow initially exceeded its five-second test deadline while the executable build was running. The test now allows 30 seconds and dumps thread stacks if it stalls. The final suite passed with real process enumeration; no process checks were mocked away to resolve this timeout.

Real-package checks cover `dxgi.dll`, `version.dll`, `winmm.dll`, `nvngx.dll`, `d3d12.dll`, `dbghelp.dll`, `wininet.dll`, and `winhttp.dll`. FakeNvapi DLL/INI deployment and restoration are included as companion components. Export checks inspect representative entry points without loading the DLLs; they do not prove every export forwards successfully in a game. The application installs proxy files while the game is closed; OptiScaler provides the runtime interception and translation.

## Remaining release acceptance on Arc

For each supported game/build, record the Arc model and driver, graphics API, selected proxy, native input, package version, and overlay/log-confirmed output. Verify cold and repeated launch, XeSS quality modes, optional FG/Reflex conversion, fullscreen changes, clean exit, crash recovery, update/hook switch, and revert. Test each proxy only in games that actually load that library. A proxy filename cannot guarantee universal game compatibility.

Downloaded future versions must satisfy the implemented schema and package contract; incompatible releases are rejected rather than silently misconfigured. Originals already lost by an older installation cannot be reconstructed from a missing or overwritten backup. Recover those through game-file verification or reinstall.

The pre-fix report and original failing tests are retained in `REVIEW.md` and `historical/`. Their historical failure totals describe the old implementation, not the rebuilt executable.
