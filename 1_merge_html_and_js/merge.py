import json
import pyzstd
from pathlib import Path
from collections import defaultdict


OUTPUT_PATH = Path('/home/maghsk/storage/Projects/WebGL Empirical Study/Crawler/output')
HTML_PATH = OUTPUT_PATH / 'simplified_html.json'
JS_PATH = OUTPUT_PATH / 'simplified_js.json'

def main():
    html_lst = [ json.loads(x) for x in HTML_PATH.read_text().splitlines() ]
    js_lst = [ json.loads(x) for x in JS_PATH.read_text().splitlines() ]

    html_final = {x['url']: x for x in html_lst}
    js_url_dict = {x['url']: x for x in js_lst}

    # html_gl_dict = {
    #     html['url']: (html['lit_used_webgl'] and html['lit_used_getcontext']) or any(x['lit_used_webgl'] and x['lit_used_getcontext'] for x in (js_url_dict.get(rurl, {'lit_used_webgl': False, 'lit_used_getcontext': False}) for rurl in html['remote_js_url_list']))
    #     for html in html_lst
    # }

    for url, item in html_final.items():
        html_gl = (item['lit_used_webgl'] and item['lit_used_getcontext'])
        gl = html_gl
        remote_js_gl = {}

        for rurl in item['remote_js_url_list']:
            if rurl not in js_url_dict:
                remote_js_gl[rurl] = None
            else:
                remote_js_gl[rurl] = (js_url_dict[rurl]['lit_used_webgl'] and js_url_dict[rurl]['lit_used_getcontext'])
                gl = gl or remote_js_gl[rurl]

        item['html_gl'] = html_gl
        item['gl'] = gl
        item['remote_js_gl'] = remote_js_gl
        
        del item['remote_js_url_list']
        del item['lit_used_getcontext']
        del item['lit_used_webgl']
        del item['url']

    # with open(OUTPUT_PATH / 'merged_html_and_js.json', 'w') as fp:
    #     json.dump(html_gl_dict, fp)

    with pyzstd.open(OUTPUT_PATH / 'html_final.json.zst', 'wt') as fp:
        json.dump(html_final, fp, indent=2)
    
    with pyzstd.open(OUTPUT_PATH / 'html_final_gl.json.zst', 'wt') as fp:
        json.dump({k: v for k, v in html_final.items() if v['gl']}, fp, indent=2)
        

if __name__ == '__main__':
    main()
