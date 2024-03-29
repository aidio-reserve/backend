import json
from pathlib import Path


def json_make(path: Path, obj: dict) -> None:
    ls = None
    with open(path, "r+") as f:
        ls = f.readlines()
        if ls == []:
            ls.append("[\n")
        if ls[-1] == "]":
            ls[-1] = ","
        ls.insert(len(ls), f"{json.dumps(obj.__dict__, indent=4 ,ensure_ascii=False)}")
        ls.insert(len(ls), "\n]")

    print(ls)
    with open(path, "w") as f:
        f.writelines(ls)
