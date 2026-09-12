"""Small structurally valid PE fixtures; never loaded or executed."""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def pe_bytes(dll=True, marker=b'fixture'):
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 60, 128)
    data[128:132] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', data, 132, 0x8664, 1, 0, 0, 0, 240, 0x2022 if dll else 0x22)
    struct.pack_into('<H', data, 152, 0x20b)
    struct.pack_into('<I', data, 152 + 56, 8192)
    struct.pack_into('<I', data, 152 + 60, 512)
    data[392:400] = b'.text\0\0\0'
    struct.pack_into('<IIII', data, 400, 512, 4096, 512, 512)
    data[512:512+len(marker)] = marker
    return bytes(data)


def package(root, tag='v0.9.4'):
    version = Path(root) / 'versions' / tag
    version.mkdir(parents=True, exist_ok=True)
    for name in ('OptiScaler.dll', 'libxess.dll', 'libxess_dx11.dll', 'libxess_fg.dll', 'libxell.dll', 'fakenvapi.dll'):
        (version / name).write_bytes(pe_bytes(marker=name.encode()))
    (version / 'OptiScaler.ini').write_bytes((ROOT / 'assets/versions/v0.9.4/OptiScaler.ini').read_bytes())
    (version / 'fakenvapi.ini').write_text('[fakenvapi]\nforce_reflex=0\n', encoding='utf-8')
    return version


def game(root, name='unique-test-game.exe'):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    exe = root / name
    exe.write_bytes(pe_bytes(dll=False))
    return exe
