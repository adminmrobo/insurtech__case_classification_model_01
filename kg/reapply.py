#!/usr/bin/env python3
"""kg/pages/에 남긴 꼬리표(kg·meta·refs JSON)를 페이지에 다시 덧붙인다 (autokg.py가 이 저장소의 kg/reapply.py로 복사).

  python3 kg/reapply.py [저장소폴더]

빌드 스크립트가 페이지를 다시 만들면 덧붙인 지식 색인이 사라지므로 빌드 끝에 이것을 부른다.
retrofit.py는 <!-- lab-kg --> 표시 사이만 바꾸므로 몇 번을 돌려도 결과가 같다.
"""
import glob, os, subprocess, sys

repo = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
kd = os.path.join(repo, 'kg')
n = 0
for kgf in sorted(glob.glob(os.path.join(kd, 'pages', '*.kg.json'))):
    base = kgf[:-len('.kg.json')]
    rel = os.path.basename(base).replace('__', '/')
    page = os.path.join(repo, rel)
    if not os.path.exists(page):
        print('페이지 없음, 건너뜀:', rel)
        continue
    js = os.path.relpath(os.path.join(kd, 'kgx.js'), os.path.dirname(page)).replace(os.sep, '/')
    r = subprocess.run([sys.executable, os.path.join(kd, 'retrofit.py'), page, '--kg', kgf, '--refs', base + '.refs.json',
                        '--meta', base + '.meta.json', '--js', js, '-o', page], capture_output=True, text=True)
    if r.returncode:
        print('실패:', rel, r.stderr[-300:])
        continue
    bak = page + '.bak'
    if os.path.exists(bak):
        os.remove(bak)
    n += 1
print('다시 덧붙임: 페이지 %d개' % n)
