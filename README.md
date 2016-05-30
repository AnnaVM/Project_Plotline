# Overview

This is a **data science project** which analyzes different **movie scripts** and extracts the evolution of the **emotional content** throughout each movie ("emotional plotline").

The aim is then to cluster the movies based on their emotional plotline.

# Requirements and installation

The required Python packages are listed in the file `requirements.txt`. In order to install them, please type:
```
pip install -r requirements.txt
```

In addition, you will need to download the `nltk` corpus (i.e. the data which is needed for the Natural Language Processing package `nltk`). To do so, type the following code in a terminal:
```
python
>>> import nltk
>>> nltk.download()
```
Then click on `Download` on the graphical window.

# Usage and data pipeline

If you wish to reproduce the analysis, here are the different steps to carry out.

## Download a set of movie scripts from Internet

The scripts are obtained by scraping the website [IMSDb](http://www.imsdb.com/). You can automatically download approximately 1000 scripts from this website by running the code in `code/scraping_script.py`:
```
cd code/
python scraping_script.py
```
The code creates a directory `data/scraping`, where it stores the movie scripts, along with some metainformation.

## Extract the emotional plotline

For each movie script, the text is divided into *windows* of 100 consecutive words, and a quantified emotional content is associated to each window.

This is done by looking up each word of a given *window* in the [Word-Emotion Association Lexicon](http://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm), which associates words with 8 emotions (anger, anticipation, disgust, fear, joy, sadness, surprise, trust) and 2 sentiments (negative, positive). A copy of the NRC lexicon is stored in `data/emotions/NRC_emotions.txt`.

The code that extract the emotional content of each movie is in `code/emotions_script.py`. It can be run by typing:
```
cd code
python emotions_script.py
```
The code creates a directory `data/emotions/arrays`, where it stores the datapoints (as .npy) needed to trace the graph for each movie.

**Option 1:** To visualize the graphs, type:
```
cd code
python load_plotline.py
```

and answer yes (y) to the prompt "Do you want to save plots as png (y/n)?". The graphs will be stored in a directory `data/emotions/graphs`.

**Option 2:** To explore the data dynamically, open the corresponding Jupyter Notebook by typing:
```
cd jupyter
jupyter notebook Visualize_Emotions.ipynb
```
The dashboard generated with iWidgets allows an interactive view of the different plots.
![alt text](/Users/AnnaVMS/Desktop/Galvanize/bitbucket_file/project_plotline/md_images/md_dashboard.png "Dashboard View")

## Compute the pairwise distance

**To be done**  
Using DTW, calculate the pairwise distance between all the movies.

## Cluster the movies

**To be done**
