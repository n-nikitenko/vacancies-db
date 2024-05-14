import os

from colorama import Fore, Style
from dotenv import load_dotenv

from src.dbmanager import DBManager
from src.hh_api import HeadHunterAPI
from src.utils import print_menu, print_vacancies_by_keyword, print_companies, print_all_vacancies, load_companies
from src.vacancy import Vacancy


def main():
    if not load_dotenv():
        print(f"{Fore.RED}Не найден файл с настройками подключения к БД: '.env'")
        print(Style.RESET_ALL)
        exit()

    db_config = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }

    hh_api = HeadHunterAPI()

    path = os.path.join(f"..{os.sep}data", "companies.json")
    try:
        companies = load_companies(path)
    except FileNotFoundError as e:
        print(f"{Fore.YELLOW}Не найден файл с id компаний: '{path}'")
        print(Style.RESET_ALL)
        companies = [
            {"3740808": "Betting Software"},
            {"10259650": "Softintermob LLC"},
            {"5801953": "ООО Точка Маркетплейсы"},
            {"8997092": "ООО Дивергент"},
            {"2416909": "ООО Смартекс"},
            {"4480129": "V4Scale"},
            {"3202190": "KTS"},
            {"2331500": "ООО Верный Код"},
            {"12504": "Сфера"},
            {"1776381": "CATAPULTO.RU"},
            {"5724503": "Amex Development"}
        ]

    print(f"\n{Fore.GREEN}Получение вакансий с сервера. Пожалуйста, подождите.")
    print(Style.RESET_ALL)
    hh_vacancies = hh_api.get_vacancies(companies)

    vacancies_list = Vacancy.cast_to_object_list(hh_vacancies)

    with DBManager(db_config) as db:
        print(f"{Fore.GREEN}Сохранение вакансий в базу данных. Пожалуйста, подождите.")
        print(Style.RESET_ALL)
        db.save_companies(companies)
        db.save_vacancies(vacancies_list)

        while True:
            user_input = print_menu().strip()

            if user_input == '1':
                print(f"\n{Fore.GREEN}Средняя зарплата: {db.get_avg_salary()} рублей.")
                print(Style.RESET_ALL)
            elif user_input == '2':
                print_vacancies_by_keyword(db)
            elif user_input == '3':
                print_companies(db)
            elif user_input == '4':
                print_all_vacancies(db)
            elif user_input == '5':
                break


if __name__ == '__main__':
    main()
