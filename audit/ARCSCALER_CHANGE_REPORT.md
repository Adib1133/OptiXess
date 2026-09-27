# ArcScaler change report

## Final visual polish

Added crisp native one-pixel pane/section/footer dividers; fixed the empty-library layout with no scrollbar; scrollbars now appear only when content exceeds the available height. Refined rounded dark buttons and their highlight borders. Replaced the coarse Tk gauge arc with a 4x supersampled, Lanczos-downsampled cyan/blue gradient and round caps. Actual backdrop blur is not used.

Validation: 86 regression tests passed, then the final divider/gauge corrections were visually inspected across the fixture screens with zero callback errors. Updated screenshots are in `arcscaler-empty.png` and `arcscaler-library.png`. The root and dist executables are rebuilt from this source; current hashes and startup evidence are in the build/smoke JSON files. Earlier follow-up notes below are historical.

## UI reference follow-up

Updated the empty-library welcome state with working discovery buttons, persisted new-game version/proxy defaults, an always-enabled recovery backup indicator, simultaneous rounded In use/Latest badges, and a rounded game menu with disabled verification and amber removal. Refined dark surface colors and borders; native Tk approximates the glass-like styling without actual backdrop blur.

Final validation: 86 tests passed (35.208 seconds), new-game defaults persistence and rediscovery checked, preview callback errors empty, standalone smoke passed (4.72 seconds). Latest executable: `../dist/ArcScaler.exe`. The root executable could not be replaced while running and remains the prior build. New build details are in `arcscaler-build-result.json`. Screens: [empty library](arcscaler-empty.png), [settings](arcscaler-app-settings.png), [menu](arcscaler-game-menu.png). Graph updated to 708 nodes and 1,763 edges.

The following inventory and resource-check evidence describe the initial redesign before this follow-up.

The native desktop application now uses the supplied ArcScaler branding and the reference layout, with shared validated settings, asynchronous game icons, reviewable installation plans, and transactional deployment/recovery.

## Requirements checklist

| Requirement | Implementation | Validation / status |
| --- | --- | --- |
| 1. Branding, icon and migration | `assets/arcscaler-icon.png`, seven-size `assets/arcscaler.ico`, Windows version metadata, `main.py`, `build.py`, `core/paths.py`, `ArcScaler.iss`. Legacy data is copied without deleting originals; conflicting values are archived. | Executable resources verified at 16/24/32/48/64/128/256 pixels; migration tests pass. Installer recipe supplied; setup EXE not compiled. |
| 2. Real game icons | `core/icons.py` resolves shortcuts, extracts actual EXE resources off the UI thread, caches on disk and generates name-based fallbacks. | Cache/fallback tests and extraction from the built executable pass. |
| 3. Reference UI and actions | Rebuilt Library, Downloads, Hardware, Log and App settings; game rail/detail pane, fixed action footer, compatibility disclosure, dry-run dialog, separate Force acknowledgment and Revert confirmation. | GUI integration tests pass; all five screens rendered with no callback errors. |
| 4. Automatic compatible deployment | `core/pe.py`, `core/detector.py`, `core/install_plan.py`, `core/compatibility_table.py`, `core/version_manager.py`, `core/injector.py`: target/API/architecture detection, native input inference, safe proxy selection, package-aware files, local overrides, anti-cheat checks, reasoned previews, hashes/backups/rollback. | Synthetic PE/API, anti-cheat, collision, stale-preview, runtime-selection and recovery cases pass. No real game files changed for validation. |
| 5. Exclusive SR/FG modes | `core/settings.py` is shared by persistence, UI, planning and INI generation. Inactive controls are disabled and removed from keyboard focus; neither mode permits installation when both are off. Installed mode is recorded. | Mode, INI and GUI tests pass; DX12-only FG gate also applies to Force. |
| 6. Maintainability and focused tests | Central settings/theme, smaller screen modules, removal of obsolete wiki/pipeline code, transactional file writes and regression coverage. | 86 tests pass; graph refreshed after code changes. |

## Size and inventory

Physical Python lines, including blank lines and comments:

| Scope | Before | After | Change |
| --- | ---: | ---: | ---: |
| Production (`core`, `gui`, `main.py`, `build.py`) | 4562 | 3428 | -1134 (-24.9%) |
| Tests | 997 | 1141 | +144 |

Dependencies, generated files, assets and audit helpers are excluded from these counts. Full per-file counts and source inventory are in [arcscaler-change-inventory.json](arcscaler-change-inventory.json).

**Added source/config:** `ArcScaler.iss`, `core/compatibility_table.py`, `core/icons.py`, `core/pe.py`, `core/settings.py`, `gui/theme.py`, `requirements-build.txt`, `tests/test_arcscaler.py`.

**Removed source/config:** `OptiScalerXeSS.spec`, `core/compatibility.py`, `gui/pipeline_view.py`.

**Changed source/config:** `README.md`, `build.py`, `core/__init__.py`, `core/config_generator.py`, `core/detector.py`, `core/files.py`, `core/game_rules.py`, `core/game_support.py`, `core/injector.py`, `core/install_plan.py`, `core/library.py`, `core/paths.py`, `core/safety.py`, `core/version_manager.py`, `gui/__init__.py`, `gui/config_tab.py`, `gui/dispatch.py`, `gui/library_tab.py`, `gui/log_widget.py`, `gui/main_window.py`, `gui/version_tab.py`, `main.py`, `tests/fixtures.py`, `tests/test_advanced_usecases.py`, `tests/test_core.py`, `tests/test_game_rules.py`, `tests/test_gui_integration.py`, `tests/test_hardware.py`, `tests/test_smart_settings.py`.

Additional assets/tools: supplied PNG, multi-size ICO, `assets/compatibility.json`, `assets/windows-version.txt`, `.graphifyignore`, `audit/preview_arcscaler.py`, updated `launch.bat` and `audit/smoke_release.py`. Removed obsolete `assets/icon.ico`, `audit/preview_settings.py`, `audit/preview_game_rules.py`, `audit/run_baseline.py` and `audit/test_review.py`. Graph outputs were updated. Built `ArcScaler.exe` is available at the project root and in `dist/`.

The original source is preserved in `pre-arcscaler-source.zip`; original hashes/counts are in `arcscaler-before.json`. Previous executables were moved into `legacy-binaries/`.

## Validation evidence

- `regression-results.txt`: **86 tests passed**, 32.117 seconds.
- `arcscaler-smoke-result.json`: standalone launch without sibling assets, exit 0, bundled package seeded and hash verified, empty stderr.
- `arcscaler-resource-check.json`: ArcScaler Windows metadata, all seven embedded icon sizes, successful actual EXE icon extraction.
- `arcscaler-build-result.json`: Python 3.12.14 / PyInstaller 6.16.0; executable SHA-256 `f215c3cb0bd30ff9d38a27789d72f7042f2c840d9173b5927f9bf4e0f038b1b3`.
- Preview images: [Library](arcscaler-library.png), [Frame Generation](arcscaler-fg.png), [Downloads](arcscaler-downloads.png), [Hardware](arcscaler-hardware.png), [Log](arcscaler-log.png), [App settings](arcscaler-app-settings.png). These use isolated fixture data.
- `graphify update .`: 695 nodes, 1,739 edges, 40 communities.

## Assumptions and deliberate differences

- This remains a native CustomTkinter application. Window decorations and some controls follow Windows/Tk rather than pixel-identical web rendering. Native disabled state and keyboard focus handling provide the requested inactive-control behavior; HTML ARIA attributes do not apply.
- The reference quality choices remain prominent; an additional selector preserves other supported presets. Real game icons and name fallbacks replace illustrative screenshot artwork.
- Upstream OptiScaler runtime filenames, configuration names and legacy recovery markers retain their upstream spelling for compatibility. User-facing app branding is ArcScaler.
- API detection uses conservative static PE evidence. Unknown/ambiguous APIs cannot enable FG. Native XeSS is retained when replacement is unnecessary; XMX/DP4a selection belongs to the runtime, independently of network preset. ASI installation requires an existing compatible loader.
- Package discovery includes relevant supported XeSS/FakeNvapi dependencies; it intentionally does not copy every unrelated optional DLL, executable or script. The bundled compatibility table is small and can be extended through local overrides.
- Inno Setup 6 is not installed, so the installer recipe is included but no setup binary was built or tested. The standalone executable was built and tested.
- Validation used structural fixtures and application startup. Actual in-game XeSS/FG activation and performance still require gameplay testing on the target game and hardware.
