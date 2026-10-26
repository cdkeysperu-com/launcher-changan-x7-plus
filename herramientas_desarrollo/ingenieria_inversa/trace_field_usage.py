# -*- coding: utf-8 -*-
import zipfile
import struct
import os

sysui = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\oem_factory_backup\F202_SystemUI.apk"
with zipfile.ZipFile(sysui, 'r') as z:
    dex_data = z.read('classes.dex')

field_ids_size = struct.unpack('<I', dex_data[80:84])[0]
field_ids_off = struct.unpack('<I', dex_data[84:88])[0]
string_ids_size = struct.unpack('<I', dex_data[56:60])[0]
string_ids_off = struct.unpack('<I', dex_data[60:64])[0]
type_ids_size = struct.unpack('<I', dex_data[64:68])[0]
type_ids_off = struct.unpack('<I', dex_data[68:72])[0]
method_ids_size = struct.unpack('<I', dex_data[88:92])[0]
method_ids_off = struct.unpack('<I', dex_data[92:96])[0]
class_defs_size = struct.unpack('<I', dex_data[96:100])[0]
class_defs_off = struct.unpack('<I', dex_data[100:104])[0]

def read_uleb128(data, off):
    res, shift = 0, 0
    while True:
        b = data[off]; off += 1; res |= (b & 0x7f) << shift
        if not (b & 0x80): break
        shift += 7
    return res, off

def get_string(idx):
    if idx >= string_ids_size: return ''
    off = struct.unpack('<I', dex_data[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    l, p = read_uleb128(dex_data, off)
    return dex_data[p:p+l].decode('utf-8', errors='replace')

def get_type_name(idx):
    if idx >= type_ids_size: return ''
    s_idx = struct.unpack('<I', dex_data[type_ids_off + idx*4 : type_ids_off + (idx+1)*4])[0]
    return get_string(s_idx)

def get_method_info(m_idx):
    c_idx, p_idx, n_idx = struct.unpack('<HHI', dex_data[method_ids_off + m_idx*8 : method_ids_off + (m_idx+1)*8])
    return get_type_name(c_idx), get_string(n_idx)

target_f_indices = []
for f_idx in range(field_ids_size):
    c_idx, t_idx, n_idx = struct.unpack('<HHI', dex_data[field_ids_off + f_idx*8 : field_ids_off + (f_idx+1)*8])
    fname = get_string(n_idx)
    cname = get_type_name(c_idx)
    if fname in ['isThirdAppForScreen', 'isSystemApp', 'mHideFromBroadcastPackage', 'mFullScreenList', 'mWhiteList']:
        print(f'Field #{f_idx} (0x{f_idx:04x}): {cname}->{fname}')
        target_f_indices.append((f_idx, fname, cname))

print('\nSearching bytecodes for field access...')
for c_idx in range(class_defs_size):
    c_off = class_defs_off + c_idx * 32
    class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off = struct.unpack('<IIIIIIII', dex_data[c_off:c_off+32])
    cname = get_type_name(class_idx)
    if 'com/chinatsp' not in cname: continue
    if class_data_off == 0: continue
    
    pos = class_data_off
    nsf, pos = read_uleb128(dex_data, pos)
    nif, pos = read_uleb128(dex_data, pos)
    ndm, pos = read_uleb128(dex_data, pos)
    nvm, pos = read_uleb128(dex_data, pos)
    
    for _ in range(nsf + nif):
        _, pos = read_uleb128(dex_data, pos)
        _, pos = read_uleb128(dex_data, pos)
        
    for methods_count, label in [(ndm, 'direct'), (nvm, 'virtual')]:
        curr_m_idx = 0
        for _ in range(methods_count):
            m_diff, pos = read_uleb128(dex_data, pos)
            m_flags, pos = read_uleb128(dex_data, pos)
            code_off, pos = read_uleb128(dex_data, pos)
            curr_m_idx += m_diff
            if code_off == 0: continue
            
            reg_size, ins_size, outs_size, tries_size, debug_off, insns_size = struct.unpack('<HHHHII', dex_data[code_off:code_off+16])
            insns_bytes = dex_data[code_off+16 : code_off+16 + insns_size*2]
            
            for f_idx, fname, fcname in target_f_indices:
                f_bytes = struct.pack('<H', f_idx)
                for pc in range(0, len(insns_bytes)-3, 2):
                    if insns_bytes[pc+2:pc+4] == f_bytes:
                        op = insns_bytes[pc]
                        op_type = 'READ' if op in [0x52, 0x54, 0x55, 0x57] else ('WRITE' if op in [0x59, 0x5b, 0x5c, 0x5e] else f'0x{op:02x}')
                        cm, nm = get_method_info(curr_m_idx)
                        print(f'  {op_type} {fname} in {cm}->{nm}() at pc 0x{pc:04x}')
