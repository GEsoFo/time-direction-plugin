/**
 * 大六壬排盘引擎（自研，规则以《六壬大全·课经》《六壬指南·心印赋》为准，
 * 并经《六壬断案》课例逐课反推验证）。
 *
 * 覆盖：四柱（定气节气）、月将（中气换将）、天地盘（月将加时）、四课、
 * 三传九宗门（贼克/比用/涉害/遥克/昴星/别责/八专/伏吟/返吟）、
 * 十二天将（昼夜贵人、亥至辰顺巳至戌逆）、遁干（五鼠遁）、
 * 空亡/驿马/禄神/羊刃/桃花/华盖/将星、六亲、十二长生。
 */
// ─────────────── 基础表 ───────────────
export const GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
export const ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
/** 天干五行 */
export const GAN_WX = {
    甲: '木', 乙: '木', 丙: '火', 丁: '火', 戊: '土',
    己: '土', 庚: '金', 辛: '金', 壬: '水', 癸: '水',
};
/** 地支五行 */
export const ZHI_WX = {
    子: '水', 丑: '土', 寅: '木', 卯: '木', 辰: '土', 巳: '火',
    午: '火', 未: '土', 申: '金', 酉: '金', 戌: '土', 亥: '水',
};
/** 地支藏干 */
export const ZHI_CANG = {
    子: ['癸'], 丑: ['己', '癸', '辛'], 寅: ['甲', '丙', '戊'], 卯: ['乙'],
    辰: ['戊', '乙', '癸'], 巳: ['丙', '庚', '戊'], 午: ['丁', '己'],
    未: ['己', '丁', '乙'], 申: ['庚', '壬', '戊'], 酉: ['辛'],
    戌: ['戊', '辛', '丁'], 亥: ['壬', '甲'],
};
/** 十干寄宫：甲课寅乙课辰，丙戊课巳，丁己课未，庚课申，辛课戌，壬课亥，癸课丑 */
export const GAN_JI_GONG = {
    甲: '寅', 乙: '辰', 丙: '巳', 丁: '未', 戊: '巳',
    己: '未', 庚: '申', 辛: '戌', 壬: '亥', 癸: '丑',
};
/** 十二神名（月将） */
export const SHEN_NAMES = {
    亥: '登明', 戌: '河魁', 酉: '从魁', 申: '传送', 未: '小吉', 午: '胜光',
    巳: '太乙', 辰: '天罡', 卯: '太冲', 寅: '功曹', 丑: '大吉', 子: '神后',
};
/** 十二天将 */
export const TIAN_JIANG = [
    '贵人', '螣蛇', '朱雀', '六合', '勾陈', '青龙',
    '天空', '白虎', '太常', '玄武', '太阴', '天后',
];
/** 昼夜贵人：甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸蛇兔藏，六辛逢马虎 */
export const GUI_REN = {
    甲: { day: '丑', night: '未' }, 戊: { day: '丑', night: '未' }, 庚: { day: '丑', night: '未' },
    乙: { day: '子', night: '申' }, 己: { day: '子', night: '申' },
    丙: { day: '亥', night: '酉' }, 丁: { day: '亥', night: '酉' },
    壬: { day: '巳', night: '卯' }, 癸: { day: '巳', night: '卯' },
    辛: { day: '午', night: '寅' },
};
/** 五鼠遁（日上起时）：子时天干 */
export const WU_SHU_DUN = {
    甲: '甲', 己: '甲', 乙: '丙', 庚: '丙', 丙: '戊',
    辛: '戊', 丁: '庚', 壬: '庚', 戊: '壬', 癸: '壬',
};
/** 五虎遁（年起月）：寅月天干 */
export const WU_HU_DUN = {
    甲: '丙', 己: '丙', 乙: '戊', 庚: '戊', 丙: '庚',
    辛: '庚', 丁: '壬', 壬: '壬', 戊: '甲', 癸: '甲',
};
/** 十干禄 */
export const LU_SHEN = {
    甲: '寅', 乙: '卯', 丙: '巳', 丁: '午', 戊: '巳',
    己: '午', 庚: '申', 辛: '酉', 壬: '亥', 癸: '子',
};
/** 十干羊刃 */
export const YANG_REN = {
    甲: '卯', 乙: '辰', 丙: '午', 丁: '未', 戊: '午',
    己: '未', 庚: '酉', 辛: '戌', 壬: '子', 癸: '丑',
};
/** 十二长生位（五行长生，不分阴阳：木亥、火寅、金巳、水土申） */
export const CHANG_SHENG_WEI = {
    甲: '亥', 乙: '亥', 丙: '寅', 丁: '寅', 戊: '申',
    己: '申', 庚: '巳', 辛: '巳', 壬: '申', 癸: '申',
};
export const CHANG_SHENG_ORDER = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养'];
/** 三刑：寅巳申 / 丑戌未 / 子卯；自刑辰午酉亥 */
export const XING = {
    寅: '巳', 巳: '申', 申: '寅',
    丑: '戌', 戌: '未', 未: '丑',
    子: '卯', 卯: '子',
};
export const ZI_XING = ['辰', '午', '酉', '亥'];
/** 冲 */
export const CHONG = {
    子: '午', 丑: '未', 寅: '申', 卯: '酉', 辰: '戌', 巳: '亥',
    午: '子', 未: '丑', 申: '寅', 酉: '卯', 戌: '辰', 亥: '巳',
};
/** 驿马（按日支三合局） */
export function yiMa(zhi) {
    if (['申', '子', '辰'].includes(zhi))
        return '寅';
    if (['寅', '午', '戌'].includes(zhi))
        return '申';
    if (['巳', '酉', '丑'].includes(zhi))
        return '亥';
    return '巳'; // 亥卯未
}
/** 桃花（咸池） */
export function taoHua(zhi) {
    if (['申', '子', '辰'].includes(zhi))
        return '酉';
    if (['寅', '午', '戌'].includes(zhi))
        return '卯';
    if (['巳', '酉', '丑'].includes(zhi))
        return '午';
    return '子';
}
/** 华盖 */
export function huaGai(zhi) {
    if (['申', '子', '辰'].includes(zhi))
        return '辰';
    if (['寅', '午', '戌'].includes(zhi))
        return '戌';
    if (['巳', '酉', '丑'].includes(zhi))
        return '丑';
    return '未';
}
/** 将星 */
export function jiangXing(zhi) {
    if (['申', '子', '辰'].includes(zhi))
        return '子';
    if (['寅', '午', '戌'].includes(zhi))
        return '午';
    if (['巳', '酉', '丑'].includes(zhi))
        return '酉';
    return '卯';
}
/** 五行相生：a 生 b？ */
export function sheng(a, b) {
    return { 木: '火', 火: '土', 土: '金', 金: '水', 水: '木' }[a] === b;
}
/** 五行相克（单向）：a 克 b？ */
export function ke(a, b) {
    return { 木: '土', 土: '水', 水: '火', 火: '金', 金: '木' }[a] === b;
}
/** 是否相克（双向） */
export function xiangKe(a, b) {
    return ke(a, b) || ke(b, a);
}
/** 六亲（以日干五行对神支五行） */
export function liuQin(dayGan, zhi) {
    const d = GAN_WX[dayGan];
    const z = ZHI_WX[zhi];
    if (d === z)
        return '兄弟';
    if (sheng(d, z))
        return '子孙';
    if (sheng(z, d))
        return '父母';
    if (ke(z, d))
        return '官鬼';
    return '妻财';
}
/** 十二长生（按五行，不分阴阳，统一顺行） */
export function changSheng(dayGan, zhi) {
    const start = ZHI.indexOf(CHANG_SHENG_WEI[dayGan]);
    const idx = ZHI.indexOf(zhi);
    const offset = (idx - start + 12) % 12;
    return CHANG_SHENG_ORDER[offset];
}
/** 地支在传统盘面上的 4×4 格位（传统方位盘：午上子下，卯左酉右） */
export const GRID_POS = {
    巳: [0, 0], 午: [1, 0], 未: [2, 0], 申: [3, 0],
    辰: [0, 1], 酉: [3, 1],
    卯: [0, 2], 戌: [3, 2],
    寅: [0, 3], 丑: [1, 3], 子: [2, 3], 亥: [3, 3],
};
// ─────────────── 节气 / 干支 ───────────────
/** 黄经目标 → 节气名 */
const TERM_BY_LONG = [
    [0, '春分'], [15, '清明'], [30, '谷雨'], [45, '立夏'], [60, '小满'], [75, '芒种'],
    [90, '夏至'], [105, '小暑'], [120, '大暑'], [135, '立秋'], [150, '处暑'], [165, '白露'],
    [180, '秋分'], [195, '寒露'], [210, '霜降'], [225, '立冬'], [240, '小雪'], [255, '大雪'],
    [270, '冬至'], [285, '小寒'], [300, '大寒'], [315, '立春'], [330, '雨水'], [345, '惊蛰'],
];
/** 中气 → 月将：雨水亥将…大寒子将（中气换将，定气） */
const ZHONG_QI_TO_JIANG = [
    [330, '亥'], [0, '戌'], [30, '酉'], [60, '申'], [90, '未'], [120, '午'],
    [150, '巳'], [180, '辰'], [210, '卯'], [240, '寅'], [270, '丑'], [300, '子'],
];
/** 节 → 月建：立春寅月… */
const JIE_TO_MONTH = [
    [315, '寅'], [345, '卯'], [15, '辰'], [45, '巳'], [75, '午'], [105, '未'],
    [135, '申'], [165, '酉'], [195, '戌'], [225, '亥'], [255, '子'], [285, '丑'],
];
/** 太阳黄经（度，近似定气，1900–2100 误差约 1 分钟） */
function sunLongitude(jde) {
    const n = jde - 2451545.0;
    const L = (280.460 + 0.9856474 * n + 360) % 360;
    const g = ((357.528 + 0.9856003 * n) % 360) * Math.PI / 180;
    let lon = L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g);
    lon = ((lon % 360) + 360) % 360;
    return lon;
}
/** 求太阳过 target 黄经的时刻（ms）。JDE 以 1970-01-01 00:00 UT（2440587.5）为基准 */
function jdOfLongitude(target, approxMs) {
    let lo = approxMs - 6 * 86400000;
    let hi = approxMs + 6 * 86400000;
    for (let i = 0; i < 48; i++) {
        const mid = (lo + hi) / 2;
        const lon = sunLongitude(mid / 86400000 + 2440587.5);
        const diff = ((lon - target + 540) % 360) - 180;
        if (diff >= 0)
            hi = mid;
        else
            lo = mid;
    }
    return (lo + hi) / 2;
}
/** 求某年所有 24 节气时刻（北京时间 ms），按黄经 0..345 排序 */
export function solarTermsOfYear(year) {
    const terms = [];
    for (const [longitude, name] of TERM_BY_LONG) {
        // 估计：春分（0°）约在年第 79.4 天，其余按黄经比例推算（误差 < 4 天，搜索窗口 ±6 天足够）
        const doy = (79.4 + (longitude / 360) * 365.2422) % 365.2422;
        const est = Date.UTC(year, 0, 1, 0, 0, 0) + doy * 86400000;
        terms.push({ name, longitude, timeMs: jdOfLongitude(longitude, est) });
    }
    return terms;
}
/** 取 ms 前后跨三年的节气表 */
function termsAround(ms) {
    const year = new Date(ms).getFullYear();
    return [...solarTermsOfYear(year - 1), ...solarTermsOfYear(year), ...solarTermsOfYear(year + 1)]
        .sort((a, b) => a.timeMs - b.timeMs);
}
/** 找到 ms 之前最近的满足条件（中气/节）的节气 */
function lastTerm(ms, kind) {
    const all = termsAround(ms);
    const targets = kind === '中气' ? ZHONG_QI_TO_JIANG.map(([lon]) => lon) : JIE_TO_MONTH.map(([lon]) => lon);
    let best = null;
    for (const t of all) {
        if (targets.includes(t.longitude) && t.timeMs <= ms)
            best = t;
    }
    return best;
}
/** 求月将（按最近中气换将，定气） */
export function yueJiangOf(ms) {
    const t = lastTerm(ms, '中气');
    if (!t)
        return '亥';
    for (const [lon, zhi] of ZHONG_QI_TO_JIANG) {
        if (lon === t.longitude)
            return zhi;
    }
    return '亥';
}
/** 求月建（按最近节） */
export function monthZhiOf(ms) {
    const t = lastTerm(ms, '节');
    if (!t)
        return '寅';
    for (const [lon, zhi] of JIE_TO_MONTH) {
        if (lon === t.longitude)
            return zhi;
    }
    return '寅';
}
/** 节气段描述（如 立春后·雨水前） */
export function termLabel(ms) {
    const all = termsAround(ms);
    let last = null;
    for (const t of all)
        if (t.timeMs <= ms)
            last = t;
    if (!last)
        return '';
    const next = all.find((t) => t.timeMs > ms);
    return next ? `${last.name}后·${next.name}前` : `${last.name}后`;
}
/** 公历 → 四柱（年以立春换，月以节换，日以 0 点换，时以五鼠遁） */
export function toGanZhi(ms) {
    const d = new Date(ms);
    const localY = d.getFullYear();
    const localM = d.getMonth();
    const localD = d.getDate();
    // 年干支：立春换年（取最近一次立春所在年）
    const liChun = termsAround(ms).filter((t) => t.longitude === 315).sort((a, b) => a.timeMs - b.timeMs);
    let lastLiChun = null;
    for (const t of liChun)
        if (t.timeMs <= ms)
            lastLiChun = t;
    const yBase = lastLiChun ? new Date(lastLiChun.timeMs).getFullYear() : localY;
    const yIdx = (((yBase - 4) % 60) + 60) % 60;
    const year = { gan: GAN[yIdx % 10], zhi: ZHI[yIdx % 12] };
    // 月干支：节换月
    const mZhi = monthZhiOf(ms);
    const mGanStart = WU_HU_DUN[year.gan];
    const mGanIdx = (GAN.indexOf(mGanStart) + (ZHI.indexOf(mZhi) - ZHI.indexOf('寅') + 12) % 12) % 10;
    const month = { gan: GAN[mGanIdx], zhi: mZhi };
    // 日干支：锚 2000-01-01 = 戊午（index 54），2024-02-10 = 甲辰（index 40）交叉验证
    const dayMs = Date.UTC(localY, localM, localD);
    const days = Math.round((dayMs - Date.UTC(2000, 0, 1)) / 86400000);
    const dIdx = (((54 + days) % 60) + 60) % 60;
    const day = { gan: GAN[dIdx % 10], zhi: ZHI[dIdx % 12] };
    // 时干支：五鼠遁
    const hZhiIdx = Math.floor((d.getHours() + 1) / 2) % 12;
    const hGanStart = WU_SHU_DUN[day.gan];
    const hGan = GAN[(GAN.indexOf(hGanStart) + hZhiIdx) % 10];
    const hour = { gan: hGan, zhi: ZHI[hZhiIdx] };
    return { year, month, day, hour };
}
export function zhiFromHour(hour) {
    return ZHI[Math.floor((hour + 1) / 2) % 12];
}
/** 昼夜：卯～申为昼（index 3..8），酉～寅为夜 */
export function isDay(zhi) {
    const i = ZHI.indexOf(zhi);
    return i >= 3 && i <= 8;
}
/** 盘面核心计算（供 paiPan 与测试直接调用） */
export function paiPanCore(input) {
    const dayGan = input.day.gan;
    const dayZhi = input.day.zhi;
    const yueJiang = input.yueJiang;
    const shiZhi = input.shiZhi;
    const yj = ZHI.indexOf(yueJiang);
    const sz = ZHI.indexOf(shiZhi);
    // 天盘：月将加时，顺布十二宫。天盘[地盘位E] = (E + 月将 - 占时) mod 12
    const tianPan = ZHI.map((_, e) => ZHI[(e + yj - sz + 12) % 12]);
    // 旬空（提前算，供回填）
    const ganIdx = GAN.indexOf(dayGan);
    const zhiIdx = ZHI.indexOf(dayZhi);
    const xunShouIdx = (zhiIdx - ganIdx + 12) % 12;
    const xunShou = { gan: '甲', zhi: ZHI[xunShouIdx] };
    const xunKong = [ZHI[(xunShouIdx + 10) % 12], ZHI[(xunShouIdx + 11) % 12]];
    // 遁干：旬首顺布天盘（甲寅旬：甲在天盘寅，乙卯丙辰…癸亥，子丑空亡无遁干）
    const dunGanOf = (zhi) => {
        const offset = (ZHI.indexOf(zhi) - ZHI.indexOf(xunShou.zhi) + 12) % 12;
        return offset < 10 ? GAN[offset] : '';
    };
    const dunGan = ZHI.map(dunGanOf);
    // 神 → 临位（加临的地盘支）
    const linWeiOf = (shen) => ZHI[(ZHI.indexOf(shen) - yj + sz + 12) % 12];
    // 昼夜贵人
    const dayNight = isDay(shiZhi) ? '昼' : '夜';
    const guiRen = GUI_REN[dayGan][dayNight === '昼' ? 'day' : 'night'];
    // 贵人加临地盘位：亥至辰顺，巳至戌逆（六壬大全：运转天盘逆顺，分为南北）
    const guiLin = (ZHI.indexOf(guiRen) + sz - yj + 12) % 12;
    const guiRenShunNi = (guiLin >= 11 || guiLin <= 4) ? '顺' : '逆';
    const guiIdx = ZHI.indexOf(guiRen);
    const tianJiang = tianPan.map((shen) => {
        const s = ZHI.indexOf(shen);
        const offset = guiRenShunNi === '顺' ? (s - guiIdx + 12) % 12 : (guiIdx - s + 12) % 12;
        return TIAN_JIANG[offset];
    });
    // 神信息（按地盘位取）
    const shenOf = (linWei) => {
        const e = ZHI.indexOf(linWei);
        const shen = tianPan[e];
        return {
            zhi: shen,
            name: SHEN_NAMES[shen],
            dunGan: dunGanOf(shen),
            tianJiang: tianJiang[e],
            linWei,
            liuQin: liuQin(dayGan, shen),
            changSheng: changSheng(dayGan, shen),
            kongWang: xunKong.includes(shen),
            yiMa: yiMa(dayZhi) === shen,
        };
    };
    const wei = ZHI.map((z) => ({ diZhi: z, shen: shenOf(z) }));
    // 四课
    const jiGong = GAN_JI_GONG[dayGan];
    const ke1Up = tianPan[ZHI.indexOf(jiGong)];
    const ke2Up = tianPan[ZHI.indexOf(ke1Up)];
    const ke3Up = tianPan[ZHI.indexOf(dayZhi)];
    const ke4Up = tianPan[ZHI.indexOf(ke3Up)];
    const relationOf = (up, down, downIsGan) => {
        const upWx = ZHI_WX[up];
        const downWx = downIsGan ? GAN_WX[dayGan] : ZHI_WX[down];
        if (ke(upWx, downWx))
            return '克'; // 上克下
        if (ke(downWx, upWx))
            return '贼'; // 下贼上
        if (sheng(upWx, downWx))
            return '生';
        if (sheng(downWx, upWx))
            return '泄';
        return '比';
    };
    const siKe = [
        { n: 1, down: jiGong, downLabel: `日干${dayGan}`, up: ke1Up, relation: relationOf(ke1Up, jiGong, true), upInfo: shenOf(jiGong) },
        { n: 2, down: ke1Up, downLabel: '干上神', up: ke2Up, relation: relationOf(ke2Up, ke1Up, false), upInfo: shenOf(ke1Up) },
        { n: 3, down: dayZhi, downLabel: `日支${dayZhi}`, up: ke3Up, relation: relationOf(ke3Up, dayZhi, false), upInfo: shenOf(dayZhi) },
        { n: 4, down: ke3Up, downLabel: '支上神', up: ke4Up, relation: relationOf(ke4Up, ke3Up, false), upInfo: shenOf(ke3Up) },
    ];
    // 三传
    const sanChuan = calcSanChuan({ dayGan, dayZhi, jiGong, tianPan, linWeiOf, siKe, yueJiang, shiZhi, shenOf });
    return {
        year: input.year ?? { gan: '甲', zhi: '子' },
        month: input.month ?? { gan: '甲', zhi: '子' },
        day: input.day,
        hour: input.hour ?? { gan: '甲', zhi: '子' },
        yueJiang,
        yueJiangName: SHEN_NAMES[yueJiang],
        shiZhi,
        dayNight,
        guiRen,
        guiRenName: SHEN_NAMES[guiRen],
        guiRenShunNi,
        tianPan,
        dunGan,
        tianJiang,
        wei,
        siKe,
        sanChuan,
        xunKong,
        xunShou,
        shenSha: {
            驿马: yiMa(dayZhi),
            禄神: LU_SHEN[dayGan],
            羊刃: YANG_REN[dayGan],
            桃花: taoHua(dayZhi),
            华盖: huaGai(dayZhi),
            将星: jiangXing(dayZhi),
        },
    };
}
/** 三传九宗门 */
function calcSanChuan(opts) {
    const { dayGan, dayZhi, jiGong, tianPan, linWeiOf, siKe, yueJiang, shiZhi, shenOf } = opts;
    const yangDay = GAN.indexOf(dayGan) % 2 === 0;
    const zhiYang = (z) => ZHI.indexOf(z) % 2 === 0;
    const tianPanAt = (z) => tianPan[ZHI.indexOf(z)];
    // 涉害深浅：从临位顺行至本宫（不含本宫），历所涉地支，凡所历支五行克发用神者各记一重
    const sheHaiDepth = (shen) => {
        const wx = ZHI_WX[shen];
        const start = (ZHI.indexOf(linWeiOf(shen)) + 1) % 12;
        const home = ZHI.indexOf(shen);
        let depth = 0;
        let e = start;
        while (e !== home) {
            const w = ZHI[e];
            if (ke(ZHI_WX[w], wx))
                depth += 1;
            e = (e + 1) % 12;
        }
        return depth;
    };
    const mengZhongJi = (shen) => {
        const i = ZHI.indexOf(linWeiOf(shen));
        if ([2, 5, 8, 11].includes(i))
            return 0; // 寅巳申亥 孟
        if ([0, 3, 6, 9].includes(i))
            return 1; // 子午卯酉 仲
        return 2; // 辰戌丑未 季
    };
    // 比用 → 涉害 → 孟仲季 → 缀瑕（阳日干上神，阴日支上神）
    const pick = (cands) => {
        const bi = cands.filter((c) => zhiYang(c.shen) === yangDay);
        let pool;
        if (bi.length === 1) {
            pool = bi;
            return { shen: pool[0].shen, via: '比用' };
        }
        pool = bi.length > 1 ? bi : cands;
        if (pool.length === 1)
            return { shen: pool[0].shen, via: '比用' };
        const depths = pool.map((c) => sheHaiDepth(c.shen));
        const maxDepth = Math.max(...depths);
        let deepest = pool.filter((_, i) => depths[i] === maxDepth);
        if (deepest.length === 1)
            return { shen: deepest[0].shen, via: '涉害' };
        // 复等：孟仲季
        const m = deepest.map((c) => mengZhongJi(c.shen));
        const minM = Math.min(...m);
        deepest = deepest.filter((_, i) => m[i] === minM);
        if (deepest.length === 1)
            return { shen: deepest[0].shen, via: '涉害·见机' };
        // 缀瑕：阳日取干上神，阴日取支上神
        const target = yangDay ? siKe[0].up : siKe[2].up;
        const hit = deepest.find((c) => c.shen === target);
        if (hit)
            return { shen: hit.shen, via: '涉害·缀瑕' };
        return { shen: deepest[0].shen, via: '涉害·缀瑕' };
    };
    // ═══ 伏吟：天地盘同位（月将加本时） ═══
    if (yueJiang === shiZhi) {
        const ganShang = tianPanAt(jiGong);
        const zhiShang = tianPanAt(dayZhi);
        const hasKe = xiangKe(ZHI_WX[ganShang], GAN_WX[dayGan]);
        const chu = hasKe ? ganShang : (yangDay ? ganShang : zhiShang);
        const xingOf = (z) => XING[z] ?? z; // 自刑：刑自身
        let zhong = xingOf(chu);
        let mo = xingOf(zhong);
        if (ZI_XING.includes(chu)) {
            zhong = yangDay ? dayZhi : jiGong;
            mo = xingOf(zhong);
        }
        if (ZI_XING.includes(zhong))
            mo = CHONG[zhong];
        return {
            method: hasKe ? '伏吟（有克为用）' : '伏吟（无克，刚干柔辰发传，迤逦三刑）',
            keTi: ['伏吟', yangDay ? '自任' : '自信'],
            chu: shenOf(linWeiOf(chu)),
            zhong: shenOf(linWeiOf(zhong)),
            mo: shenOf(linWeiOf(mo)),
            detail: `${yangDay ? '阳日' : '阴日'}伏吟，发用${chu}，三刑流转（${chu}→${zhong}→${mo}）`,
        };
    }
    // ═══ 返吟：天地盘相冲（占时为月将之冲） ═══
    if ((ZHI.indexOf(yueJiang) + 6) % 12 === ZHI.indexOf(shiZhi)) {
        const zei = siKe.filter((k) => k.relation === '贼').map((k) => ({ ke: k, shen: k.up }));
        const keG = siKe.filter((k) => k.relation === '克').map((k) => ({ ke: k, shen: k.up }));
        const group = zei.length ? zei : keG;
        const ganShang = tianPanAt(jiGong);
        const zhiShang = tianPanAt(dayZhi);
        if (group.length) {
            const { shen: chu, via } = pick(group);
            const zhong = CHONG[chu];
            return {
                method: `返吟（${via}，初末相同而冲乎中传）`,
                keTi: ['返吟'],
                chu: shenOf(linWeiOf(chu)),
                zhong: shenOf(linWeiOf(zhong)),
                mo: shenOf(linWeiOf(chu)),
                detail: `返吟课：发用${chu}，中传取冲${zhong}，末传复归${chu}`,
            };
        }
        // 无依（井栏）：丁丑己丑辛丑丁未己未辛未六日，取日支驿马为初传
        const ma = yiMa(dayZhi);
        return {
            method: '返吟·无依（井栏格：无克，取日支驿马发用）',
            keTi: ['返吟', '无依·井栏'],
            chu: shenOf(linWeiOf(ma)),
            zhong: shenOf(linWeiOf(zhiShang)),
            mo: shenOf(linWeiOf(ganShang)),
            detail: `井栏课：${dayZhi}日无克，取支之驿马${ma}（${SHEN_NAMES[ma]}）为初传，支上神${zhiShang}为中，干上神${ganShang}为末`,
        };
    }
    // ═══ 常课：贼克 → 比用 → 涉害 ═══
    const zei = siKe.filter((k) => k.relation === '贼').map((k) => ({ ke: k, shen: k.up }));
    const keG = siKe.filter((k) => k.relation === '克').map((k) => ({ ke: k, shen: k.up }));
    if (zei.length || keG.length) {
        const isZei = zei.length > 0;
        const group = isZei ? zei : keG;
        const { shen: chu, via } = pick(group);
        const zhong = tianPanAt(chu);
        const mo = tianPanAt(zhong);
        const keTi = [];
        if (group.length === 1)
            keTi.push(isZei ? '重审' : '元首');
        else
            keTi.push(via === '比用' ? '知一' : via.startsWith('涉害') ? '涉害' : '知一');
        if (siKe.every((k) => k.relation === '克'))
            keTi.push('无禄');
        if (siKe.every((k) => k.relation === '贼'))
            keTi.push('绝嗣');
        const name = group.length === 1
            ? (isZei ? '重审（一下贼上）' : '元首（一上克下）')
            : (via === '比用' ? '知一·比用' : via);
        return {
            method: `${name}（中末相因）`,
            keTi,
            chu: shenOf(linWeiOf(chu)),
            zhong: shenOf(linWeiOf(zhong)),
            mo: shenOf(linWeiOf(mo)),
            detail: `${isZei ? '下贼上' : '上克下'}发用${chu}，中传${zhong}（初之上神），末传${mo}（中之上神）`,
        };
    }
    // ═══ 八专：干支同位（两课），无克不论遥，先于遥克判定 ═══
    const ganShang = tianPanAt(jiGong);
    const zhiShang = tianPanAt(dayZhi);
    const distinctKe = new Set(siKe.map((k) => `${k.down}:${k.up}`)).size;
    const ganZhiTong = jiGong === dayZhi;
    if (ganZhiTong) {
        // 阳日从干上神顺数三位（连根），阴日从支上神逆数三位，中末俱干上神
        const base = ganShang; // 干支同位，干上神 = 支上神
        const chu = ZHI[(ZHI.indexOf(base) + (yangDay ? 2 : -2) + 12) % 12];
        return {
            method: '八专（干支同位，论克不论遥，顺逆数三辰）',
            keTi: ['八专'],
            chu: shenOf(linWeiOf(chu)),
            zhong: shenOf(linWeiOf(ganShang)),
            mo: shenOf(linWeiOf(ganShang)),
            detail: `八专课：${yangDay ? '从干上阳神' : '从支上阴神'}${base}${yangDay ? '顺' : '逆'}数三位得${chu}，中末俱干上神${ganShang}`,
        };
    }
    // ═══ 遥克：四课无克，取课二/三/四上神与日干相克者 ═══
    const yaoCands = [
        { ke: siKe[1], shen: siKe[1].up },
        { ke: siKe[2], shen: siKe[2].up },
        { ke: siKe[3], shen: siKe[3].up },
    ];
    const shenKeRi = yaoCands.filter((c) => ke(ZHI_WX[c.shen], GAN_WX[dayGan]));
    const riKeShen = yaoCands.filter((c) => ke(GAN_WX[dayGan], ZHI_WX[c.shen]));
    if (shenKeRi.length || riKeShen.length) {
        const isShenKeRi = shenKeRi.length > 0;
        const group = isShenKeRi ? shenKeRi : riKeShen;
        const { shen: chu, via } = pick(group);
        const zhong = tianPanAt(chu);
        const mo = tianPanAt(zhong);
        return {
            method: `${isShenKeRi ? '遥克·蒿矢（神遥克日）' : '遥克·弹射（日遥克神）'}${via !== '比用' ? `（${via}）` : ''}`,
            keTi: [isShenKeRi ? '蒿矢' : '弹射'],
            chu: shenOf(linWeiOf(chu)),
            zhong: shenOf(linWeiOf(zhong)),
            mo: shenOf(linWeiOf(mo)),
            detail: `${isShenKeRi ? '神遥克日' : '日遥克神'}：${group.map((c) => c.shen).join('、')}与日干相克${via !== '比用' ? '，' + via : ''}，发用${chu}`,
        };
    }
    // ═══ 无克无遥：课不全取别责，课全取昴星 ═══
    if (distinctKe <= 3) {
        // 别责：课不全（三课），阳日取干合上神，阴日取支前三合，中末俱干上神
        let chu;
        if (yangDay) {
            // 五合：甲己、乙庚、丙辛、丁壬、戊癸
            const heGan = GAN[(GAN.indexOf(dayGan) + 5) % 10];
            chu = tianPanAt(GAN_JI_GONG[heGan]);
        }
        else {
            chu = ZHI[(ZHI.indexOf(dayZhi) + 4) % 12];
        }
        return {
            method: '别责（四课不全三课备，无遥无克，别取一合神）',
            keTi: ['别责'],
            chu: shenOf(linWeiOf(chu)),
            zhong: shenOf(linWeiOf(ganShang)),
            mo: shenOf(linWeiOf(ganShang)),
            detail: `别责课：${yangDay ? '取干合上神' : '取支前三合'}发用${chu}，中末俱干上神${ganShang}`,
        };
    }
    // 昴星：四课全无克无遥。阳日仰视地盘酉上之神，阴日俯视天盘酉下之神
    if (yangDay) {
        const chu = tianPanAt('酉');
        return {
            method: '昴星（阳日仰视地盘酉上之神）',
            keTi: ['昴星', '虎视转蓬'],
            chu: shenOf(linWeiOf(chu)),
            zhong: shenOf(linWeiOf(zhiShang)),
            mo: shenOf(linWeiOf(ganShang)),
            detail: `昴星课：阳日仰视酉上取${chu}为初传，中传支上神${zhiShang}，末传干上神${ganShang}`,
        };
    }
    const chu = linWeiOf('酉');
    return {
        method: '昴星（阴日俯视天盘酉下之神）',
        keTi: ['昴星', '冬蛇掩目'],
        chu: shenOf(linWeiOf(chu)),
        zhong: shenOf(linWeiOf(ganShang)),
        mo: shenOf(linWeiOf(zhiShang)),
        detail: `昴星课：阴日俯视酉下取${chu}为初传，中传干上神${ganShang}，末传支上神${zhiShang}`,
    };
}
// ─────────────── 对外入口 ───────────────
/** 由公历时间排盘 */
export function paiPan(input = {}) {
    let ms;
    try {
        if (input.datetime == null)
            ms = Date.now();
        else if (input.datetime instanceof Date)
            ms = input.datetime.getTime();
        else if (typeof input.datetime === 'number')
            ms = input.datetime;
        else {
            const s = String(input.datetime).trim().replace(' ', 'T');
            const d = new Date(s);
            if (isNaN(d.getTime()))
                throw new Error(`无法解析时间: ${input.datetime}`);
            ms = d.getTime();
        }
    }
    catch (e) {
        return errorResult(String(e.message ?? e));
    }
    try {
        const gz = toGanZhi(ms);
        const yueJiang = input.yueJiang ? input.yueJiang : yueJiangOf(ms);
        const shiZhi = input.shiZhi ? input.shiZhi : zhiFromHour(new Date(ms).getHours());
        let day;
        let year;
        let month;
        let hour;
        if (input.dayGanZhi) {
            day = { gan: input.dayGanZhi[0], zhi: input.dayGanZhi[1] };
            year = input.yearGanZhi ? { gan: input.yearGanZhi[0], zhi: input.yearGanZhi[1] } : gz.year;
            month = input.monthGanZhi ? { gan: input.monthGanZhi[0], zhi: input.monthGanZhi[1] } : gz.month;
            hour = input.hourGanZhi ? { gan: input.hourGanZhi[0], zhi: input.hourGanZhi[1] } : gz.hour;
        }
        else {
            day = gz.day;
            year = gz.year;
            month = gz.month;
            hour = gz.hour;
        }
        const core = paiPanCore({ day, year, month, hour, yueJiang, shiZhi });
        return {
            ok: true,
            datetime: new Date(ms).toISOString(),
            termLabel: input.dayGanZhi ? '' : termLabel(ms),
            question: input.question ?? '',
            ...core,
        };
    }
    catch (e) {
        return errorResult(String(e.message ?? e));
    }
}
function errorResult(error) {
    const empty = {
        zhi: '子', name: '', dunGan: '甲', tianJiang: '', linWei: '子',
        liuQin: '', changSheng: '', kongWang: false, yiMa: false,
    };
    return {
        ok: false,
        error,
        datetime: '',
        year: { gan: '甲', zhi: '子' }, month: { gan: '甲', zhi: '子' }, day: { gan: '甲', zhi: '子' }, hour: { gan: '甲', zhi: '子' },
        termLabel: '',
        yueJiang: '亥', yueJiangName: '', shiZhi: '子', dayNight: '昼',
        guiRen: '丑', guiRenName: '', guiRenShunNi: '顺',
        tianPan: [], dunGan: [], tianJiang: [], wei: [],
        siKe: [],
        sanChuan: { method: '', keTi: [], chu: empty, zhong: empty, mo: empty, detail: '' },
        xunKong: [], xunShou: { gan: '甲', zhi: '子' },
        shenSha: { 驿马: '寅', 禄神: '寅', 羊刃: '卯', 桃花: '酉', 华盖: '辰', 将星: '子' },
        question: '',
    };
}
/** 排盘结果 → 中文文字报告（工具输出，LLM 友好结构化） */
export function formatChartText(r) {
    if (!r.ok)
        return `排盘失败：${r.error}`;
    const gz = (g) => g.gan + g.zhi;
    const shenDetail = (s) => `${s.zhi}（${s.name}）：五行${ZHI_WX[s.zhi]}，${s.dunGan ? '遁' + s.dunGan + GAN_WX[s.dunGan] : '无遁干'}，加临${s.linWei}，乘${s.tianJiang}，六亲${s.liuQin}，${s.changSheng}${s.kongWang ? '，空亡' : ''}${s.yiMa ? '，驿马' : ''}`;
    const relationFull = (k) => {
        const upWx = ZHI_WX[k.up];
        const downWx = k.downLabel.startsWith('日干') ? GAN_WX[r.day.gan] : ZHI_WX[k.down];
        switch (k.relation) {
            case '克': return `上克下（${upWx}${k.up} 克 ${downWx}${k.down}）`;
            case '贼': return `下贼上（${downWx}${k.down} 克 ${upWx}${k.up}）`;
            case '生': return `上生下（${upWx}${k.up} 生 ${downWx}${k.down}）`;
            case '泄': return `下生上（${downWx}${k.down} 生 ${upWx}${k.up}）`;
            default: return `比和（${upWx}${k.up} 与 ${downWx}${k.down} 同五行）`;
        }
    };
    const lines = [];
    lines.push(`【大六壬排盘】${r.datetime ? new Date(r.datetime).toLocaleString('zh-CN', { hour12: false }) : ''}${r.question ? `｜问：${r.question}` : ''}`);
    lines.push('【基本信息】');
    lines.push(`四柱：${gz(r.year)}年 ${gz(r.month)}月 ${gz(r.day)}日 ${gz(r.hour)}时${r.termLabel ? `（${r.termLabel}）` : ''}`);
    lines.push(`日干：${r.day.gan}（${GAN_WX[r.day.gan]}）｜日支：${r.day.zhi}（${ZHI_WX[r.day.zhi]}）｜日干寄宫：${r.siKe[0]?.down ?? '—'}`);
    lines.push(`月将：${r.yueJiang}（${r.yueJiangName}）｜占时：${r.shiZhi}时｜${r.dayNight}占｜贵人：${r.guiRen}（${r.guiRenName}）${r.guiRenShunNi}布`);
    lines.push(`课体：${r.sanChuan.keTi.join('、') || '—'}｜起法：${r.sanChuan.method}`);
    lines.push('');
    lines.push('【天地盘总览】');
    lines.push('  地盘 | 天盘 | 神名 | 五行 | 遁干 | 天将 | 六亲 | 十二长生 | 空亡/驿马');
    for (const { diZhi, shen } of r.wei) {
        const flags = [shen.kongWang ? '空亡' : '', shen.yiMa ? '驿马' : ''].filter(Boolean).join('/') || '—';
        lines.push(`  ${diZhi} | ${shen.zhi} | ${shen.name} | ${ZHI_WX[shen.zhi]} | ${shen.dunGan ? shen.dunGan + GAN_WX[shen.dunGan] : '—'} | ${shen.tianJiang} | ${shen.liuQin} | ${shen.changSheng} | ${flags}`);
    }
    lines.push('');
    lines.push('【四课】');
    for (const k of r.siKe) {
        const u = k.upInfo;
        lines.push(`  ${['一', '二', '三', '四'][k.n - 1]}课：${k.downLabel}（${k.down}${k.downLabel.startsWith('日干') ? GAN_WX[r.day.gan] : ZHI_WX[k.down]}）上见 ${k.up}（${u.name}·${ZHI_WX[k.up]}）`);
        lines.push(`    关系：${relationFull(k)}`);
        lines.push(`    上神：${shenDetail(u)}`);
    }
    lines.push('  递进关系：二课下神 = 一课干上神；四课下神 = 三课支上神');
    lines.push('');
    lines.push('【三传】');
    for (const [label, t] of [['初传', r.sanChuan.chu], ['中传', r.sanChuan.zhong], ['末传', r.sanChuan.mo]]) {
        lines.push(`  ${label} ${shenDetail(t)}`);
    }
    if (r.sanChuan.zhong.linWei === r.sanChuan.chu.zhi) {
        lines.push(`  关系链：中传${r.sanChuan.zhong.zhi} = ${r.sanChuan.chu.zhi}支上神（${r.sanChuan.chu.zhi}位天盘）`);
        if (r.sanChuan.mo.linWei === r.sanChuan.zhong.zhi) {
            lines.push(`          末传${r.sanChuan.mo.zhi} = ${r.sanChuan.zhong.zhi}支上神（${r.sanChuan.zhong.zhi}位天盘）`);
        }
    }
    lines.push(`  起法说明：${r.sanChuan.detail}`);
    lines.push('');
    lines.push('【神煞】');
    lines.push(`旬空：${r.xunKong.join('、')}（${r.xunShou.gan}${r.xunShou.zhi}旬）｜驿马：${r.shenSha['驿马']}｜禄神：${r.shenSha['禄神']}｜羊刃：${r.shenSha['羊刃']}｜桃花：${r.shenSha['桃花']}｜华盖：${r.shenSha['华盖']}｜将星：${r.shenSha['将星']}`);
    const keyShen = [r.sanChuan.chu, r.sanChuan.zhong, r.sanChuan.mo, ...r.siKe.map(k => k.upInfo)];
    const kongInKey = [...new Set(keyShen.filter(s => s.kongWang).map(s => `${s.zhi}（${s.name}）`))];
    const maInKey = [...new Set(keyShen.filter(s => s.yiMa).map(s => `${s.zhi}（${s.name}）`))];
    if (kongInKey.length > 0)
        lines.push(`空亡落于关键：${kongInKey.join('、')}`);
    if (maInKey.length > 0)
        lines.push(`驿马落于关键：${maInKey.join('、')}`);
    return lines.join('\n');
}
/** 排盘结果 → JSON 文字报告（结构化，适合 LLM 直接阅读） */
export function formatChartJson(r) {
    if (!r.ok)
        return JSON.stringify({ ok: false, error: r.error }, null, 2);
    const gz = (g) => g.gan + g.zhi;
    const shenJson = (s) => ({
        zhi: s.zhi,
        name: s.name,
        wuXing: ZHI_WX[s.zhi],
        dunGan: s.dunGan,
        dunGanWuXing: s.dunGan ? GAN_WX[s.dunGan] : '',
        linWei: s.linWei,
        tianJiang: s.tianJiang,
        liuQin: s.liuQin,
        changSheng: s.changSheng,
        kongWang: s.kongWang,
        yiMa: s.yiMa,
    });
    const relationFull = (k) => {
        const upWx = ZHI_WX[k.up];
        const downWx = k.downLabel.startsWith('日干') ? GAN_WX[r.day.gan] : ZHI_WX[k.down];
        switch (k.relation) {
            case '克': return { label: '上克下', detail: `${upWx}${k.up} 克 ${downWx}${k.down}` };
            case '贼': return { label: '下贼上', detail: `${downWx}${k.down} 克 ${upWx}${k.up}` };
            case '生': return { label: '上生下', detail: `${upWx}${k.up} 生 ${downWx}${k.down}` };
            case '泄': return { label: '下生上', detail: `${downWx}${k.down} 生 ${upWx}${k.up}` };
            default: return { label: '比和', detail: `${upWx}${k.up} 与 ${downWx}${k.down} 同五行` };
        }
    };
    const keyShen = [r.sanChuan.chu, r.sanChuan.zhong, r.sanChuan.mo, ...r.siKe.map(k => k.upInfo)];
    const kongInKey = [...new Set(keyShen.filter(s => s.kongWang).map(s => `${s.zhi}（${s.name}）`))];
    const maInKey = [...new Set(keyShen.filter(s => s.yiMa).map(s => `${s.zhi}（${s.name}）`))];
    const relationChain = [];
    if (r.sanChuan.zhong.linWei === r.sanChuan.chu.zhi) {
        relationChain.push(`中传${r.sanChuan.zhong.zhi} = ${r.sanChuan.chu.zhi}支上神（${r.sanChuan.chu.zhi}位天盘）`);
        if (r.sanChuan.mo.linWei === r.sanChuan.zhong.zhi) {
            relationChain.push(`末传${r.sanChuan.mo.zhi} = ${r.sanChuan.zhong.zhi}支上神（${r.sanChuan.zhong.zhi}位天盘）`);
        }
    }
    const data = {
        type: '大六壬排盘',
        meta: {
            datetime: r.datetime,
            question: r.question || undefined,
            sizhu: {
                year: gz(r.year),
                month: gz(r.month),
                day: gz(r.day),
                hour: gz(r.hour),
            },
            dayGan: r.day.gan,
            dayGanWuXing: GAN_WX[r.day.gan],
            dayZhi: r.day.zhi,
            dayZhiWuXing: ZHI_WX[r.day.zhi],
            riGanJiGong: r.siKe[0]?.down,
            yueJiang: r.yueJiang,
            yueJiangName: r.yueJiangName,
            shiZhi: r.shiZhi,
            dayNight: r.dayNight,
            guiRen: r.guiRen,
            guiRenName: r.guiRenName,
            guiRenShunNi: r.guiRenShunNi,
            keTi: r.sanChuan.keTi,
            method: r.sanChuan.method,
        },
        tianPan: r.wei.map(w => ({
            diZhi: w.diZhi,
            ...shenJson(w.shen),
        })),
        siKe: r.siKe.map(k => {
            const rel = relationFull(k);
            return {
                n: k.n,
                down: k.down,
                downLabel: k.downLabel,
                downWuXing: k.downLabel.startsWith('日干') ? GAN_WX[r.day.gan] : ZHI_WX[k.down],
                up: k.up,
                upName: k.upInfo.name,
                upWuXing: ZHI_WX[k.up],
                relation: rel.label,
                relationDetail: rel.detail,
                upInfo: shenJson(k.upInfo),
            };
        }),
        siKeChain: ['二课下神 = 一课干上神', '四课下神 = 三课支上神'],
        sanChuan: {
            method: r.sanChuan.method,
            detail: r.sanChuan.detail,
            relationChain,
            chu: shenJson(r.sanChuan.chu),
            zhong: shenJson(r.sanChuan.zhong),
            mo: shenJson(r.sanChuan.mo),
        },
        shenSha: { ...r.shenSha },
        xunKong: r.xunKong,
        xunShou: `${gz(r.xunShou)}旬`,
        keyFlags: {
            ...(kongInKey.length > 0 ? { kongWangInKey: kongInKey } : {}),
            ...(maInKey.length > 0 ? { yiMaInKey: maInKey } : {}),
        },
    };
    return JSON.stringify(data, null, 2);
}
//# sourceMappingURL=liuren.js.map
