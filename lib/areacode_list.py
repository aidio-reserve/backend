import json

json_open = open("local_area_code.json", "r", encoding="utf-8")
json_load = json.load(json_open)


def get_smallClassCodes(prefecture):
    prefecturecodes = json_load["areaClasses"]["largeClasses"][0]["largeClass"][1][
        "middleClasses"
    ]
    smallcasscodes_of_prefecture = []
    if prefecture is None:
        return None
    else:
        for item in prefecturecodes:
            if item["middleClass"][0]["middleClassCode"] == prefecture:
                for smallClass in item["middleClass"][1]["smallClasses"]:
                    f1code = smallClass["smallClass"][0]["smallClassCode"]
                    f2name = smallClass["smallClass"][0]["smallClassName"]
                    smallcasscodes_of_prefecture.append(
                        str(f2name)
                        + "・"
                        + str(f1code)
                        + "のsmallClassCodeは'"
                        + str(f1code)
                        + "'です"
                    )
        return smallcasscodes_of_prefecture
