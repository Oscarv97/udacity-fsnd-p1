#!/usr/bin/env python3

import psycopg2
import sys
import datetime

DBNAME = "news"


def execute_query(query):
    try:
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        c.execute(query)
        results = c.fetchall()
        db.close()
        return (results)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_top_articles():
    query = ("""
        SELECT title, count(title)
        FROM log, articles
        WHERE '/article/' || articles.slug = log.path
        GROUP BY title
        ORDER BY count DESC
        LIMIT 3""")

    top_articles = execute_query(query)

    print('\nWhat are they most popular three articles of all time?\n')

    for title, views in top_articles:
        articles = " " + '"' + title + '"' + " — " + str(views) + " views\n"
        sys.stdout.write(articles)


def get_top_authors():
    query = ("""
        SELECT name, count(title)
        FROM log, articles, authors
        WHERE '/article/' || articles.slug = log.path
        AND authors.id = articles.author
        GROUP BY authors.name
        ORDER BY count DESC""")

    popular_authors = execute_query(query)

    print('\nWho are the most popular article authors of all time?\n')

    for name, views in popular_authors:
        print("  ", name, "-", views, "views")


def get_error_percentage():

    query3 = ("""
        SELECT * from (SELECT a.day,
            round(cast((100*b.hits) AS numeric) / cast(a.hits as numeric), 2)
        AS errorPercent FROM
            (SELECT date(time) AS day, count(*) AS hits FROM log GROUP BY day) AS a
        INNER JOIN
            (SELECT date(time) AS day, count(*) AS hits FROM log WHERE status
            LIKE '%404%' GROUP BY day) AS b on a.day = b.day)
        AS t where errorPercent > 1.0;
"""
              )
    error_days = execute_query(query3)

    print("\nOn which days did more than 1% of requests lead to errors?\n")

    for i in range(len(error_days)):
        print('\t',error_days[i][0].strftime("%B"),error_days[i][0].strftime("%d"),',',error_days[i][0].strftime("%Y"),'——', error_days[i][1], '%')


if __name__ == '__main__':
    get_top_articles()

    get_top_authors()

    get_error_percentage()
