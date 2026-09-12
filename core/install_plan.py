"""One read-only plan shared by preview and the installer preflight."""
from pathlib import Path
from core.game_rules import recipe_for, validate_location, WIKI, REVIEWED
from core.game_support import capabilities
from core.safety import SafetyManager
from core.files import canonical
from core.config_generator import ConfigGenerator

HOOKS = ('dxgi.dll', 'version.dll', 'winmm.dll', 'nvngx.dll', 'd3d12.dll', 'dbghelp.dll', 'wininet.dll', 'winhttp.dll')


def build_plan(analysis, settings):
    effective = {key: settings.get(key, default) for key, default in {
        'hook_method': 'dxgi.dll', 'starting_upscaler': 'DLSS', 'fg_input': 'dlssg',
        'upscaler_enabled': False, 'frame_gen_enabled': False,
        'gpu_spoofing': False, 'reflex_to_xell_enabled': False}.items()}
    force = bool(settings.get('force', False))
    notes, errors = [], []
    result = {'settings': effective, 'notes': notes, 'errors': errors, 'files': [],
              'target_dir': analysis['target_dir'], 'target_exe': analysis['target_exe'],
              'sources': [], 'recipe_id': None, 'reviewed': None}
    mode = settings.get('installation_mode', 'automatic')
    if mode not in ('automatic', 'manual'):
        errors.append('Invalid installation mode.')
    try:
        recipe = recipe_for(analysis)
        native = capabilities(analysis)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        return result
    result['capabilities'] = native
    preserve_xess = native['xess'] or bool(recipe and recipe.get('native_xess'))
    if recipe:
        result.update(recipe_id=recipe['id'], title=recipe['title'], reviewed=REVIEWED,
                      sources=[WIKI + recipe['page']])
        notes.append(recipe['notes'])
        try:
            validate_location(recipe, analysis['target_exe'])
        except ValueError as exc:
            errors.append(str(exc))
        if mode == 'automatic':
            effective['hook_method'] = recipe['hook']
            effective['starting_upscaler'] = recipe['input']
            if recipe['fg']:
                # Prefer the documented FSR route for Spider-Man to avoid launch-marker dependencies.
                effective['fg_input'] = recipe['fg'][0]
        if recipe.get('no_spoof'):
            if effective['gpu_spoofing']:
                notes.append('Saved GPU spoofing was overridden to prevent the documented startup crash.')
            effective['gpu_spoofing'] = False
            installed_ini = Path(analysis['target_dir']) / 'OptiScaler.ini'
            try:
                if installed_ini.is_file() and installed_ini.stat().st_size < 1_000_000:
                    cfg = ConfigGenerator.parser(installed_ini.read_text(encoding='utf-8-sig'))
                    if cfg.get('Spoofing', 'Dxgi', fallback='auto').strip().lower() == 'true':
                        notes.append('The currently installed INI enables DXGI spoofing. Install / Update will replace that setting with false; this is a possible cause of your startup crash.')
            except (OSError, ValueError):
                notes.append('Could not read the existing INI for startup diagnostics.')
        if recipe.get('native_xess'):
            notes.append('The official game entry documents native XeSS upscaling; retain it and install only missing FG when selected.')
        if effective['starting_upscaler'] != recipe['input'] and effective['upscaler_enabled'] and not preserve_xess:
            errors.append('Selected upscaler input is outside this reviewed recipe. Use ' + recipe['input'] + '.')
        if effective['frame_gen_enabled'] and not native['xefg'] and effective['fg_input'] not in recipe['fg']:
            errors.append('No reviewed XeSS FG route for the selected input. ' +
                          ('Choose ' + ', '.join(recipe['fg']) + '.' if recipe['fg'] else 'Leave XeSS FG disabled for this recipe.'))
        # In force mode: allow the user-chosen hook even if the recipe expects a different one.
        if effective['hook_method'] != recipe['hook'] and not force:
            errors.append('This recipe requires ' + recipe['hook'] + '; alternate routes require separate game-specific work.')
        elif effective['hook_method'] != recipe['hook'] and force:
            notes.append(f'Force inject: using {settings.get("hook_method", effective["hook_method"])} instead of recipe-recommended {recipe["hook"]}.')
    elif mode == 'automatic':
        errors.append('No reviewed automatic recipe for this game. Read the online findings, then select Manual mode to choose and review a generic installation.')
    else:
        notes.append('Manual generic installation: game-specific compatibility and input availability are not certified.')
    if effective['hook_method'] not in HOOKS:
        errors.append('Unsupported proxy filename.')
    if not effective['upscaler_enabled'] and not effective['frame_gen_enabled']:
        errors.append('Select XeSS upscaling, XeSS Frame Generation, or both before installing.')
    effective['upscaler_enabled'] = bool(effective['upscaler_enabled'] and not preserve_xess)
    effective['frame_gen_enabled'] = bool(effective['frame_gen_enabled'] and not native['xefg'])
    if not effective['upscaler_enabled'] and not effective['frame_gen_enabled']:
        if not errors:
            errors.append('Selected XeSS runtimes already exist natively. No injection needed; use in-game settings.')
        return result
    fg = effective['frame_gen_enabled']
    if fg and effective['fg_input'] == 'upscaler' and not effective['upscaler_enabled']:
        errors.append('Upscaler-driven FG requires upscaling interception; use a native FG input to retain native XeSS.')
    files = [effective['hook_method'], 'OptiScaler.ini']
    if effective['upscaler_enabled']:
        files += ['libxess.dll', 'libxess_dx11.dll']
    if fg:
        files += ['libxess_fg.dll', 'libxell.dll']
        notes.append('XeSS FG requires DX12, borderless display, and SDR or HDR10 (not scRGB/FP16 HDR). Enable ' + str(effective['fg_input']) + ' in game; restart after changing FG.')
        notes.append('FakeNvapi is a required XeSS FG dependency; this does not require DXGI GPU spoofing.')
    if fg or effective['gpu_spoofing'] or effective['reflex_to_xell_enabled']:
        files += ['fakenvapi.dll', 'fakenvapi.ini', 'libxell.dll']
    result['files'] = list(dict.fromkeys(files))
    if mode == 'automatic' and not force:
        managed = set()
        if SafetyManager.has_active_backup(analysis['target_dir']):
            manifest = SafetyManager.load_manifest(analysis['target_dir'], analysis.get('all_target_dirs', []))
            for folder, record in manifest['folders'].items():
                managed.update(canonical(Path(folder) / name) for name in [*record['created_files'], *(i['filename'] for i in record['overwritten_files'])])
        for hook in HOOKS:
            path = Path(analysis['target_dir']) / hook
            if path.exists() and canonical(path) not in managed:
                errors.append(f'Existing unmanaged proxy/library: {path}. Resolve the mod conflict before automatic installation; it will not be overwritten.')
    elif mode == 'automatic' and force:
        notes.append('Force inject: unmanaged proxy conflict check skipped.')
    return result



def format_plan(plan):
    lines = ['Recipe: ' + (plan.get('title') or 'Unverified / manual')]
    if plan.get('reviewed'):
        lines.append('Rules reviewed: ' + plan['reviewed'])
    lines.append('Destination: ' + plan['target_dir'])
    if plan['files']:
        lines.append('Files: ' + ', '.join(plan['files']))
    settings = plan['settings']
    lines.append(f"Input: {settings['starting_upscaler']} • FG: {settings['fg_input']} • GPU spoofing: {'on' if settings['gpu_spoofing'] else 'off'}")
    lines += plan['notes']
    lines += ['Not ready: ' + error for error in plan['errors']]
    return '\n'.join(lines)
