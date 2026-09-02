import json, csv, re

rows=[json.loads(l) for l in open('research/findings.jsonl',encoding='utf-8')]
high=[r for r in rows if r.get('確度')=='高']

base={}
for r in csv.reader(open('data/harowaka_coder_jobs_base.csv',encoding='utf-8')):
    if r and r[0] != '会社名':
        base[r[0]] = r[1] if len(r)>1 else ''

def norm(s):
    return re.sub(r'[（(].*?[)）]|[・\s（）()]', '', s)
basenorm = {norm(k):v for k,v in base.items()}

def find_url(name):
    n = norm(name)
    if n in basenorm: return basenorm[n]
    for k,v in basenorm.items():
        if n in k or k in n: return v
    return ''

def clean_quotes_only_from_shinen(text):
    """Only 理念・想い is treated as genuine sourced company wording."""
    if not text: return []
    return [q.strip() for q in re.findall(r'[「『]([^」』]+)[」』]', text) if 6 <= len(q.strip()) <= 45]

# Fact-based hooks (my own honest description, NOT presented as a quote) for the 18 companies
# with no clean short quote in 理念・想い.
MANUAL_HOOKS = {
    'アサプリ': '印刷・動画・Webを社内に持ち、従業員50〜100名という規模で地方の総合クリエイティブ企業として案件を安定して回されている',
    'アット・ウエルネス': 'ダイレクト・レスポンス・マーケティングの考え方に基づき、反応率を軸にしたコンテンツ設計に取り組まれている',
    'アルファ―企画': '1982年の創業以来、群馬で38年にわたり広告デザインの仕事を続けてこられた',
    'アンクベル・ジャパン': '内閣府や外務省、文部科学省、横浜国立大学など、官公庁・国立大学の実績を数多くお持ちである',
    'クロスシード': '社員ではなくフリーランスのプロデューサー・ディレクター・エンジニアで組織を構成されている',
    '桑原敬事務所（Web Company）': '福岡の小規模事務所でありながら、Yahoo・Google・福岡タワーといった実績を積み重ねてこられた',
    'ゴーメディア': 'SEOを強みに札幌から全国のクライアントを支援し、副業での関わり方も歓迎されている',
    'サンヨー': '1955年の設立以来、化粧品・美容医療からゲーム・アニメ、学校・教育まで幅広い分野を手がけてこられた',
    'スタニング': 'メーカーや商社、広告代理店など、企業間の橋渡しとなる仕事を数多く手がけられている',
    'ダブルアールジー（RRG）': '90年代のインターネット黎明期からのメンバーが中心となり、フリーランスチームから法人化された',
    'チビコ（CHIBICO）': 'CI/VIやデザインガイドラインの策定から手がける、少数精鋭のブランディング会社でいらっしゃる',
    'ディスプレイ（DISPLAY）': 'ご自身を山岳ガイドになぞらえ、不確実な時代をデザインの力で導く役割を掲げていらっしゃる',
    'トップ': 'ウェブ解析士マスターの資格を持つ代表のもと、制作だけでなく解析・改善提案まで一貫して取り組まれている',
    'バルクライン': '空間デザインとWebデザインを両輪に持ち、東京・名古屋・福岡の3拠点で事業を展開されている',
    'ブレーンセンター': '1975年に出版社として創業され、IRやサステナビリティ広報という専門領域を早くから切り拓かれてきた',
    'レイ・クリエーション': '情報デザインという考え方を軸に、企業プレゼンテーションからホームページ制作まで手がけられている',
    'LEFANA（レファーナ）': '元・東京ガールズコレクションのブランドデザイナーによって創業され、5,000件以上の制作実績を積み重ねてこられた',
    'ワンクルー（One-clue）': '仙台の女性クリエイターだけで制作チームを構成され、女性目線でのホームページ制作を手がけられている',
}

OPEN_QUOTE_VARIANTS = [
    "貴社が掲げる「{hook}」という言葉に、強く共感いたしました。",
    "「{hook}」——貴社のこの一文を拝見し、心を動かされました。",
    "貴社の「{hook}」というお考えを拝見し、素直に惹かれました。",
    "「{hook}」という貴社の言葉に、深く共感いたしました。",
    "貴社が大切にされている「{hook}」という言葉に、感銘を受けました。",
]

OPEN_FACT_VARIANTS = [
    "貴社が{hook}ことを拝見し、大変興味を持ちました。",
    "貴社が{hook}と知り、ぜひご一緒したいと感じました。",
    "貴社が{hook}点に、強く惹かれました。",
]

CLOSE_VARIANTS = [
    "コーポレートサイトや採用サイト・LP制作を中心に10〜30件ほど携わってきた者で、HTML/CSSでのデザイン再現とWordPress実装を得意としています。貴社のお力になれればと思い、ご連絡いたしました。",
    "コーポレートサイト・採用サイト・LP制作の実装（HTML/CSS・WordPress・JavaScript）を10〜30件ほど経験してきました。貴社のものづくりに少しでもお役に立てればと思い、ご連絡差し上げました。",
    "WordPress実装やHTML/CSSでのデザイン再現を中心に、コーポレートサイト・採用サイト・LPを10〜30件ほど制作してきました。貴社のご制作をご一緒できればと思い、ご連絡いたしました。",
]

out_rows = [['会社名','URL','1行目','2行目','種別','根拠原文（要確認）','出典','確度']]
for i, r in enumerate(high):
    name = r['会社名']
    url = find_url(name)
    quotes = clean_quotes_only_from_shinen(r.get('理念・想い') or '')
    if quotes:
        quote = quotes[0]
        line1 = OPEN_QUOTE_VARIANTS[i % len(OPEN_QUOTE_VARIANTS)].format(hook=quote)
        kind = '直接引用（理念・想いページより）'
        rationale = quote
    else:
        hook = MANUAL_HOOKS.get(name)
        assert hook, f"missing manual hook for {name}"
        line1 = OPEN_FACT_VARIANTS[i % len(OPEN_FACT_VARIANTS)].format(hook=hook)
        kind = '事実ベース（要約・引用ではない）'
        rationale = hook
    line2 = CLOSE_VARIANTS[i % len(CLOSE_VARIANTS)]
    out_rows.append([name, url, line1, line2, kind, rationale, r.get('出典',''), r.get('確度','')])

with open('outreach/messages_91.csv','w',encoding='utf-8',newline='') as f:
    csv.writer(f).writerows(out_rows)

print('generated', len(out_rows)-1)
