"""Bounded, read-only PE import inspection; never loads the executable."""
from pathlib import Path
import struct

def inspect_pe(path):
    with Path(path).open('rb') as stream:
        size = Path(path).stat().st_size
        def read(offset, count):
            if offset < 0 or offset + count > size:
                raise ValueError('PE table points outside file.')
            stream.seek(offset)
            return stream.read(count)
        dos = read(0, 64)
        if dos[:2] != b'MZ':
            raise ValueError('Missing PE DOS header.')
        pe = struct.unpack_from('<I', dos, 60)[0]
        header = read(pe, 24)
        if header[:4] != b'PE\0\0':
            raise ValueError('Missing PE signature.')
        machine, count = struct.unpack_from('<HH', header, 4)
        optional_size = struct.unpack_from('<H', header, 20)[0]
        if not 1 <= count <= 96 or optional_size > 4096:
            raise ValueError('Invalid PE tables.')
        optional = read(pe + 24, optional_size)
        magic = struct.unpack_from('<H', optional)[0]
        directory = 112 if magic == 0x20b else 96 if magic == 0x10b else 0
        if not directory or len(optional) < directory:
            raise ValueError('Invalid optional header.')
        sections = []
        for i in range(count):
            section = read(pe + 24 + optional_size + i * 40, 40)
            virtual_size, rva, raw_size, raw = struct.unpack_from('<IIII', section, 8)
            sections.append((rva, raw_size, raw))
        def offset(rva):
            for start, length, raw in sections:
                if start <= rva < start + length:
                    return raw + rva - start
            raise ValueError('Import address is not file-backed.')
        imports = set()
        for index, stride, name_at in ((1, 20, 12), (13, 32, 4)):
            if len(optional) < directory + index * 8 + 8:
                continue
            rva, length = struct.unpack_from('<II', optional, directory + index * 8)
            if not rva:
                continue
            table = offset(rva)
            for i in range(min(4096, max(1, length // stride))):
                descriptor = read(table + i * stride, stride)
                if not any(descriptor):
                    break
                name_rva = struct.unpack_from('<I', descriptor, name_at)[0]
                if index == 13 and not struct.unpack_from('<I', descriptor)[0] & 1:
                    continue  # Old VA-based delay imports are not guessed.
                pos = offset(name_rva)
                raw_name = read(pos, min(256, size-pos)).split(b'\0',1)[0]
                imports.add(raw_name.decode('ascii', errors='strict').lower())
    apis = [api for dll,api in (('d3d11.dll','DX11'),('d3d12.dll','DX12'),('vulkan-1.dll','Vulkan')) if dll in imports]
    return {'architecture': {0x8664:'x64',0x14c:'x86',0xaa64:'ARM64'}.get(machine,'Unknown'),
            'imports': sorted(imports), 'graphics_apis': apis,
            'graphics_api': apis[0] if len(apis)==1 else 'Unknown' if not apis else 'Multiple'}
