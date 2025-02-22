import pandas as pd
import matplotlib.pyplot as plt

"""
creates the visualisation between Cocomelon and Bluey and showcases how still Bluey's scenes are while Cocomelon is not
"""
def RGB(x):
    file = f"values{x}.csv"

    data = pd.read_csv(file, sep=";")


    #data = pd.DataFrame(table)

    data.plot(kind="scatter",x="frame_number", y="all_frames", ylim=(0,160))
    plt.title("RBG Differences Between Consecutive Frames")
    plt.ylabel("RGB Difference")
    plt.xlabel("Frames")
    data.plot(kind="scatter",x="frame_number", y="half_half_second", ylim=(0,160))
    plt.title("RBG Differences Between Frames Separated by a Quarter Second")
    plt.ylabel("RGB Difference")
    plt.xlabel("Frames")
    data.plot(kind="scatter",x="frame_number", y="half_second", ylim=(0,160))
    plt.title("RBG Differences Between Frames Separated by a Half Second")
    plt.ylabel("RGB Difference")
    plt.xlabel("Frames")
    data.plot(kind="scatter",x="frame_number", y="per_second", ylim=(0,160))
    plt.title("RBG Differences Between Frames Separated by a Second")
    plt.ylabel("RGB Difference")
    plt.xlabel("Frames")
    data.plot(kind="scatter",x="frame_number", y="two_seconds", ylim=(0,160))
    plt.title("RBG Differences Between Frames Separated by two Second")
    plt.ylabel("RGB Difference")
    plt.xlabel("Frames")

    #data = pd.read_csv(f"scene_change_{x}.csv", sep=";")

    #data.plot(kind = "bar", x="type", y="count")
    plt.show()

def HLS(x):
    file = fr"C:\Users\HP\PycharmProjects\BigData2\Video\HLS_values_{x}.csv"

    data = pd.read_csv(file, sep=";")
    data.plot(kind="scatter", x="frame_number", y="Hue", ylim=(0,360))
    data.plot(kind="scatter", x="frame_number", y="Lightness", ylim=(0,100))
    data.plot(kind="scatter", x="frame_number", y="Saturation", ylim=(0,100))
    plt.show()

def HLS_diff(x):
    file = fr"C:\Users\HP\PycharmProjects\BigData2\Video\HLS_values_{x}.csv"
    data = pd.read_csv(file, sep=";")
    data.plot(kind="scatter", x="frame_number", y="Hue_difference", ylim=(0, 360))
    data.plot(kind="scatter", x="frame_number", y="Lightness_difference", ylim=(0, 100))
    data.plot(kind="scatter", x="frame_number", y="Saturation_difference", ylim=(0, 100))
    plt.show()

RGB("Coco1")
RGB("Bluey1")
