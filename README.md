# Children Video Project

This is code used to download, collect, and analyse videos from Cocomelon and other children content creators / shows (BabyChaCha, Bebefinn, Bluey, Pinkgfong, and SuperSimple Songs) for a research paper I worked on and waiting in submission. 

This research focuses on researching video components that are claimed by media and experts to cause Cocomelon videos to become "hyperstimulating" and fast-paced because most reporting did not rely on concrete evidence which gives room for questions of how mnay scene changes, how long are scenes, how fast-pace is Cocomelon, and how does it compare to other channels.

This code provides the data for analysing if Cocomleon is more fast-pace than other channels (those mentioned above).

The files are a little disorganised but here is an explanation:

### video_frame.py
This is the main file used for collecting my video data which are mainly colour values to detect scene changes. 

We collect Colour values because if there is a big enough change in colour values, it must mean the scene had change

This is calculated using the Colour Euclidian Distance of RGB.

And this finds:
- the number of scene changes per minute, 
- the length of scenes, 
- varience of scene change detection if frames are compared over a time interval. (Look `graph.py` to understand what I mean by varience in time interval)
- Hue, Lightness, and Saturation Values (not used in the paper though)

### graph.py

generates graph that illustrates the idea that if frames are seperated long enough, changes in an object position in a scene or the camera's perspective of a scene would cause false positives in scene change detection. 

capturing these two ideas would show fast-pacedness of a video, if points are a mess too many movements; if a distinction between non-scene changes data points and scene changes data point is still seen, then the scene must be very still.

so generated graphs shows the RGB values collected across time intervals / or none and a bar chart that tallies up all scene changes collected from said intervals.

uses the `valuesBluey1.csv` and `valuesCoco1.csv` files

### now the other files...

the `combine2.py`, `data combine.py`, `fixing.py` are just files use to transform the data to be used in Tableau. When video_frame.py is run it returns hundreds of csv files, so they had to be merged and transformed.

## Data files for Tableau

`RGBCombine.csv`, `video_time.csv`, and `HLSCombine.csv` are data files that can be used to make visualisations on Tableau


## Notes

yes I know it is messy hush :~)