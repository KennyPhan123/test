#!/usr/bin/env python3
"""
rimbrief.py v2 — Bản state TỐI GIẢN nhưng CHỊU ĐƯỢC QUY MÔ LỚN (colony vài trăm giờ).

So với v1:
  • Phân loại sức khoẻ ĐÚNG: tách vết thương / cấy ghép-bionic / sẹo / bệnh mãn / nghiện
    (v1 đếm mọi hediff thành "vết thương" → sai nặng ở late game)
  • Thêm: tù nhân & nô lệ · mech · điện · quest · ý thức hệ · tước hiệu/psycast · gene
  • Thêm: dòng thời gian sự kiện (từ combatLogText của vết thương)
  • Chống phình: tự chuyển sang chế độ GỌN khi > 8 người; gom nhóm bills / thú;
    bỏ giới hạn top-14 của kho
  • Nhiều cảnh báo hơn: thiếu điện, thiếu bác sĩ, băng thông mech, tù nhân nổi loạn...

Dùng:  python3 tools/rimbrief.py <save.rws> [-o brief.md] [--json] [--full]
"""
import sys, os, json, re
from collections import Counter, defaultdict
from rimstate import (tag, T, P, load_save, decode_recorder, WORKTYPES,
                      TICKS_DAY, TICKS_HOUR, TICKS_YEAR, DESIG2WORK, RANGED)

ABBR = ['FF','PT','DR','BR','BAS','WRD','HND','COK','HNT','CON','GRW','MIN','PC',
        'SMI','TAI','ART','CRA','HAU','CLE','RES','CHI','DKS','FSH']
SKILL = {'Shooting':'Sho','Melee':'Mee','Construction':'Con','Mining':'Min','Cooking':'Cok',
         'Plants':'Pla','Animals':'Ani','Crafting':'Cra','Artistic':'Art','Medicine':'Med',
         'Social':'Soc','Intellectual':'Int'}
DANGEROUS = {'Megasloth','Rhinoceros','Warg','Lynx','Wolverine','Badger','Boomrat',
             'Bear_Grizzly','Bear_Polar','Cougar','Panther','Elephant','Thrumbo','Alphabeaver'}

# ── Phân loại sức khoẻ ────────────────────────────────────────────────
IMPLANT_HINT = ('Bionic','Archotech','Prosthetic','Implant','Painstopper','Happiness',
                'Circadian','Detoxifier','Coagulator','Immunoenhancer','Neurocalculator',
                'Psychic','Aesthetic','Learning','HealingEnhancer','NuclearStomach',
                'Reprocessor','Venom','DeathAcidifier','Joywire','Armorskin','Stoneskin',
                'ToughSkin','Steriliz','PregnancyPreventer','Exoskeleton','DrillArm',
                'ElbowBlade','KneeSpike','FleshTendril','HeartLung','Lung')
CHRONIC = {'Asthma','BadBack','Carcinoma','Dementia','Frail','Blindsight','Cataract',
           'ChronicPain','Arteriosclerosis','HeartArterialBlockage','Tuberculosis',
           'Alzheimer','DementiaSenile','GutWorms','HepatitisK','MuscleParasites',
           'SleepApnea','Apnea','BackPain','Cryptosickness','BloodRot','CreepingRot',
           'ResurrectionPsychosis','SensoryMechanites','SleepingSickness','ToxicBuildup',
           'WastingDisease','Blindness','Deafness','Paralysis','HeartAttack','Dementia',
           'Cirrhosis','ChemicalDamageSevere','OrganDecay','BadBack'}
PREGNANT = {'Pregnancy','Pregnant','Labor','LaborPushing','PregnancyLabor'}

def hediff_kind(h, tg):
    """Trả về (nhóm, tuổi_ngày, đã_băng, mô_tả)"""
    d = T(h,'def') or ''
    cls = h.get('Class') or ''
    sev = float(T(h,'severity',0) or 0)
    old = int(T(h,'ageTicks',0) or 0) / TICKS_DAY
    tend = T(h,'tendQuality')
    if cls in ('Hediff_Injury','Hediff_MissingPart'):
        if cls == 'Hediff_MissingPart' or any(x in d for x in IMPLANT_HINT):
            return 'implant', old, True, d
        return 'injury', old, tend is not None, d
    if cls == 'Hediff_Implant' or any(x in d for x in IMPLANT_HINT):
        return 'implant', old, True, d
    if 'Addiction' in cls or 'Addiction' in d:
        return 'addiction', old, True, d
    if d in PREGNANT or 'Pregnan' in d:
        return 'pregnant', old, True, d
    if d in CHRONIC:
        return 'chronic', old, True, d
    return 'condition', old, True, d

COLORS = re.compile(r'</?color[^>]*>')
def N(v):
    """RimWorld ghi null dưới dạng CHUỖI 'null' — phải chuẩn hoá thành None."""
    return None if v in (None, '', 'null', 'Null', 'NULL', 'False') else v

def clean_log(s):
    return COLORS.sub('', (s or '')).strip()

def role_of(t, pf):
    """colonist / slave / prisoner / mech"""
    f = T(t,'faction'); gd = t.find('guest')
    sf = N(T(gd,'slaveFaction')) if gd is not None else None
    hf = N(T(gd,'hostFaction')) if gd is not None else None
    kind = T(t,'kindDef') or ''
    d = T(t,'def') or ''
    if d.startswith('Mech_') or 'Mech' == kind: return 'mech'
    if f == pf:
        return 'slave' if sf else 'colonist'
    if hf == pf: return 'prisoner'
    return 'enemy'

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(__doc__); sys.exit(1)
    path = args[0]
    out = sys.argv[sys.argv.index('-o')+1] if '-o' in sys.argv else None
    as_json = '--json' in sys.argv
    force_full = '--full' in sys.argv

    root, _ = load_save(path); G = root.find('game')
    maps = list(G.find('maps'))
    things, tidx = [], {}
    for mi, m in enumerate(maps):
        for t in m.find('things'):
            things.append((mi, t)); tidx[T(t,'id')] = t
    worldpawns = []
    wp = G.find('world').find('worldPawns')
    if wp is not None:
        for c in wp:
            if tag(c) == 'pawns':
                for p in c: worldpawns.append(p)

    facman = G.find('world').find('factionManager')
    pf = next(('Faction_'+T(f,'loadID') for f in facman.find('allFactions')
               if T(f,'def')=='PlayerColony'), None)

    # ── phân loại sinh vật ────────────────────────────────────────────
    pawns = [('map%d'%mi if isinstance(mi,int) else mi, t)
             for mi,t in things if t.get('Class')=='Pawn']
    pawns += [('world', p) for p in worldpawns if p.get('Class')=='Pawn'
              or (T(p,'def')=='Human' and T(p,'faction')==pf)]
    mine_all = [x for x in pawns if T(x[1],'faction')==pf]
    cols    = [x for x in mine_all if role_of(x[1],pf)=='colonist' and T(x[1],'def')=='Human']
    slaves  = [x for x in mine_all if role_of(x[1],pf)=='slave']
    pris    = [x for x in pawns   if role_of(x[1],pf)=='prisoner']
    mechs   = [x for x in mine_all if role_of(x[1],pf)=='mech']
    animals = [x for x in mine_all if T(x[1],'def')!='Human' and role_of(x[1],pf)=='colonist']

    tm = G.find('tickManager')
    tg = int(T(tm,'ticksGame',0)); abs_t = int(T(tm,'gameStartAbsTick',0)) + tg
    yr  = int(T(tm,'startingYear',5500)) + abs_t // TICKS_YEAR
    day = (abs_t % TICKS_YEAR)//TICKS_DAY + 1
    hr  = (abs_t % TICKS_DAY)//TICKS_HOUR

    wealth = mood = None; mtrend = []
    for grp in G.find('history').find('autoRecorderGroups'):
        for rec in grp.find('recorders'):
            for f in rec:
                if tag(f) in ('records','recordsDeflate'):
                    v = decode_recorder((f.text or '').strip())
                    if not v: continue
                    if T(rec,'def')=='Wealth_Total': wealth = v[-1]
                    if T(rec,'def')=='ColonistMood': mood = v[-1]; mtrend = v[-3:]

    compact = (not force_full) and len(cols) > 8

    L = []
    def w(s=''): L.append(s)
    w('# STATE — `%s`' % os.path.basename(path))
    w()
    w('**Y%d %s d%d %02dh** · colony **%dd%dh** (tick %d) · %s/%s · %d map %s · %s · raids %s' % (
        yr, T(G.find('dateNotifier'),'lastSeason') or '?', day, hr,
        tg//TICKS_DAY, (tg%TICKS_DAY)//TICKS_HOUR, tg,
        T(G.find('storyteller'),'def'), T(G.find('storyteller'),'difficulty'),
        len(maps), T(maps[0].find('mapInfo'),'size') if maps else '',
        T(maps[0].find('weatherManager'),'curWeather') if maps else '',
        T(G.find('storyWatcher').find('statsRecord'),'numRaidsEnemy') if G.find('storyWatcher') is not None else '?'))
    w('**Wealth** %s · **Mood TB** %s %s · adaptation %s d' % (
        wealth, mood, ('▼' if len(mtrend)>1 and mtrend[-1]<mtrend[0] else '▲'),
        T(G.find('storyWatcher').find('watcherPopAdaptation'),'adaptDays') if G.find('storyWatcher') is not None else '?'))

    events = []   # (tick, mô tả) — dòng thời gian
    prio, sched, cbn = {}, {}, {}

    def fmt_pawn(mi, t, mark=''):
        nm = t.find('name')
        first = T(nm,'nick') or T(nm,'first')
        who = '%s %s' % (first, T(nm,'last'))
        age = int(T(t.find('ageTracker'),'ageBiologicalTicks',0))/TICKS_YEAR
        traits = ','.join(T(x,'def') for x in t.find('story').find('traits').find('allTraits'))
        sk = []
        for s in t.find('skills').find('skills'):
            d = T(s,'def'); lv = T(s,'level','0'); p = T(s,'passion')
            sk.append('%s%s%s' % (SKILL.get(d,d), lv, '*' if p=='Minor' else ('**' if p=='Major' else '')))
        # ── sức khoẻ: PHÂN LOẠI ──
        hs = t.find('healthTracker').find('hediffSet').find('hediffs')
        grp = defaultdict(list)
        if hs is not None:
            for h in hs:
                k, old, tended, d = hediff_kind(h, tg)
                grp[k].append((d, float(T(h,'severity',0) or 0), old, tended, h))
                lg = clean_log(T(h,'combatLogText'))
                if lg:
                    events.append((int(T(h,'tickAdded',0) or 0), lg))
        parts = []
        inj = grp.get('injury',[])
        if inj:
            tot = sum(x[1] for x in inj)
            unt = [x for x in inj if not x[3]]
            fresh = [x for x in inj if x[2] < 3]
            parts.append('%d VẾT THƯƠNG (tổng %.1f%s%s)' % (
                len(inj), tot,
                ', %d mới' % len(fresh) if fresh else '',
                ', **%d chưa băng bó**' % len(unt) if unt else ''))
            parts.append('   - chi tiết: %s' % '; '.join(
                '%s %.1f%s' % (d, v, ' (cũ %.0fd)'%o if o>=3 else '') for d,v,o,_,_ in inj[:6]))
        if grp.get('implant'):
            parts.append('%d cấy ghép/bionic' % len(grp['implant']))
        if grp.get('chronic'):
            parts.append('%d bệnh mãn: %s' % (len(grp['chronic']),
                ','.join(d for d,_,_,_,_ in grp['chronic'][:5])))
        if grp.get('addiction'):
            parts.append('%d nghiện: %s' % (len(grp['addiction']),
                ','.join(d for d,_,_,_,_ in grp['addiction'])))
        if grp.get('pregnant'):
            parts.append('**có thai**')
        if grp.get('condition'):
            parts.append('%d tình trạng: %s' % (len(grp['condition']),
                ','.join(d for d,_,_,_,_ in grp['condition'][:5])))
        hp = '\n'.join(parts) if parts else 'khoẻ'
        nd = {T(n,'def'): float(T(n,'curLevel',0) or 0) for n in t.find('needs').find('needs')}
        appr = t.find('apparel').find('wornApparel').find('innerList')
        armor = [T(a,'def').replace('Apparel_','') for a in appr] if appr is not None else []
        eq = t.find('equipment').find('equipment').find('innerList')
        wpn = [T(a,'def') for a in eq] if eq is not None and len(eq) else []
        inv = t.find('inventory').find('innerContainer').find('innerList')
        cj = t.find('jobs').find('curJob')
        # ── Royalty / psycast / gene ──
        extra = []
        ry = t.find('royalty')
        if ry is not None:
            tt = [x for x in ry.find('titles')] if ry.find('titles') is not None else []
            if tt:
                extra.append('tước hiệu: %s' % ','.join(T(x,'def') or tag(x) for x in tt))
            fv = ry.find('favor')
            ks = [x.text for x in fv.find('keys')] if fv is not None and fv.find('keys') is not None else []
            vs = [x.text for x in fv.find('values')] if fv is not None and fv.find('values') is not None else []
            if ks:
                extra.append('ân sủng: %s' % ','.join('%s=%s'%(k,v) for k,v in zip(ks,vs)))
            pm = ry.find('permits')
            if pm is not None and len(list(pm)):
                extra.append('%d permit' % len(list(pm)))
        ab = t.find('abilities')
        abs_ = [x for x in ab.find('abilities')] if ab is not None and ab.find('abilities') is not None else []
        if abs_:
            extra.append('psycast: %s' % ','.join(T(x,'def') or tag(x) for x in abs_[:6]))
        gn = t.find('genes')
        if gn is not None:
            eg = gn.find('endogenes'); xg = gn.find('xenogenes')
            ne = len(list(eg)) if eg is not None else 0
            nx = len(list(xg)) if xg is not None else 0
            if ne or nx: extra.append('gene: %d nội sinh + %d ngoại sinh' % (ne, nx))
        rel = t.find('social').find('directRelations')
        if compact:
            w('**%s**%s `%s` · %s %.0ft · %s · %s · %s' % (
                who, mark, T(t,'id'), T(t,'gender') or 'M', age,
                T(gn,'xenotype') or T(t,'def'), traits or '—',
                '%s %s'%(mi,T(t,'pos')) if mi!='world' else 'NGOÀI MAP'))
            w('- Kỹ năng: %s' % ' '.join(sk))
            w('- %s' % hp.replace('\n',' | '))
            w('- Mood%.0f Food%.0f Rest%.0f Joy%.0f · %s | Cầm: %s | Đang: %s%s' % (
                nd.get('Mood',0)*100, nd.get('Food',0)*100, nd.get('Rest',0)*100, nd.get('Joy',0)*100,
                ','.join(armor) or 'trần', ','.join(wpn) or 'không',
                T(cj,'def') if cj is not None else '?',
                ' · '+' · '.join(extra) if extra else ''))
        else:
            w(); w('**%s**%s `%s` · %s %.0f tuổi · %s · %s · %s' % (
                who, mark, T(t,'id'), T(t,'gender') or 'M', age, T(gn,'xenotype') or T(t,'def'),
                traits or '—', '%s %s'%(mi,T(t,'pos')) if mi!='world' else 'NGOÀI MAP (caravan/thế giới)'))
            w('- Kỹ năng: %s' % ' '.join(sk))
            w('- HP: %s' % hp)
            w('- Nhu cầu: Mood%.0f Food%.0f Rest%.0f Joy%.0f · thoughts: %s' % (
                nd.get('Mood',0)*100, nd.get('Food',0)*100, nd.get('Rest',0)*100, nd.get('Joy',0)*100,
                ','.join(T(m,'def') for n in t.find('needs').find('needs') if T(n,'def')=='Mood'
                         for m in n.find('thoughts').find('memories').find('memories'))))
            w('- Trang bị: %s | Vũ khí: %s | Túi: %s' % (
                ','.join(armor) or 'trần', ','.join(wpn) or 'không',
                ','.join('%s×%s'%(T(a,'def'),T(a,'stackCount')) for a in inv) if inv is not None and len(inv) else '—'))
            w('- Đang làm: **%s** %s | Giường: %s | medCare: %s' % (
                T(cj,'def') if cj is not None else '?', T(cj,'targetA') if cj is not None else '',
                T(t.find('ownership'),'ownedBed'), T(t.find('playerSettings'),'medCare')))
            if extra: w('- Khác: %s' % ' · '.join(extra))
            if rel is not None and len(list(rel)):
                w('- Quan hệ: %s' % ','.join('%s→%s'%(T(r,'def'),T(r,'otherPawn')) for r in rel))
        prio[who] = [x.text for x in t.find('workSettings').find('priorities').find('vals')] \
            if t.find('workSettings') is not None else []
        sched[who] = [x.text for x in t.find('timetable').find('times')] \
            if t.find('timetable') is not None else []
        cbn[who] = t

    # ── NGƯỜI ─────────────────────────────────────────────────────────
    w(); w('## NGƯỜI (%d colonist%s)' % (len(cols), ' · CHẾ ĐỘ GỌN' if compact else ''))
    for mi, t in cols: fmt_pawn(mi, t)

    # ── NÔ LỆ / TÙ NHÂN ───────────────────────────────────────────────
    if slaves or pris:
        w(); w('## NÔ LỆ & TÙ NHÂN (%d nô lệ · %d tù nhân)' % (len(slaves), len(pris)))
        for mi, t in slaves:
            gd = t.find('guest')
            nm = t.find('name'); who = T(nm,'nick') or T(nm,'first') or T(t,'id')
            w('- **NÔ LỆ** %s `%s` · sức chịu đựng %s · chế độ %s · %s' % (
                who, T(t,'id'), N(T(gd,'resistance')) or '—',
                T(gd,'slaveInteractionMode') or '?', '%s %s'%(mi,T(t,'pos'))))
        for mi, t in pris:
            gd = t.find('guest')
            nm = t.find('name'); who = T(nm,'nick') or T(nm,'first') or T(t,'id')
            w('- **TÙ NHÂN** %s `%s` · kháng cự %s · có thể chiêu mộ: %s · %s' % (
                who, T(t,'id'), N(T(gd,'resistance')) or '—',
                T(gd,'recruitable') or '?', '%s %s'%(mi,T(t,'pos'))))

    # ── MECH ──────────────────────────────────────────────────────────
    if mechs:
        w(); w('## MECH (%d)' % len(mechs))
        for mi, t in mechs:
            nm = t.find('name')
            w('- %s `%s` @%s · %s' % (T(t,'def'), T(t,'id'), T(t,'pos'),
                T(nm,'name') if nm is not None and len(nm) else 'không tên'))

    # ── WORK ──────────────────────────────────────────────────────────
    w(); w('## WORK (chỉ mục bật; còn lại = 0)'); w()
    for who, v in prio.items():
        on = []
        for i, x in enumerate(v):
            if x != '0':
                nm = ABBR[i] if i < len(ABBR) else 'M%d'%i
                on.append('%s%s' % (nm, x))
        w('- **%s**: %s' % (who, ' '.join(on)))

    # ── SCHEDULE ──────────────────────────────────────────────────────
    w(); w('## SCHEDULE')
    uniq = {tuple(v) for v in sched.values() if v}
    if len(uniq) == 1:
        v = list(uniq)[0]
        w('- Tất cả giống nhau: ngủ %s' % ','.join(str(i) for i,x in enumerate(v) if x=='Sleep'))
    else:
        for who, v in sched.items():
            if v: w('- %s: ngủ %s' % (who, ','.join(str(i) for i,x in enumerate(v) if x=='Sleep')))

    # ── COLONY (từng map) ─────────────────────────────────────────────
    for mi, m in enumerate(maps):
        th = [t for mm,t in things if mm==mi]
        mine = [t for t in th if T(t,'faction')==pf and t.get('Class','').startswith('Building')]
        w(); w('## COLONY (map %d)' % mi)
        w('- Công trình: %s' % ' '.join('%s×%d'%(d,k) for d,k in
              sorted(Counter(T(t,'def') for t in mine).items())))
        # ── ĐIỆN ──
        gen = con = bat = 0.0; ngen = 0
        for t in th:
            cp = t.find('comps')
            if cp is None: continue
            for c in cp:
                cl = c.get('Class') or ''
                if 'Battery' in cl:
                    bat += float(T(c,'storedEnergy', T(c,'energy',0)) or 0)
                elif 'Power' in cl:
                    o = float(T(c,'powerOutput',0) or 0)
                    if o > 0: gen += o; ngen += 1
                    elif o < 0: con += -o
        if gen or con or bat:
            w('- **Điện**: sản xuất ~%.0f W (%d nguồn) · tiêu thụ ~%.0f W · pin %.0f W · %s' % (
                gen, ngen, con, bat,
                '🔴 THIẾU ĐIỆN' if con > gen and gen > 0 else ('✅ đủ' if gen >= con and gen > 0 else '?')))
        bp = [t for t in th if t.get('Class','').startswith('Blueprint')]
        wood = sum(int(T(t,'stackCount','1') or 1) for t in th if T(t,'def')=='WoodLog')
        if bp:
            w('- Blueprint: %s → cần ~%d gỗ, **có %d**' % (
                ' '.join('%s×%d'%(d,k) for d,k in Counter(T(t,'def') for t in bp).items()),
                len(bp)*5, wood))
        ds = m.find('designationManager').find('allDesignations')
        if ds is not None and len(list(ds)):
            w('- Chỉ thị: %s' % ' '.join('%s×%d'%(d,k) for d,k in Counter(T(d,'def') for d in ds).items()))
        zs = m.find('zoneManager').find('allZones')
        if zs is not None and len(list(zs)):
            w('- Zone: %s' % '; '.join('%s(%d ô%s)'%(T(z,'label'), len(list(z.find('cells'))),
                                                     ','+T(z,'plantDefToGrow') if T(z,'plantDefToGrow') else '') for z in zs))
        rice = [t for t in th if T(t,'def')=='Plant_Rice']
        if rice:
            w('- Lúa: %d cây, lớn %.0f%%' % (len(rice), 100*sum(float(T(t,'growth',0)) for t in rice)/len(rice)))
        stock = defaultdict(int)
        for t in th:
            if t.get('Class') in ('ThingWithComps','Medicine','Apparel','MinifiedThing'):
                stock[T(t,'def')] += int(T(t,'stackCount','1') or 1)
        w('- Kho (%d loại): %s' % (len(stock),
              ' · '.join('%s %s'%(d,k) for d,k in sorted(stock.items(), key=lambda x:-x[1]))))

    # ── RESEARCH / BILLS ──────────────────────────────────────────────
    rm = G.find('researchManager'); pr = rm.find('progress')
    keys = [x.text for x in pr.find('keys')]; vals = [x.text for x in pr.find('values')]
    d_ = dict(zip(keys,vals))
    done = [k for k,v in d_.items() if v not in (None,'','0','0.0')]
    w(); w('## RESEARCH & BILLS')
    w('- Xong (%d): %s' % (len(done), ','.join(done) if len(done)<=15 else
                           ','.join(done[:8])+' … +%d nữa'%(len(done)-8)))
    w('- Đang làm: **%s** tiến độ %s' % (T(rm,'currentProj'), d_.get(T(rm,'currentProj'))))
    bl = []
    for mm, t in things:
        if T(t,'faction')==pf and t.find('billStack') is not None:
            bs = t.find('billStack').find('bills')
            if bs is not None:
                for b in bs:
                    bl.append('%s@%s:%s×%s'%(T(t,'def').replace('Building_',''),
                                             T(t,'pos'), T(b,'recipe'), T(b,'targetCount')))
    if bl:
        cnt = Counter(bl)
        w('- Bills (%d): %s' % (len(bl), ' | '.join((k if n==1 else '%s ×%d'%(k,n)) for k,n in cnt.items())))

    # ── ANIMALS ───────────────────────────────────────────────────────
    w(); w('## ANIMALS')
    if animals:
        if len(animals) > 6:
            w('- Thuần (%d): %s' % (len(animals),
                ' · '.join('%s×%d'%(d,k) for d,k in Counter(T(t,'def') for _,t in animals).items())))
        else:
            for mi, t in animals:
                tr = t.find('training')
                wt = [i for i,v in enumerate(tr.find('wantedTrainables').find('vals')) if v.text=='True'] if tr is not None else []
                nmn = T(t.find('name'),'name') if t.find('name') is not None and len(t.find('name')) else None
                w('- Thuần: %s (%s, %.1f tuổi) @%s · huấn luyện: %s' % (
                    nmn or T(t,'def'), T(t,'def'),
                    int(T(t.find('ageTracker'),'ageBiologicalTicks',0))/TICKS_YEAR, T(t,'pos'), wt or 'không'))
    wild = Counter(T(t,'def') for mm,t in things if t.get('Class')=='Pawn' and not T(t,'faction'))
    dang = {d:k for d,k in wild.items() if d in DANGEROUS}
    w('- Hoang dã: %d con · **nguy hiểm: %s**' % (sum(wild.values()),
        ', '.join('%s×%d'%(d,k) for d,k in dang.items()) or 'không'))

    # ── THREATS + điều kiện ───────────────────────────────────────────
    w(); w('## THREATS')
    for mi, m in enumerate(maps):
        gc = m.find('gameConditionManager')
        ac = gc.find('activeConditions') if gc is not None else None
        if ac is not None and len(list(ac)):
            w('- ⚠ Điều kiện map%d: %s' % (mi, ','.join(T(c,'def') or c.get('Class') for c in ac)))
    for mi, t in things:
        if t.get('Class')=='Pawn' and T(t,'faction') not in (None, pf):
            w('- **%s** phe %s @%s · active=%s' % (T(t,'def'), T(t,'faction'), T(t,'pos'), T(t,'active')))
    for mi, t in things:
        if tag(t)=='thing' and T(t,'def') in ('VoidMonolith','RectTrigger'):
            w('- %s @%s' % (T(t,'def'), T(t,'pos')))
    if not any(T(t,'faction') not in (None,pf) and t.get('Class')=='Pawn' for _,t in things):
        w('- Không có địch trên map')

    # ── QUESTS ────────────────────────────────────────────────────────
    qm = G.find('questManager')
    ql = qm.find('quests') if qm is not None else None
    if ql is not None and len(list(ql)):
        w(); w('## QUESTS (%d)' % len(list(ql)))
        for q in list(ql)[:15]:
            w('- **%s** · %s · %s' % (T(q,'name') or q.get('Class'), T(q,'state') or '?',
                                      T(q,'ticksUntilAcceptanceExpire') or ''))

    # ── Ý THỨC HỆ ─────────────────────────────────────────────────────
    im = G.find('world').find('ideoManager')
    if im is not None and im.find('ideos') is not None and len(list(im.find('ideos'))):
        w(); w('## Ý THỨC HỆ')
        for i in im.find('ideos'):
            tid = T(i,'id')
            n = len([1 for _,t in cols if t.find('ideo') is not None and T(t.find('ideo'),'ideo') in (tid,'Ideo_%s'%tid)])
            memes = [T(x,'def') for x in i.find('memes')] if i.find('memes') is not None else []
            w('- **%s** (id %s · %d người theo) · memes: %s' % (
                T(i,'name') or '?', tid, n, ','.join(memes) or '—'))

    # ── FACTIONS ──────────────────────────────────────────────────────
    fm = {}
    for fi, f in enumerate(facman.find('allFactions')):
        fm['Faction_'+(T(f,'loadID') or str(fi))] = '%s(%s)'%(T(f,'name') or '?', T(f,'def'))
    w(); w('## FACTIONS')
    for f in facman.find('allFactions'):
        if T(f,'def')=='PlayerColony' and f.find('relations') is not None:
            for r in f.find('relations'):
                if T(r,'kind')=='Hostile':
                    w('- 🔴 %s — %s' % (fm.get(T(r,'other'),T(r,'other')), T(r,'goodwill')))
            w('- ⚪ trung lập: %s' % ', '.join(fm.get(T(r,'other'),T(r,'other'))
                                               for r in f.find('relations') if not T(r,'kind')))

    # ── DÒNG THỜI GIAN SỰ KIỆN ───────────────────────────────────────
    if events:
        w(); w('## SỰ KIỆN GẦN ĐÂY (từ vết thương)')
        for tk, txt_ in sorted(set(events), key=lambda x:-x[0])[:10]:
            w('- ngày -%.1f (tick %d): %s' % ((tg-tk)/TICKS_DAY, tk, txt_))

    # ── BOTTLENECKS ───────────────────────────────────────────────────
    w(); w('## ⚠ BOTTLENECKS')
    probs = []
    for i, nm in enumerate(WORKTYPES):
        if nm in ('Firefighter','Patient','Doctor','PatientBedRest','BasicWorker'): continue
        on = [who for who,v in prio.items() if i < len(v) and v[i] != '0']
        if not on: probs.append('🔴 không ai làm %s' % nm)
        elif len(on)==1: probs.append('🟠 %s chỉ 1 người: %s' % (nm, on[0]))
    for mi, m in enumerate(maps):
        th = [t for mm,t in things if mm==mi]
        ds = m.find('designationManager').find('allDesignations')
        for d,k in Counter(T(x,'def') for x in (ds or [])).items():
            wt = DESIG2WORK.get(d)
            if wt and wt in WORKTYPES:
                i = WORKTYPES.index(wt)
                if not [who for who,v in prio.items() if i<len(v) and v[i]!='0']:
                    probs.append('🔴 %d chỉ thị %s cần %s nhưng không ai gán' % (k,d,wt))
        bp = [t for t in th if t.get('Class','').startswith('Blueprint')]
        if bp and not [who for who,v in prio.items() if len(v)>9 and v[9]!='0']:
            probs.append('🔴 %d blueprint kẹt (Construction = 0)' % len(bp))
        wood = sum(int(T(t,'stackCount','1') or 1) for t in th if T(t,'def')=='WoodLog')
        if bp and wood < len(bp)*3:
            probs.append('🔴 %d blueprint cần ~%d gỗ, chỉ còn %d' % (len(bp), len(bp)*5, wood))
        meals = sum(int(T(t,'stackCount','1') or 1) for t in th if T(t,'def','').startswith('Meal'))
        nc = len([1 for mm,_ in cols if mm=='map%d'%mi])
        if nc and meals*0.9/(nc*1.6) < 5:
            probs.append('🔴 thức ăn chỉ đủ %.1f ngày' % (meals*0.9/(nc*1.6)))
        gen = con = 0.0
        for t in th:
            cp = t.find('comps')
            if cp is None: continue
            for c in cp:
                if 'Power' in (c.get('Class') or ''):
                    o = float(T(c,'powerOutput',0) or 0)
                    if o > 0: gen += o
                    elif o < 0: con += -o
        if con > gen > 0:
            probs.append('🔴 THIẾU ĐIỆN: tiêu thụ ~%.0f W > sản xuất ~%.0f W' % (con, gen))
    # bác sĩ
    i = WORKTYPES.index('Doctor')
    docs = [who for who,v in prio.items() if i<len(v) and v[i]!='0']
    if not docs: probs.append('🔴 không ai làm bác sĩ')
    injured = sum(1 for _,t in cols
                  if [h for h in (t.find('healthTracker').find('hediffSet').find('hediffs') or [])
                      if hediff_kind(h,tg)[0]=='injury'])
    if injured and not docs:
        probs.append('🔴 %d người đang có vết thương mà KHÔNG AI làm bác sĩ' % injured)
    for who, v in prio.items():
        i = WORKTYPES.index('Hunting')
        if i < len(v) and v[i] != '0':
            t = cbn.get(who)
            if t is not None:
                eq = t.find('equipment').find('equipment').find('innerList')
                ww = [T(a,'def') for a in eq] if eq is not None and len(eq) else []
                if not any(x.startswith(RANGED) for x in ww):
                    probs.append('🟠 %s gán Hunt nhưng cầm %s' % (who, ww or 'tay không'))
    cp = T(rm,'currentProj')
    if d_.get(cp) in (None,'','0','0.0'):
        probs.append('🟠 nghiên cứu %s chưa có tiến độ' % cp)
    for p in (probs or ['✅ không có']): w('- ' + p)

    res = '\n'.join(L)
    if as_json:
        json.dump({'state': res}, open((out or '/tmp/brief.json'),'w',encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('JSON ->', out or '/tmp/brief.json')
    elif out:
        open(out,'w',encoding='utf-8').write(res)
        print('Đã ghi %s' % out)
    else:
        print(res)

if __name__ == '__main__':
    main()
