import os

import pytest
from dotenv import load_dotenv

from src.dbmanager import DBManager
from src.vacancy import Vacancy


@pytest.fixture
def companies():
    return [{"5801953": "ООО Точка Маркетплейсы"},
            {"10259650": "Softintermob LLC"}]


@pytest.fixture
def vacancies():
    return [
        Vacancy('97835750', 'Тестировщик',
                "5801953", "ООО Точка Маркетплейсы",
                "https://api.hh.ru/vacancies/97835750?host=hh.ru"),
        Vacancy('97802709', 'Frontend developer (React)',
                "5801953", "ООО Точка Маркетплейсы",
                "https://api.hh.ru/vacancies/97802709?host=hh.ru"),
        Vacancy('98530610', 'Python backend developer (middle/senior)',
                "5801953", "ООО Точка Маркетплейсы",
                "https://api.hh.ru/vacancies/98530610?host=hh.ru"),
        Vacancy('97418037', 'Менеджер по продажам b2b',
                "5801953", "ООО Точка Маркетплейсы",
                "https://api.hh.ru/vacancies/97418037?host=hh.ru", 100000)
    ]


def test_db_manager(companies, vacancies):
    load_dotenv()

    db_config = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }

    with DBManager(db_config) as db:
        db.clear()
        assert len(db.get_all_vacancies()) == 0
        db.save_companies(companies)
        db.save_vacancies(vacancies)
        assert len(db.get_all_vacancies()) == len(vacancies)
        assert len(db.get_companies_and_vacancies_count()) == len(companies)
        keyword = 'Developer'
        vacancies_by_keyword = list(filter(lambda v: keyword.lower() in v.name.lower(), vacancies))
        assert len(db.get_vacancies_with_keyword('Developer')) == len(vacancies_by_keyword)
