import requests
import json
import datetime
import os
import copy

class Ignore:
    def __init__(self, json):
        self.members = list(map(lambda x: x["nsaid"], json))

class Stats:
    def __init__(self, json, shiftType, stageId, startTime, weaponList):
        self.stage_id = stageId
        self.salmon_id = json["id"]
        self.shift_type = shiftType
        self.golden_eggs = json["golden_eggs"]
        self.power_eggs = json["power_eggs"]
        self.members = json["members"]
        self.start_time = startTime
        self.weapon_list = weaponList
        self.event_type = json["event_type"]
        self.water_level = json["water_level"]


class Record:
    def __init__(self, json):
        try:
            self.id = json["id"]
            self.members = sorted(json["members"])
            self.golden_eggs = json["golden_eggs"]
            self.power_eggs = json["power_eggs"]
            try:
                self.water_level = self.getWaterLevel(json["water_id"])
                self.event_type = self.getEventType(json["event_id"])
            except TypeError:
                self.water_level = None
                self.event_type = None
        except KeyError:
            self.water_level = None
            self.event_type = None
        except TypeError:
            return

    def getEventType(self, eventType):
        if eventType == 0:
            return "-"
        if eventType == 1:
            return "cohock-charge"
        if eventType == 2:
            return "fog"
        if eventType == 3:
            return "goldie-seeking"
        if eventType == 4:
            return "griller"
        if eventType == 5:
            return "the-mothership"
        if eventType == 6:
            return "rush"

    def getWaterLevel(self, waterLevel):
        if waterLevel == 1:
            return "low"
        if waterLevel == 2:
            return "normal"
        if waterLevel == 3:
            return "high"


if __name__ == "__main__":
    with open("src/assets/json/schedule.json", mode="r") as f:
        print(f"Getting latest records from Salmon Stats")
        currentTime = datetime.datetime.now().timestamp()
        schedules = list(filter(lambda x: x["start_time"] >= 1568246400 and x["start_time"] < currentTime, json.load(f)))
        # schedules = list(filter(lambda x: x["start_time"] >= 1577188800 and x["start_time"] <= 1577188800, json.load(f)))
        # schedules = list(filter(lambda x: x["start_time"] > currentTime - 3600 * 24 * 0 and x["start_time"] < currentTime, json.load(f)))
        print(f"Getting {len(schedules)} records")
        scheduleRecords = []

        for schedule in schedules:
            # 元データからコピー
            stageId = schedule["stage_id"]
            startTime = schedule["start_time"]
            endTime = schedule["end_time"]
            rareWeapon = None
            if -1 in schedule["weapon_list"]:
                rareWeapon = schedule["rare_weapon"]
            scheduleId = datetime.datetime.fromtimestamp(startTime, datetime.timezone.utc).strftime("%Y%m%d%H")
            weaponList = schedule["weapon_list"]
            shiftType = "normal"
            if weaponList.count(-1) == 1:
                # 単緑編成
                shiftType = "random1"
            if weaponList.count(-1) == 4:
                # 単緑編成
                shiftType = "random4"
            if weaponList.count(-2) == 4:
                # 単緑編成
                shiftType = "grizzco"

            url = f"https://salmon-stats-api.yuki.games/api/schedules/{scheduleId}"
            print(f"Getting {scheduleId} records")
            records = requests.get(url).json()["records"]

            # データがあれば抽出
            if records is not None:
                # 無視するプレイヤーのリスト
                ignoreList = Ignore(json.load(open("src/assets/json/ignore.json", mode="r")))

                # 夜のみ記錄
                records["totals"]["golden_eggs"] = None if len(set(records["totals"]["golden_eggs"]["members"]) & set(ignoreList.members)) != 0 else records["totals"]["golden_eggs"]
                records["totals"]["power_eggs"] = None if len(set(records["totals"]["power_eggs"]["members"]) & set(ignoreList.members)) != 0 else records["totals"]["power_eggs"]
                
                totals = [
                    None if records["totals"]["golden_eggs"] == None else Record(records["totals"]["golden_eggs"]).__dict__,
                    None if records["totals"]["power_eggs"] == None else Record(records["totals"]["power_eggs"]).__dict__
                ]
                # 昼のみ記錄
                records["no_night_totals"]["golden_eggs"] = None if len(set(records["no_night_totals"]["golden_eggs"]["members"]) & set(ignoreList.members)) != 0 else records["no_night_totals"]["golden_eggs"]
                records["no_night_totals"]["power_eggs"] = None if len(set(records["no_night_totals"]["power_eggs"]["members"]) & set(ignoreList.members)) != 0 else records["no_night_totals"]["power_eggs"]

                no_night_totals = [
                    None if records["no_night_totals"]["golden_eggs"] == None else Record(records["no_night_totals"]["golden_eggs"]).__dict__,
                    None if records["no_night_totals"]["golden_eggs"] == None else Record(records["no_night_totals"]["power_eggs"]).__dict__
                ]

                # フィルタリング
                records["wave_records"]["golden_eggs"] = list(filter(lambda x: len(list(set(x["members"]) & set(ignoreList.members))) == 0, records["wave_records"]["golden_eggs"]))
                records["wave_records"]["power_eggs"] = list(filter(lambda x: len(list(set(x["members"]) & set(ignoreList.members))) == 0, records["wave_records"]["power_eggs"]))

                waves = [
                    list(map(lambda x: Record(x).__dict__, records["wave_records"]["golden_eggs"])),
                    list(map(lambda x: Record(x).__dict__, records["wave_records"]["power_eggs"]))
                ]

                dict = {
                    "stage_id": stageId,
                    "start_time": startTime,
                    "shift_type": shiftType,
                    "end_time": endTime,
                    "weapon_list": weaponList,
                    "rare_weapon": rareWeapon,
                    "records": {
                        "golden_eggs": {
                            "total": totals[0],
                            "no_night_event": no_night_totals[0],
                            "waves": waves[0]
                        },
                        "power_eggs": {
                            "total": totals[1],
                            "no_night_event": no_night_totals[1],
                            "waves": waves[1]
                        },
                    }
                }
                with open(f"src/assets/json/records/{startTime}.json", mode="w") as w:
                    json.dump(dict, w)
                scheduleRecords.append(dict)
        with open(f"src/assets/json/current.json", mode="w") as w:
            json.dump(dict, w)

    # 全記錄を読み込んで編成ごとに最も良いものを計算する
    records = os.listdir("src/assets/json/records")

    waves = [[], []]
    totals = [[], []]
    for record in records:
        with open(f"src/assets/json/records/{record}", mode="r") as f:
            try:
                record = json.load(f)
                stageId = record["stage_id"]
                shiftType = record["shift_type"]
                weaponList = record["weapon_list"]
                startTime = record["start_time"]
                # 金イクラWAVE記錄
                waves[0].extend(list(map(lambda x: Stats(x, shiftType, stageId, startTime, weaponList), record["records"]["golden_eggs"]["waves"])))
                waves[1].extend(list(map(lambda x: Stats(x, shiftType, stageId, startTime, weaponList), record["records"]["power_eggs"]["waves"])))
                # 総合記録
                if record["records"]["golden_eggs"]["total"] is not None:
                    totals[0].append(Stats(record["records"]["golden_eggs"]["total"], shiftType, stageId, startTime, weaponList))
                if record["records"]["power_eggs"]["no_night_event"] is not None:
                    totals[1].append(Stats(record["records"]["golden_eggs"]["no_night_event"], shiftType, stageId, startTime, weaponList))
            except KeyError:
                print(record)
    records = {}
    for stage_id in [5000, 5001, 5002, 5003, 5004]:
        shift_records = {}
        for shift_type in ["normal", "random1", "random4", "grizzco"]:
            golden_eggs = []
            power_eggs = []
            try:
                total = [
                    copy.deepcopy(max(list(filter(lambda x:
                                                  x.shift_type == shift_type and
                                                  x.stage_id == stage_id, totals[0])), key=lambda x: x.golden_eggs)).__dict__,
                    copy.deepcopy(max(list(filter(lambda x:
                                                  x.shift_type == shift_type and
                                                  x.stage_id == stage_id, totals[0])), key=lambda x: x.power_eggs)).__dict__
                ]
                no_night_total = [
                    copy.deepcopy(max(list(filter(lambda x:
                                                  x.shift_type == shift_type and
                                                  x.stage_id == stage_id, totals[1])), key=lambda x: x.golden_eggs)).__dict__,
                    copy.deepcopy(max(list(filter(lambda x:
                                                  x.shift_type == shift_type and
                                                  x.stage_id == stage_id, totals[1])), key=lambda x: x.power_eggs)).__dict__
                ]
            except ValueError:
                pass

            for water_level in ["low", "normal", "high"]:
                for event_type in ["-", "rush", "goldie-seeking", "griller", "the-mothership", "fog", "cohock-charge"]:
                    try:
                        # ディープコピーしないと上書きされてしまう
                        golden_eggs_result = copy.deepcopy(max(list(filter(lambda x:
                                                                           x.shift_type == shift_type and
                                                                           x.stage_id == stage_id and
                                                                           x.water_level == water_level and
                                                                           x.event_type == event_type, waves[0])), key=lambda x: x.golden_eggs).__dict__)
                        power_eggs_result = copy.deepcopy(max(list(filter(lambda x:
                                                                          x.shift_type == shift_type and
                                                                          x.stage_id == stage_id and
                                                                          x.water_level == water_level and
                                                                          x.event_type == event_type, waves[1])), key=lambda x: x.power_eggs).__dict__)
                        # 不要な項目の削除
                        golden_eggs_result.pop("stage_id")
                        golden_eggs_result.pop("shift_type")
                        power_eggs_result.pop("stage_id")
                        power_eggs_result.pop("shift_type")
                        power_eggs.append(power_eggs_result)
                        golden_eggs.append(golden_eggs_result)
                    except ValueError:
                        pass
            # 総合記錄の不要な項目の削除
            total[0].pop("stage_id")
            total[0].pop("shift_type")
            total[0].pop("event_type")
            total[0].pop("water_level")
            total[1].pop("stage_id")
            total[1].pop("shift_type")
            total[1].pop("event_type")
            total[1].pop("water_level")
            # 編成区分ごとの記錄
            shift_records[shift_type] = {
                "golden_eggs": {
                    "total": total[0],
                    "no_night_event": no_night_total[0],
                    "waves": golden_eggs,
                },
                "power_eggs": {
                    "total": total[1],
                    "no_night_event": no_night_total[1],
                    "waves": power_eggs,
                },
            }
        # ステージごとの記錄
        records[stage_id] = shift_records
    with open("src/assets/json/records.json", mode="w") as f:
        json.dump(records, f)
