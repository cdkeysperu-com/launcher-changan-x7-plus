# -*- coding: utf-8 -*-
"""
DUMP COMPLETO Y DESENSAMBLADO DE TODAS LAS FUNCIONES DE PageChangeHandler
"""
import zipfile
import struct
import os

sysui = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\oem_factory_backup\F202_SystemUI.apk"
OUTPUT = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\PageChangeHandler_full_methods.txt"

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

# Opcodes mapping for key Dalvik instructions
OPCODES = {
    0x00: "nop",
    0x01: "move",
    0x0e: "return-void",
    0x0f: "return",
    0x12: "const/4",
    0x13: "const/16",
    0x14: "const",
    0x15: "const/high16",
    0x1a: "const-string",
    0x1b: "const-string/jumbo",
    0x1c: "const-class",
    0x22: "new-instance",
    0x23: "new-array",
    0x28: "goto",
    0x38: "if-eqz",
    0x39: "if-nez",
    0x3a: "if-ltz",
    0x3b: "if-gez",
    0x3c: "if-gtz",
    0x3d: "if-lez",
    0x32: "if-eq",
    0x33: "if-ne",
    0x34: "if-lt",
    0x35: "if-ge",
    0x36: "if-gt",
    0x37: "if-le",
    0x52: "iget-object",
    0x54: "sget-object",
    0x59: "iput-object",
    0x5b: "sput-object",
    0x6e: "invoke-virtual",
    0x6f: "invoke-super",
    0x70: "invoke-direct",
    0x71: "invoke-static",
    0x72: "invoke-interface"
}

with open(OUTPUT, "w", encoding="utf-8") as out:
    for c_idx in range(class_defs_size):
        c_off = class_defs_off + c_idx * 32
        class_idx, access_flags, superclass_idx, interfaces_off, source_file_idx, annotations_off, class_data_off, static_values_off = struct.unpack('<IIIIIIII', dex_data[c_off:c_off+32])
        cname = get_type_name(class_idx)
        if cname != 'Lcom/chinatsp/custom/PageChangeHandler;':
            continue
            
        out.write(f"CLASS: {cname}\n")
        out.write(f"Superclass: {get_type_name(superclass_idx)}\n\n")
        
        pos = class_data_off
        num_static_fields, pos = read_uleb128(dex_data, pos)
        num_instance_fields, pos = read_uleb128(dex_data, pos)
        num_direct_methods, pos = read_uleb128(dex_data, pos)
        num_virtual_methods, pos = read_uleb128(dex_data, pos)
        
        # Read fields
        curr_f_idx = 0
        for _ in range(num_static_fields):
            f_diff, pos = read_uleb128(dex_data, pos)
            f_flags, pos = read_uleb128(dex_data, pos)
            curr_f_idx += f_diff
            c_f, t_f, n_f = get_field_info(curr_f_idx)
            out.write(f"static field {n_f} : {t_f}\n")
            
        curr_f_idx = 0
        for _ in range(num_instance_fields):
            f_diff, pos = read_uleb128(dex_data, pos)
            f_flags, pos = read_uleb128(dex_data, pos)
            curr_f_idx += f_diff
            c_f, t_f, n_f = get_field_info(curr_f_idx)
            out.write(f"instance field {n_f} : {t_f}\n")
            
        out.write("\n" + "="*80 + "\n")
        
        def disassemble_methods(count, label, current_pos):
            curr_m_idx = 0
            for _ in range(count):
                m_diff, current_pos = read_uleb128(dex_data, current_pos)
                m_flags, current_pos = read_uleb128(dex_data, current_pos)
                code_off, current_pos = read_uleb128(dex_data, current_pos)
                curr_m_idx += m_diff
                c_m, n_m = get_method_info(curr_m_idx)
                
                out.write(f"\nMETHOD: {n_m}() (code_off: 0x{code_off:X})\n")
                if code_off == 0:
                    out.write("  [No Code / Native / Abstract]\n")
                    continue
                    
                reg_size, ins_size, outs_size, tries_size, debug_off, insns_size = struct.unpack('<HHHHII', dex_data[code_off:code_off+16])
                out.write(f"  registers: {reg_size}, ins: {ins_size}, outs: {outs_size}, insns_size: {insns_size}\n")
                
                insns_bytes = dex_data[code_off+16 : code_off+16 + insns_size*2]
                
                pc = 0
                while pc < len(insns_bytes):
                    op = insns_bytes[pc]
                    op_name = OPCODES.get(op, f"op_{op:02x}")
                    
                    details = ""
                    step = 2
                    if op in [0x1a]: # const-string vAA, string@BBBB
                        if pc + 4 <= len(insns_bytes):
                            s_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
                            details = f'"{get_string(s_idx)}"'
                            step = 4
                    elif op in [0x1b]: # const-string/jumbo vAA, string@BBBBBBBB
                        if pc + 6 <= len(insns_bytes):
                            s_idx = struct.unpack('<I', insns_bytes[pc+2:pc+6])[0]
                            details = f'"{get_string(s_idx)}"'
                            step = 6
                    elif op in [0x1c, 0x22]: # const-class / new-instance
                        if pc + 4 <= len(insns_bytes):
                            t_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
                            details = get_type_name(t_idx)
                            step = 4
                    elif op in [0x52, 0x54, 0x59, 0x5b]: # field get/put
                        if pc + 4 <= len(insns_bytes):
                            f_idx = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
                            c_f, t_f, n_f = get_field_info(f_idx)
                            details = f"{c_f}->{n_f}:{t_f}"
                            step = 4
                    elif op in [0x6e, 0x6f, 0x70, 0x71, 0x72]: # invoke
                        if pc + 6 <= len(insns_bytes):
                            m_idx_ref = struct.unpack('<H', insns_bytes[pc+2:pc+4])[0]
                            c_ref, n_ref = get_method_info(m_idx_ref)
                            details = f"{c_ref}->{n_ref}()"
                            step = 6
                            
                    out.write(f"    [0x{pc:04x}] {op_name:<16} {details}\n")
                    pc += step
                    
            return current_pos

        pos = disassemble_methods(num_direct_methods, "Direct", pos)
        pos = disassemble_methods(num_virtual_methods, "Virtual", pos)

print(f"Extraccion completa guardada en {OUTPUT}")
