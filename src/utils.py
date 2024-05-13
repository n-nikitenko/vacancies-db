from json import load
from typing import List

from prettytable import PrettyTable

from src.dbmanager import DBManager


def print_menu():
    '''выводит на экран меню программы'''

    return input("Введите:\n"
                 "1 - просмотр среднего значения зарплаты\n"
                 "2 - поиск вакансий по ключевому слову\n"
                 "3 - просмотр списка компаний\n"
                 "4 - просмотр списка вакансий\n"
                 "5 - завершить работу с программой\n")


def print_vacancies_by_keyword(db: DBManager):
    '''выводит на экран список вакансий, отфильтрованных по ключевому слову в названии'''

    keyword = input("Введите ключевое слово для фильтрации вакансий: ").strip() or "python"
    filtered_vacancies = db.get_vacancies_with_keyword(keyword)
    if filtered_vacancies:
        t = PrettyTable(['Вакансия', 'Зарплата', 'Компания', 'Ссылка на вакансию'])
        t.align = 'r'
        print(f"Вакансии, найденные по ключевому слову '{keyword}':")
        for v in filtered_vacancies:
            t.add_row([v.name, v.salary if v.salary > 0 else 'не указана', v.employer_name, v.url])
        print(t)
    else:
        print(f"Не найдено вакансий по ключевому слову '{keyword}'.")


def print_all_vacancies(db: DBManager):
    '''выводит на экран список всех вакансий'''

    all_vacancies = db.get_all_vacancies()
    if all_vacancies:
        t = PrettyTable(['Вакансия', 'Зарплата', 'Компания', 'Ссылка на вакансию'])
        t.align = 'r'
        print(f"Список всех вакансий:")
        for v in all_vacancies:
            t.add_row([v.name, v.salary if v.salary > 0 else 'не указана', v.employer_name, v.url])
        print(t)
    else:
        print(f"В базе данных нет вакансий.")


def print_companies(db: DBManager):
    '''выводит на экран список компаний и кол-во опбуликованных вакансий'''

    companies_and_vacancies_count = db.get_companies_and_vacancies_count()
    t = PrettyTable(['Компания', 'Кол-во вакансий'])
    t.align = 'r'
    for data in companies_and_vacancies_count:
        t.add_row(data.values())
    print(t)


def load_companies(path: str) -> List[dict]:
    '''загружает список словарей формата id компании: название компании из json'''

    with open(path, 'r', encoding='utf-8') as f:
        companies = load(f)
    return companies or []
