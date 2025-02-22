import pandas as pd
import os

def merge(channel, folder_path,x):
    combined_data = pd.DataFrame()
    videoid = 0

    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".csv"):
            print(filename)
            videoid = videoid + 1
            file_path = os.path.join(folder_path, filename)
            data = pd.read_csv(file_path)
            data['videoid'] = videoid
            data['channel'] = channel
            combined_data = pd.concat([combined_data, data], ignore_index=True)

    combined_data.to_csv(f"{x}Combine.csv", index=False)

channels = ["Coco", "PinkFong", "Bebefinn", "BabyChaCha", "Bluey", "SuperSimpleSongs"]
for x in channels:
    merge(x, f"Scene/{x}",x+"RGB")
    #merge(x, f"HSL/{x}",x+"HLS")


print(1)



