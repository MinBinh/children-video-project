from pytube import YouTube
import cv2
import numpy as np
import pandas as pd
import os
import math

#creates the 100 x 100 grid for average RGB values collecting of each box in the grid.
def divide_image(image, num_rows, num_cols, type):
    # Read the image
    # Get the dimensions of the image
    height, width, _ = image.shape

    # Convert the image to HSV color space
    if type == "hsv":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    elif type == "hls":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

    # Calculate the size of each square
    square_height = height // num_rows
    square_width = width // num_cols

    averages = ""

    # Iterate through each square

    for i in range(num_rows):
        row_averages = ""
        for j in range(num_cols):
            # Define the coordinates of the current square
            start_row = i * square_height
            end_row = (i + 1) * square_height
            start_col = j * square_width
            end_col = (j + 1) * square_width

            square = (image)[start_row:end_row, start_col:end_col]
            average_square = str(np.mean(square, axis=(0, 1)).astype(int))
            if j != 0:
                row_averages += ","
            row_averages += average_square
        # Append the row averages to the main list
        if i != 0:
            averages += ","
        averages += row_averages

    return averages

# downloads YouTube videos based on provided link (PyTube library)
def extract_frames_from_youtube(url):
    # Download the YouTube video
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    filename = "youtube_video_" + str(url.__hash__()) + ".mp4"
    video.download(filename=filename)
    video_path = os.path.join(filename)

    # Extract frames from the downloaded video
    return extract_frames(video_path)

"""
This function collects RGB values by creating a 100 x 100 grid on a frame
an average RGB value from a box within this 100 x 100 grid is taken and then mapped into a 2D array 
The same thing is then done to the next consecutive frame, and then the next and next.
These values are then stored in a csv file "scrapped{x}.csv" with x detailing the creator of the video 
and the video id 1-20 (for we collect the top 20 videos from each creator).
"""
def extract_frames(video_path):
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    frame_number = []
    seconds = []
    rgb_values = []
    hls_values = []

    # Get video properties
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Video Properties: FPS={fps}, Frame Count={frame_count}, Width={width}, Height={height}")

    # Read and save frames at the specified interval
    success, frame = video_capture.read()
    count = 0

    # i want all frames
    while success:
        extracted_rgb = divide_image(frame, 100, 100, "brg")
        extracted_hls = divide_image(frame, 100, 100, "hls")
        frame_number.append(count)
        seconds.append(count / fps)
        rgb_values.append(extracted_rgb)
        hls_values.append(extracted_hls)
        print(f"frame: {count}/{frame_count}, second: {count / fps}")
        print("-----------")
        success, frame = video_capture.read()
        count += 1
    print("done")

    rgb_table = pd.DataFrame({
        "frame_number": frame_number,
        "seconds": seconds,
        "val": rgb_values,
        "fps": fps
    }).set_index('frame_number')

    hls_table = pd.DataFrame({
        "frame_number": frame_number,
        "seconds": seconds,
        "val": rgb_values,
        "fps": fps
    }).set_index('frame_number')

    # Release the video capture object and close the window if opened
    video_capture.release()
    cv2.destroyAllWindows()

    return rgb_table, hls_table

"""
Comparing 2 frames by finding the colour difference of the euclidian RGB difference
When the differences of each index RGB from the 100x100 grid of both frames are found,
it is all stored in a thrid 100x100 grid
all values within this array use to find the total average of RGB differences between 2 frames
"""
def compareValues(first, second):
    sum = 0
    first = first.split(","); second = second.split(",")
    for x in range(len(first)):
        v1 = str(first[x])[1:-1].strip().split(" "); v2 = str(second[x])[1:-1].strip().split(" ")
        while ("" in v1):v1.remove("")
        while ("" in v2):v2.remove("")
        val1 = (int(v2[0]) - int(v1[0])) ** 2
        val2 = (int(v2[1]) - int(v1[1])) ** 2
        val3 = (int(v2[2]) - int(v1[2])) ** 2
        value = math.sqrt(val1+val2+val3)
        sum += value
    average = sum/(len(first))
    return average

"""
This function compares the RGB value differences to detect Scene Changes
Scene Changes are detected when the total average difference in RGB is bigger than 70
 - This value we got from testing and results in the least amount of false positives when frames are compared consecetively
 while providing room for adjustment for the various kinds of videos downloaded and compared
variable i for loop is used to collect RGB based on seperating frames by different time intervals
 - i = 0: there is no time interval
 - i = 1: quarter of a second time interval
 - i = 2: half a second interval
 - i = 3: a second interval
 - i = 4: two second interval
 - This is to see how still frames are is throughout a scene

Returns scene changes of all types,
Standard Deviation is of the different scene changes detected based on time intervals
"""
def RGB(x, intro = 0, outro = 0):
    file = fr"scraped{x}.csv"

    data = pd.read_csv(file, sep=";")
    brg_frames = data.val
    fps = data.fps[0]

    frame_number = len(brg_frames)
    all_values = []
    total_change = []
    change = [0] * frame_number
    scene_interval = []
    n = 1
    for i in range(5):
        counter = 0
        frame_values = [None] * frame_number
        scene_change_values = [None] * frame_number
        recorded_change = []

        previous_time = 0
        if i == 1:
            print("4 fps")
            n = int(fps/4)
        elif i == 2:
            print("2 fps")
            n = int(fps/2)
        elif i == 3:
            print("1 fps")
            n = fps
        elif i == 4:
            print("0.5 fps")
            n = 2*fps
        current_frame = (intro * fps + int(n))
        while current_frame < (frame_number - outro*fps):
            print(i)
            difference = compareValues(brg_frames[current_frame-n],brg_frames[current_frame])
            frame_values[current_frame] = difference
            if difference > 70  :
                print("scene change")
                counter+=1
                if i == 0:
                    change[current_frame] = 1
                    scene_interval.append((current_frame / fps) - previous_time)
                    previous_time = current_frame / fps
            print(frame_values[current_frame])
            print(f"-------------({current_frame})---{current_frame/fps}")
            current_frame += int(n)
        all_values.append(frame_values)
        scene_change_values.append(recorded_change)
        total_change.append(counter)

    all_values_table = pd.DataFrame({
        "frame_number": [y for y in range(frame_number)],
        "scene_change_boolean": change,
        "all_frames": all_values[0],
        "half_half_second": all_values[1],
        "half_second": all_values[2],
        "per_second": all_values[3],
        "two_seconds": all_values[4],
        }).set_index('frame_number')

    video_length = frame_number / fps / 60
    a = total_change[0] / (video_length)

    print(a)

    scene_change_count = pd.DataFrame({
        "type": ["all_frames","half_half_second","half_second","per_second","two_seconds"],
        "count": total_change,
        "std_count":[pd.Series(total_change).std()] * 5,
        "scene_changes_per_min":[a] * 5,
        "time_interval":[pd.Series(scene_interval).mean()] * 5
    })

    all_values_table.to_csv(f"values{x}.csv",sep=";")
    scene_change_count.to_csv(f"scene_change_{x}.csv",sep=";")
def HLS_compare(frame):
    H = 0; L = 0; S = 0
    frame = frame.split(",")
    a = len(frame)
    for x in range(a):
        v = str(frame[x])[1:-1].strip().split(" ")
        while ("" in v): v.remove("")
        H += int(v[0]); L += int(v[1]); S += int(v[2])
    return H/a*(360/179), (L/a)*(100/255), (S/a)*(100/255)

#Collects values over regions of a frame like function RGB() but now with Hue, Light, and Saturation
#Was not used in the eventual research project
#differences measured
def HLS(a, intro = 0, outro = 0):
    file = fr"scrapedHLS{a}.csv"
    Hue = []; Lightness = []; Saturation = []
    th = 0; tl = 0; ts = 0
    Hdiff = [None]; Ldiff = [None]; Sdiff = [None]
    data = pd.read_csv(file, sep=";")
    frames = data.val
    fps = data.fps[0]
    thd = 0; tld = 0; tsd = 0

    for x in range(intro*fps,len(frames)-outro*fps):
        H, L, S = HLS_compare(frames[x])
        print(H, L, S)
        Hue.append(H); Lightness.append(L); Saturation.append(S)
        if x > 0:
            dh = abs(Hue[x-1] - Hue[x]); dl = abs(Lightness[x-1]-Lightness[x]); ds = abs(Saturation[x-1]-Saturation[x])
            Hdiff.append(dh); Ldiff.append(dl); Sdiff.append(ds)

    table = pd.DataFrame({
        "frame_number":[y for y in range(len(frames))],
        "Hue":Hue,
        "Hue_difference": Hdiff,
        "Lightness":Lightness,
        "Lightness_difference":Ldiff,
        "Saturation":Saturation,
        "Saturation_difference":Sdiff,
    }).set_index('frame_number')

    average_difference = pd.DataFrame({
        "Values": ["Hue", "Lightness", "Saturation"],
        "Average_difference": [pd.Series(Hdiff).mean(), pd.Series(Ldiff).mean(), pd.Series(Sdiff).mean()],
        "Average_value": [pd.Series(Hue).mean(), pd.Series(Lightness).mean(), pd.Series(Saturation).mean()],
        "Std_values": [pd.Series(Hue).std(), pd.Series(Lightness).std(), pd.Series(Saturation).std()]
    })

    table.to_csv(f"HLS_values_{a}.csv",sep=";")
    average_difference.to_csv(f"HLS_diff_{a}.csv",sep=";")


#Gives data and the video length
def time():
    channel = []
    id = []
    length = []

    for x in range(6):
        a = ["Coco", "PinkFong", "Bebefinn", "BabyChaCha", "Bluey", "SuperSimpleSongs"]
        for i in range(1, 21):
            file = fr"scraped{a[x]}{i}.csv"
            data = pd.read_csv(file, sep=";")
            brg_frames = data.val
            fps = data.fps[0]
            channel.append(a[x])
            id.append(i)
            length.append(len(brg_frames) / fps)
            print(i, x)

    table = pd.DataFrame({
        "channel": channel,
        "videoid": id,
        "length": length,
    })

    table.to_csv(f"video_time.csv",sep=";")



"""These are the videos collected and downloaded for the research
Should be in the order of Cocomelon, Pinkfong, Bebefinn, BabyChaCha, Bluey, and the SuperSimpleSongs
Seperated by the | character"""

URLs = """https://www.youtube.com/watch?v=n38kGst16sI
https://www.youtube.com/watch?v=Y2T_rIZ4Pho
https://www.youtube.com/watch?v=TJmTHuuYx3k
https://www.youtube.com/watch?v=WF8iaqRqI60
https://www.youtube.com/watch?v=GDMel6oO2fU
https://www.youtube.com/watch?v=2E0hHjSwdW4
https://www.youtube.com/watch?v=HvNdJ2RCReg
https://www.youtube.com/watch?v=3YltYCrPZos
https://www.youtube.com/watch?v=fsQVfQt0HOk
https://www.youtube.com/watch?v=TOTd78ZTDGE
https://www.youtube.com/watch?v=ygcN65SlLFg
https://www.youtube.com/watch?v=ABEVNHqmbJ4
https://www.youtube.com/watch?v=Oq61TxejZ5g
https://www.youtube.com/watch?v=pUu0FWlMpgk
https://www.youtube.com/watch?v=_Tr9Ncoo-yw|https://www.youtube.com/watch?v=R93ce4FZGbc
https://www.youtube.com/watch?v=Dybkj4VU2H0
https://www.youtube.com/watch?v=gX2gOpgoTgw
https://www.youtube.com/watch?v=JYnvpJL-0HA
https://www.youtube.com/watch?v=sLFdnqMrGCM
https://www.youtube.com/watch?v=nDE3Ff-5zG4
https://www.youtube.com/watch?v=S-kJQbq6oaA
https://www.youtube.com/watch?v=KyBYuEgvFl0
https://www.youtube.com/watch?v=3XWRT0JZd5k
https://www.youtube.com/watch?v=d8pqPa7D8Ps
https://www.youtube.com/watch?v=eVDGYl0p6nU
https://www.youtube.com/watch?v=y3F7tthwdf8
https://www.youtube.com/watch?v=KFKGPOMusZk
https://www.youtube.com/watch?v=lR-vzUw8sWo
https://www.youtube.com/watch?v=d2S87jXhlV0|https://www.youtube.com/watch?v=stMZrWNXTKI
https://www.youtube.com/watch?v=Lh93IVFQU-Q
https://www.youtube.com/watch?v=0PNiZflV2JQ
https://www.youtube.com/watch?v=WKXXoPXQHjk
https://www.youtube.com/watch?v=Vk24cZJQTwE
https://www.youtube.com/watch?v=QXMHKfTtah4
https://www.youtube.com/watch?v=oiKji3JjkgY
https://www.youtube.com/watch?v=RLRsSeEPgJY
https://www.youtube.com/watch?v=dzfgTCMl_M8
https://www.youtube.com/watch?v=9F1UObhYxuI
https://www.youtube.com/watch?v=JOKJhCK8JTE
https://www.youtube.com/watch?v=gfEYJG2CfzI
https://www.youtube.com/watch?v=ozDX0kkf8hM
https://www.youtube.com/watch?v=_A2VpvVdlvI
https://www.youtube.com/watch?v=78rSZ9iEQeo|https://www.youtube.com/watch?v=O9ZTcTS3mbs
https://www.youtube.com/watch?v=8uCRUXDFDvY
https://www.youtube.com/watch?v=Rfdmg2mrD6I
https://www.youtube.com/watch?v=Vv077PwD9is
https://www.youtube.com/watch?v=wYlDPSz56aA
https://www.youtube.com/watch?v=D9soflf2hhc
https://www.youtube.com/watch?v=2FX_Tfn1XzQ
https://www.youtube.com/watch?v=fEin_yWwfpk
https://www.youtube.com/watch?v=Ggw785ZfGZc
https://www.youtube.com/watch?v=-LHZ35TZSAs
https://www.youtube.com/watch?v=AJM23Izv36s
https://www.youtube.com/watch?v=7_k7ewRmtKQ
https://www.youtube.com/watch?v=kgvLk3YonT8
https://www.youtube.com/watch?v=bI7tIqX2W6w
https://www.youtube.com/watch?v=Yru9Zj32j78|https://www.youtube.com/watch?v=DklpM_lZIOU&t=10s
https://www.youtube.com/watch?v=d3XW_lvBRVw
https://www.youtube.com/watch?v=mBNrdanTs3A
https://www.youtube.com/watch?v=JcinTAfwdVw
https://www.youtube.com/watch?v=7rQydySZ-oU
https://www.youtube.com/watch?v=08-Y1_KcSe0
https://www.youtube.com/watch?v=zL_vNn06a5M
https://www.youtube.com/watch?v=TErxJFNisBM
https://www.youtube.com/watch?v=V3r4UWtoN_o
https://www.youtube.com/watch?v=rKTkYi2J6BY
https://www.youtube.com/watch?v=Kf0jwCmNKfU
https://www.youtube.com/watch?v=VX-lYkW4WuQ
https://www.youtube.com/watch?v=1LC6Lbbp71o
https://www.youtube.com/watch?v=RDYe2vL0oVM
https://www.youtube.com/watch?v=bLRfuwN0Hk0|https://www.youtube.com/watch?v=M6LoRZsHMSs
https://www.youtube.com/watch?v=eBVqcTEC3zQ
https://www.youtube.com/watch?v=13mftBvRmvM
https://www.youtube.com/watch?v=-jBfb33_KHU
https://www.youtube.com/watch?v=fXFg5QsTcLQ
https://www.youtube.com/watch?v=tbbKjDjMDok
https://www.youtube.com/watch?v=9mmF8zOlh_g
https://www.youtube.com/watch?v=HGgsklW-mtg
https://www.youtube.com/watch?v=_6HzoUcx3eo
https://www.youtube.com/watch?v=2S__fbCGwOM
https://www.youtube.com/watch?v=zXEq-QO3xTg
https://www.youtube.com/watch?v=r5WLXZspD1M
https://www.youtube.com/watch?v=trDl36m9pgA
https://www.youtube.com/watch?v=fPMjnlTEZwU
https://www.youtube.com/watch?v=zMdq9jSaNLg
https://www.youtube.com/watch?v=hW2DDGX7Tcc"""

urls = URLs.split("|")
x = ["Coco", "PinkFong", "Bebefinn", "BabyChaCha", "Bluey", "SuperSimpleSongs"]
l = 0

time()

"""
for n in range(15):
    print(x[l], n + 1 + 5)
    a = urls[l].split("\n")
    url = a[n]
    print(url)
    extracted_rgb, extracted_hls = extract_frames_from_youtube(url)
    extracted_rgb.to_csv(f'scraped{x[l]}{n + 1 + 5}.csv', sep=";");
    extracted_hls.to_csv(f"scrapedHLS{x[l]}{n + 1 + 5}.csv", sep=";")

for i in range(5,21):
    RGB(f"{x[l]}{i}")
    HLS(f"{x[l]}{i}")
"""