# Overview

This is a **data science project** which analyzes different **movie scripts** and extracts the evolution of the **emotional content** throughout each movie ("emotional plotline").

The aim is then to cluster the movies based on their emotional plotline. A visualization dashboard helps with the exploration of these clusters.

*Example output*

An example of an interactive dashboard allowing the user to explore the results of clustering (3 clusters) is shown here.


Page: https://annavm.github.io/Project_Plotline/example/

Screencast: ![dashboard demo](https://github.com/AnnaVM/Project_Plotline/blob/master/data/Dashboard_Demo.gif "Dashboard demo")

the page can take a little while to load, you can then use the tools to select a point, see its name and the corresponding emotional plotline.

Screenshot:
![Screenshot of example_output][ex_out]

# Requirements and installation

It is recommended to use the [Anaconda](https://www.continuum.io/downloads) distribution, to install a set of standard required packages. Once Anaconda is installed, please type:
```
conda install numpy pandas matplotlib numba jupyter
```
The additional required Python packages are listed in the file `requirements.txt`. In order to install them, please type:
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
![iWidget](https://github.com/AnnaVM/Project_Plotline/blob/master/md_images/md_dashboard.png "Dashboard View")

## Compute the pairwise distance

The aim is to compare the evolution of emotions in two movies. This relies on a building a comparison tool to contrast a set of 'emotion' plotlines defining a given movie to the set obtained for another. The approach retained here is based on Dynamic Time Wrapping, which calculates the pairwise distance between all the movies.

The code that returns a dictionary containing the pairwise distances in pickled form is in `code/dtw_script.py`. It can be run by typing:
```
cd code
python dtw_script.py
```

The dictionary of pairwise is stored in `data/distances.pkl`, the lookup structure is as follows: `distances[filename1][filename2]`.

A Jupyter Notebook, `jupyter/Explore_closest_movies.ipynb`, is available to give an easy access the top 10 closest movies to a selected movie.

## Cluster the movies

The motivation is to group the movies according to the evolution of emotions in their scripts. This is achieved thanks to the pairwise distances calculated previously and a modified Kmeans clustering algorithm called medoids (instead of taking the mean as the prototype of the cluster the median is retained). As with any unsupervised algorithm, assessing the performance of the clustering is not straightforward. Here, I develop 2 ways to investigate the results of clustering: first observing the cost associated with a given number of clusters (option 1), second, analyzing how reproducible the clustering is (option 3).

The code  `code/medoids.py` has 3 main features:

option 1: picking the number of clusters
```
cd code
python medoids.py pick_k
```

option 2: running the k medoids algorithm (here for 3 clusters)
```
cd code
python medoids.py k=3
```

option 3: investigating the reproducibility of the clustering is (change 3 to number of clusters chosen)
```
cd code
python medoids.py 3_stability
```

The most meaningful clustering occurred for k = 3, as the vast majority of movies stay in the same clusters.

## Develop the visualization tool

I build an interactive scatter graph with linked emotional plotline thanks to the `mpld3` package (http://mpld3.github.io/). This package is a great way of combining Javascript, D3js and python. I used an [example of custom plugin](http://mpld3.github.io/examples/custom_plugin.html) to write the appropriate D3js script to develop a tool where the plotlines and the movie name appear on hover.


[ex_out]: https://github.com/AnnaVM/Project_Plotline/blob/master/md_images/screenshot_final_dashboard1.png
