'''
this script gets the movie script, movie name, genres and writer
the progression of scraping can be followed on the terminal

Usage:
------
To execute this script, type in a terminal
$ python scraping_script.py

Challenges --> choices:
-----------------------
some scripts are in html, some in pdf (<50) --> pdfs are ignored
some html scripts have javascript --> requests is not enough, selenium is used

Files created:
--------------
in ../data/scraping/texts folder: all of the scripts available in html
in ../data/scraping folder: a successful_files.csv with a row for each movie
successfully scraped, with in each row:
    the name; writer list; genre list; compact name
                            a movies_pdf_script.csv with a row for each movie
not available in html (usually as pdf) with simply the title of the movie
'''

import requests
import re
import os
import sys
import codecs
from bs4 import BeautifulSoup
from selenium import webdriver

def get_all_movies():
    '''
    Scraping 'http://www.imsdb.com/all%20scripts/'
    returns:
    --------
    movie list: list of tuples
        each tuple contains:
        (movie title, link to movie page, movie_title)
        movie page: string with space and commas
        link: string href= ...
        movie_title: title with the whitespaces as _, name cropped at '.' or ','

    ex1:
    (u'10 Things I Hate About You',
    u'/Movie Scripts/10 Things I Hate About You Script.html',
    u'10_Things_I_Hate_About_You')

    ex2
    (u'Abyss, The', u'/Movie Scripts/Abyss, The Script.html', u'Abyss')
    '''
    link_all_scripts = 'http://www.imsdb.com/all%20scripts/'
    response_all_scripts = requests.get(link_all_scripts)
    soup = BeautifulSoup(response_all_scripts.text, 'html.parser')

    #page is constructed with tables, the 3 one is the one we want
    find_tables = soup.findAll('td', valign='top')
    all_movies = find_tables[2].findAll('a')

    # exemple of item in list all_movies
    # <a href="/Movie Scripts/10 Things I Hate About You Script.html"
    # title="10 Things I Hate About You Script">10 Things I Hate About You</a>

    movies = [(movie_info.string, \
              movie_info["href"], \
              re.split("[,.]",movie_info.string)[0].replace(' ', '_'))
              for movie_info in all_movies]
    return movies

def check_movie_info(movies):
    '''
    short script to check that list of tuples (movie title, link, movie_title)
    in movies have a link that start with '/Movie Scripts/'
    '''
    for movie in movies:
        if movie[1][0:15] !='/Movie Scripts/':
            return 'somethings rotten in the state of Denmark'
    return 'flying true and straight'

def handle_movie (movie, browser):
    '''
    parameters:
    -----------
    movie: a tuple from movies list created by get_all_movies
            (movie title, link to movie page, movie_title)
    browser: browser created from selenium to get complete html page
    '''
    #unpack tuple
    title, link_to_movie_page, movie_title = movie

    #interrogate the page with all the movie information (ratings, writer,
    #genre, link to script)
    full_html_link = u'http://www.imsdb.com' + link_to_movie_page
    response_script = requests.get(full_html_link)
    soup = BeautifulSoup(response_script.text, 'html.parser')

    #get all relevant information (genre, writer, script) from page
    list_links = soup.findAll('table', "script-details")[0].findAll('a')
    genre = []
    writer = []
    script = ''
    for link in list_links:
        href = link['href']
        if href[0:7]== "/writer":
            writer.append(link.get_text())
        if href[0:7]== "/genre/":
            genre.append(link.get_text())
        if href[0:9]== "/scripts/" and href[-5:]=='.html':
            script = href
    #if we get a link to html, let's write the script to a file and include
    #the movie in a csv file with all information
    if script:
        #writing the script text to the file
        full_html_to_text =  u'http://www.imsdb.com' + script

        browser.get(full_html_to_text)
        response_to_text = browser.page_source
        soup = BeautifulSoup(response_to_text, 'html.parser')

        path_to_file = '../data/scraping/texts/'
        filename = path_to_file + movie_title + '.txt'
        with codecs.open(filename, "w", encoding='ascii', errors='ignore') as f:
            #if scraping does not go as planned (different structure)
            if len(soup.findAll('td', "scrtext"))!=1:
                path_to_file = '../data/scraping/'
                scraping_error_files = path_to_file + 'scraping_error.csv'
                with open(scraping_error_files, 'a') as i:
                    new_row = title
                    i.write(new_row)
            #normal scraping
            else:
                text = soup.findAll('td', "scrtext")[0].get_text()
                f.write(text)
        #including the movie in csv of successfulmy scraped movies
        path_to_file = '../data/scraping/'
        successful_files = path_to_file + 'successful_files.csv'
        with open(successful_files, 'a') as h:
            new_row = title + ';' + str(genre) + ';' + str(writer) + ';' \
                    + movie_title + ';' + filename + '\n'
            h.write(new_row)
    else:
        #some movies have scripts as pdf, the movie names are recorded
        path_to_file = '../data/scraping/'
        pdf_files = path_to_file + 'movies_pdf_script.csv'
        with open(pdf_files, 'a') as g:
            new_row = title
            g.write(new_row)

def progression_bar(i, Ntot, Nbars=60, char='-'):
    '''
    Shows a progression bar with Nbars
    parameters:
    -----------
    i: index of the files
    Ntot: total number of files
    Nbars: how many bars to fill
    char: character to show as progression
    '''
    nbars = int( (i+1)*1./Ntot * Nbars )
    sys.stdout.write('\r[' + nbars*char)
    sys.stdout.write((Nbars-nbars)*' '+']')
    sys.stdout.write('%d/%d'%(i, Ntot))
    sys.stdout.flush()

if __name__ == '__main__':
    #create data/scraping/texts files
    if not os.path.exists('../data'):
        os.mkdir('../data')
        print 'making ../data folder'
    if not os.path.exists('../data/scraping'):
        os.mkdir('../data/scraping')
        print 'making ../data/scraping folder'
    if not os.path.exists('../data/scraping/texts'):
        os.mkdir('../data/scraping/texts')
        print 'making ../data/scraping/texts folder'

    #get all the movie information
    movies = get_all_movies()
    print check_movie_info(movies)
    #get all the scripts (in texts folder) and summary of movies in .csv format
    #(in scraping folder)
    browser = webdriver.Firefox()
    for i,movie in enumerate(movies):
        handle_movie(movie, browser)
        progression_bar(i, len(movies))

'''comments on the scraping results
movies that were not scraped successfully:
-------
3 texts are manually removed:
Appolo 13 & Scary Movie 2 (no actual script available on website)
They (zero octet file - the results of the findAll is a little different than
    for other movies: as only one movie was in this situation, it is ignored)

list of pdfs:
--------------
8 Mile was pdf
A.I. was pdf
Back to the Future was pdf
Back to the Future II & III was pdf
Batman and Robin was pdf
Batman Begins was pdf
Batman Forever was pdf
Batman Returns was pdf
Blues Brothers, The was pdf
Casablanca was pdf
Clockwork Orange, A was pdf
Contact was pdf
Courage Under Fire was pdf
Dark Knight, The was pdf
Donnie Darko was pdf
Equilibrium was pdf
Executive Decision was pdf
Eyes Wide Shut was pdf
Full Metal Jacket was pdf
Fury was pdf
Goodfellas was pdf
Harry Potter and the Chamber of Secrets was pdf
Harry Potter and the Deathly Hallows Part 1 was pdf
Harry Potter and the Goblet of Fire was pdf
Harry Potter and the Half-Blood Prince was pdf
Harry Potter and the Prisoner of Azkaban was pdf
Harry Potter and the Sorcerer's Stone was pdf
Innerspace was pdf
Jade was pdf
Kiss of the Spider Woman was pdf
Lethal Weapon was pdf
Lethal Weapon 4 was pdf
Lion King, The was pdf
Matchstick Men was pdf
Monster's Ball was pdf
Mr. Holland's Opus was pdf
Officer and a Gentleman, An was pdf
Outbreak was pdf
Robocop was pdf
Shadow of the Vampire was pdf
Sneakers was pdf
Speed was pdf
Superfights was pdf
Troy was pdf
Unforgiven was pdf
Valentine's Day was pdf
Vertigo was pdf
When Harry Met Sally was pdf
'''
