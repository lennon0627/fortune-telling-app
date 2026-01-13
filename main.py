from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, date, timedelta  # 【修正1】timedeltaを追加
from lunardate import LunarDate
import html
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 定数・辞書データ
# ==========================================

ETO_LIST = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
JIKKAN_LIST = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
GOGYOU_MAP = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
    '寅': '木', '卯': '木', '巳': '火', '午': '火', '辰': '土', '丑': '土', '未': '土', '戌': '土',
    '申': '金', '酉': '金', '子': '水', '亥': '水'
}

# 24節気（節入り日）計算用の定数（1900年〜2099年対応の略算式用）
SETSUIRI_CONSTANTS = {
    1: 6.1697,   # 1月 小寒
    2: 4.8693,   # 2月 立春
    3: 6.3609,   # 3月 啓蟄
    4: 5.5909,   # 4月 清明
    5: 6.3189,   # 5月 立夏
    6: 6.5806,   # 6月 芒種
    7: 8.0939,   # 7月 小暑
    8: 8.4358,   # 8月 立秋
    9: 8.4758,   # 9月 白露
    10: 9.0983,  # 10月 寒露
    11: 8.2422,  # 11月 立冬
    12: 7.9152   # 12月 大雪
}

KYUSEI_DATA = {
    '一白水星': {'score': 15, 'color': '白・黒', 'direction': '北', 'food': '塩辛いもの・魚介類', 'action': '温泉・睡眠', 
                'desc': '水の精気を受け、柔軟で適応力があります。表向きはソフトですが、内面は芯が強く秘密主義な一面も。苦労を乗り越えて大成するタイプです。'},
    '二黒土星': {'score': 5, 'color': '黄・茶・ベージュ', 'direction': '南西', 'food': '甘味・根菜類・お米', 'action': '園芸・ボランティア', 
                'desc': '大地の象徴であり、母性的な優しさと忍耐強さを持ちます。真面目で堅実、人を育てるのが得意で、「縁の下の力持ち」として信頼を集めます。'},
    '三碧木星': {'score': 20, 'color': '青・緑', 'direction': '東', 'food': '酸味・柑橘類・野菜', 'action': '朝の散歩・音楽鑑賞', 
                'desc': '雷の象徴で、若々しくエネルギッシュです。決断が早く行動力抜群ですが、少しせっかちな面も。新しい流行や技術をいち早く取り入れる才能があります。'},
    '四緑木星': {'score': 18, 'color': '緑', 'direction': '南東', 'food': '麺類・うなぎ・長いもの', 'action': '旅行・アロマテラピー', 
                'desc': '風のように自由で、人当たりが良く社交的です。争いを好まず「整える」力に長けていますが、優柔不断になりやすい一面も。人脈が財産となる星です。'},
    '五黄土星': {'score': 5, 'color': '黄・茶', 'direction': '中央', 'food': '発酵食品・納豆・味噌', 'action': '断捨離・古着屋巡り', 
                'desc': '帝王の星と呼ばれ、圧倒的なパワーとリーダーシップを持ちます。破壊と再生の力を秘め、逆境に強い大器晩成型。面倒見が良い親分肌です。'},
    '六白金星': {'score': 10, 'color': '金・銀・パール', 'direction': '北西', 'food': '辛いもの・高級食材・果物', 'action': '神社仏閣巡り・投資', 
                'desc': '天の象徴で、高潔で完璧主義なリーダータイプです。責任感が強く、目標に向かって妥協せず突き進みます。プライドは高いですが実力は本物です。'},
    '七赤金星': {'score': 8, 'color': 'オレンジ・ピンク', 'direction': '西', 'food': '鶏肉・卵・コーヒー', 'action': '外食・カラオケ', 
                'desc': '喜びと悦楽を司る星で、愛嬌があり話術に長けた人気者です。衣食住に困らない運を持ちますが、少し浪費家な一面も。人生を楽しむ天才です。'},
    '八白土星': {'score': 6, 'color': 'アイボリー・ブラウン', 'direction': '北東', 'food': '牛肉・魚卵・甘いもの', 'action': '登山・貯蓄・模様替え', 
                'desc': '山の象徴で、どっしりとした安定感と意志の強さを持ちます。変化と改革を好み、一度決めた目標は困難があってもやり遂げる粘り強さがあります。'},
    '九紫火星': {'score': 12, 'color': '紫・赤', 'direction': '南', 'food': '苦味・海苔・甲殻類（カニ・エビ）', 'action': '美容・芸術鑑賞・日光浴', 
                'desc': '火の象徴で、情熱的かつ美的センスに優れています。直感力が鋭く頭脳明晰ですが、熱しやすく冷めやすい気分屋なところも。華やかな舞台が似合います。'}
}

NIKKAN_DATA = {
    '甲': {'title': '大樹', 'desc': '曲がったことが嫌いなリーダータイプ。向上心が強く、一本気で頼りがいがあります。挫折すると脆い一面も。'},
    '乙': {'title': '草花', 'desc': '環境適応能力が高い柔軟なタイプ。協調性があり、粘り強く目的を達成します。少し依存心が強いところも。'},
    '丙': {'title': '太陽', 'desc': '明るく情熱的で、中心的な存在。裏表がなく開放的ですが、熱しやすく冷めやすい気分屋な面も。'},
    '丁': {'title': '灯火', 'desc': '温和で思慮深い芸術家タイプ。内面に熱い情熱を秘めており、洞察力が鋭いです。神経質な一面があります。'},
    '戊': {'title': '山岳', 'desc': 'どっしりと構えた包容力のある親分肌。楽観的でマイペースですが、頑固で融通が利かないことも。'},
    '己': {'title': '大地', 'desc': '多才で教養があり、人を育てるのが得意。堅実で家庭的ですが、少し迷いやすく複雑な内面を持ちます。'},
    '庚': {'title': '鋼鉄', 'desc': '決断力と行動力に優れた改革者。正義感が強く白黒はっきりさせますが、攻撃的になりやすいので注意。'},
    '辛': {'title': '宝石', 'desc': '繊細で美意識が高い感受性豊かなタイプ。品格があり努力家ですが、プライドが高く傷つきやすいです。'},
    '壬': {'title': '大海', 'desc': 'スケールが大きく、自由を愛する冒険家。知性的で臨機応変に対応できますが、束縛を嫌い流されやすいです。'},
    '癸': {'title': '雨露', 'desc': '穏やかで慈愛に満ちた癒やし系。忍耐強くコツコツ努力しますが、潔癖で少し悲観的になりやすい傾向も。'}
}

SUKUYO_ORDER = ['角', '亢', '氏', '房', '心', '尾', '箕', '斗', '女', '虚', '危', '室', '壁', '奎', '婁', '胃', '昴', '畢', '觜', '参', '井', '鬼', '柳', '星', '張', '翼', '軫']
SUKUYO_MONTH_START = ['室', '奎', '胃', '畢', '参', '鬼', '張', '角', '氏', '心', '斗', '虚']

SUKUYO_DATA_LIST = {
    '角': {'score': 18, 'desc': '社交的で華やか、純粋な心を持つ人気者。', 'fortune': '人間関係が広がる年。新しい出会いを大切に。'},
    '亢': {'score': 15, 'desc': '信念が強く、正義感にあふれるリーダータイプ。', 'fortune': '自分の信じる道を進むことで道が開けます。'},
    '氏': {'score': 12, 'desc': '知恵と直感に優れ、戦略的に物事を進める策士。', 'fortune': '計画の見直しが吉。焦らず足元を固めて。'},
    '房': {'score': 20, 'desc': '財運とカリスマ性を兼ね備えた、生まれながらの王様。', 'fortune': '金運が絶好調。大きな決断をするなら今。'},
    '心': {'score': 16, 'desc': '愛嬌があり誰からも好かれるが、内面は孤独を好む一面も。', 'fortune': '心のケアを優先して。趣味に没頭すると吉。'},
    '尾': {'score': 18, 'desc': '粘り強く、一度決めたことは最後までやり遂げる武人。', 'fortune': '努力が実を結ぶ時期。諦めずに継続を。'},
    '箕': {'score': 14, 'desc': 'サバサバとしていて細かいことは気にしない、豪快な自由人。', 'fortune': '旅行や移動にツキあり。遠出をしてみては。'},
    '斗': {'score': 19, 'desc': '精神性が高く、不思議なカリスマ性で人を惹きつける。', 'fortune': '直感が冴え渡る年。ひらめきを信じて行動を。'},
    '女': {'score': 15, 'desc': '努力家で実務能力が高く、組織の中で重宝される存在。', 'fortune': 'スキルアップに最適な時期。勉強を始めよう。'},
    '虚': {'score': 10, 'desc': '感受性が強くデリケート。複雑な内面を持つロマンチスト。', 'fortune': '感情の波に注意。冷静な判断を心がけて。'},
    '危': {'score': 12, 'desc': '好奇心旺盛で流行に敏感。常に新しい刺激を求める。', 'fortune': '新しい趣味や流行を取り入れると運気アップ。'},
    '室': {'score': 18, 'desc': '大胆不敵で自信家。我が道を突き進む実力者。', 'fortune': '自信過剰に注意しつつ、大胆な挑戦が吉。'},
    '壁': {'score': 16, 'desc': '穏やかで慈悲深く、周囲を支える縁の下の力持ち。', 'fortune': '人助けが自分に返ってくる年。優しさを大切に。'},
    '奎': {'score': 17, 'desc': '気品があり、礼儀正しい。恵まれた環境で育つことが多い。', 'fortune': '目上の人からの引き立てがあるかも。礼節を重んじて。'},
    '婁': {'score': 15, 'desc': '器用で多才。人の心を掴むのが上手いアイデアマン。', 'fortune': 'アイデアが形になる時。企画や提案を積極的に。'},
    '胃': {'score': 18, 'desc': '独立心が強く、エネルギッシュ。逆境に強いチャレンジャー。', 'fortune': '困難を乗り越えられる年。挑戦を恐れずに。'},
    '昴': {'score': 20, 'desc': '名誉と美を愛する芸術肌。周囲から一目置かれる存在。', 'fortune': '名声が得られるチャンス。自分磨きに力を入れて。'},
    '畢': {'score': 19, 'desc': '庶民的で落ち着きがあり、着実に財を成す大器晩成型。', 'fortune': 'コツコツとした努力が評価されます。堅実に。'},
    '觜': {'score': 14, 'desc': '弁が立ち、説得力がある。知識欲が旺盛な知性派。', 'fortune': 'コミュニケーション能力が鍵。積極的に発言を。'},
    '参': {'score': 16, 'desc': '陽気で改革心があり、古い体制を打ち破るエネルギーを持つ。', 'fortune': '変化を恐れない姿勢が幸運を呼びます。'},
    '井': {'score': 15, 'desc': '几帳面で理性的。物事を冷静に分析する管理者タイプ。', 'fortune': '整理整頓が運気アップの鍵。断捨離もおすすめ。'},
    '鬼': {'score': 18, 'desc': '好奇心旺盛で自由奔放。不思議な霊感や直感を持つことも。', 'fortune': '直感を大切に。不思議な巡り合わせがある予感。'},
    '柳': {'score': 13, 'desc': '情熱的だが気性が激しい面も。仲間思いの熱血漢。', 'fortune': '感情のコントロールが課題。穏やかに過ごして。'},
    '星': {'score': 15, 'desc': '地味ながらも実力がある。粘り強く目標に向かう努力家。', 'fortune': '地道な作業が評価につながる。焦らず一歩ずつ。'},
    '張': {'score': 19, 'desc': '華やかでドラマチックな人生を好む。存在感抜群の主役。', 'fortune': 'スポットライトを浴びる年。堂々と振る舞って。'},
    '翼': {'score': 17, 'desc': '完璧主義で責任感が強い。海外や遠方と縁がある。', 'fortune': '海外旅行や異文化交流にツキあり。視野を広げて。'},
    '軫': {'score': 16, 'desc': '柔軟で適応力が高い。人の心を読むのが得意な癒やし系。', 'fortune': '対人運が好調。聞き役に徹すると信頼度アップ。'}
}

GOSEI_DATA = {
    '金のイルカ': {'score': 20, 'desc': '明るく社交的で、人を楽しませる才能があります。'},
    '銀のイルカ': {'score': 15, 'desc': '柔軟性があり、人当たりが良い人気者です。'},
    '金の鳳凰': {'score': 18, 'desc': '忍耐強く、一度決めたことは最後までやり遂げる力があります。'},
    '銀の鳳凰': {'score': 12, 'desc': '信念が強く、自分のルールを持っています。'},
    '金のインディアン': {'score': 8, 'desc': '好奇心旺盛で、新しいことが大好きです。'},
    '銀のインディアン': {'score': 6, 'desc': '多趣味で情報通、同時に複数のことをこなせます。'},
    '金の時計': {'score': 10, 'desc': '親切で面倒見が良く、人とのつながりを大切にします。'},
    '銀の時計': {'score': 8, 'desc': '世話好きで、人の役に立つことに喜びを感じます。'},
    '金のカメレオン': {'score': 18, 'desc': '学習能力が高く、確実に結果を出します。'},
    '銀のカメレオン': {'score': 12, 'desc': '几帳面で真面目、ルールや伝統を重んじます。'},
    '金の羅針盤': {'score': 10, 'desc': '礼儀正しく、品格があります。直感力に優れます。'},
    '銀の羅針盤': {'score': 5, 'desc': '真面目で責任感が強く、控えめながらも芯の強さを持っています。'}
}

KABBALAH_DESC = {
    1: '開拓者・リーダー', 2: '協調・サポーター', 3: '表現者・クリエイター', 4: '建設者・堅実', 5: '冒険家・自由',
    6: '教育者・調和', 7: '探求者・分析', 8: '権力者・成功', 9: '慈善家・完結', 11: 'メッセンジャー', 22: 'マスタービルダー'
}
KABBALAH_SCORE_MAP = {1: 20, 2: 8, 3: 15, 4: 6, 5: 12, 6: 10, 7: 7, 8: 18, 9: 10, 11: 18, 22: 18}

ETO_SCORES = {'寅': 20, '戌': 20, '未': 18, '巳': 15, '午': 10, '申': 10, '酉': 10, '亥': 10, '辰': 10, '丑': 5, '子': 5, '卯': 5}

RANKING_MASTER = []

def generate_ranking_master():
    combinations = []
    for star_name, s_data in KYUSEI_DATA.items():
        for eto_name, e_score in ETO_SCORES.items():
            base_score = s_data['score'] + e_score + 10
            combinations.append({"kyusei": star_name, "eto": eto_name, "score": base_score})
    combinations.sort(key=lambda x: x["score"], reverse=True)
    for rank, item in enumerate(combinations, start=1):
        item["rank"] = rank
    return combinations

RANKING_MASTER = generate_ranking_master()

# ==========================================
# リクエストモデル
# ==========================================

class UserData(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    gender: str = "female"
    name: str = "あなた"

# ==========================================
# 占い計算ロジック
# ==========================================

def get_setsuiri_day(year, month):
    """
    指定された年・月の節入り日（四柱推命の月の変わり目）を計算する
    1900年〜2099年対応の略算式を使用
    """
    if month not in SETSUIRI_CONSTANTS:
        return 5 

    constant = SETSUIRI_CONSTANTS[month]
    delta_year = year - 1900
    
    # 略算式
    term_day = int(constant + 0.2422 * delta_year - int(delta_year / 4))
    
    return term_day

def get_risshun_date(year):
    """立春の日付を取得"""
    day = get_setsuiri_day(year, 2)
    return date(year, 2, day)

def calculate_kyusei(year, month, day):
    """九星気学の計算"""
    target_date = date(year, month, day)
    risshun = get_risshun_date(year)
    
    calc_year = year - 1 if target_date < risshun else year
    
    s = sum(int(d) for d in str(calc_year))
    while s > 9:
        s = sum(int(d) for d in str(s))
    star_num = 11 - s
    if star_num > 9:
        star_num -= 9
    if star_num <= 0:
        star_num += 9
    stars = [None, '一白水星', '二黒土星', '三碧木星', '四緑木星', '五黄土星', '六白金星', '七赤金星', '八白土星', '九紫火星']
    return stars[star_num]

def calculate_shichu_full(year, month, day, hour):
    """四柱推命の計算"""
    target_date = date(year, month, day)
    risshun = get_risshun_date(year)
    calc_year = year - 1 if target_date < risshun else year
    
    year_idx = (36 + (calc_year - 1900)) % 60
    year_pillar = JIKKAN_LIST[year_idx % 10] + ETO_LIST[year_idx % 12]

    term_day = get_setsuiri_day(year, month)
    calc_month = month
    if day < term_day:
        calc_month = month - 1
        if calc_month == 0:
            calc_month = 12
    
    year_kan_idx = year_idx % 10
    month_base = [2, 4, 6, 8, 0][year_kan_idx % 5]
    m_offset = calc_month - 2
    if m_offset < 0:
        m_offset += 12
    
    month_kan_idx = (month_base + m_offset) % 10
    month_shi_idx = (2 + m_offset) % 12
    month_pillar = JIKKAN_LIST[month_kan_idx] + ETO_LIST[month_shi_idx]

    base_date = date(2000, 1, 1)
    diff_days = (target_date - base_date).days
    
    if hour >= 23:
        diff_days += 1
    
    day_idx = (54 + diff_days) % 60
    if day_idx < 0:
        day_idx += 60
    day_pillar = JIKKAN_LIST[day_idx % 10] + ETO_LIST[day_idx % 12]

    day_kan_idx = day_idx % 10
    hour_base = [0, 2, 4, 6, 8][day_kan_idx % 5]
    
    if hour >= 23 or hour < 1:
        hour_shi_idx = 0 
    else:
        hour_shi_idx = (hour + 1) // 2 % 12
    
    hour_kan_idx = (hour_base + hour_shi_idx) % 10
    hour_pillar = JIKKAN_LIST[hour_kan_idx] + ETO_LIST[hour_shi_idx]

    # --- 空亡（天中殺）計算の修正 ---
    # 計算式: 日支数 - 日干数
    # その余りに応じて空亡となる地支が決まる
    diff = (day_idx % 12) - (day_idx % 10)
    if diff < 0:
        diff += 12
    
    # 修正後のマッピング
    kubou_map = {0: '戌亥', 2: '申酉', 4: '午未', 6: '辰巳', 8: '寅卯', 10: '子丑'}
    kubou = kubou_map.get(diff, '--')

    elements = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
    for p in [year_pillar, month_pillar, day_pillar, hour_pillar]:
        for char in p:
            if char in GOGYOU_MAP:
                elements[GOGYOU_MAP[char]] += 1
    
    return {
        "year": year_pillar, "month": month_pillar, "day": day_pillar, "hour": hour_pillar,
        "kubou": kubou, "elements": elements, "day_idx": day_idx,
        "eto": ETO_LIST[year_idx % 12]
    }

def calculate_sukuyo(year, month, day, hour):  # 【修正2】引数にhourを追加
    """宿曜占星術の計算"""
    # 日付オブジェクトを作成
    target_date = date(year, month, day)

    # 宿曜では「夜明け」を日付の区切りとします。
    # ここでは午前5時より前に生まれた場合は「前日」として扱います。
    if hour < 5:
        target_date = target_date - timedelta(days=1)
    
    lunar = LunarDate.fromSolarDate(target_date.year, target_date.month, target_date.day)
    l_month = lunar.month
    l_day = lunar.day
    
    start_star_name = SUKUYO_MONTH_START[l_month - 1]
    start_idx = SUKUYO_ORDER.index(start_star_name)
    target_idx = (start_idx + l_day - 1) % 27
    
    return SUKUYO_ORDER[target_idx]

def calculate_gosei(year, day_idx):
    """五星三心占いの計算"""
    fate = (day_idx % 60) + 1
    
    if fate <= 10:
        t = '羅針盤'
    elif fate <= 20:
        t = 'インディアン'
    elif fate <= 30:
        t = '鳳凰'
    elif fate <= 40:
        t = '時計'
    elif fate <= 50:
        t = 'カメレオン'
    else:
        t = 'イルカ'
    
    m = '金' if year % 2 == 0 else '銀'
    return f"{m}の{t}"

def calculate_kabbalah(year, month, day):
    """カバラ数秘術の計算"""
    s = sum(int(c) for c in f"{year}{month}{day}")
    while s > 9 and s != 11 and s != 22:
        s = sum(int(c) for c in str(s))
    return s

def generate_fortune_text(name, kyusei, gosei, sukuyo):
    """総合運勢テキスト生成"""
    safe_name = html.escape(name)
    return f"""
    <p><strong>{safe_name}さんの2026年は...</strong></p>
    <p>九星気学では「{kyusei}」、五星三心では「{gosei}」という強力な星回りにあります。</p>
    <p>特に宿曜占星術の「{sukuyo}宿」の運気が巡ってきており、個性が輝く一年となるでしょう。</p>
    <p>全体を通して、自信を持って決断することで、大きなチャンスを引き寄せられます。</p>
    """

# ==========================================
# APIエンドポイント
# ==========================================

@app.post("/api/fortune")
def calculate_fortune(data: UserData):
    try:
        kyusei = calculate_kyusei(data.year, data.month, data.day)
        shichu = calculate_shichu_full(data.year, data.month, data.day, data.hour)
        sukuyo = calculate_sukuyo(data.year, data.month, data.day, data.hour) # 【修正3】引数にdata.hourを渡す
        gosei = calculate_gosei(data.year, shichu['day_idx'])
        kabbalah = calculate_kabbalah(data.year, data.month, data.day)
        
        nikkan_char = shichu['day'][0]
        nikkan_info = NIKKAN_DATA.get(nikkan_char, {'title': '不明', 'desc': 'データがありません'})
        shichu_desc_text = f"あなたは自然界で表すと<strong>「{nikkan_info['title']}」</strong>の性質を持っています。<br>{nikkan_info['desc']}"
        
        k_data = KYUSEI_DATA.get(kyusei, {})
        s_data = SUKUYO_DATA_LIST.get(sukuyo, {'score': 10, 'desc': '独自の才能と可能性を秘めた星です。', 'fortune': '自分自身を見つめ直す良い機会です。'})
        g_data = GOSEI_DATA.get(gosei, {'score': 10, 'desc': '個性を活かして進みましょう。'})
        kab_score = KABBALAH_SCORE_MAP.get(kabbalah, 10)
        kab_desc = KABBALAH_DESC.get(kabbalah, '独自の世界観')

        counts = list(shichu['elements'].values())
        diff = max(counts) - min(counts)
        shichu_score = max(5, 25 - (diff * 3))

        personal_bonus = (s_data['score'] + g_data['score'] + kab_score + shichu_score) * 0.6
        
        rank_info = next((i for i in RANKING_MASTER if i["kyusei"] == kyusei and i["eto"] == shichu['eto']), None)
        base_rank = rank_info["rank"] if rank_info else 50
        base_score = rank_info["score"] if rank_info else 25
        
        total_score = max(30, min(100, int(base_score + personal_bonus)))

        return {
            "results": {
                "kyusei": {
                    "star": kyusei,
                    "desc": k_data.get('desc', ''),
                    "lucky_color": k_data.get('color', ''),
                    "lucky_direction": k_data.get('direction', ''),
                    "lucky_food": k_data.get('food', ''),
                    "lucky_action": k_data.get('action', ''),
                },
                "shichu": {
                    "year": shichu['year'],
                    "month": shichu['month'],
                    "day": shichu['day'],
                    "hour": shichu['hour'],
                    "kubou": shichu['kubou'],
                    "elements": shichu['elements'],
                    "desc": shichu_desc_text,
                },
                "sukuyo": {
                    "star": f"{sukuyo}宿",
                    "desc": s_data['desc'],
                    "fortune": s_data['fortune'],
                    "work": "得意分野を伸ばすと吉",
                    "love": "誠実な対応が鍵",
                },
                "gosei": {
                    "type": gosei,
                    "desc": g_data['desc'],
                },
                "kabbalah": {
                    "num": kabbalah,
                    "desc": kab_desc,
                },
                "total_score": total_score,
                "rank": base_rank,
                "eto_year": shichu['eto'],
                "fortune_text": generate_fortune_text(data.name, kyusei, gosei, sukuyo),
                
                "score_detail": {
                    "base": {
                        "name": "基本運勢 (九星×干支)",
                        "score": base_score,
                        "max": 45
                    },
                    "bonus": {
                        "sukuyo": {"name": "宿曜占星術", "score": int(s_data['score'] * 0.6)},
                        "gosei": {"name": "五星三心", "score": int(g_data['score'] * 0.6)},
                        "kabbalah": {"name": "数秘術", "score": int(kab_score * 0.6)},
                        "shichu": {"name": "五行バランス", "score": int(shichu_score * 0.6)}
                    }
                }
            }
        }
    except Exception as e:
        print(f"Error calculating fortune: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 静的ファイル配信（staticフォルダ対応版）
# ==========================================

# staticフォルダを静的ファイルとしてマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# ルートパスにアクセスしたら staticフォルダ内の index.html を返す
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')