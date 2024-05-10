import psycopg2


try:
    connection = psycopg2.connect(
        host='31.129.63.105',
        user='admin',
        password='root',
        database='postgres'
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT VERSION()"""
        )
        print(cursor.fetchall())
    connection.close()
except Exception as e:
    print(e)