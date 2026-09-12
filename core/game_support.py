"""Separate local runtime evidence from confirmed in-game feature availability."""
from pathlib import Path
from core.files import canonical
from core.safety import SafetyManager


def capabilities(analysis):
    excluded = set()
    target = analysis.get('target_dir')
    if target and SafetyManager.has_active_backup(target):
        manifest = SafetyManager.load_manifest(target, analysis.get('all_target_dirs', []))
        for folder, record in manifest['folders'].items():
            excluded.update(canonical(Path(folder) / n) for n in record['created_files'])
    names = {d['filename'].lower() for loc in analysis.get('discovered_locations', [])
             for d in loc['details'] if canonical(d['full_path']) not in excluded}
    return {'xess': bool(names & {'libxess.dll', 'libxess_dx11.dll'}),
            'xefg': bool(names & {'libxess_fg.dll', 'libxessfg.dll'}),
            'dlss': 'nvngx_dlss.dll' in names,
            'dlssg': 'nvngx_dlssg.dll' in names,
            'fsr': any(n.startswith(('ffx_fsr2', 'ffx_fsr3', 'amd_fidelityfx')) for n in names),
            'fsrfg': any(n.startswith(('ffx_fsr3', 'amd_fidelityfx')) for n in names)}


def describe(caps):
    lines = []
    if caps['xess']:
        lines.append('XeSS upscaler runtime is present. Keep native upscaling; select only FG if needed.')
    elif caps['dlss'] or caps['fsr']:
        lines.append('DLSS/FSR runtime evidence is present, but XeSS upscaling was not detected.')
    else:
        lines.append('No supported upscaler runtime detected. Statically linked features may be missed.')
    if caps['xefg']:
        lines.append('XeSS FG runtime is present; native FG may already be available.')
    elif caps['dlssg'] or caps['fsrfg']:
        lines.append('XeSS FG was not detected; DLSS/FSR FG runtime evidence is present. Confirm FG in game settings.')
    else:
        lines.append('No FG runtime detected. Upscaler-driven FG requires upscaling interception and HUD tuning.')
    lines.append('DLL presence is evidence, not proof of native feature availability or the active graphics API.')
    return '\n'.join(lines)
