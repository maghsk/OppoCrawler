import json
from pathlib import Path
from typing import Dict

OUTPUT_PATH = Path('/home/maghsk/storage/Projects/WebGL Empirical Study/Crawler/output')

with open(OUTPUT_PATH / 'merged_html_and_js.json', 'r') as fp:
    data: Dict[str, bool] = json.load(fp)

print("{}/{}".format(sum(data.values()), len(data)))
with open(OUTPUT_PATH / 'url_list.txt', 'w') as fp:
    fp.write('\n'.join(k for k,v in data.items() if v))