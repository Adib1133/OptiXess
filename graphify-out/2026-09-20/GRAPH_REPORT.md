# Graph Report - GUI astra  (2026-09-20)

## Corpus Check
- 72 files · ~141,976 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 28 file(s) not represented in the graph (top: .dll 14, .ini 4, .exe 3)

## Summary
- 708 nodes · 1763 edges · 38 communities (23 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 102 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Injector
- README.md
- .analyze_game
- CoreTests
- ConfigTab
- SafetyManager
- icons.py
- ArcScaler change report
- settings.py
- Astra static landing page specification
- Game Settings
- Game Settings
- CrashWatchdog
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

## God Nodes (most connected - your core abstractions)
1. `Injector` - 38 edges
2. `game()` - 38 edges
3. `ConfigTab` - 37 edges
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
- `CoreTests` --uses--> `ConfigGenerator`  [INFERRED]
  tests/test_core.py → core/config_generator.py
- `GameRuleTests` --uses--> `ConfigGenerator`  [INFERRED]
  tests/test_game_rules.py → core/config_generator.py
- `SmartSettingsTests` --uses--> `ConfigGenerator`  [INFERRED]
  tests/test_smart_settings.py → core/config_generator.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Recoverable per-game deployment workflow** — website_prompt_closed_game_installation, website_prompt_safe_recovery, website_prompt_launch_monitor, website_prompt_ini_preservation [EXTRACTED 1.00]
- **Frame generation input-output selection contract** — audit_frame_generation_options_fg_input, audit_frame_generation_options_fg_output, audit_frame_generation_options_xefg [EXTRACTED 1.00]
- **Reversible per-game installation lifecycle** — readme_proxy, readme_snapshot, readme_recovery, readme_watchdog [EXTRACTED 1.00]

## Communities (38 total, 15 thin omitted)

### Community 0 - "Injector"
Cohesion: 0.06
Nodes (58): Build with workspace dependencies and a workspace-local build cache., check(), Verify installed package deployment and PE exports without loading DLLs., Deterministic visual smoke run using isolated fixtures; no real games touched., run(), Run isolated regression tests; never mutate the installed reference package., Launch the rebuilt EXE alone, with fresh isolated user data and no network., build() (+50 more)

### Community 1 - "README.md"
Cohesion: 0.05
Nodes (59): FSR4 Windows 10 Agility SDK workaround, Official OptiScaler Wiki, Intel XeSS SDK license, Historical baseline: 13 tests pass, Community compatibility list, OptiPatcher, DLSSG via Streamline, Frame-generation input (+51 more)

### Community 2 - ".analyze_game"
Cohesion: 0.07
Nodes (17): GameDetector, GameLibrary, Updates properties of a profile., Removes a game from the library., Returns all game profiles with fresh injection status., Automatically discovers installed games from Steam and Epic Games., Finds all configured Steam library folders on the system., Checks if injection files are present in target directory. (+9 more)

### Community 3 - "CoreTests"
Cohesion: 0.09
Nodes (4): CoreTests, fail(), GameRuleTests, RecoveryEdges

### Community 4 - "ConfigTab"
Cohesion: 0.10
Nodes (11): format_plan(), ConfigTab, crash(), ready(), install(), done(), done(), worker() (+3 more)

### Community 5 - "SafetyManager"
Cohesion: 0.06
Nodes (39): lookup(), Local, user-overridable compatibility data; no remote executable rules., atomic_write(), canonical(), inside(), operation_lock(), OS-released lock. Persistent file prevents unlink/reopen lock races., safe_path() (+31 more)

### Community 6 - "icons.py"
Cohesion: 0.16
Nodes (8): concurrent_futures, IconCache, worker(), placeholder(), Disk-cached Windows executable icons, resolved entirely off the UI thread., ctypes, pil, uuid

### Community 7 - "ArcScaler change report"
Cohesion: 0.33
Nodes (5): ArcScaler change report, Assumptions and deliberate differences, Requirements checklist, Size and inventory, Validation evidence

### Community 8 - "settings.py"
Cohesion: 0.13
Nodes (12): Compatibility method name; output is deployed as OptiScaler.ini., Update key-value pairs in INI text in-place, preserving all comments, sections,…, _merge_ini(), Overlay any custom sections from the existing installed INI onto the freshly-…, defaults(), migrate(), Single settings contract shared by profiles, controls, planning and INI output., select_mode() (+4 more)

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

### Community 16 - "main_window.py"
Cohesion: 0.06
Nodes (34): customtkinter, menu(), section(), Release-backed controls and asynchronous per-game deployment workflows., Workers enqueue Python callables; only the Tk thread touches Tk., UIDispatcher, LibraryTab, done() (+26 more)

### Community 17 - "MainWindow"
Cohesion: 0.07
Nodes (12): Any, HardwareDetector, Returns comprehensive hardware diagnostics and tailored recommendations., Detects system hardware with dedicated Intel Arc classification., MainWindow, save(), done(), worker() (+4 more)

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

## Knowledge Gaps
- **45 isolated node(s):** `Setting`, `Requirements checklist`, `Size and inventory`, `Validation evidence`, `Assumptions and deliberate differences` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 216 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MainWindow` connect `MainWindow` to `Injector`, `.analyze_game`, `ConfigTab`, `SafetyManager`, `icons.py`, `main_window.py`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `Injector` connect `Injector` to `.analyze_game`, `CoreTests`, `SafetyManager`, `CrashWatchdog`, `main_window.py`, `MainWindow`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `ConfigTab` connect `ConfigTab` to `Injector`, `.analyze_game`, `SafetyManager`, `CrashWatchdog`, `main_window.py`, `MainWindow`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Injector` (e.g. with `ConfigGenerator` and `GameDetector`) actually correct?**
  _`Injector` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ConfigTab` (e.g. with `ConfigGenerator` and `GameDetector`) actually correct?**
  _`ConfigTab` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `MainWindow` (e.g. with `HardwareDetector` and `IconCache`) actually correct?**
  _`MainWindow` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Setting`, `Requirements checklist`, `Size and inventory` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._