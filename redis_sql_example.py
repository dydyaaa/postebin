import psycopg2, redis, json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

try:
    news_id = 1
    cache_key = f'news:{news_id}'
    cached_news = redis_client.get(cache_key)
    if cached_news:
        news = json.loads(cached_news)
        redis_client.expire(cache_key, 180)
        print('Data from redis')
        for item in news:
            print(item)
    else:
        connection = psycopg2.connect(
            host='0.0.0.0',
            user='admin',
            password='root',
            database='postgres'
        )

        connection.autocommit=True

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM news
                WHERE id = %s""", (news_id, )
            )
            news = cursor.fetchall()
            if news:
                redis_client.setex(cache_key, 180, json.dumps(news))
                print('Data from sql')
                for item in news:
                    print(item)
            else:
                print('None')

        connection.close()
except Exception as e:
    print(e)