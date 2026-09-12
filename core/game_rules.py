"""Reviewed game recipes. Network prose never becomes executable configuration."""
from pathlib import Path
import re
import unicodedata

WIKI = 'https://github.com/optiscaler/OptiScaler/wiki/'
REVIEWED = '2026-09-10'


def normalize_title(value):
    value = unicodedata.normalize('NFKD', str(value)).casefold()
    return ''.join(c for c in value if c.isalnum())


RECIPES = (
    dict(id='spider-man-2', title="Marvel's Spider-Man 2", aliases=('Spider-Man2', 'Spider Man 2'),
         page='Marvels-Spider%E2%80%90Man-2', hook='dxgi.dll', input='FSR', fg=('fsrfg', 'dlssg'),
         no_spoof=True, native_xess=True,
         notes='Intel/AMD: ray tracing with DXGI spoofing can crash at startup. Use FSR/XeSS in game. Enable the matching native FG option; DLSSG must be enabled to provide HUD-less frames.'),
    dict(id='spider-man-remastered', title="Marvel's Spider-Man Remastered", aliases=('Spider-Man Remastered', 'Spider-Man'),
         page='Marvels-Spider%E2%80%90Man-Remastered', hook='dxgi.dll', input='FSR', fg=('fsrfg', 'dlssg'),
         no_spoof=True, native_xess=True,
         notes='Keep DXGI spoofing off to avoid the Intel/AMD ray-tracing startup crash. DLSSG on Intel/AMD requires -forceReflexMarkers in launcher options; FSR 3.1 FG avoids that requirement.'),
    dict(id='spider-man-miles-morales', title="Marvel's Spider-Man: Miles Morales", aliases=('MilesMorales', 'Spider Man Miles Morales'),
         page='Marvels-Spider%E2%80%90Man-Miles-Morales', hook='dxgi.dll', input='FSR', fg=('fsrfg', 'dlssg'),
         no_spoof=True, native_xess=True,
         notes='Keep DXGI spoofing off to avoid the Intel/AMD ray-tracing startup crash. DLSSG on Intel/AMD requires -forceReflexMarkers in launcher options; FSR 3.1 FG avoids that requirement.'),
    dict(id='midnight-suns', title="Marvel's Midnight Suns", aliases=('MidnightSuns', 'Midnight Suns'),
         page='Marvels-Midnight-Suns', hook='d3d12.dll', input='DLSS', fg=(),
         suffix='MidnightSuns/Binaries/Win64',
         notes='FSR2 input is unsupported. This is a Streamline 1 game; its documented Nukem FG route cannot output XeSS FG. Use d3d12.dll beside the Win64 game executable. The alternate dbghelp route needs separate engine-file changes and is not automated.'),
    dict(id='dcs-world', title='DCS World', aliases=('DCS', 'DCS World OpenBeta'),
         page='DCS-World', hook='dxgi.dll', input='DLSS', fg=(), suffix='bin',
         notes='Install beside DCS.exe in bin, not bin-mt. No native FG route is documented. The reported FakeNvapi/FSR4 issue concerns FSR4 output, not a verified XeSS failure.'),
)


def match_recipe(names):
    identities = {normalize_title(n) for n in names if n}
    matches = [r for r in RECIPES if identities & {normalize_title(n) for n in (r['title'], *r['aliases'])}]
    if len(matches) > 1:
        raise ValueError('Conflicting game identities. Select the actual game executable in its own installation folder.')
    return matches[0] if matches else None


def identity_names(analysis):
    exe = Path(analysis['target_exe'])
    stem = re.sub(r'(?i)[-_](win64|wingdk)[-_]shipping$', '', exe.stem)
    return [stem, analysis.get('game_name', ''), Path(analysis.get('base_dir', exe.parent)).name]


def recipe_for(analysis):
    return match_recipe(identity_names(analysis))


def validate_location(recipe, exe):
    suffix = recipe.get('suffix')
    if suffix and not Path(exe).parent.as_posix().casefold().endswith('/' + suffix.casefold()):
        raise ValueError(f"{recipe['title']}: select the executable in {suffix}; this selected folder is not the documented injection location.")
