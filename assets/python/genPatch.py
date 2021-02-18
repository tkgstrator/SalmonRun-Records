import urllib
import requests
import json
import urllib
from functools import reduce

def get_nickname_and_icon(query):
    url = f"https://app.splatoon2.nintendo.net/api/nickname_and_icon?{query}"
    return requests.get(url, cookies=dict(iksm_session="74f69491dad720a4d0cefafdc9804c1edc75fd84")).json()["nickname_and_icons"]

with open("nsaid.json", mode="r") as f:
    try:
        players = json.load(f)
        # URLクエリを作成
        query = reduce(lambda x, y: f"{x}&{y}", list(map(lambda p: urllib.parse.urlencode({"id" : p["nsaid"]}), players)))
    
        res = get_nickname_and_icon(query)
        # Map使って書き直せるけどまあいいや
        for r in res:
            reason = {"banned-reason": list(filter(lambda p: p["nsaid"] == r["nsa_id"], players))[0]["banned-reason"]}
            r.update(reason) # JSON配列を直接書き換えてくれる、神
        with open("../json/lanplay.json", mode="w") as w:
            w.write(json.dumps(res))
    except:
        print("ERROR")