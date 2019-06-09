#!/usr/bin/env python3

import psycopg2
import sys
import datetime

DBNAME = "news"


def execute_query(query):
    # Elements of sql lesson - DRY principles
    #  Also makes this easier to unit test as you
    # can assert execute_query was called
    try:
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        try:
            c.execute(query)
        except (Exception) as error:
            print('Failed to execute Query', error)

        results = c.fetchall()
        db.close()
        return (results)

    except (Exception, psycopg2.DatabaseError) as error:
        print('Failed to connect to DataBase', DBNAME, error)


question1 = ("""
    SELECT title, count(title)
    FROM log, articles
    WHERE '/article/' || articles.slug = log.path
    GROUP BY title
    ORDER BY count DESC
    LIMIT 3""")

question2 = ("""
    SELECT name, count(title)
    FROM log, articles, authors
    WHERE '/article/' || articles.slug = log.path
    AND authors.id = articles.author
    GROUP BY authors.name
    ORDER BY count DESC""")

question3 = ("""
    SELECT * from (SELECT a.day,
        round(cast((100*b.hits) AS numeric) / cast(a.hits as numeric), 2)
    AS errorPercent FROM
        (SELECT date(time) AS day, count(*) AS hits FROM log GROUP BY day) AS a
    INNER JOIN
        (SELECT date(time) AS day, count(*) AS hits FROM log WHERE status
        LIKE '%40%' GROUP BY day) AS b on a.day = b.day)
    AS t where errorPercent > 1.0;
"""
             )


def get_top_articles():

    print('\nQ1: What are they most popular three articles of all time?\n')
    # potential point of failure
    try:
        top_articles = execute_query(question1)

        for title, views in top_articles:
            articles = " " + '"' + title + '"' + \
                " — " + str(views) + " views\n"
            sys.stdout.write(articles)

    except (Exception) as error:
        print('Failed run Query for question 1', error)


def get_top_authors():

    print('\nQ2: Who are the most popular article authors of all time?\n')
    try:
        popular_authors = execute_query(question2)

        for name, results in popular_authors:
            print("  ", name, "-", results, "results")
    except (Exception) as error:
        print('Failed run Query for question 2', error)


def get_error_percentage():
    print("\nQ3: On which days did more than 1% of requests lead to errors?\n")
    try:
        error_days = execute_query(question3)

        for i in range(len(error_days)):
            print('\t', error_days[i][0].strftime("%B"),
                  error_days[i][0].strftime(
                "%d"), ',', error_days[i][0].strftime("%Y"),
                '——', error_days[i][1], '%')
    except (Exception) as error:
        print('Failed run Query for question 3', error)


if __name__ == '__main__':
    get_top_articles()

    get_top_authors()

    get_error_percentage()
