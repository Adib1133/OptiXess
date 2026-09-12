## Table of Contents
* [**FG Input**](#fg-input---the-native-fg-which-the-game-supports)  
* [**FG Output**](#fg-output---what-you-select-in-optiscaler-and-want-to-use)  
* [**Example use cases**](#example-use-cases) 
* [**XeFG requirements**](#xefg-requirements)  
* [**List of SL1 games**](#list-of-streamline-1-sl1-games)

---

# FG Input and FG Output

With the release of OptiScaler 0.9, the FG section has received a major rewrite/revamp in order to expand support for different tech. This section will try explaining each setting and recommended use cases.  

**_Both FG Input and FG Output now must be selected in order for FG to work!_**  
  
_It's required to **Save INI** and **restart the game** as FG options don't apply realtime!_  
  
:exclamation::exclamation::exclamation: **Select FG options -> Save INI -> Restart game** :exclamation::exclamation::exclamation:
  

> [!NOTE]
> * Added enable/disable **FG shortcut key** - default is **`End`** _(customisable, Keybinds in Overlay, `FGShortcutKey` in INI)_
> * _Some options aren't supported and may be implemented down the line (e.g. XeFG as FG Input, DLSSG as FG Output)_
> * _**OptiScaler now comes bundled with latest Fakenvapi and Nukems dlssg-to-fsr3**_

![FGinput_and_output](https://github.com/user-attachments/assets/13056e36-0ca1-4606-b3f7-74f4035f4193)

---

## FG Input - the native FG which the game supports

![FGInputs](https://github.com/user-attachments/assets/38627a59-809d-4b78-9f1d-0b8c1e23615f)

> [!TIP]
> * **DLSSG via SL** FG Input is _**recommended**_, then **FSR-FG/Nukems** and ultimately **OptiFG/Upscaler** as a final resort
> * _Always best to use native FG inputs if the game already supports FG!_
> * _OptiFG/Upscaler should only be used for games without any FG support_
> * _**DLSS-FG will be greyed out in game options unless you select DLSSG via SL or Nukems! Shows on next boot after saving the INI!**_

### DLSSG via Streamline inputs 
* Only supports **DX12** and **Streamline 2+ games**, _otherwise tooltip warns about unsupported version_
  * _Doesn't support a small number of old SL1 games - e.g. The Witcher 3, Dying Light 2, A Plague Tale Requiem, Returnal_ 
    * [List of SL1 games](#list-of-sl1-games)
* Required to _**enable DLSS-FG in the game**_ and then _**tick (FG) Active in Opti's overlay**_
* _A solution similar to our own version of Nukem’s mod, designed to be more versatile and forward-looking, with some trade-offs in legacy compatibility_ 
  * _Uses native swapchains for frame pacing, instead of SL one like Nukems_

### **Nukem's DLSSG**
* Supports **DX12** and **Vulkan**, **locked to FSR3-FG**, doesn't support anything else
  * _Selecting automatically locks FG Output to FSR3-FG via Nukem's_
 * Requires _**DLSS FG activated in-game**_

### **FSR 3.1/FSR3.0 FG Inputs**
* Also a new addition in Opti 0.9 for games that have native FSR3.1/FSR3.0 FG
* Requires **_FSR-FG enabled in game settings_** and then _**tick (FG) Active in Opti's overlay**_

### **OptiFG (Upscaler)** 
* Previously only supported FSR3-FG, now also supports **XeFG**, in addition to **FSR4-FG** 
* Since OptiFG doesn't have access to the HUDless resource, depending on the used FG Output, HUD will have artifacting
* Unlike FSR3 FG, XeFG/FSR4-FG deal with the HUD variably well (might not even require HUDfix), while FSR3-FG always requires HUDfix
  * **Show Detected UI** option can be used to verify if HUDfix limit is correctly marking only the UI or extra stuff too
* Enabled by **ticking (FG) Active in Opti's overlay**
* More specific OptiFG info located here - [OptiFG](https://github.com/optiscaler/OptiScaler/wiki/OptiFG)

> [!NOTE]
> _OptiFG/Upscaler should only be used for games without any FG support, or as a last resort if native FG inputs are busted_

---

## FG Output - what you select in OptiScaler and want to use

![FGOutputs](https://github.com/user-attachments/assets/4cb47e0c-b7f6-4722-afd0-e8640ff03199)

### FSR3-FG via Nukem's
* **Reserved for Nukem's DLSSG FG Input**
  * _Selecting automatically locks FG Input to Nukem's DLSSG_

### FSR FG
* Depending on your GPU, activates either FSR4-FG or FSR3-FG
  * **RDNA4** automatically uses **FSR4-FG**, while **other GPUs** are limited to **FSR3-FG**

### XeFG
* Works on GPUs with DP4a support
  * **Intel Arc** uses the **XMX** model, while **other GPUs** use the general **DP4a** model
* **XeMFG** support is currently limited to **Intel Arc only!**
* XeFG has some special requirements, so please read the [**special XeFG section**](#xefg-requirements) below

---

## Example use cases

* **Cyberpunk 2077** - DLSSG via SL -> XeFG/FSR-FG (or Nukems)
* **The Last of Us Part II** - DLSSG via SL -> XeFG
* **Lies of P** - FSR 3.1 FG -> FSR-FG/XeFG
  * Latest version of the game has FSR 3.1 FG which works well as an FG Input  

* **STAR WARS Jedi: Survivor** - DLSSG via SL -> FSR-FG/XeFG (Nukems works too)
* **Warhammer 40,000: Darktide** - DLSSG via SL -> XeFG
* **The Witcher 3: Wild Hunt** - Nukems 
  * SL1 game, if you want FSR4-FG or XeFG, might try OptiFG -> XeFG/FSR-FG, but more info here - [Witcher 3 Compatibility Entry](https://github.com/optiscaler/OptiScaler/wiki/The-Witcher-3-Wild-Hunt)  

* **Kingdom Come: Deliverance II** - OptiFG -> XeFG with HUDfix limit 1

---

## XeFG requirements

* **XeFG doesn't work in Exclusive Fullscreen!** 
  * Make sure you are using **Borderless Windowed/Borderless Fullscreen/Fullscreen Windowed!**  

* XeFG **doesn't support Vulkan!**  

* XeFG **doesn't support HDR16 (FP16 HDR) nor scRGB!** XeFG **ONLY supports HDR10!**

* **Do not use RTSS with Reflex injection when using XeFG!**
  * For optimal compatibility, also **enable Use MS Detours API hooking** in RTSS Setup/Settings

![ReflexMarkers](https://github.com/user-attachments/assets/cd349b14-fa9f-45a9-9b94-abd57abcfd50)

* If you have an issue where enabling XeFG (or maybe any FG) results in lower framerate than pre-FG, and you have HAGS ON, **try disabling HAGS** in System Settings - Display - Graphics - Advanced Graphics (requires restart). 
  * HAGS = Hardware-accelerated GPU scheduling
  * This fixed an issue with XeFG in Hitman 3.

* ***DO NOT USE Anti-Lag 1*** from Adrenaline with XeFG!
* ***DO NOT USE Enhanced Sync*** from Adrenaline with XeFG!

---

* **Easiest way to verify XeFG is working:**
  *  **Debug view** shows **pink vertical lines**
  * FPS jump + the **frametimes** will be **doubled/thicker** (but should be flat) - _Intel's own Flip Metering equivalent_

![NoFG](https://github.com/user-attachments/assets/d02fd0be-e8f9-41cd-b66e-a12b773e88f1)
![XeFG](https://github.com/user-attachments/assets/f567e803-600d-4842-ad3d-b03c7ba0c806)

<details>
<summary><b>Click here for XeFG Debug View example</b></summary>

![XeFGDebug](https://github.com/user-attachments/assets/9ab22eca-203e-40ae-a889-5495f91350b0)

</details>

---

* Due to how XeFG works, you might need to activate XeFG once and then restart the game for all settings to apply.
  * _**Yellow XeFG restart text must be followed, otherwise e.g. character ghosting will be noticeable!**_

![YellowText](https://github.com/user-attachments/assets/06984eec-840d-4e34-8f29-d871f99406a8)

---

* For Unreal Engine games, **in-game XeSS is not a valid upscaler input!** (no depth provided by the XeSS UE plugin)  

* For Unreal Engine games, when trying to use **OptiFG(Upscaler) FG Input with DLSS inputs selected in-game**, please **disable dilated motion vectors**
  * To locate the game's `Engine.ini`, the easiest way is to go to **PCGW** and look at the **`Configuration file(s) location`** section.
    * **Example** - for Clair Obscur Expedition 33, it's located in `%LOCALAPPDATA%\Sandfall\Saved\Config\Windows`, create if missing
    * **Example** - for Witchfire, `%LOCALAPPDATA%\Witchfire\Saved\Config\WindowsNoEditor`
  * _**If the `Engine.ini` doesn't exist, you'll have to create it, and possibly make it `Read-Only` if the game deletes it on boot or doesn't work in general.**_
* Add the command below, _requires a free line space from last entry_

```ini
[SystemSettings]
r.NGX.DLSS.DilateMotionVectors=0
```

---

### List of Streamline 1 (SL1) games:

* The Witcher 3
* ~Dying Light 2~
  * _Updated to SL2 with February 2026 update_
* Returnal
* A Plague Tale Requiem
* Marvel's Midnight Suns
* Loopmancer
* The Lord of the Rings Gollum
* WRC Generations
* Destroy All Humans! 2 - Reprobed
* F.I.S.T.: Forged In Shadow Torch
* Bright Memory Infinite

> [!CAUTION]
> * _**It's not possible to update SL1 games to SL2!!!**_  
> * **These games will only work with Nukems**, since DLSSG via SL doesn't support SL1