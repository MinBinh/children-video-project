import pandas as pd
import os

def merge(folder_path,x):
    combined_data = pd.DataFrame()
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".csv"):
            print(filename)
            file_path = os.path.join(folder_path, filename)
            data = pd.read_csv(file_path)
            combined_data = pd.concat([combined_data, data], ignore_index=True)

    combined_data.to_csv(f"{x}Combine.csv", index=False)

merge("RGB","RGB")
#merge("HLS","HLS")