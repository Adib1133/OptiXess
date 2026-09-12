"""Verify installed package deployment and PE exports without loading DLLs."""
import json
from pathlib import Path
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / '.audit-deps')]
from core.files import sha256, validate_pe
from core.injector import Injector
from tests.fixtures import game


def check():
    version = ROOT / 'assets/versions/v0.9.4'
    before = {p.name: sha256(p) for p in version.glob('*.dll')}
    import pefile
    pe = pefile.PE(str(version / 'OptiScaler.dll'), fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
    exports = {symbol.name.decode('ascii') for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols if symbol.name}
    pe.close()
    required = {'dxgi.dll': 'CreateDXGIFactory', 'version.dll': 'GetFileVersionInfoW',
                'winmm.dll': 'timeGetTime', 'nvngx.dll': 'NVSDK_NGX_D3D12_Init',
                'd3d12.dll': 'D3D12CreateDevice', 'dbghelp.dll': 'MiniDumpWriteDump',
                'wininet.dll': 'InternetOpenW', 'winhttp.dll': 'WinHttpOpen'}
    rows = []
    injector = Injector(ROOT / 'assets')
    for hook in Injector.DEFAULT_HOOKS:
        with tempfile.TemporaryDirectory(prefix='opti-real-') as tmp:
            exe = game(Path(tmp) / 'game')
            folder = exe.parent
            plugin = folder / 'plugins'
            plugin.mkdir()
            (folder / hook).write_bytes(b'original third-party proxy')
            (folder / 'fakenvapi.ini').write_bytes(b'original settings')
            (plugin / 'fakenvapi.dll').write_bytes(b'original native runtime')
            originals = {p.relative_to(folder).as_posix(): sha256(p) for p in folder.rglob('*') if p.is_file()}
            result = injector.apply_injection(str(folder), str(exe), additional_dirs=[str(plugin)],
                                              hook_method=hook, optiscaler_version='v0.9.4',
                                              frame_gen_enabled=True, fg_input='dlssg', upscaler_enabled=True, gpu_spoofing=True, installation_mode='manual')
            assert result['success'], result
            for name in ['libxess.dll', 'libxess_dx11.dll', 'libxess_fg.dll', 'libxell.dll', 'fakenvapi.dll']:
                assert sha256(folder / name) == before[name]
                assert sha256(plugin / name) == before[name]
            assert sha256(folder / hook) == before['OptiScaler.dll']
            assert sha256(plugin / hook) == before['OptiScaler.dll']
            assert (folder / 'OptiScaler.ini').is_file()
            result = injector.revert_injection(str(folder), additional_dirs=[str(plugin)])
            assert result['success'], result
            after = {p.relative_to(folder).as_posix(): sha256(p) for p in folder.rglob('*')
                     if p.is_file() and p.name != '.optiscaler-operation.lock'}
            assert after == originals, (hook, after, originals)
            rows.append({'hook': hook, 'required_export': required[hook], 'export_present': required[hook] in exports,
                         'deployment_hashes_match': True, 'rollback_matches_originals': True})
    assert before == {p.name: sha256(p) for p in version.glob('*.dll')}
    report = {'source_dlls_unchanged': True, 'method_results': rows,
              'proxy_exports': sorted(exports), 'runtime_rendering_tested': False}
    (ROOT / 'audit/real-package-fixed-results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(rows, indent=2))
    return report


if __name__ == '__main__':
    check()
