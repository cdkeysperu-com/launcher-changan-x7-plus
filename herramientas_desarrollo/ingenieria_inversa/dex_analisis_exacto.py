# -*- coding: utf-8 -*-
import zipfile
import struct
import os

sysui = r"C:\Users\axeln\OneDrive\Desktop\OSHAN X7 VIRTUAL\APK CHANGAN X7 PLUS\oem_factory_backup\F202_SystemUI.apk"

with zipfile.ZipFile(sysui, 'r') as z:
    dex_data = z.read('classes.dex')

magic = dex_data[:8]
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

print(f"Strings: {string_ids_size}, Types: {type_ids_size}, Classes: {class_defs_size}")

def get_string(idx):
    if idx >= string_ids_size: return ''
    off = struct.unpack('<I', dex_data[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    pos = off
    length = 0
    shift = 0
    while True:
        b = dex_data[pos]
        pos += 1
        length |= (b & 0x7f) << shift
        if not (b & 0x80):
            break
        shift += 7
    return dex_data[pos:pos+length].decode('utf-8', errors='replace')

def get_type_name(idx):
    if idx >= type_ids_size: return ''
    str_idx = struct.unpack('<I', dex_data[type_ids_off + idx*4 : type_ids_off + (idx+1)*4])[0]
    return get_string(str_idx)

target_strings = [
    'showThirdAppFullScreen', 'hideThirdAppFullScreen', 
    'mFullScreenList', 'mWhiteList', 'mWhitelistedApps', 
    'LeftCarNavigationBar', 'RightCarNavigationBar',
    'com.chinatsp.action.FULL_SCREEN',
    'com.chinatsp.systemui.NAVI_PAGE',
    'showTopStatusBar', 'hideTopStatusBar',
    'navigationbar_left', 'navigationbar_right'
]

target_str_indices = {}
for i in range(string_ids_size):
    s = get_string(i)
    for ts in target_strings:
        if ts in s:
            target_str_indices[s] = i
            print(f"Found string [{s}] at index {i}")

print("\n--- Searching Method IDs ---")
matched_methods = []
for m_idx in range(method_ids_size):
    class_idx, proto_idx, name_idx = struct.unpack('<HHI', dex_data[method_ids_off + m_idx*8 : method_ids_off + (m_idx+1)*8])
    if name_idx in target_str_indices.values():
        cname = get_type_name(class_idx)
        mname = get_string(name_idx)
        print(f"Method #{m_idx}: {cname}->{mname}()")
        matched_methods.append((m_idx, cname, mname))

print("\n--- Searching Field IDs ---")
matched_fields = []
for f_idx in range(field_ids_size):
    class_idx, type_idx, name_idx = struct.unpack('<HHI', dex_data[field_ids_off + f_idx*8 : field_ids_off + (f_idx+1)*8])
    if name_idx in target_str_indices.values():
        cname = get_type_name(class_idx)
        ftype = get_type_name(type_idx)
        fname = get_string(name_idx)
        print(f"Field #{f_idx}: {cname}->{fname} : {ftype}")
        matched_fields.append((f_idx, cname, fname))
