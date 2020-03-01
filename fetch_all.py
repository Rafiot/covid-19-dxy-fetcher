#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import json

initial_url = "https://ncov.dxy.cn/ncovh5/view/pneumonia"

current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
current_file = Path('data') / f'{current_hour}.html'

if not current_file.exists():
    # get the whole page
    response = requests.get(initial_url)
    response.encoding = response.apparent_encoding
    with current_file.open('w') as f:
        f.write(response.text)

    # Parse the file
    with current_file.open('rb') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    # Get the json blob for the cases/region
    script_blob = soup.find('script', id="getAreaStat").string
    j_china = json.loads(script_blob[script_blob.find('['):script_blob.rfind(']') + 1], encoding='utf-8')
    # Get the cases for the rest of the world
    script_blob = soup.find('script', id="getListByCountryTypeService2").string
    j_world = json.loads(script_blob[script_blob.find('['):script_blob.rfind(']') + 1], encoding='utf-8')

    # Save the blobs accordingly
    json_dir = Path('data') / f'{current_hour}_json'
    json_dir.mkdir(exist_ok=True)
    with (json_dir / 'current_china.json').open('w') as f:
        json.dump(j_china, f, indent=2, ensure_ascii=False)
    with (json_dir / 'current_world.json').open('w') as f:
        json.dump(j_world, f, indent=2, ensure_ascii=False)

    # Get & save the evolution by province
    for province in j_china:
        response = requests.get(province['statisticsData'])
        response.encoding = response.apparent_encoding
        with (json_dir / f'{province["provinceName"]}.json').open('w') as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)
