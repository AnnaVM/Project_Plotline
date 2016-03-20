# Overview

This is a **data science project** which analyzes different **movie scripts** and extracts the evolution of the **emotional content** throughout each movie ("emotional plotline").

The aim is then to cluster the movies based on their emotional plotline.

# Usage and data pipeline

If you wish to reproduce the analysis, here are the different steps to carry out.

## Download a set of movie scripts from Internet

The scripts are obtained by scraping the website [IMSDb](http://www.imsdb.com/). You can automatically download approximately 1000 scripts from this website by running the code in `code/scraping_script.py`:
```
cd code/
python scraping_script.py
```
The code creates a directory `data/`, where it stores the movie scripts, along with some metainformation.

## Extract the emotional plotline

**To be done**  
Quantify the amount of each of 8 different emotions as a function of time, for each movie.

## Compute the pairwise distance

**To be done**  
Using DTW, calculate the pairwise distance between all the movies.

## Cluster the movies

**To be done**


