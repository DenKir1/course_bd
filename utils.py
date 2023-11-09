import psycopg2
import requests


def get_vacancies(employer_id):
    """Получение данных вакансий по API"""

    params = {
        'area': 1,
        'page': 0,
        'per_page': 100
    }
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}"
    data_vacancies = requests.get(url, params=params).json()

    vacancies_data = []
    for item in data_vacancies["items"]:
        hh_vacancies = {
            'vacancy_id': int(item['id']),
            'vacancies_name': item['name'],
            'payment': item["salary"]["from"] if item["salary"] else None,
            'requirement': item['snippet']['requirement'],
            'vacancies_url': item['alternate_url'],
            'employer_id': employer_id
        }
        if hh_vacancies['payment'] is not None:
            vacancies_data.append(hh_vacancies)

        return vacancies_data


def get_employer(employer_id):
    """Получение данных о работодателей  по API"""

    url = f"https://api.hh.ru/employers/{employer_id}"
    data_vacancies = requests.get(url).json()
    hh_company = {
        "employer_id": int(employer_id),
        "company_name": data_vacancies['name'],
        "open_vacancies": data_vacancies['open_vacancies']
        }

    return hh_company


def create_table():
    """Создание БД, созданение таблиц"""

    conn = psycopg2.connect(host="localhost", database="postgres",
                            user="postgres", password="12345")
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("DROP DATABASE IF EXISTS course_work_5")
    cur.execute("CREATE DATABASE course_work_5")

    conn.close()

    conn = psycopg2.connect(host="localhost", database="hh_vacan",
                            user="postgres", password="12345")
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE employers (
                    employer_id INTEGER PRIMARY KEY,
                    company_name varchar(255),
                    open_vacancies INTEGER
                    )""")

        cur.execute("""
                    CREATE TABLE vacancies (
                    vacancy_id SERIAL PRIMARY KEY,
                    vacancies_name varchar(255),
                    payment INTEGER,
                    requirement TEXT,
                    vacancies_url TEXT,
                    employer_id INTEGER REFERENCES employers(employer_id)
                    )""")
    conn.commit()
    conn.close()


def add_to_table(employers_list):
    """Заполнение базы данных компании и вакансии"""

    with psycopg2.connect(host="localhost", database="course_work_5",
                          user="postgres", password="12345") as conn:
        with conn.cursor() as cur:
            cur.execute('TRUNCATE TABLE employers, vacancies RESTART IDENTITY;')

            for employer in employers_list:
                employer_list = get_employer(employer)
                cur.execute('INSERT INTO employers (employer_id, company_name, open_vacancies) '
                            'VALUES (%s, %s, %s) RETURNING employer_id',
                            (employer_list['employer_id'], employer_list['company_name'],
                             employer_list['open_vacancies']))

            for employer in employers_list:
                vacancy_list = get_vacancies(employer)
                for v in vacancy_list:
                    cur.execute('INSERT INTO vacancies (vacancy_id, vacancies_name, '
                                'payment, requirement, vacancies_url, employer_id) '
                                'VALUES (%s, %s, %s, %s, %s, %s)',
                                (v['vacancy_id'], v['vacancies_name'], v['payment'],
                                 v['requirement'], v['vacancies_url'], v['employer_id']))

        conn.commit()


def create_database(database_name: str, params: dict):
    """Создание базы данных и таблиц для сохранения данных о каналах и видео."""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE channels (
                channel_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                views INTEGER,
                subscribers INTEGER,
                videos INTEGER,
                channel_url TEXT
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE videos (
                video_id SERIAL PRIMARY KEY,
                channel_id INT REFERENCES channels(channel_id),
                title VARCHAR NOT NULL,
                publish_date DATE,
                video_url TEXT
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(data, database_name: str, params: dict):
    """Сохранение данных о каналах и видео в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for channel in data:
            channel_data = channel['channel']['snippet']
            channel_stats = channel['channel']['statistics']
            cur.execute(
                """
                INSERT INTO channels (title, views, subscribers, videos, channel_url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING channel_id
                """,
                (channel_data['title'], channel_stats['viewCount'], channel_stats['subscriberCount'],
                 channel_stats['videoCount'], f"https://www.youtube.com/channel/{channel['channel']['id']}")
            )
            channel_id = cur.fetchone()[0]
            videos_data = channel['videos']
            for video in videos_data:
                video_data = video['snippet']
                cur.execute(
                    """
                    INSERT INTO videos (channel_id, title, publish_date, video_url)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (channel_id, video_data['title'], video_data['publishedAt'],
                     f"https://www.youtube.com/watch?v={video['id']['videoId']}")
                )

    conn.commit()
    conn.close()