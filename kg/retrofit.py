#!/usr/bin/env python3
"""완성된 HTML에 지식 색인(#kg)·꾸러미(#export) 섹션과 데이터 블록을 덧붙인다.

본문은 건드리지 않는다. 덧붙인 부분은 모두 <!-- lab-kg:… --> 표시 사이에 들어가므로
다시 실행하면 그 부분만 바뀐다(몇 번을 돌려도 결과가 같다).

사용:
  python3 retrofit.py 원본.html --kg kg.json --refs refs.json --meta meta.json \
      [--backbone backbone.json] [--js inline | --js assets/js/kgx.js] [-o 결과.html]

  --js inline (기본)  kgx.js를 HTML 안에 넣는다 (단일 파일 페이지)
  --js <경로>         <script src="경로">로 연결한다 (여러 파일 사이트, 같은 kgx.js를 공유)
  -o 생략             원본.html 자리에 결과를 쓴다 (원본은 원본.html.bak로 남긴다)
"""
import argparse, html, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
M = {k: ('<!-- lab-kg:%s -->' % k, '<!-- /lab-kg:%s -->' % k) for k in ('head', 'body', 'script')}


COVER = ('<!-- lab-cover -->', '<!-- /lab-cover -->')  # 글 표지 블록 (ai-lab-explainer 18-15). 조립 때는 그대로 둔다


def strip_marked(h, cover=False):
    for a, b in list(M.values()) + ([COVER] if cover else []):
        h = re.sub(re.escape(a) + r'.*?' + re.escape(b) + r'\n?', '', h, flags=re.S)
    return h


def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def jsonld(kg, meta, kgx):
    try:
        tmp = tempfile.mkdtemp()
        for n, o in (('kg.json', kg), ('meta.json', meta)):
            with open(os.path.join(tmp, n), 'w', encoding='utf-8') as f:
                json.dump(o, f, ensure_ascii=False)
        code = ("global.document={readyState:'complete',getElementById:function(){return null},head:{appendChild:function(){}},"
                "createElement:function(){return {}}};global.window={addEventListener:function(){}};"
                "eval(require('fs').readFileSync(process.argv[1],'utf8')+';global.K=KGX;');var fs=require('fs'),d=process.argv[2];"
                "process.stdout.write(JSON.stringify(K.toJsonLd(JSON.parse(fs.readFileSync(d+'/kg.json','utf8')),JSON.parse(fs.readFileSync(d+'/meta.json','utf8')))));")
        return json.loads(subprocess.check_output(['node', '-e', code, kgx, tmp], stderr=subprocess.DEVNULL).decode())
    except Exception:
        return None  # node가 없으면 kg-ld는 빼고, 페이지가 열릴 때 꾸러미에서 만든다


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('page'); ap.add_argument('--kg', required=True); ap.add_argument('--refs', required=True)
    ap.add_argument('--meta', required=True); ap.add_argument('--backbone'); ap.add_argument('--js', default='inline')
    ap.add_argument('-o', '--out')
    a = ap.parse_args()
    load = lambda p: json.load(open(p, encoding='utf-8'))
    H0 = open(a.page, encoding='utf-8').read()
    H = strip_marked(H0)
    kg, refs, meta = load(a.kg), load(a.refs), load(a.meta)
    if a.backbone:
        bb = load(a.backbone)
        kg['topicLabels'] = {n['id']: n['label']['ko'] for n in bb['nodes']}
    kgx = os.path.join(HERE, 'kgx.js')
    ld = jsonld(kg, meta, kgx)

    t = meta.get('title', '')
    head = ['<meta name="citation_title" content="%s">' % html.escape(t),
            '<meta name="dc.title" content="%s">' % html.escape(t),
            '<meta name="dc.date" content="%s">' % html.escape(meta.get('date', '')),
            '<meta name="dc.language" content="ko">', '<meta name="dc.type" content="InteractiveResource">']
    for c in meta.get('creator') or []:
        if c.get('name'):
            head.append('<meta name="citation_author" content="%s">' % html.escape(c['name']))
    if meta.get('series'):
        head.append('<meta name="dcterms.isPartOf" content="%s">' % html.escape(meta['series']))
    for r in refs:
        if r.get('DOI'):
            head.append('<meta name="dc.source" content="doi:%s">' % html.escape(r['DOI']))
    blk_head = M['head'][0] + '\n' + '\n'.join(head) + '\n' + M['head'][1] + '\n'

    def sec(i, title, sub, mount):
        return ('<section class="kgx kgx-sec" id="%s"><div class="kgx-wrap">\n<h2>%s</h2>\n<p class="kgx-sub">%s</p>\n'
                '<div id="%s"></div>\n</div></section>\n') % (i, title, sub, mount)
    body = (M['body'][0] + '\n' +
            sec('kg', '지식 색인 — 이 페이지에서 찾아보기',
                '이 페이지에 나온 개념, 방법, 생물 대응, 주장, 열린 질문을 한곳에 모았다. 검색하고, 항목을 눌러 이웃 관계를 보고, "설명 보러 가기"로 본문에 돌아간다.', 'kg-mount') +
            sec('export', '온톨로지·서지 꾸러미 — 이 페이지의 지식을 가져가기',
                '지식 색인을 출처와 함께 파일로 내려받는다. Zotero(BibTeX·RIS), Protégé(Turtle), Neo4j·Gephi(CSV), 여러 페이지 합치기(kg.json)에 쓴다.', 'export-mount') +
            '<script type="application/json" id="kg-raw">%s</script>\n' % js(kg) +
            ('<script type="application/ld+json" id="kg-ld">%s</script>\n' % js(ld) if ld else '') +
            '<script type="application/json" id="refs-csl">%s</script>\n' % js(refs) +
            '<script type="application/json" id="page-meta">%s</script>\n' % js(meta) + M['body'][1] + '\n')
    if a.js == 'inline':
        s = '<script>\n' + open(kgx, encoding='utf-8').read() + '\n</script>'
    else:
        s = '<script src="%s"></script>' % html.escape(a.js)
    blk_script = M['script'][0] + '\n' + s + '\n' + M['script'][1] + '\n'

    if '</head>' not in H or '</body>' not in H:
        sys.exit('오류: </head> 또는 </body>가 없다')
    H = H.replace('</head>', blk_head + '</head>', 1)
    i = H.rfind('<footer')
    j = H.rfind('</body>')
    pos = i if 0 <= i < j else j  # 마지막 바닥글 앞, 없으면 </body> 앞
    H = H[:pos] + body + H[pos:]
    j = H.rfind('</body>')
    H = H[:j] + blk_script + H[j:]

    out = a.out or a.page
    if not a.out:
        shutil.copyfile(a.page, a.page + '.bak')
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(H)
    print('완료:', out, '| 노드', len(kg['nodes']), '관계', len(kg['edges']), '문헌', len(refs),
          '| JSON-LD', '있음' if ld else '없음(node 없음, 페이지에서 생성)', '| 스크립트', a.js)


if __name__ == '__main__':
    main()
