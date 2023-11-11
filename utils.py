import requests
import psycopg2


def add_employers(company_ids: list[int], company_id: str):
    """Добавляет в список компаний id новой компании"""
    if company_id.isnumeric():
        print('Компания добавлена для поиска')
        return company_ids.append(int(company_id))
    print('Неправильный id, продолжим поиск компаний по-умолчанию')
    return company_ids


def get_employers(companies):
    """ Запрос через API hh.ru """
    employers = []
    params = {
        'area': 1,
        'page': 0,
        'per_page': 100
    }
    for company in companies:
        url = f'https://api.hh.ru/employers/{company}'
        company_response = requests.get(url).json()
        vacancy_response = requests.get(company_response['vacancies_url'], params=params).json()
        employers.append({
            'company': company_response,
            'vacancies': vacancy_response['items']
        })
    print('Запрос по API прошел успешно')
    return employers


def filter_strings(string: str) -> str:
    """  Убирает из описания HTML коды  """
    symbols = [
                '\n', '<strong>', '\r', '</strong>', '</p>', '<p>', '</li>', '<li>', '<h2>',
                '<b>', '</b>', '<ul>', '<li>', '</li>', '<br />', '</ul>', '<em>', '&mdash;',
               ]
    for symbol in symbols:
        string = string.replace(symbol, '')
    return string


def filter_salary(salary):
    """ Фильтр зарплаты"""
    if salary is not None:
        if salary['from'] is not None:
            return salary['from']
        elif salary['to'] is not None:
            return salary['to']
    return None


def create_db(database_name, params):
    """ Создание базы данных"""
    conn = psycopg2.connect(database='postgres', **params)
    conn.autocommit = True

    with conn.cursor() as cursor:
        cursor.execute(f'DROP DATABASE IF EXISTS {database_name}')
        cursor.execute(f'CREATE DATABASE {database_name}')

    conn.close()
    print('Хранилище создано.')


def create_tables(database_name, params):
    """Создание таблиц в PostgreSQL"""
    connection = psycopg2.connect(database=database_name, **params)

    with connection.cursor() as cursor:
        cursor.execute('CREATE TABLE companies('
                       'company_id SERIAL PRIMARY KEY,'
                       'company_name varchar(255) NOT NULL,'
                       'description text,'
                       'link_com varchar(255),'
                       'url_vacancies varchar(255))')

        cursor.execute('CREATE TABLE vacancies('
                       'vacancy_id SERIAL PRIMARY KEY,'
                       'company_id int REFERENCES companies (company_id) NOT NULL,'
                       'title_vacancy varchar(255) NOT NULL,'
                       'salary INTEGER,'
                       'link_vac varchar(255),'
                       'description text,'
                       'experience varchar(255))')

    connection.commit()
    connection.close()
    print('Таблицы созданы.')


def fill_db(employers: list[dict], database_name, params):
    """Заполнение базы данных словарем"""
    print('Заполняем хранилище.')
    conn = psycopg2.connect(database=database_name, **params)

    with conn.cursor() as cur:
        for employer in employers:
            cur.execute('''INSERT INTO companies 
                            (company_name, description, link_com, url_vacancies)
                            VALUES (%s, %s, %s, %s)
                            RETURNING company_id''',
                        (employer["company"].get("name"),
                         filter_strings(employer["company"].get("description")),
                         employer["company"].get("alternate_url"),
                         employer["company"].get("vacancies_url")))

            company_id = cur.fetchone()[0]

            for vacancy in employer["vacancies"]:
                salary = filter_salary(vacancy["salary"])
                cur.execute('''INSERT INTO vacancies
                               (company_id, title_vacancy, salary, link_vac, description, experience)
                               VALUES (%s, %s, %s, %s, %s, %s)''',
                            (company_id, vacancy["name"], salary,
                             vacancy["alternate_url"], vacancy["snippet"].get("responsibility"),
                             vacancy["experience"].get("name")))

    conn.commit()
    conn.close()
    print('Хранилище заполнено вакансиями.')