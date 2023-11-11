import psycopg2
from config import config


class DBManager:
    """ Класс для взаимодействия с базой вакансий"""
    def __init__(self, database_name):
        self.database_name = database_name
        params = config()
        self.params = params

    def get_companies_and_vacancies_count(self):
        """ Возвращает количество вакансий"""
        try:
            conn = psycopg2.connect(database=self.database_name, **self.params)
            with conn.cursor() as cur:
                cur.execute('SELECT company_name, COUNT(vacancy_id) '
                            'FROM companies '
                            'JOIN vacancies USING (company_id) '
                            'GROUP BY company_name;')
                data = cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            return f'[INFO] {error}'
        conn.close()
        return data

    def get_all_vacancies(self):
        """Получение списка всех вакансий"""
        try:
            connection = psycopg2.connect(database=self.database_name, **self.params)
            with connection.cursor() as cursor:
                cursor.execute('SELECT title_vacancy, company_name, salary, link_vac '
                               'FROM vacancies '
                               'JOIN companies USING (company_id);')

                data = cursor.fetchall()

        except (Exception, psycopg2.DatabaseError) as error:
            return f'[INFO] {error}'

        connection.close()
        return data

    def get_avg_salary(self):
        """ Средняя зарплата"""
        try:
            connection = psycopg2.connect(database=self.database_name, **self.params)
            with connection.cursor() as cursor:
                cursor.execute('SELECT company_name, round(AVG(salary)) AS avg_salary '
                               'FROM companies '
                               'JOIN vacancies USING (company_id) '
                               'GROUP BY company_name;')
                data = cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            return f'[INFO] {error}'
        connection.close()
        return data

    def get_vacancies_with_highest_salary(self):
        """ Вакансии с зарплатой выше средней"""
        try:
            connection = psycopg2.connect(database=self.database_name, **self.params)
            with connection.cursor() as cursor:
                cursor.execute('SELECT title_vacancy, salary, link_vac '
                               'FROM vacancies '
                               'WHERE salary > (SELECT AVG(salary) FROM vacancies);')
                data = cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as err:
            return f'[INFO] {err}'
        connection.close()
        return data

    def get_vacancies_with_keyword(self, keyword):
        """ Вакансии по названию"""
        try:
            connection = psycopg2.connect(database=self.database_name, **self.params)
            with connection.cursor() as cursor:
                cursor.execute(f"""
                SELECT title_vacancy, salary, link_vac 
                FROM vacancies
                WHERE lower(title_vacancy) LIKE '%{keyword}%'
                OR lower(title_vacancy) LIKE '%{keyword}'
                OR lower(title_vacancy) LIKE '{keyword}%'""")
                data = cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as err:
            return f'[INFO] {err}'
        connection.close()
        return data
