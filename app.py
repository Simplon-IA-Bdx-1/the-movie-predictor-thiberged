#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TheMoviePredictor script
Author: Arnaud de Mouhy <arnaud@admds.net>
"""

import mysql.connector
import sys
import argparse
import csv
import datetime

def connectToDatabase():
    return mysql.connector.connect(user='predictor', password='predictor',
                              host='127.0.0.1',
                              database='predictor')

def disconnectDatabase(cnx):
    cnx.close()

def createCursor(cnx):
    return cnx.cursor(dictionary=True)

def closeCursor(cursor):    
    cursor.close()

def findQuery(table, id):
    return ("SELECT * FROM {} WHERE id = {}".format(table, id))

def findAllQuery(table):
    return ("SELECT * FROM {}".format(table))

def insertQuery(table, first, last):
    return ("INSERT INTO {} (firstname, lastname) VALUES ('{}', '{}')".format(table, first, last))

def insertMovieQuery(table, movieTitle, movieDuration, movieOriginalTitle, movieRating, movieRelease):
    return ("INSERT INTO {} (title, original_title, duration, rating, release_date) VALUES ('{}', '{}', {}, '{}', '{}')".format(table, movieTitle, movieOriginalTitle, movieDuration, movieRating, movieRelease))

def find(table, id):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    query = findQuery(table, id)
    cursor.execute(query)
    results = cursor.fetchall()
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return results

def findAll(table):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(findAllQuery(table))
    results = cursor.fetchall()
    closeCursor(cursor)
    disconnectDatabase(cnx)
    return results

def insert(table, firstname, lastname):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(insertQuery(table, firstname, lastname))
    cnx.commit()
    closeCursor(cursor)
    disconnectDatabase(cnx)

def insertMovie(table, movieTitle, movieDuration, movieOriginalTitle, movieRating, movieRelease):
    cnx = connectToDatabase()
    cursor = createCursor(cnx)
    cursor.execute(insertMovieQuery(table, movieTitle, movieDuration, movieOriginalTitle, movieRating, movieRelease))
    cnx.commit()
    closeCursor(cursor)
    disconnectDatabase(cnx)

def printPerson(person):
    print("#{}: {} {}".format(person['id'], person['firstname'], person['lastname']))

def printMovie(movie):
    print("#{}: {} released on {}".format(movie['id'], movie['title'], movie['release_date']))

parser = argparse.ArgumentParser(description='Process MoviePredictor data')

parser.add_argument('context', choices=['people', 'movies'], help='Le contexte dans lequel nous allons travailler')

action_subparser = parser.add_subparsers(title='action', dest='action')

list_parser = action_subparser.add_parser('list', help='Liste les entitÃ©es du contexte')
list_parser.add_argument('--export' , help='Chemin du fichier exportÃ©')

find_parser = action_subparser.add_parser('find', help='Trouve une entitÃ© selon un paramÃ¨tre')
find_parser.add_argument('id' , help='Identifant Ã  rechercher')

import_parser = action_subparser.add_parser('import', help='import')
import_parser.add_argument('--file' , help='fichier importÃ©')

insert_parser = action_subparser.add_parser('insert', help='Ajout d\'une nouvelle entité')
insert_parser.add_argument('--firstname' , type=str, help='prénom de l\'entité')
insert_parser.add_argument('--lastname' , type=str, help='nom de l\'entité')
insert_parser.add_argument('--title' , type=str, help='titre film')
insert_parser.add_argument('--duration' , type=int, help='durée film')
insert_parser.add_argument('--original-title' , type=str, dest='original', help='titre original')
insert_parser.add_argument('--rating' , type=str, help='rating')
insert_parser.add_argument('--release-date' , type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), dest='release', help='date de lancement')

args = parser.parse_args()

if args.context == "people":
    if args.action == "list":
        people = findAll("people")
        if args.export:
            with open(args.export, 'w', encoding='utf-8', newline='\n') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(people[0].keys())
                for person in people:
                    writer.writerow(person.values())
        else:
            for person in people:
                printPerson(person)
    if args.action == "find":
        peopleId = args.id
        people = find("people", peopleId)
        for person in people:
            printPerson(person)
    if args.action == "insert":
        peopleFirstname = args.firstname
        peopleLastname = args.lastname
        insert("people", peopleFirstname, peopleLastname)

if args.context == "movies":
    if args.action == "list":  
        movies = findAll("movies")
        for movie in movies:
            printMovie(movie)
    if args.action == "find":  
        movieId = args.id
        movies = find("movies", movieId)
        for movie in movies:
            printMovie(movie)
    if args.action == "insert":
        movieTitle = args.title
        movieDuration = args.duration
        movieOriginalTitle = args.original
        movieRating = args.rating
        movieRelease = args.release
        insertMovie("movies", movieTitle, movieDuration, movieOriginalTitle, movieRating, movieRelease)
    if args.action == "import":
        movies = findAll("movies")
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                n=0
                for row in reader:
                    if n > 0:
                        insertMovie("movies", row[0], row[2], row[1], row[3], row[4] )
                    n = n + 1
