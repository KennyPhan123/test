#!/usr/bin/env python3
"""
rimstrip.py - Cắt bỏ khỏi file save những vật thể KHÔNG ảnh hưởng sinh tồn dài hạn.
Có kiểm tra toàn vẹn tham chiếu: vật thể nào còn được chỗ khác trỏ tới thì được GIỮ LẠI.

Dùng: python3 tools/rimstrip.py <save.rws> -o <out.rws> [--keep-grass] [--dry-run]
"""
import sys, os, re, base64, zlib
import xml.etree.ElementTree as ET

DECOR_PLANT = {'Plant_Grass','Plant_TallGrass','Plant_Brambles','Plant_Bush','Plant_Dandelion',
               'Plant_Reeds','Plant_Bulrush','Plant_LilyPad'}
DECOR_BUILD = {'AncientShoppingCart','AncientBarrel','AncientVendingMachine','Urn','Column',
               'AncientFence','AncientRustedJeep','SteleGrand','SteleLarge','Table2x2c',
               'AncientPipelineSection','AncientRazorWire','AncientWarwalkerFoot',
               'AncientExostriderLeg','AncientExostriderHead','AncientExostriderCannon',
               'AncientExostriderRemains','AncientATM'}
JUNK_CLASS = {'Filth', 'DeadPlant'}

def tag(e): return e.tag.split('}')[-1]
def txt(e, p):
    c = e.find(p)
    return c.text if c is not None and c.text is not None else None

def removep(t, keep_grass):
    d = txt(t, 'def') or ''
    cls = t.get('Class', '')
    if cls in JUNK_CLASS or d == 'SmashedStump': return True, 'rác/cây chết'
    if not keep_grass and cls == 'Plant' and d in DECOR_PLANT: return True, 'cỏ trang trí'
    if d in DECOR_BUILD: return True, 'trang trí đền cổ'
    return False, None

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[sys.argv.index('-o')+1] if '-o' in sys.argv else None
    keep_grass = '--keep-grass' in sys.argv
    dry = '--dry-run' in sys.argv

    print('Đọc %s ...' % src)
    tree = ET.parse(src); root = tree.getroot()
    things_el = root.find('game/maps/li/things')
    kids = list(things_el)
    print('  %d thing' % len(kids))

    cand = []           # (index, element, lý do, id)
    for i, t in enumerate(kids):
        r, why = removep(t, keep_grass)
        if r: cand.append((i, t, why, txt(t, 'id') or ''))

    print('  ứng viên xoá: %d' % len(cand))

    # ── giải nén compressedThingMapDeflate để kiểm tra tham chiếu luôn ──
    blob_text = ''
    for el in root.iter():
        if tag(el) == 'compressedThingMapDeflate' and el.text:
            try:
                blob_text = zlib.decompress(base64.b64decode(el.text.strip())).decode('utf8','ignore')
            except Exception: pass
    print('  compressedThingMapDeflate giải nén: %d ký tự' % len(blob_text))

    # ── Vòng lặp: xoá → kiểm tra → khôi phục cái còn bị trỏ tới ──
    to_drop = [c for c in cand]
    round_no = 0
    while True:
        round_no += 1
        drop_idx = {c[0] for c in to_drop}
        things_el[:] = [t for i, t in enumerate(kids) if i not in drop_idx]
        body = ET.tostring(root, encoding='unicode')
        bad = [c for c in to_drop if c[3] and (c[3] in body or c[3] in blob_text)]
        if not bad: break
        print('  vòng %d: %d vật thể vẫn bị tham chiếu → khôi phục' % (round_no, len(bad)))
        for c in bad[:10]: print('      giữ lại %s (%s)' % (c[3], c[2]))
        badset = {c[0] for c in bad}
        to_drop = [c for c in to_drop if c[0] not in badset]
        if not to_drop: break

    drop_idx = {c[0] for c in to_drop}
    things_el[:] = [t for i, t in enumerate(kids) if i not in drop_idx]
    from collections import Counter
    print('  đã xoá: %d  (%s)' % (len(to_drop), dict(Counter(c[2] for c in to_drop))))
    print('  còn lại: %d thing' % len(list(things_el)))

    if dry or not out:
        print('--dry-run: không ghi file'); return

    s = ET.tostring(root, encoding='unicode')
    s = '<?xml version="1.0" encoding="utf-8"?>\n' + s
    with open(out, 'w', encoding='utf-8', newline='\r\n') as f: f.write(s)
    print('Đã ghi %s' % out)

if __name__ == '__main__':
    main()
