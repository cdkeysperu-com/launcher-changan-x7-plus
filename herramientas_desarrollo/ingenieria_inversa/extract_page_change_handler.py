# -*- coding: utf-8 -*-
import zipfile
import struct
import os

sysui = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\oem_factory_backup\F202_SystemUI.apk"

with zipfile.ZipFile(sysui, 'r') as z:
    dex_data = z.read('classes.dex')

string_ids_size = struct.unpack('<I', dex_data[56:60])[0]
string_ids_off = struct.unpack('<I', dex_data[60:64])[0]
type_ids_size = struct.unpack('<I', dex_data[64:68])[0]
type_ids_off = struct.unpack('<I', dex_data[68:72])[0]
proto_ids_size = struct.unpack('<I', dex_data[72:76])[0]
proto_ids_off = struct.unpack('<I', dex_data[76:80])[0]
field_ids_size = struct.unpack('<I', dex_data[80:84])[0]
field_ids_off = struct.unpack('<I', dex_data[84:88])[0]
method_ids_size = struct.unpack('<I', dex_data[88:92])[0]
method_ids_off = struct.unpack('<I', dex_data[92:96])[0]
class_defs_size = struct.unpack('<I', dex_data[96:100])[0]
class_defs_off = struct.unpack('<I', dex_data[100:104])[0]

def read_uleb128(data, off):
    result = 0
    shift = 0
    while True:
        b = data[off]
        off += 1
        result |= (b & 0x7f) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, off

def get_string(idx):
    if idx >= string_ids_size: return ''
    off = struct.unpack('<I', dex_data[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    pos = off
    length, pos = read_uleb128(dex_data, pos)
    return dex_data[pos:pos+length].decode('utf-8', errors='replace')

def get_type_name(idx):
    if idx >= type_ids_size: return ''
    str_idx = struct.unpack('<I', dex_data[type_ids_off + idx*4 : type_ids_off + (idx+1)*4])[0]
    return get_string(str_idx)

def get_field_info(f_idx):
    class_idx, type_idx, name_idx = struct.unpack('<HHI', dex_data[field_ids_off + f_idx*8 : field_ids_off + (f_idx+1)*8])
    return get_type_name(class_idx), get_type_name(type_idx), get_string(name_idx)

def get_method_info(m_idx):
    class_idx, proto_idx, name_idx = struct.unpack('<HHI', dex_data[method_ids_off + m_idx*8 : method_ids_off + (m_idx+1)*8])
    return get_type_name(class_idx), get_string(name_idx)

target_classes = [
    'Lcom/chinatsp/custom/PageChangeHandler;',
    'Lcom/chinatsp/custom/view/NavigationBarLeft;',
    'Lcom/chinatsp/custom/view/NavigationBarRight;'
]

print("Scanning classes...")
for c_idx in range(class_defs_size):
    c_off = class_defs_off + c_idx * 32
    class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off = struct.unpack('<IIIIIIII', dex_data[c_off:c_off+32])
    cname = get_type_name(class_idx)
    if cname in target_classes:
        print(f"\n========================================================")
        print(f"CLASS: {cname} (class_idx: {class_idx})")
        print(f"Superclass: {get_type_name(superclass_idx)}")
        print(f"class_data_off: 0x{class_data_off:X}, static_values_off: 0x{static_values_off:X}")
        
        if class_data_off == 0:
            continue
            
        pos = class_data_off
        num_static_fields, pos = read_uleb128(dex_data, pos)
        num_instance_fields, pos = read_uleb128(dex_data, pos)
        num_direct_methods, pos = read_uleb128(dex_data, pos)
        num_virtual_methods, pos = read_uleb128(dex_data, pos)
        
        print(f"Static fields: {num_static_fields}, Instance fields: {num_instance_fields}")
        print(f"Direct methods: {num_direct_methods}, Virtual methods: {num_virtual_methods}")
        
        curr_f_idx = 0
        for _ in range(num_static_fields):
            f_diff, pos = read_uleb128(dex_data, pos)
            f_flags, pos = read_uleb128(dex_data, pos)
            curr_f_idx += f_diff
            c_f, t_f, n_f = get_field_info(curr_f_idx)
            print(f"  [Static Field] {n_f} : {t_f}")
            
        curr_f_idx = 0
        for _ in range(num_instance_fields):
            f_diff, pos = read_uleb128(dex_data, pos)
            f_flags, pos = read_uleb128(dex_data, pos)
            curr_f_idx += f_diff
            c_f, t_f, n_f = get_field_info(curr_f_idx)
            print(f"  [Instance Field] {n_f} : {t_f}")
            
        def parse_methods_list(count, label, current_pos):
            curr_m_idx = 0
            for _ in range(count):
                m_diff, current_pos = read_uleb128(dex_data, current_pos)
                m_flags, current_pos = read_uleb128(dex_data, current_pos)
                code_off, current_pos = read_uleb128(dex_data, current_pos)
                curr_m_idx += m_diff
                c_m, n_m = get_method_info(curr_m_idx)
                print(f"  [{label}] {n_m}() (code_off: 0x{code_off:X})")
                
                if code_off != 0:
                    reg_size, ins_size, outs_size, tries_size, debug_off, insns_size = struct.unpack('<HHHHII', dex_data[code_off:code_off+16])
                    insns_bytes = dex_data[code_off+16 : code_off+16 + insns_size*2]
                    
                    strings_in_method = []
                    i = 0
                    while i < len(insns_bytes) - 4:
                        op = insns_bytes[i]
                        # 0x1a = const-string (2 bytes: op, vAA; followed by string@BBBB)
                        if op == 0x1a:
                            s_idx = struct.unpack('<H', insns_bytes[i+2:i+4])[0]
                            s_val = get_string(s_idx)
                            if s_val and len(s_val) < 200:
                                strings_in_method.append(s_val)
                            i += 4
                        elif op == 0x1b and i < len(insns_bytes) - 6: # const-string/jumbo
                            s_idx = struct.unpack('<I', insns_bytes[i+2:i+6])[0]
                            s_val = get_string(s_idx)
                            if s_val and len(s_val) < 200:
                                strings_in_method.append(s_val)
                            i += 6
                        else:
                            i += 2
                    if strings_in_method:
                        print(f"      -> STRINGS: {strings_in_method}")
            return current_pos

        pos = parse_methods_list(num_direct_methods, "Direct Method", pos)
        pos = parse_methods_list(num_virtual_methods, "Virtual Method", pos)
