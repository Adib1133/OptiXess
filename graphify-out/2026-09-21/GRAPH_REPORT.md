# Graph Report - GUI astra  (2026-09-20)

## Corpus Check
- 72 files · ~142,134 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 28 file(s) not represented in the graph (top: .dll 14, .ini 4, .exe 3)

## Summary
- 719 nodes · 1797 edges · 44 communities (26 shown, 18 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 105 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- injector.py
- README.md
- GameLibrary
- Injector
- ConfigTab
- VersionManager
- icons.py
- ArcScaler change report
- ConfigGenerator
- Astra static landing page specification
- Game Settings
- Game Settings
- CrashWatchdog
- HardwareDetector
- core/__init__.py
- VersionTests
- main_window.py
- MainWindow
- gui/__init__.py
- html_parser
- Pinned runtime dependencies
- Microsoft DirectX license
- v0.9.4/setup_linux.sh
- runpy
- FSR4 Windows 10 crash workaround
- test_extract_py7zr/setup_linux.sh
- urllib_error
- FidelityFX v2 license
- Intel Simplified Software License October 2022
- FidelityFX v1 license
- AGENTS.md
- Microsoft DirectX license
- FidelityFX_v1_LICENSE.md
- FidelityFX_v2_LICENSE.md
- build-log.txt
- game-rules-tests.txt
- new-regression.txt
- webbrowser
- .analyze_game
- game
- GameRuleTests
- SmartSettingsTests
- inspect_pe

## God Nodes (most connected - your core abstractions)
1. `Injector` - 38 edges
2. `ConfigTab` - 38 edges
3. `game()` - 38 edges
4. `MainWindow` - 33 edges
5. `SafetyManager` - 31 edges
6. `VersionManager` - 31 edges
7. `build_plan()` - 27 edges
8. `CoreTests` - 27 edges
9. `GameDetector` - 25 edges
10. `GameLibrary` - 25 edges

## Surprising Connections (you probably didn't know these)
- `First snapshot preservation` --semantically_similar_to--> `Historical baseline test isolation`  [INFERRED] [semantically similar]
  README.md → audit/historical/run_baseline_original.py.txt
- `ConfigTab` --uses--> `ConfigGenerator`  [INFERRED]
  gui/config_tab.py → core/config_generator.py
- `ArcScalerAcceptance` --uses--> `ConfigGenerator`  [INFERRED]
  tests/test_arcscaler.py → core/config_generator.py
- `CoreTests` --uses--> `ConfigGenerator`  [INFERRED]
  tests/test_core.py → core/config_generator.py
- `GameRuleTests` --uses--> `ConfigGenerator`  [INFERRED]
  tests/test_game_rules.py → core/config_generator.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Recoverable per-game deployment workflow** — website_prompt_closed_game_installation, website_prompt_safe_recovery, website_prompt_launch_monitor, website_prompt_ini_preservation [EXTRACTED 1.00]
- **Frame generation input-output selection contract** — audit_frame_generation_options_fg_input, audit_frame_generation_options_fg_output, audit_frame_generation_options_xefg [EXTRACTED 1.00]
- **Reversible per-game installation lifecycle** — readme_proxy, readme_snapshot, readme_recovery, readme_watchdog [EXTRACTED 1.00]

## Communities (44 total, 18 thin omitted)

### Community 0 - "injector.py"
Cohesion: 0.06
Nodes (73): Build with workspace dependencies and a workspace-local build cache., Verify installed package deployment and PE exports without loading DLLs., Deterministic visual smoke run using isolated fixtures; no real games touched., Run isolated regression tests; never mutate the installed reference package., Launch the rebuilt EXE alone, with fresh isolated user data and no network., build(), Build ArcScaler's standalone Windows executable from portable project paths., configparser (+65 more)

### Community 1 - "README.md"
Cohesion: 0.05
Nodes (59): FSR4 Windows 10 Agility SDK workaround, Official OptiScaler Wiki, Intel XeSS SDK license, Historical baseline: 13 tests pass, Community compatibility list, OptiPatcher, DLSSG via Streamline, Frame-generation input (+51 more)

### Community 2 - "GameLibrary"
Cohesion: 0.11
Nodes (13): GameLibrary, Updates properties of a profile., Removes a game from the library., Returns all game profiles with fresh injection status., Automatically discovers installed games from Steam and Epic Games., Finds all configured Steam library folders on the system., Checks if injection files are present in target directory., Creates a stable unique ID for a game path. (+5 more)

### Community 3 - "Injector"
Cohesion: 0.07
Nodes (7): check(), run(), Injector, package(), CoreTests, fail(), RecoveryEdges

### Community 4 - "ConfigTab"
Cohesion: 0.09
Nodes (15): format_plan(), ConfigTab, crash(), ready(), install(), done(), done(), worker() (+7 more)

### Community 5 - "VersionManager"
Cohesion: 0.20
Nodes (4): Permanently delete an installed version directory. Raises ValueError if the tag…, Re-validate a locally placed (manually dropped) version directory. Returns…, Regenerate version_meta.json for a manually placed / modified version. This…, VersionManager

### Community 6 - "icons.py"
Cohesion: 0.16
Nodes (8): concurrent_futures, IconCache, worker(), placeholder(), Disk-cached Windows executable icons, resolved entirely off the UI thread., ctypes, pil, uuid

### Community 7 - "ArcScaler change report"
Cohesion: 0.29
Nodes (6): ArcScaler change report, Assumptions and deliberate differences, Requirements checklist, Size and inventory, UI reference follow-up, Validation evidence

### Community 8 - "ConfigGenerator"
Cohesion: 0.27
Nodes (5): ConfigGenerator, Compatibility method name; output is deployed as OptiScaler.ini., Update key-value pairs in INI text in-place, preserving all comments, sections,…, _merge_ini(), Overlay any custom sections from the existing installed INI onto the freshly-…

### Community 9 - "Astra static landing page specification"
Cohesion: 0.08
Nodes (24): Accessible responsive layout, Dark Intel Arc blue and XeSS cyan visual style, OptiScaler XeSS GUI - Astra, Windows bsdtar BCJ2 extraction, Closed-game file deployment, DCS World, Force Inject, Smart Game Detection (+16 more)

### Community 10 - "Game Settings"
Cohesion: 0.09
Nodes (23): Install / Update, Launch & Monitor, Revert, Open Folder, Use suggested settings, Choose components, Live Diagnostic & Safety Console, Downloads, DXGI spoofing and ray tracing startup crash guidance, XeSS FG display and restart requirements, XeSS frame generation selected (+15 more)

### Community 11 - "Game Settings"
Cohesion: 0.12
Nodes (18): Install / Update, Launch & Monitor, Revert, Open Folder, Use suggested settings, Choose components, Live Diagnostic & Safety Console, Downloads, Scrollable settings with persistent action bar and diagnostic console, Game Library, Offline research and unverified compatibility (+10 more)

### Community 12 - "CrashWatchdog"
Cohesion: 0.23
Nodes (3): CrashWatchdog, Observe startup. Recover only confirmed failures after game processes exit.…, WatchdogTests

### Community 13 - "HardwareDetector"
Cohesion: 0.14
Nodes (10): Any, HardwareDetector, Hardware and GPU detection engine with specific Intel Arc architecture…, Returns comprehensive hardware diagnostics and tailored recommendations., Detects system hardware with dedicated Intel Arc classification., done(), worker(), platform (+2 more)

### Community 16 - "main_window.py"
Cohesion: 0.06
Nodes (38): customtkinter, menu(), section(), Release-backed controls and asynchronous per-game deployment workflows., Workers enqueue Python callables; only the Tk thread touches Tk., UIDispatcher, LibraryTab, done() (+30 more)

### Community 17 - "MainWindow"
Cohesion: 0.07
Nodes (20): identity_names(), match_recipe(), normalize_title(), Reviewed game recipes. Network prose never becomes executable configuration., recipe_for(), recipes(), data_root(), prepare_assets() (+12 more)

### Community 20 - "Pinned runtime dependencies"
Cohesion: 0.29
Nodes (7): Build dependencies, PyInstaller 6.16.0, customtkinter==6.0.0, Pillow==11.3.0, psutil==7.2.2, py7zr==1.0.0, Pinned runtime dependencies

### Community 21 - "Microsoft DirectX license"
Cohesion: 0.33
Nodes (6): Conditional distributable object code rights, Microsoft GDPR terms, Microsoft DirectX license, Microsoft Corporation, Microsoft privacy statement, Windows-only use rights

### Community 22 - "v0.9.4/setup_linux.sh"
Cohesion: 0.70
Nodes (4): create_uninstaller(), select_filename(), setup_linux.sh script, show_help()

### Community 24 - "FSR4 Windows 10 crash workaround"
Cohesion: 0.40
Nodes (5): D3D12_Optiscaler folder, FSR4 Windows 10 crash workaround, FsrAgilitySDKUpgrade=true, OptiScaler project readme, OptiScaler installation and compatibility wiki

### Community 25 - "test_extract_py7zr/setup_linux.sh"
Cohesion: 0.70
Nodes (4): create_uninstaller(), select_filename(), setup_linux.sh script, show_help()

### Community 27 - "FidelityFX v2 license"
Cohesion: 0.50
Nodes (4): Default binary-only redistribution rights, FidelityFX v2 license, Permissive license for enumerated exceptions, Enumerated source and SDK file license exceptions

### Community 28 - "Intel Simplified Software License October 2022"
Cohesion: 0.50
Nodes (4): Unmodified binary redistribution with notices, Intel Simplified Software License October 2022, Separate third-party software terms, Intel Xe Super Sampling SDK

### Community 29 - "FidelityFX v1 license"
Cohesion: 0.67
Nodes (3): Advanced Micro Devices, FidelityFX v1 license, Modification and redistribution with retained notices

### Community 39 - ".analyze_game"
Cohesion: 0.20
Nodes (3): GameDetector, prepare(), DiscoveryTests

### Community 40 - "game"
Cohesion: 0.39
Nodes (3): game(), pe_bytes(), ArcScalerAcceptance

## Knowledge Gaps
- **46 isolated node(s):** `Setting`, `UI reference follow-up`, `Requirements checklist`, `Size and inventory`, `Validation evidence` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 221 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MainWindow` connect `MainWindow` to `injector.py`, `GameLibrary`, `Injector`, `ConfigTab`, `icons.py`, `HardwareDetector`, `main_window.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `Injector` connect `Injector` to `injector.py`, `VersionManager`, `.analyze_game`, `ConfigGenerator`, `game`, `GameRuleTests`, `SmartSettingsTests`, `CrashWatchdog`, `main_window.py`, `MainWindow`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `ConfigTab` connect `ConfigTab` to `injector.py`, `.analyze_game`, `ConfigGenerator`, `CrashWatchdog`, `main_window.py`, `MainWindow`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Injector` (e.g. with `ConfigGenerator` and `GameDetector`) actually correct?**
  _`Injector` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ConfigTab` (e.g. with `ConfigGenerator` and `GameDetector`) actually correct?**
  _`ConfigTab` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `MainWindow` (e.g. with `HardwareDetector` and `IconCache`) actually correct?**
  _`MainWindow` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Setting`, `UI reference follow-up`, `Requirements checklist` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._