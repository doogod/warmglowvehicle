import re
# ---------- colours (Carsensor, katakana -> English) ----------
COL = {
"ホワイト":"White","クレヨン":"Crayon","ブラック":"Black","ビアンコ":"Bianco","ジェットブラックメタリック":"Jet Black Metallic",
"アイスグレーメタリック":"Ice Grey Metallic","ネロ・テンペスタ":"Nero Tempesta","グレー":"Grey","GTシルバーメタリック":"GT Silver Metallic",
"ビアンコ・アストロ":"Bianco Astro","ネロ・リベーレ":"Nero Ribelle","ブルー":"Blue","グリージョ・ラヴァ":"Grigio Lava","シリカホワイト":"Silica White",
"ビアンコアヴス":"Bianco Avus","レッド":"Red","シャークブルー":"Shark Blue","オニキスブラック":"Onyx Black","ロッソコルサ":"Rosso Corsa",
"シルバー":"Silver","ガンメタリック":"Gunmetal","サーペンタイン":"Serpentine","ビアンコイタリア":"Bianco Italia","パールホワイト":"Pearl White",
"カーマインレッド":"Carmine Red","ゲンチアンブルーメタリック":"Gentian Blue Metallic","キャララホワイトメタリック":"Carrara White Metallic",
"オニキス":"Onyx","グラッシャーホワイト":"Glacier White","ブルー・エモツィオーネ":"Blu Emozione","タンザナイトブルー":"Tanzanite Blue",
"グリジオシルバーストーン":"Grigio Silverstone","ダークグリーン":"Dark Green","グリーン":"Green","スレートグレーネオ":"Slate Grey Neo",
"シェードグリーンメタリック":"Shade Green Metallic","ブルー・インテンソ":"Blu Intenso","プラトー":"Plateau","サロス":"Saros",
"マクラーレンオレンジ":"McLaren Orange","シーラスグレー":"Cirrus Grey","ビアンコアブス":"Bianco Avus","ゴールド":"Gold",
"ネロプロサングエ":"Nero Purosangue","アルジェントニュルブルクリンク":"Argento Nürburgring","ビアンコセルヴィノ":"Bianco Cervino",
"グレーメタリック":"Grey Metallic","パール":"Pearl","アークティックグレー":"Arctic Grey","カルタヘナイエローメタリック":"Cartagena Yellow Metallic",
"バナジウムグレーメタリック":"Vanadium Grey Metallic","ルビースターネオ":"Ruby Star Neo","ガーズレッド":"Guards Red","ダークブルー":"Dark Blue",
"ネロ・アッソルート":"Nero Assoluto","ビアンコ・アルピ":"Bianco Alpi","グリージョ・ラヴァ・オパーコ":"Grigio Lava Opaco","ネロ アッソルート":"Nero Assoluto",
"ブルーインテンソ":"Blu Intenso","ビアンコ・オーディス":"Bianco Audace","ネロ・エニグマ":"Nero Enigma","アマランスレッド":"Amaranth Red",
"マンティスグリーン":"Mantis Green","アンスラサイト":"Anthracite","グレイシアホワイト":"Glacier White","トウキョウシアン":"Tokyo Cyan",
"アビスブラック":"Abyss Black","ブレードシルバー":"Blade Silver","グレー（特注オプションカラー）":"Grey (special order)","ネロデイトナ":"Nero Daytona",
"ロッソ・イモラ（Rosso Imola）":"Rosso Imola","ビアンコセルヴィーノ":"Bianco Cervino","ビアンコセルビノ":"Bianco Cervino","クオイオ":"Cuoio",
"グリジオグラニート":"Grigio Granito","ネロギャラクシー":"Nero Galaxy","ネロ":"Nero","グリジオスクーロ 792":"Grigio Scuro","ロッソイモラ":"Rosso Imola",
"アルジェントニュルブルクリングオパコ":"Argento Nürburgring Opaco","ロッソフェラーリ":"Rosso Ferrari","ロッソカリフォルニア":"Rosso California",
"グリジオ シルバーストーン":"Grigio Silverstone","ネロステラート":"Nero Stellato","ライトベージュメタリック":"Light Beige Metallic","ワインレッド":"Wine Red",
"グリジオメディオン":"Grigio Medio","ビアンコオンダマリーナ":"Bianco Onda Marina","メタリックゴールドグリーン":"Metallic Gold Green","マットパール":"Matte Pearl",
"ネロ・ヘレネ":"Nero Helene","ネロ・ヘレーネ":"Nero Helene","ライトグリーン":"Light Green","アークティックホワイト":"Arctic White",
"テンペストグレー":"Tempest Grey","ブラックダイアモンド":"Black Diamond","ルガーノブルー":"Lugano Blue","ゲンチアンブルー":"Gentian Blue",
"アゲートグレーメタリック":"Agate Grey Metallic","ドロマイトシルバー":"Dolomite Silver","イパネマブルーメタリック":"Ipanema Blue Metallic",
"アイスグレー":"Ice Grey","エトナブルー":"Etna Blue","ホワイトツートン":"White two-tone","ブルーメタリック":"Blue Metallic","シャークブルー（D7）":"Shark Blue",
"スレートグレーメタリック":"Slate Grey Metallic","プロヴァンス":"Provence","ダークブルーメタリック":"Dark Blue Metallic","パイソングリーン":"Python Green",
"レーシングイエロー":"Racing Yellow","カーボングレーメタリック":"Carbon Grey Metallic","オークグリーンメタリック":"Oak Green Metallic",
"オークグリーンメタリックネオ":"Oak Green Metallic Neo","グリーン(元色シャークブルー）":"Green (originally Shark Blue)",
"OP有償レジェンズカラー シェードグリーン":"Shade Green (Legends colour)","ブリーズ":"Breeze","シークインブルー":"Sequin Blue","ベージュシルバー":"Beige Silver",
"グレイシアホワイトM":"Glacier White Metallic","タングステン":"Tungsten","ブラックＭ":"Black Metallic","モロッカン・ブルー・メタリック":"Moroccan Blue Metallic",
"グレイシャーホワイト":"Glacier White","ドラゴンレッドII":"Dragon Red II","マグネティックメタリック":"Magnetic Metallic","エクストリームシルバー":"Extreme Silver",
"カンブリアングレイ":"Cambrian Grey","カンブリアングレー":"Cambrian Grey","ブラックブラック":"Black","ブラックメタリック":"Black Metallic","グラビティグレー":"Gravity Grey",
"ブラッククリスタル":"Black Crystal","ライトブルーメタリック":"Light Blue Metallic","ライトベージュ":"Light Beige","オレンジ":"Orange","ロッソ・トリブート":"Rosso Tributo",
"グリジオ・マラテア":"Grigio Maratea","ネロ・リベッレ":"Nero Ribelle","ダークブルーブルー":"Dark Blue","グリジオ":"Grigio","モデナブルー":"Blu Modena",
"グリージョ・マラテア・マット":"Grigio Maratea Matt","グリージョ・ルミエラ・マット":"Grigio Lumiera Matt","オペラビアンカ":"Opera Bianca","ペルシャ・ブルー":"Blu Persia",
"ビアンコホワイト":"Bianco","ペルシャ・ブルー・シェード":"Blu Persia","ブルー ノビレ":"Blu Nobile","ネロエッセンツァ":"Nero Essenza","ブルー インテンソ":"Blu Intenso",
"ブルー・ノービレ":"Blu Nobile","グリジオ マラテア":"Grigio Maratea","グリジオ ラヴァ オパコ":"Grigio Lava Opaco","ネロテンペスタ":"Nero Tempesta","ネロ テンペスタ":"Nero Tempesta",
"ブラウン":"Brown","ロッソヴィンセント":"Rosso Vincente","ブルーエモツィオーネ":"Blu Emozione","ブルー モデナ":"Blu Modena","ビアンコ パステッロ":"Bianco Pastello",
"ジアッロジェニオ":"Giallo Genio","イエロー":"Yellow","ホワイトパール":"White Pearl","ヴェルデロイヤル":"Verde Royale","ブルー・モデナ":"Blu Modena","ブルーモデナ":"Blu Modena",
"ホワイトシルバー":"White Silver","グリージョラヴァ":"Grigio Lava","エンバーオレンジ":"Ember Orange","ＭＳＯビスポークブラック":"MSO Bespoke Black","ビリディアン":"Viridian",
"MSOイエロー":"MSO Yellow","ナマカブルー":"Namaka Blue","ルードゥスブルー":"Ludus Blue","シブヤスピリット":"Shibuya Spirit","ラヴァグレー":"Lava Grey","XPグリーン":"XP Green",
"オレンジパール":"Orange Pearl","ベガブルー":"Vega Blue","ラヴァグレイ（MSOペイント）":"Lava Grey (MSO)","オーロラブルー":"Aurora Blue","ベリーズ・ブルー":"Belize Blue",
"エンバリーオレンジ／ブラック":"Ember Orange / Black","イエローグリーンゴールド":"Yellow Green Gold","トーキョーシアン":"Tokyo Cyan","シルバーメタリック":"Silver Metallic",
"スーパーノヴァシルバー":"Supernova Silver","オニキスブラック（フルPPF）":"Onyx Black","フラックスグリーンII":"Flux Green II","サルテグレー":"Sarthe Grey",
"セラミックグレー":"Ceramic Grey","パパイヤスパーク":"Papaya Spark","ドラゴンレッド":"Dragon Red","ポルトフィーノ":"Portofino",
}
def col(s):
    s=(s or '').strip()
    if s in COL: return COL[s]
    s=s.replace('Girigio','Grigio').replace('Grijio','Grigio').replace('BlackDiamond','Black Diamond').replace('RoseGold overMagnetic','Rose Gold over Magnetic').replace('DoveGrey','Dove Grey').replace('BluEmozione','Blu Emozione').replace('Cremewhite','Creme White').replace('Dragon RedII','Dragon Red II')
    s=re.sub(r'\s*WB\d+$','',s); s=re.sub(r'[（(][^）)]*[）)]','',s).strip()
    s=re.sub(r'\s*[ァ-ヶー・]+$','',s).strip()
    m=re.match(r'^(.+?)\s+\1$',s)
    if m: s=m.group(1)
    if re.fullmatch(r'[A-Z /]+',s) and len(s)>3: s=s.title()
    if re.search(r'[ァ-ヶ]',s): return ''
    return s

PREF={"北海道":"Hokkaido","青森県":"Aomori","岩手県":"Iwate","宮城県":"Miyagi","秋田県":"Akita","山形県":"Yamagata","福島県":"Fukushima","茨城県":"Ibaraki","栃木県":"Tochigi","群馬県":"Gunma","埼玉県":"Saitama","千葉県":"Chiba","東京都":"Tokyo","神奈川県":"Kanagawa","新潟県":"Niigata","富山県":"Toyama","石川県":"Ishikawa","福井県":"Fukui","山梨県":"Yamanashi","長野県":"Nagano","岐阜県":"Gifu","静岡県":"Shizuoka","愛知県":"Aichi","三重県":"Mie","滋賀県":"Shiga","京都府":"Kyoto","大阪府":"Osaka","兵庫県":"Hyogo","奈良県":"Nara","和歌山県":"Wakayama","鳥取県":"Tottori","島根県":"Shimane","岡山県":"Okayama","広島県":"Hiroshima","山口県":"Yamaguchi","徳島県":"Tokushima","香川県":"Kagawa","愛媛県":"Ehime","高知県":"Kochi","福岡県":"Fukuoka","佐賀県":"Saga","長崎県":"Nagasaki","熊本県":"Kumamoto","大分県":"Oita","宮崎県":"Miyazaki","鹿児島県":"Kagoshima","沖縄県":"Okinawa"}
PREF_ZH={"Hokkaido":"北海道","Tokyo":"东京","Osaka":"大阪","Kyoto":"京都"}
def pref(p):
    p=(p or '').replace('・','').strip()
    for k,v in PREF.items():
        if k in p: return v
    return p

def z(s):
    return re.sub(r'\s+',' ',(s or '').replace('　',' ').translate({c:c-0xFEE0 for c in range(0xFF01,0xFF5F)})).strip()

SHOPW=[("ポルシェセンター","Porsche Centre "),("認定中古車センター"," Approved Centre"),("フェラーリ正規ディーラー","Ferrari dealer "),("マセラティ","Maserati "),("ベントレー","Bentley "),
("マクラーレン","McLaren "),("ランボルギーニ","Lamborghini "),("ロールス・ロイス・モーター・カーズ","Rolls-Royce Motor Cars "),("コーンズ","Cornes "),
("大阪中古車ショールーム","Osaka Pre-owned Showroom"),("ショールーム"," Showroom"),("芝","Shiba"),("麻布","Azabu"),("東京","Tokyo"),("大阪","Osaka"),("横浜","Yokohama"),("名古屋","Nagoya"),
("福岡","Fukuoka"),("札幌","Sapporo"),("広島","Hiroshima"),("神戸","Kobe"),("京都","Kyoto"),("仙台","Sendai"),("心斎橋","Shinsaibashi"),("浜田山","Hamadayama"),("世田谷","Setagaya"),
("目黒","Meguro"),("青山","Aoyama"),("港北","Kohoku"),("千葉","Chiba"),("埼玉","Saitama"),("浦和","Urawa"),("大宮","Omiya"),("静岡","Shizuoka"),("浜松","Hamamatsu"),("沼津","Numazu"),
("岡山","Okayama"),("高松","Takamatsu"),("松山","Matsuyama"),("熊本","Kumamoto"),("鹿児島","Kagoshima"),("新潟","Niigata"),("金沢","Kanazawa"),("長野","Nagano"),("宇都宮","Utsunomiya"),
("高崎","Takasaki"),("つくば","Tsukuba"),("水戸","Mito"),("幕張","Makuhari"),("湘南","Shonan"),("川崎","Kawasaki"),("相模原","Sagamihara"),("厚木","Atsugi"),("立川","Tachikawa"),
("練馬","Nerima"),("足立","Adachi"),("江戸川","Edogawa"),("品川","Shinagawa"),("渋谷","Shibuya"),("新宿","Shinjuku"),("杉並","Suginami"),("八王子","Hachioji"),("町田","Machida"),
("岐阜","Gifu"),("四日市","Yokkaichi"),("奈良","Nara"),("堺","Sakai"),("北摂","Hokusetsu"),("西宮","Nishinomiya"),("姫路","Himeji"),("宮崎","Miyazaki"),("大分","Oita"),("長崎","Nagasaki"),
("沖縄","Okinawa"),("盛岡","Morioka"),("郡山","Koriyama"),("富山","Toyama"),("福井","Fukui"),("山梨","Yamanashi"),("甲府","Kofu"),("豊橋","Toyohashi"),("岡崎","Okazaki"),("一宮","Ichinomiya"),
("ガリバー","Gulliver "),("店"," "),("本社",""),("株式会社",""),("(株)",""),("有限会社",""),("合同会社",""),
]
def shop(s):
    s=z(s)
    for a,b in SHOPW: s=s.replace(a,b)
    s=re.sub(r'/.*$','',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s

# ---------- models ----------
def model_po(m,h):
    h=h.replace('ポルシェ','').strip()
    cab='カブリオレ' in m or 'カブリオレ' in h[:20]
    tg=re.search(r'タルガ\s*4\s*GTS|タルガ4GTS',h) and 'Targa 4 GTS' or (re.search(r'タルガ\s*4\s*S|タルガ4S',h) and 'Targa 4S') or (('タルガ' in h[:20]) and 'Targa 4')
    if 'ダカール' in m or 'ダカール' in h[:15]: v='Dakar'
    elif tg: v=tg
    elif re.search(r'GT3\s*RS|GT3RS',h): v='GT3 RS'
    elif 'GT3' in h[:15]: v='GT3 Touring' if 'ツーリング' in h[:25] else 'GT3'
    elif re.search(r'S/T',h[:15]): v='S/T'
    elif re.search(r'ターボ\s*S|ターボS',h[:18]): v='Turbo S'
    elif 'ターボ' in h[:15]: v='Turbo 50 Years' if '50' in h[:25] else 'Turbo'
    elif 'スポーツクラシック' in h[:20]: v='Sport Classic'
    elif 'エディション' in h[:15] and '50' in h[:30]: v='50 Years Porsche Design Edition'
    elif re.search(r'カレラ\s*4\s*GTS|カレラ4GTS',h): v='Carrera 4 GTS'
    elif re.search(r'カレラ\s*GTS|カレラGTS',h): v='Carrera GTS'
    elif re.search(r'カレラ\s*4\s*S|カレラ4S',h): v='Carrera 4S'
    elif re.search(r'カレラ\s*S\b|カレラS',h): v='Carrera S'
    elif re.search(r'カレラ\s*4|カレラ4',h): v='Carrera 4'
    elif re.search(r'カレラ\s*T\b|カレラT',h): v='Carrera T'
    else: v='Carrera'
    name='911 '+v+(' Cabriolet' if cab and not v.startswith('Targa') else '')
    fam='911 Cabriolet' if cab and not v.startswith('Targa') else ('911 Targa' if v.startswith('Targa') else '911')
    return name,fam

def pick(h,opts,default=''):
    for k,v in opts:
        if re.search(k,h): return v
    return default
def model_ms(m,h):
    base={'グレカーレ':'Grecale','レヴァンテ':'Levante','ギブリ':'Ghibli','MC20チェロ':'MC20 Cielo','MC20':'MC20','グラントゥーリズモ':'GranTurismo','グランカブリオ':'GranCabrio','クアトロポルテ':'Quattroporte'}.get(m,m)
    hh=h[:40]
    v=pick(hh,[(r'フォルゴーレ|Folgore','Folgore'),(r'トロフェオ|Trofeo','Trofeo'),(r'モデナ\s*S','Modena S'),(r'モデナ|Modena','Modena'),(r'75th|75周年','75th Anniversary'),(r'F\s*トリブート','F Tributo'),(r'GT\s*ハイブリッド','GT Hybrid'),(r'GT','GT')])
    if base in('MC20','MC20 Cielo'): v=''
    return (base+' '+v).strip(), base
def model_be(m,h):
    base={'ベンテイガ':'Bentayga','フライングスパー':'Flying Spur','コンチネンタルGT':'Continental GT','コンチネンタルGTコンバーチブル':'Continental GTC'}.get(m,m)
    hh=h[:45]
    ewb=bool(re.search(r'エクステンデッド|EWB',hh))
    v=pick(hh,[(r'スピード|Speed','Speed'),(r'マリナー|Mulliner','Mulliner'),(r'ハイブリッド\s*アズール','Hybrid Azure'),(r'ハイブリッド\s*S','Hybrid S'),(r'ハイブリッド','Hybrid'),(r'アズール|Azur','Azure'),(r'V8\s*S|V8S','V8 S'),(r'\bS\b 4WD','S'),(r'W12|6\.0','W12'),(r'V8','V8')])
    name=base+(' EWB' if ewb else '')+(' '+v if v else '')
    return name, base
def model_ml(m,h):
    base={'アルトゥーラ':'Artura','アルトゥーラスパイダー':'Artura Spider','GT':'GT','GTS':'GTS','750S':'750S','750Sスパイダー':'750S Spider','720S':'720S','720Sスパイダー':'720S Spider'}.get(m,m)
    return base, base.replace(' Spider','')
FE_M={"ローマスパイダー":"Roma Spider","ローマ":"Roma","296GTS":"296 GTS","296GTB":"296 GTB","プロサングエ":"Purosangue","ポルトフィーノM":"Portofino M","12チリンドリ":"12Cilindri","F8トリブート":"F8 Tributo"}
RR_M={"ブラックバッジゴースト":"Black Badge Ghost","スペクター":"Spectre","ブラックバッジスペクター":"Black Badge Spectre","ブラックバッジカリナン":"Black Badge Cullinan","カリナン":"Cullinan","ゴースト":"Ghost"}
def model_cs(x):
    b=x['b']; m=x.get('model') or ''; h=re.sub(r'^\S+\s*','',x.get('h1',''))
    if not m and b=='FE' and 'ローマ' in h: m='ローマ'
    if b=='PO': return model_po(m,h)
    if b=='MS': return model_ms(m,h)
    if b=='BE': return model_be(m,h)
    if b=='ML': return model_ml(m,h)
    if b=='FE':
        n=FE_M.get(m,m)
        if m=='12チリンドリ' and re.search(r'スパイダー|Spider',h[:30]): n='12Cilindri Spider'
        if m.startswith('296') and re.search(r'アセット|Assetto',h[:40]): n+=' Assetto Fiorano'
        return n, n.replace(' Assetto Fiorano','').replace(' Spider','') if n.startswith('12') else ('Roma Spider' if n=='Roma Spider' else n.replace(' Assetto Fiorano',''))
    if b=='LG':
        if m=='ウルス':
            v=pick(h[:30],[(r'ペルフォルマンテ|Performante','Performante'),(r'\bSE\b|ＳＥ|ウルスSE','SE'),(r'ウルス\s*S|Urus S|^S\b','S')],'')
            return ('Urus '+v).strip(),'Urus'
        if 'ステラート' in m or re.search(r'ステラート|Sterrato',h[:40],re.I): return 'Huracán Sterrato','Huracán'
        if m.startswith('ウラカン'):
            v=pick(h[:40],[(r'STO','STO'),(r'テクニカ|Tecnica','Tecnica'),(r'EVO.*(スパイダー|Spyder)|(スパイダー|Spyder).*EVO','EVO Spyder'),(r'EVO','EVO'),(r'スパイダー|Spyder','Spyder')],'')
            return ('Huracán '+v).strip(),'Huracán'
        if 'レヴエルト' in m: return 'Revuelto','Revuelto'
        if 'テメラリオ' in m: return 'Temerario','Temerario'
        return m,m
    if b=='RR':
        n=RR_M.get(m,m)
        if re.search(r'シリーズ\s*(II|2|Ⅱ)|Series\s*(II|2|Ⅱ)',h,re.I) and ('Cullinan' in n or 'Ghost' in n): n+=' Series II'
        fam=n.replace('Black Badge ','').replace(' Series II','')
        return n,fam
    return m,m

def tm_cs(s):
    s=s or ''
    m=re.search(r'(\d)\s*速?\s*(?:MT|マニュアル)(?!モード)',s)
    if m and 'MTモード' not in s: return m.group(1)+'MT'
    m=re.search(r'(\d)\s*(?:速)?AT',s)
    if m: return m.group(1)+'AT'
    if re.search(r'^\d?MT$|フロア\d?MT$|^\d速MT',s): return 'MT'
    return 'AT'
