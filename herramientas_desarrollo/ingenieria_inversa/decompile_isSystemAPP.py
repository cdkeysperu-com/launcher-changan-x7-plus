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

def get_field_info(f_idx):
    c_idx, t_idx, n_idx = struct.unpack('<HHI', dex_data[field_ids_off + f_idx*8 : field_ids_off + (f_idx+1)*8])
    return get_type_name(c_idx), get_type_name(t_idx), get_string(n_idx)

def get_method_info(m_idx):
    c_idx, p_idx, n_idx = struct.unpack('<HHI', dex_data[method_ids_off + m_idx*8 : method_ids_off + (m_idx+1)*8])
    return get_type_name(c_idx), get_string(n_idx)

# Find isSystemAPP method in PageChangeHandler
for c_idx in range(class_defs_size):
    c_off = class_defs_off + c_idx * 32
    class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off = struct.unpack('<IIIIIIII', dex_data[c_off:c_off+32])
    cname = get_type_name(class_idx)
    if cname != 'Lcom/chinatsp/custom/PageChangeHandler;':
        continue
        
    pos = class_data_off
    nsf, pos = read_uleb128(dex_data, pos)
    nif, pos = read_uleb128(dex_data, pos)
    ndm, pos = read_uleb128(dex_data, pos)
    nvm, pos = read_uleb128(dex_data, pos)
    for _ in range(nsf + nif):
        _, pos = read_uleb128(dex_data, pos)
        _, pos = read_uleb128(dex_data, pos)
        
    curr_m_idx = 0
    for _ in range(ndm + nvm):
        m_diff, pos = read_uleb128(dex_data, pos)
        m_flags, pos = read_uleb128(dex_data, pos)
        code_off, pos = read_uleb128(dex_data, pos)
        curr_m_idx += m_diff
        cm, nm = get_method_info(curr_m_idx)
        if nm in ['isSystemAPP', 'isHideFromBroadcast']:
            print(f"\n=======================================================")
            print(f"DISASSEMBLING {nm}() at code_off 0x{code_off:X}")
            print(f"=======================================================")
            reg_size, ins_size, outs_size, tries_size, debug_off, insns_size = struct.unpack('<HHHHII', dex_data[code_off:code_off+16])
            insns_bytes = dex_data[code_off+16 : code_off+16 + insns_size*2]
            
            pc = 0
            while pc < len(insns_bytes):
                op = insns_bytes[pc]
                # decode instructions
                line = f"[0x{pc:04x}] op_0x{op:02x}"
                step = 2
                if op == 0x1a: # const-string
                    s_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
                    line = f"[0x{pc:04x}] const-string v{insns_bytes[pc+1]}, \"{get_string(s_idx)}\""
                    step = 4
                elif op == 0x1b: # const-string/jumbo
                    s_idx = struct.unpack('<I', insns_bytes[pc+2:pc+6])[0]
                    line = f"[0x{pc:04x}] const-string/jumbo v{insns_bytes[pc+1]}, \"{get_string(s_idx)}\""
                    step = 6
                elif op in [0x52, 0x54, 0x55, 0x57, 0x59, 0x5b, 0x5c, 0x5e]: # iget/sget/iput/sput
                    f_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
                    fc, ft, fn = get_field_info(f_idx)
                    op_names = {0x52:'iget-obj', 0x54:'sget-obj', 0x55:'iget-bool', 0x57:'iget', 0x59:'iput-obj', 0x5b:'sput-obj', 0x5c:'iput-bool', 0x5e:'iput'}
                    line = f"[0x{pc:04x}] {op_names.get(op, 'field_op')} v{insns_bytes[pc+1]}, {fc}->{fn}"
                    step = 4
                elif op in [0x6e, 0x6f, 0x70, 0x71, 0x72]: # invoke
                    m_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
                    mc, mn = get_method_info(m_idx)
                    op_names = {0x6e:'invoke-virtual', 0x6f:'invoke-super', 0x70:'invoke-direct', 0x71:'invoke-static', 0x72:'invoke-interface'}
                    line = f"[0x{pc:04x}] {op_names.get(op, 'invoke')} {mc}->{mn}()"
                    step = 6
                elif op in [0x38, 0x39]: # if-eqz, if-nez
                    target = pc + struct.unpack('<h', insns_bytes[pc+2:pc+4])[0] * 2
                    line = f"[0x{pc:04x}] {'if-eqz' if op==0x38 else 'if-nez'} v{insns_bytes[pc+1]}, -> 0x{target:04x}"
                    step = 4
                elif op in [0x32, 0x33]: # if-eq, if-ne
                    target = pc + struct.unpack('<h', insns_bytes[pc+2:pc+4])[0] * 2
                    line = f"[0x{pc:04x}] {'if-eq' if op==0x32 else 'if-ne'} -> 0x{target:04x}"
                    step = 4
                elif op == 0x28: # goto
                    offset = struct.unpack('<b', bytes([insns_bytes[pc+1]]))[0]
                    target = pc + offset * 2
                    line = f"[0x{pc:04x}] goto -> 0x{target:04x}"
                    step = 2
                elif op == 0x0e: # return-void
                    line = f"[0x{pc:04x}] return-void"
                    step = 2
                elif op == 0x0f: # return
                    line = f"[0x{pc:04x}] return v{insns_bytes[pc+1]}"
                    step = 2
                elif op == 0x12: # const/4
                    line = f"[0x{pc:04x}] const/4 v{insns_bytes[pc+1] & 0xf}, {insns_bytes[pc+1] >> 4}"
                    step = 2
                print(f"  {line}")
                pc += step
