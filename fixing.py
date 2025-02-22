import pandas as pd

file = "RGBCombine.csv"


data = pd.read_csv(file, sep=";")

def from_max():

    num = data.num_scene_changes
    difference = []
    a = len(num)
    i = 0
    while i < a:
        max = 0
        for j in range(5):
            if num[j] > max: max = num[j]
        for l in range(5):
            difference.append(max - num[l])
        i+=5

    fix = pd.DataFrame({
        "type": data.type,
        "num_scene_changes": data.num_scene_changes,
        "difference":difference,
        "std_count": data.std_count,
        "scene_changes_per_min": data.scene_changes_per_min,
        "time_interval": data.time_interval,
        "videoid": data.videoid,
        "channel": data.channel,
    })

    fix.to_csv(f"RGBCombine.csv",sep=";")

from_max()