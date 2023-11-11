from utils import get_employers, create_db, create_tables, fill_db, add_employers
from config import config
from db_manager import DBManager


def main():
    companies = [78638,  # Тинькофф
                 84585,  # Авито
                 3529,  # Сбер
                 633069,  # Selectel
                 1740,  # Яндекс
                 1375441,  # Okko
                 1272486,  # Сбермаркет
                 2180,  # Ozon
                 1122462,  # Skyeng
                 15478,  # VK
                 1057,  # Kaspersky
                 2136954,  # DomClick
                 ]

    database_name = 'course_db'
    params = config()

    create_db(database_name, params)
    create_tables(database_name, params)

    new_id = input('Введите id компании для добавление, например Cian 1429999 - ')
    add_employers(companies, new_id)
    fill_db(get_employers(companies), database_name, params)

    db_m = DBManager(database_name)
    count_vac = db_m.get_companies_and_vacancies_count()
    print('Всего найдено вакансий')
    for vacancy in count_vac:
        print(f"У компании {vacancy[0]} получено {vacancy[1]} вакансий")
        print()

    input("Для получения всех вакансий нажмите ENTER")
    all_vac = db_m.get_all_vacancies()
    print('Список вакансий')
    for vacanc in all_vac:
        print(vacanc)
        print()

    input("Для получения средней зарплаты нажмите ENTER")
    avg_sal = db_m.get_avg_salary()
    for vacan in avg_sal:
        sal_vaca = None if vacan[1] is None else int(vacan[1])
        print(f'Средняя зарплата у компании {vacan[0]} - {sal_vaca}')
        print()

    input("Для получения вакансий с зарплатой выше среднего нажмите ENTER")
    high_sal = db_m.get_vacancies_with_highest_salary()
    for vaca in high_sal:
        print(vaca)
        print()

    key = input("Введите слово для поиска вакансий. ")
    key_vac = db_m.get_vacancies_with_keyword(key)
    for vac in key_vac:
        print(vac)
        print()


if __name__ == '__main__':
    main()
