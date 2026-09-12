# OptiScaler XeSS GUI — OptiXess

A Windows desktop tool built specifically for **Intel Arc GPU owners** that automates per-game [OptiScaler](https://github.com/cdblgr/OptiScaler) installation, configuration, and recovery. It deploys XeSS upscaling (SR), XeSS Frame Generation (XeFG), and FakeNvapi by placing a proxy DLL beside the game executable. Rendering interception is performed by OptiScaler and Intel's runtime libraries after the game loads them.

> **OptiXess is not a game mod, cheat, or process injector.** It never touches a running process. It writes files to the game folder with full snapshotted recovery, the same way you would copy files manually.

---

## Features at a Glance

| Feature | Details |
|---|---|
| **Intel Arc detection** | Detects A-series (Alchemist) and B-series (Battlemage) Arc GPUs, confirms XMX AI matrix acceleration, shows system info badge in the header |
| **Automatic recipe mode** | Reviewed per-game installation plans for Spider-Man 2, Spider-Man Remastered, Miles Morales, Midnight Suns, DCS World |
| **Manual mode** | Generic installation for any game — choose proxy, input, and components yourself |
| **Install / Update** | Deploys OptiScaler under the chosen proxy filename with snapshotted backup |
| **⚡ Force Inject** | Overrides ALL validation errors and conflicts — use when Install is blocked but you know what you are doing |
| **Revert** | Restores original game files from snapshot; hash-verified before write |
| **OptiScaler.ini preserved** | On re-injection, your manual INI edits are merged into the new config |
| **Proxy filename enforced** | The DLL is deployed with exactly the filename you choose (winmm.dll, version.dll, etc.) |
| **Downloads management** | Browse official GitHub releases, download with progress, open the downloads folder, validate local files, rebuild file hashes, delete versions |
| **Launch & Monitor** | Launches the game and watches for startup crashes; rolls back automatically on failure |
| **Smart game detection** | Detects native XeSS SR/FG, DLSS SR/G, FSR FG, anti-cheat — never overwrites native XeSS |
| **Wiki research** | Searches the official OptiScaler compatibility wiki by game title/alias for documented settings |

---

## Requirements

- Windows 10 / 11 (64-bit)
- Intel Arc GPU (A-series or B-series recommended; other GPUs work in manual mode)
- The game must be **closed** during installation and revert

No Python required for the pre-built `.exe`.

---

## Getting Started

1. **Launch `OptiScalerXeSS.exe`.**
   On first run, bundled assets are extracted to `%LOCALAPPDATA%\OptiScalerXeSS\assets\versions`. Profiles and logs go to `%LOCALAPPDATA%\OptiScalerXeSS`.

2. **Go to the Downloads tab** and click **⟳ Refresh official releases** to see available OptiScaler versions. Click **⬇ Download & Install** on the version you want.

3. **Add your game** in the Library tab. Point to the actual `.exe` inside the game folder.

4. **Select the game** in the Library — the Config tab opens with:
   - Suggested settings from local runtime scan + online wiki lookup
   - Arc GPU detection badge in the header
   - Automatic recipe (if the game is in the reviewed list)

5. **Choose components:**
   - ✅ Install XeSS upscaling — replaces DLSS/FSR with XeSS SR
   - ✅ Install XeSS Frame Generation (DX12 only)

6. **Choose settings** (or click **Use suggested settings**):
   - **Proxy filename** — the DLL name OptiScaler loads as (`dxgi.dll`, `winmm.dll`, `version.dll`, etc.)
   - **Game upscaler input** — `DLSS` or `FSR`
   - **Frame-generation input** — `dlssg` (native DLSSG), `fsrfg` (FSR 3.1), `fsrfg30` (FSR 3.0), `upscaler`
   - **Render resolution preset** — `User Defined` leaves resolution under in-game control (recommended)
   - **Installation mode** — `automatic` uses a reviewed recipe; `manual` allows any game

7. **Click Install / Update** with the game closed. The proxy DLL is deployed under the exact filename you selected, and `OptiScaler.ini` is written. Any pre-existing user edits in `OptiScaler.ini` are preserved.

8. **Launch the game.** Open the OptiScaler overlay (`Insert` key) to confirm XeSS/XeFG is active.

9. **Revert** at any time with the game closed to fully restore original files.

---

## Force Inject

When the standard **Install / Update** is blocked by a validation error (e.g. unmanaged proxy conflict, recipe hook mismatch, unlisted game in automatic mode), use **⚡ Force Inject**:

- Bypasses all plan validation errors
- Skips the unmanaged proxy conflict check
- Honours your chosen proxy filename regardless of what the recipe recommends
- Preserves your existing `OptiScaler.ini` user edits
- Shows a confirmation dialog before proceeding; overridden errors appear as warnings in the log

Use force inject only after you have read the online compatibility notes and understand the trade-offs.

---

## Proxy Filename

OptiScaler needs to be named as a DLL that the game imports so Windows loads it automatically. Common choices:

| Filename | When to use |
|---|---|
| `dxgi.dll` | Default — most DX11/DX12 games |
| `winmm.dll` | Useful when dxgi conflicts with another mod |
| `version.dll` | Alternative for some Unreal games |
| `nvngx.dll` | Games that load DLSS via nvngx |
| `d3d12.dll` | Some DX12 games (careful — may conflict) |
| `dbghelp.dll` | Fallback for older engines |
| `wininet.dll` / `winhttp.dll` | Rare alternatives |

OptiXess deploys `OptiScaler.dll` **under the filename you select**. If a file with that name already exists in the game folder, it is snapshotted first and will be restored on Revert.

---

## Downloads Tab

| Button | What it does |
|---|---|
| **⟳ Refresh official releases** | Fetches the latest release list from GitHub (cached when offline) |
| **📂 Open Download Folder** | Opens `assets/versions/` in Windows Explorer |
| **✔ Validate Local Files** | Scans every version sub-folder, runs structural checks, rebuilds file hashes for user-modified installs |
| **⬇ Download & Install** (per card) | Downloads and extracts the release using Windows bsdtar (supports BCJ2 compression) |
| **🔄 Re-download** (per card) | Re-downloads over an existing install |
| **✔ Validate & Rebuild Hashes** (per card) | Validates a single installed version; useful after manually replacing a file |
| **🗑 Delete** (per card) | Permanently removes the version from the downloads folder after confirmation |

### Manual Install
1. Click **📂 Open Download Folder**
2. Extract OptiScaler into a new sub-folder named after the version, e.g. `v0.9.4/`
3. Click **✔ Validate Local Files** — OptiXess will find the folder, run structural checks, and register it

---

## Configuration and Recovery

- Each installation takes a snapshot before writing any files. A failed install rolls back automatically.
- The first snapshot is preserved across updates and hook changes — Revert always goes back to your original files.
- Original backups are hash-verified before restoration.
- Failed restores retain their recovery data and report failure rather than silently deleting it.
- `OptiScaler.ini` is generated fresh on each install and then merged with any user edits from the previous install. FakeNvapi settings go to `fakenvapi.ini`.
- Operation locks prevent overlapping modifications. Process checks reject active games — do not start the game during installation or revert.

---

## Startup Monitoring (Launch & Monitor)

Click **Launch & Monitor** after installing to:
- Launch the game executable
- Watch for abnormal exits within the observation window
- Automatically roll back files if a startup crash is confirmed
- Report success once the observation window closes normally

A completed observation window does not certify rendering or backend activation — use the in-game overlay.

---

## Smart Detection

On game selection, OptiXess runs a local scan + wiki lookup:

- **Local scan**: reads DLL names to distinguish XeSS SR, XeSS FG, DLSS SR, DLSSG, and possible FSR FG. XeLL alone does not confirm XeSS capability.
- **Wiki lookup**: normalises the game title and searches the official OptiScaler compatibility wiki. Sources are shown inline. Web prose is never executed or silently applied.
- **Suggested settings**: populated from both. Clicking **Use suggested settings** applies the supported input evidence and wiki proxy recommendation. It does not select components — you must still choose XeSS upscaling and/or XeSS FG explicitly.
- Files created by OptiXess are excluded from native detection on subsequent scans so they do not appear as "already native".

---

## Intel Arc GPU Detection

OptiXess reads Windows WMI device data on launch:

- Identifies A-series (Alchemist, XMX hardware) and B-series (Battlemage, XMX hardware) Arc GPUs
- Shows a hardware badge in the header
- Click the badge to open a full **System Info** panel (GPU name, VRAM, driver, XeSS acceleration mode)
- GPU spoofing is disabled by default for Arc (not required; may cause issues)
- For unlisted games, **Use suggested settings** automatically switches to Manual mode with XeSS upscaling enabled

---

## Reviewed Recipes

Automatic mode includes verified installation plans for:

| Game | Proxy | Notes |
|---|---|---|
| Marvel's Spider-Man 2 | `dxgi.dll` | FSR FG input, no GPU spoofing (crash risk), native XeSS upscaling retained |
| Marvel's Spider-Man Remastered | `dxgi.dll` | FSR FG preferred; DLSSG needs `-forceReflexMarkers` |
| Miles Morales | `dxgi.dll` | Same as Remastered |
| Marvel's Midnight Suns | `d3d12.dll` | `MidnightSuns/Binaries/Win64` executable required |
| DCS World | `dxgi.dll` | `bin/` preferred over `bin-mt/`; no verified XeFG route |

Unknown games require **Manual mode**. An online compatibility list match alone is not a complete automatic recipe.

---

## Diagnostics

For issues, collect:
- `%LOCALAPPDATA%\OptiScalerXeSS\application.log`
- The game's OptiScaler log (in the game folder)
- Game build, graphics API, driver version, proxy filename, OptiScaler release, overlay backend status

---

## Development

64-bit Python 3.12+ on Windows:

```powershell
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -t .
```

Build:

```powershell
python -m pip install -r requirements-build.txt
python build.py
```

Set `OPTISCALER_GUI_DATA_DIR` to an isolated directory for testing. Never test against real game installations or overwrite live DLLs with fixture bytes.

Audit scripts in `audit/`:
- `audit/run_checks.py` — all regression tests + reference asset checks
- `audit/check_real_package.py` — proxy exports, deployed hashes, exact restoration
- `audit/smoke_release.py` — launches EXE with fresh temporary user data

See `audit/REMEDIATION.md` and `audit/REVIEW.md` for the validation history.

---

## License

OptiScaler is developed by the OptiScaler project. Intel XeSS runtime libraries are subject to Intel's license. OptiXess (this GUI) is a separate configuration tool and does not modify or redistribute the OptiScaler or XeSS source code.

