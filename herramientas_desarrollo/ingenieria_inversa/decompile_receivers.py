# -*- coding: utf-8 -*-
import zipfile
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

def get_field_info(f_idx):
    c_idx, t_idx, n_idx = struct.unpack('<HHI', dex_data[field_ids_off + f_idx*8 : field_ids_off + (f_idx+1)*8])
    return get_type_name(c_idx), get_type_name(t_idx), get_string(n_idx)

# Find class PageChangeHandler$6
for c_idx in range(class_defs_size):
    c_off = class_defs_off + c_idx * 32
    class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off = struct.unpack('<IIIIIIII', dex_data[c_off:c_off+32])
    cname = get_type_name(class_idx)
    if 'PageChangeHandler$' not in cname: continue
    
    pos = class_data_off
    nsf, pos = read_uleb128(dex_data, pos)
    nif, pos = read_uleb128(dex_data, pos)
    ndm, pos = read_uleb128(dex_data, pos)
    nvm, pos = read_uleb128(dex_data, pos)
    for _ in range(nsf + nif):
        _, pos = read_uleb128(dex_data, pos)
        _, pos = read_uleb128(dex_data, pos)
        
    for count in [ndm, nvm]:
        curr_m = 0
        for _ in range(count):
            m_diff, pos = read_uleb128(dex_data, pos)
            m_flags, pos = read_uleb128(dex_data, pos)
            code_off, pos = read_uleb128(dex_data, pos)
            curr_m += m_diff
            if code_off == 0: continue
            cm, nm = get_method_info(curr_m)
            if nm == 'onReceive':
                print(f"=== {cm}->{nm}() (code_off 0x{code_off:X}) ===")
                reg_size, ins_size, outs_size, tries_size, debug_off, insns_size = struct.unpack('<HHHHII', dex_data[code_off:code_off+16])
                insns = dex_data[code_off+16 : code_off+16 + insns_size*2]
                pc = 0
                while pc < len(insns):
                    op = insns[pc]
                    step = 2
                    desc = f"op_0x{op:02x}"
                    if op == 0x1a:
                        s_idx = struct.unpack('<H', insns[pc+2:pc+4])[0]
                        desc = f'const-string "{get_string(s_idx)}"'
                        step = 4
                    elif op in [0x6e, 0x6f, 0x70, 0x71, 0x72]:
                        m_idx = struct.unpack('<H', insns[pc+2:pc+4])[0]
                        mc, mn = get_method_info(m_idx)
                        desc = f"invoke {mc}->{mn}()"
                        step = 6
                    elif op in [0x55, 0x5c, 0x52, 0x54, 0x59, 0x5b]:
                        f_idx = struct.unpack('<H', insns[pc+2:pc+4])[0]
                        fc, ft, fn = get_field_info(f_idx)
                        desc = f"field {fn}"
                        step = 4
                    elif op in [0x38, 0x39, 0x32, 0x33]:
                        tgt = pc + struct.unpack('<h', insns[pc+2:pc+4])[0]*2
                        desc = f"branch -> 0x{tgt:04x}"
                        step = 4
                    elif op == 0x28:
                        tgt = pc + struct.unpack('<b', bytes([insns[pc+1]]))[0]*2
                        desc = f"goto -> 0x{tgt:04x}"
                    elif op in [0x0e, 0x0f]:
                        desc = "return"
                    print(f"  [0x{pc:04x}] {desc}")
                    pc += step
