from utils import get_employers, create_db, create_tables, fill_db
from config import config
from bd_manager import DBManager

if __name__ == '__main__':
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
                 1429999,  # Cian
                 ]

    database_name = 'имя базы данных'
    params = config()

    create_db(database_name, params)
    create_tables(database_name, params)
    fill_db(get_employers(companies), database_name, params)

    db_manager = DBManager(database_name, params)