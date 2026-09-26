#!/usr/bin/env python3
"""
rimstate.py - Trích xuất TOÀN BỘ trạng thái game từ 1 file save RimWorld (.rws).

Dung lượng:  python3 tools/rimstate.py <duong_dan_save.rws> [-o report.md]

Hoạt động với save XML thường và save nén gzip.
Tự động phát hiện colonist trên mọi map + colonist đang ở caravan (world pawns).
"""
import sys, os, re, gzip, base64, struct, zlib
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

# ─────────────────────────────────────────────────────────────────────
# Thứ tự WorkTypeDef trong RimWorld 1.6 (Core 20 + Biotech/Anomaly/Odyssey).
# LƯU Ý: mods thêm work type sẽ được nối THÊM vào cuối mảng (chỉ mục >= 23).
# ─────────────────────────────────────────────────────────────────────
WORKTYPES = ['Firefighter','Patient','Doctor','PatientBedRest','BasicWorker','Warden',
             'Handling','Cooking','Hunting','Construction','Growing','Mining','PlantCutting',
             'Smithing','Tailoring','Art','Crafting','Hauling','Cleaning','Research',
             'Childcare[Biotech]','DarkStudy[Anomaly]','Fishing[Odyssey]']
TICKS_DAY, TICKS_HOUR, TICKS_YEAR = 60000, 2500, 3600000
DESIG2WORK = {'Mine':'Mining','HarvestPlant':'PlantCutting','CutPlant':'PlantCutting',
              'Hunt':'Hunting','Deconstruct':'Construction','SmoothFloor':'Construction',
              'SmoothWall':'Construction','BuildRoof':'Construction','RemoveRoof':'Construction',
              'Strip':'Hauling','Haul':'Hauling','FellTree':'PlantCutting'}
RANGED = ('Gun_', 'Bow_', 'Pila', 'NerveSpear', 'Beam')

def tag(e): return e.tag.split('}')[-1]
def T(e, p, d=None):
    c = e.find(p) if e is not None else None
    return c.text if c is not None and c.text is not None else d
def P(s):
    m = re.match(r'\((\d+), 0, (\d+)\)', s or '')
    return (int(m.group(1)), int(m.group(2))) if m else None

def load_save(path):
    with open(path, 'rb') as f: head = f.read(2)
    if head == b'\x1f\x8b':
        with gzip.open(path, 'rb') as f: data = f.read()
        return ET.fromstring(data), 'gzip'
    return ET.parse(path).getroot(), 'plain'

def decode_recorder(raw):
    try:
        b = base64.b64decode(raw)
        try: b = zlib.decompress(b)
        except Exception: pass
        if len(b) >= 4:
            return [round(v, 1) for v in struct.unpack('<%df' % (len(b)//4), b[:len(b)//4*4])]
    except Exception: pass
    return None

# ═══════════════════════════════════════════════════════════════════════
def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    path = sys.argv[1]
    out = sys.argv[sys.argv.index('-o')+1] if '-o' in sys.argv else None
    root, enc = load_save(path)
    G = root.find('game')
    O = []
    def w(s=''): O.append(s)

    # ── 1. THIẾT LẬP ────────────────────────────────────────────────
    meta = root.find('meta')
    w('# BÁO CÁO TRẠNG THÁI GAME — `%s`' % os.path.basename(path))
    w(); w('Nguồn: `%s` (định dạng %s, %.1f MB)' % (path, enc, os.path.getsize(path)/1e6))
    w()
    w('## 1. THIẾT LẬP'); w()
    w('| Mục | Giá trị |'); w('|---|---|')
    w('| Phiên bản | %s |' % T(meta, 'gameVersion'))
    w('| Mods | %s |' % ', '.join(x.text for x in (meta.find('modNames') or [])))
    w('| Kịch bản | %s |' % T(G.find('scenario'), 'name'))
    w('| Storyteller | %s / %s |' % (T(G.find('storyteller'), 'def'), T(G.find('storyteller'), 'difficulty')))
    w('| Manual priorities | %s |' % T(G.find('playSettings'), 'useWorkPriorities'))
    w('| Learning helper | %s |' % T(G.find('playSettings'), 'showLearningHelper'))
    w('| Số map | %d |' % len(list(G.find('maps'))))
    w('| Quest | %d |' % (len(list(G.find('questManager').find('quests'))) if G.find('questManager') is not None else 0))
    sw = G.find('storyWatcher')
    w('| Số đột kích | %s |' % (T(sw.find('statsRecord'), 'numRaidsEnemy') if sw is not None else '?'))

    # ── 2. THỜI GIAN ─────────────────────────────────────────────────
    tm = G.find('tickManager')
    tg = int(T(tm, 'ticksGame', 0)); start = int(T(tm, 'gameStartAbsTick', 0))
    yr0 = int(T(tm, 'startingYear', 5500)); abs_t = start + tg
    season = T(G.find('dateNotifier'), 'lastSeason') or '?'
    w(); w('## 2. THỜI GIAN & MÔI TRƯỜNG'); w()
    w('| Mục | Giá trị |'); w('|---|---|')
    w('| Tuổi thuộc địa | %s tick = **%d ngày %d giờ** |' % (tg, tg//TICKS_DAY, (tg%TICKS_DAY)//TICKS_HOUR))
    w('| Năm | **%d** |' % (yr0 + abs_t//TICKS_YEAR))
    w('| Ngày trong năm | %d / 60 |' % ((abs_t % TICKS_YEAR)//TICKS_DAY + 1))
    w('| Mùa | **%s** |' % season)
    w('| Giờ | ~%02d:00 |' % ((abs_t % TICKS_DAY)//TICKS_HOUR))
    for i, m in enumerate(G.find('maps')):
        wm = m.find('weatherManager')
        w('| Thời tiết (map %d) | %s |' % (i, T(wm, 'curWeather')))

    # ── 3. TÀI SẢN ───────────────────────────────────────────────────
    w(); w('## 3. TÀI SẢN & TÂM TRẠNG (lịch sử)'); w()
    for grp in G.find('history').find('autoRecorderGroups'):
        for rec in grp.find('recorders'):
            for f in rec:
                if tag(f) in ('records', 'recordsDeflate'):
                    v = decode_recorder((f.text or '').strip())
                    if v and len(v) > 1:
                        w('- **%s / %s**: %s → **%s**' % (T(grp,'def'), T(rec,'def'),
                          ' → '.join(str(x) for x in v[:-1]), v[-1]))

    # ── 4. THU THẬP THỰC THỂ ─────────────────────────────────────────
    maps = list(G.find('maps'))
    allthings, thing_index = [], {}
    for mi, m in enumerate(maps):
        for t in m.find('things'):
            allthings.append((mi, t)); thing_index[T(t,'id')] = (mi, t)
    worldpawns = []
    wp = G.find('world').find('worldPawns')
    if wp is not None:
        for c in wp:
            if tag(c) == 'pawns':
                for p in c: worldpawns.append(p)
        thing_index.update({T(p,'id'): ('world', p) for p in worldpawns})

    facman = G.find('world').find('factionManager')
    player_f = None
    for f in facman.find('allFactions'):
        if T(f,'def') == 'PlayerColony': player_f = 'Faction_' + T(f,'loadID')
    colonists = [(mi,t) for mi,t in allthings
                 if t.get('Class')=='Pawn' and T(t,'def')=='Human' and T(t,'faction')==player_f]
    colonists += [('world',p) for p in worldpawns if T(p,'def')=='Human' and T(p,'faction')==player_f]

    # ── 5. COLONIST ──────────────────────────────────────────────────
    priorities, timetables, col_by_name = {}, {}, {}
    for mi, t in colonists:
        nm = t.find('name'); nick = T(nm,'nick') or ''
        who = '%s %s' % (nick or T(nm,'first'), T(nm,'last')) if nick != T(nm,'first') else '%s %s' % (T(nm,'first'), T(nm,'last'))
        w(); w('## %s  (%s)' % (who, T(t,'id'))); w()
        st = t.find('story')
        w('| | |'); w('|---|---|')
        w('| Tuổi / Giới | %.1f tuổi · %s |' % (int(T(t.find('ageTracker'),'ageBiologicalTicks',0))/TICKS_YEAR,
                                                 T(t,'gender') or 'Nam'))
        w('| Vị trí | %s%s |' % (T(t,'pos') or '—', '' if mi=='world' else ' (map %s)'%mi))
        w('| Xuất thân | %s / %s |' % (T(st,'childhood'), T(st,'adulthood')))
        w('| Tính cách | %s |' % ', '.join('%s%s'%(T(x,'def'), '(%s)'%T(x,'degree') if T(x,'degree') else '')
                                          for x in st.find('traits').find('allTraits')))
        w('| Chủng | %s |' % T(t.find('genes'),'xenotype'))
        jobs = t.find('jobs'); cj = jobs.find('curJob') if jobs is not None else None
        w('| ĐANG LÀM | **%s** %s |' % (T(cj,'def') if cj is not None else '?',
                                        T(cj,'targetA') if cj is not None else ''))
        w('| Giường | %s |' % T(t.find('ownership'),'ownedBed'))
        w('| medCare | %s |' % T(t.find('playerSettings'),'medCare'))
        w()
        w('**Kỹ năng:**'); w(); w('| Kỹ năng | Lv | Đam mê |'); w('|---|---|---|')
        for s in t.find('skills').find('skills'):
            lv = T(s,'level','0'); ps = T(s,'passion') or '—'
            w('| %s%s | %s | %s |' % (T(s,'def'), ' ⭐' if ps=='Minor' else (' ⭐⭐' if ps=='Major' else ''), lv, ps))
        hs = t.find('healthTracker').find('hediffSet')
        w(); w('**Sức khoẻ (%d hediff):**' % len(list(hs.find('hediffs'))))
        if len(list(hs.find('hediffs'))):
            w(); w('| Loại | Độ nặng | Chi tiết |'); w('|---|---|---|')
            for h in hs.find('hediffs'):
                w('| %s | %s | %s |' % (T(h,'def'), T(h,'severity'),
                  (T(h,'combatLogText') or T(h,'sourceLabel') or '')[:70]))
        else: w(); w('_Khoẻ mạnh, không có vết thương_')
        w(); w('**Nhu cầu & tâm trạng:**'); w()
        for n in t.find('needs').find('needs'):
            if T(n,'def')=='Mood':
                w('- **Mood %.1f%%** · ' % (float(T(n,'curLevel',0))*100) +
                  ' · '.join(T(m,'def') for m in n.find('thoughts').find('memories').find('memories')))
            else:
                w('- %s: %.1f%%' % (T(n,'def'), float(T(n,'curLevel',0))*100))
        ap = t.find('apparel').find('wornApparel').find('innerList')
        w(); w('**Trang bị:** ' + (', '.join('%s(%s)'%(T(a,'def'),T(a,'stuff') or '—') for a in ap) or '_trần trụi_'))
        eq = t.find('equipment').find('equipment').find('innerList')
        w(); w('**Vũ khí:** ' + (', '.join(T(a,'def') for a in eq) if eq is not None and len(eq) else '_không có_'))
        inv = t.find('inventory').find('innerContainer').find('innerList')
        w(); w('**Túi:** ' + (', '.join('%s x%s'%(T(a,'def'),T(a,'stackCount')) for a in inv)
                             if inv is not None and len(inv) else '_rỗng_'))
        ct = t.find('carryTracker').find('innerContainer').find('innerList')
        if ct is not None and len(ct):
            w(); w('**Đang xách:** ' + ', '.join('%s x%s'%(T(a,'def'),T(a,'stackCount')) for a in ct))
        rel = t.find('social').find('directRelations')
        if rel is not None and len(list(rel)):
            w(); w('**Quan hệ:** ' + ', '.join('%s→%s'%(T(r,'def'),T(r,'otherPawn')) for r in rel))
        p = t.find('workSettings').find('priorities').find('vals')
        priorities[who] = [x.text for x in p]
        col_by_name[who] = t
        tb = t.find('timetable').find('times')
        timetables[who] = [x.text for x in tb]

    # ── 6. MA TRẬN CÔNG VIỆC ─────────────────────────────────────────
    if priorities:
        w(); w('## MA TRẬN ƯU TIÊN CÔNG VIỆC'); w()
        n = max(len(v) for v in priorities.values())
        if n != len(WORKTYPES):
            w('> ⚠ Save có **%d** work type (vanilla+DLC = %d). %d mục cuối là do **mod** thêm '
              '(được nối vào cuối mảng), không giải mã được tên.' % (n, len(WORKTYPES), n-len(WORKTYPES)))
            w()
        names = [who for who in priorities]
        w('| # | Công việc | ' + ' | '.join(names) + ' |')
        w('|---|---|' + '---|'*len(names))
        for i in range(n):
            nm = WORKTYPES[i] if i < len(WORKTYPES) else '`Mod#%d`' % i
            row = []
            for who in names:
                v = priorities[who][i] if i < len(priorities[who]) else '?'
                row.append('❌0' if v=='0' else ('**%s**'%v if v=='1' else v))
            w('| %d | %s | %s |' % (i, nm, ' | '.join(row)))
        w(); w('*(0 = tắt; 1 = ưu tiên cao nhất)*')

    # ── 7. LỊCH TRÌNH ────────────────────────────────────────────────
    if timetables:
        w(); w('## LỊCH TRÌNH'); w()
        w('| Colonist | ' + ' | '.join(str(h) for h in range(24)) + ' |')
        w('|---|' + '---|'*24)
        for who, tt in timetables.items():
            w('| %s | %s |' % (who, ' | '.join('😴' if x=='Sleep' else
                                               ('🛠' if x=='Work' else '·') for x in tt)))

    # ── 8. BẢN ĐỒ ────────────────────────────────────────────────────
    for mi, m in enumerate(maps):
        w(); w('## BẢN ĐỒ %d' % mi); w()
        things = [t for mm, t in allthings if mm == mi]
        bld = Counter(T(t,'def') for t in things if t.get('Class','').startswith('Building'))
        mine = [t for t in things if T(t,'faction')==player_f and t.get('Class','').startswith('Building')]
        w('**Công trình của người chơi (%d):**' % len(mine)); w()
        w('| Công trình | Số lượng | Vị trí |'); w('|---|---|---|')
        cc = Counter(T(t,'def') for t in mine)
        for d, k in sorted(cc.items()):
            w('| %s | %d | %s |' % (d, k, ', '.join(str(P(T(t,'pos'))) for t in mine
                                                     if T(t,'def')==d)[:90]))
        bp = [t for t in things if t.get('Class','').startswith('Blueprint')]
        if bp:
            w(); w('**Blueprint đang chờ (%d):** %s' % (len(bp), dict(Counter(T(t,'def') for t in bp))))
        des = m.find('designationManager').find('allDesignations')
        if des is not None and len(list(des)):
            w(); w('**Chỉ thị (%d):** %s' % (len(list(des)), dict(Counter(T(d,'def') for d in des))))
        zs = m.find('zoneManager').find('allZones')
        if zs is not None:
            w(); w('**Zone:** ' + '; '.join('%s (%s, %d ô, %s)' % (T(z,'label'), z.get('Class'),
                   len(list(z.find('cells'))), T(z,'plantDefToGrow') or '') for z in zs))
        stock = defaultdict(int)
        for t in things:
            if t.get('Class') in ('ThingWithComps','Medicine','Apparel','MinifiedThing'):
                stock[T(t,'def')] += int(T(t,'stackCount','1') or 1)
        w(); w('**Kho (top 15):**'); w(); w('| Vật phẩm | Tổng |'); w('|---|---|')
        for d, k in sorted(stock.items(), key=lambda x:-x[1])[:15]:
            w('| %s | %s |' % (d, k))

    # ── 9. NGHIÊN CỨU / BILLS ────────────────────────────────────────
    rm = G.find('researchManager')
    pr = rm.find('progress')
    keys = [x.text for x in pr.find('keys')]; vals = [x.text for x in pr.find('values')]
    done = [k for k,v in zip(keys,vals) if v not in (None,'','0','0.0')]
    w(); w('## NGHIÊN CỨU & SẢN XUẤT'); w()
    w('- **Đã xong (%d):** %s' % (len(done), ', '.join(done)))
    w('- **Đang nghiên cứu:** %s (tiến độ %s)' % (T(rm,'currentProj'), dict(zip(keys,vals)).get(T(rm,'currentProj'))))
    w(); w('**Bills:**')
    any_b = False
    for mm, t in allthings:
        if T(t,'faction')==player_f and t.find('billStack') is not None:
            bs = t.find('billStack').find('bills')
            if bs is not None:
                for b in bs:
                    any_b = True
                    w('  - %s @ %s: `%s` ×%s (%s) → %s' % (T(t,'def'), T(t,'pos'), T(b,'recipe'),
                      T(b,'targetCount'), T(b,'repeatMode'), T(b,'storeMode')))
    if not any_b: w('  _(không có bill nào)_')

    # ── 10. ĐỘNG VẬT / ĐE DOẠ ────────────────────────────────────────
    w(); w('## ĐỘNG VẬT'); w()
    for mm, t in allthings:
        if t.get('Class')=='Pawn' and T(t,'faction')==player_f and T(t,'def')!='Human':
            tr = t.find('training')
            wt = [i for i,v in enumerate(tr.find('wantedTrainables').find('vals')) if v.text=='True'] if tr is not None else []
            w('- **%s** (%s, %s) @ %s · huấn luyện bật: %s' % (
                (T(t.find('name'),'name') if t.find('name') is not None and len(t.find('name')) else T(t,'def')),
                T(t,'def'), T(t,'gender') or '?', T(t,'pos'), wt or 'không'))
    wild = Counter(T(t,'def') for mm,t in allthings if t.get('Class')=='Pawn' and not T(t,'faction'))
    w(); w('- **Hoang dã:** ' + ', '.join('%s×%d'%(d,k) for d,k in wild.most_common(15)))
    w(); w('## MỐI ĐE DOẠ'); w()
    for mm, t in allthings:
        if t.get('Class')=='Pawn' and T(t,'faction') not in (None, player_f):
            w('- **%s** (%s) phe %s @ %s · active=%s' % (T(t,'id'), T(t,'def'), T(t,'faction'),
              T(t,'pos'), T(t,'active')))

    # ── 11. PHE PHÁI ─────────────────────────────────────────────────
    fmap = {}
    for fi, f in enumerate(facman.find('allFactions')):
        fmap['Faction_' + (T(f,'loadID') or str(fi))] = '%s (%s)' % (T(f,'name') or '?', T(f,'def'))
    w(); w('## QUAN HỆ PHE PHÁI'); w()
    for f in facman.find('allFactions'):
        if T(f,'def')=='PlayerColony' and f.find('relations') is not None:
            for r in f.find('relations'):
                k = T(r,'kind') or 'Trung lập'
                w('- %-45s → %s%s' % (fmap.get(T(r,'other'), T(r,'other')), k,
                  ' (%s)'%T(r,'goodwill') if T(r,'goodwill') else ''))

    # ── 12. TỰ ĐỘNG PHÁT HIỆN NÚT THẮT ───────────────────────────────
    w(); w('## ⚠ NÚT THẮT TỰ ĐỘNG PHÁT HIỆN'); w()
    probs = []
    for i, nm in enumerate(WORKTYPES):
        base = nm.split('[')[0]
        if base in ('Firefighter','Patient','Doctor','PatientBedRest','BasicWorker'): continue
        on = [who for who, v in priorities.items() if i < len(v) and v[i] != '0']
        if i >= max(len(v) for v in priorities.values()): continue
        if not on:
            probs.append('🔴 **Không ai làm `%s`** (cả %d colonist đều = 0)' % (base, len(priorities)))
        elif len(on) == 1:
            probs.append('🟠 `%s` chỉ do **1 người** đảm nhiệm: %s' % (base, on[0]))
    for mi, m in enumerate(maps):
        things = [t for mm, t in allthings if mm == mi]
        des = m.find('designationManager').find('allDesignations')
        dcount = Counter(T(d,'def') for d in (des or []))
        for d, k in dcount.items():
            wt = DESIG2WORK.get(d)
            if wt:
                i = [j for j,n in enumerate(WORKTYPES) if n.split('[')[0]==wt]
                if i:
                    on = [who for who,v in priorities.items() if i[0] < len(v) and v[i[0]]!='0']
                    if not on:
                        probs.append('🔴 %d chỉ thị **%s** cần `%s` nhưng **không ai được gán**' % (k,d,wt))
        bp = [t for t in things if t.get('Class','').startswith('Blueprint')]
        if bp:
            ci = [j for j,n in enumerate(WORKTYPES) if n.split('[')[0]=='Construction'][0]
            on = [who for who,v in priorities.items() if ci < len(v) and v[ci]!='0']
            if not on:
                probs.append('🔴 **%d blueprint đang kẹt** — không ai có Construction' % len(bp))
            wood = sum(int(T(t,'stackCount','1') or 1) for t in things if T(t,'def')=='WoodLog')
            if wood < len(bp)*3:
                probs.append('🔴 **Chỉ còn %d gỗ** cho %d blueprint (cần ~%d)' % (wood, len(bp), len(bp)*5))
        meals = sum(int(T(t,'stackCount','1') or 1) for t in things
                    if T(t,'def','').startswith('Meal'))
        nc = len([1 for mm,t in colonists if mm==mi])
        if nc and meals < nc*8:
            probs.append('🟠 Thức ăn chỉ đủ ~%.1f ngày (%d bữa / %d colonist)' % (meals*0.9/(nc*1.6), meals, nc))
    for who, v in priorities.items():
        hi = [j for j,n in enumerate(WORKTYPES) if n.split('[')[0]=='Hunting']
        if hi and hi[0] < len(v) and v[hi[0]] != '0':
            t = col_by_name.get(who)
            if t is not None:
                eq = t.find('equipment').find('equipment').find('innerList')
                wp_ = [T(a,'def') for a in eq] if eq is not None and len(eq) else []
                if not any(x.startswith(RANGED) for x in wp_):
                    probs.append('🟠 %s được gán **Hunting** nhưng cầm vũ khí cận chiến (%s)' % (who, wp_ or 'không có'))
    cp = T(G.find('researchManager'),'currentProj')
    prog = dict(zip(keys,vals)).get(cp)
    if prog in (None,'','0','0.0'):
        probs.append('🟠 Nghiên cứu `%s` chưa có tiến độ (0)' % cp)
    if not probs: probs = ['✅ Không phát hiện nút thắt rõ ràng']
    for p in probs: w('- ' + p)

    txt = '\n'.join(O)
    if out:
        open(out, 'w', encoding='utf-8').write(txt)
        print('Đã ghi %s (%d dòng)' % (out, len(O)))
    else:
        print(txt)

if __name__ == '__main__':
    main()
