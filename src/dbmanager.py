import psycopg2
from typing import List

from colorama import Fore, Style
from psycopg2 import OperationalError

from src.vacancy import Vacancy


class DBManager:

    def __init__(self, dbname: str, params: dict):
        self.__vacancies_table_name = 'vacancies'
        self.__employers_table_name = 'employers'
        self._create_database(dbname, params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn is not None:
            self.conn.close()

    def _create_database(self, dbname: str, params: dict):
        """Создание базы данных и таблиц для сохранения данных о компаниях и вакансиях"""
        vacancies_dbname = "vacancies"
        try:
            conn = psycopg2.connect(dbname=dbname, **params)
            conn.autocommit = True
            cur = conn.cursor()

            cur.execute(f"DROP DATABASE IF EXISTS {vacancies_dbname}")
            cur.execute(f"CREATE DATABASE {vacancies_dbname}")

            conn.close()

            self.conn = psycopg2.connect(dbname=vacancies_dbname, **params)
            self.cur = self.conn.cursor()
            self._create_tables()
        except OperationalError as e:
            self.conn = None
            print(f"{Fore.RED}Ошибка подключения к базе данных {dbname}:\n", e)
            print(Style.RESET_ALL)
            exit()

    def _create_tables(self):
        with self.conn:
            self.cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {self.__employers_table_name} (
                        employer_id VARCHAR(255) PRIMARY KEY,
                        employer_name VARCHAR(255) NOT NULL
                        );
                        """)
            self.conn.commit()
            self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            employer_id VARCHAR(255) REFERENCES {self.__employers_table_name}(employer_id),
            url VARCHAR(255) NOT NULL,
            salary INT DEFAULT 0
            );
            """)

    def get_companies_and_vacancies_count(self) -> List[dict]:
        '''получает список всех компаний и количество вакансий у каждой компании'''
        # TODO: check this using group by
        with self.conn:
            self.cur.execute(f"SELECT employer_name, COUNT(vacancy_id) from vacancies "
                             f"JOIN {self.__employers_table_name} "
                             f"USING(employer_id) "
                             f"GROUP BY employer_name "
                             f"ORDER BY COUNT(vacancy_id) DESC")
            data = self.cur.fetchall()
            vacancies = [{'company_name': d[0], 'count': d[1]} for d in data]
            return vacancies

    def get_all_vacancies(self) -> List[Vacancy]:
        '''получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.'''
        with self.conn:
            self.cur.execute(f"SELECT vacancy_id, name, employer_id, employer_name, url, salary FROM vacancies "
                             f"JOIN {self.__employers_table_name} USING(employer_id)"
                             f"ORDER BY salary DESC;")
            data = self.cur.fetchall()
            vacancies = [Vacancy(*d) for d in data]
            return vacancies

    def get_avg_salary(self) -> float:
        "получает среднюю зарплату по вакансиям"
        with self.conn:
            self.cur.execute(f"SELECT AVG(salary) FROM vacancies")
            data = self.cur.fetchone()[0]
            return round(data) if data is not None else 0

    def get_vacancies_with_higher_salary(self) -> List[Vacancy]:
        '''получает список всех вакансий, у которых зарплата выше средней по всем вакансиям'''
        with self.conn:
            self.cur.execute(f"SELECT vacancy_id, name, employer_id, employer_name, url, salary "
                             f"FROM vacancies JOIN {self.__employers_table_name} USING(employer_id) "
                             f"WHERE salary > (SELECT AVG(salary) FROM vacancies) "
                             f"ORDER BY salary DESC;")
            data = self.cur.fetchall()
            vacancies = [Vacancy(*d) for d in data]
            return vacancies

    def get_vacancies_with_keyword(self, keyword: str) -> List[Vacancy]:
        '''получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python'''
        with self.conn:
            self.cur.execute(f"SELECT vacancy_id, name, employer_id, employer_name, url, salary from vacancies "
                             f"JOIN {self.__employers_table_name} USING(employer_id) "
                             f"WHERE LOWER(name) LIKE '%' || LOWER('{keyword}') || '%'"
                             f"ORDER BY salary DESC;")
            data = self.cur.fetchall()
            vacancies = [Vacancy(*d) for d in data]
            return vacancies

    def save_companies(self, companies: List[dict]):
        '''Сохраняет список компаний в базу данных'''
        with self.conn:
            for c in companies:
                self.cur.execute(f"INSERT INTO {self.__employers_table_name} (employer_id, employer_name) "
                                 f"VALUES (%s, %s)  "
                                 f"ON CONFLICT (employer_id) DO UPDATE SET employer_name = EXCLUDED.employer_name",
                                 (list(c.keys())[0], list(c.values())[0]))

    def save_vacancies(self, vacancies: List[Vacancy]):
        '''Сохраняет список вакансий в базу данных'''
        with self.conn:
            for v in vacancies:
                self.cur.execute(f"INSERT INTO vacancies (vacancy_id, name, employer_id, url, salary) "
                                 f"VALUES (%s, %s, %s, %s, %s)  "
                                 f"ON CONFLICT (vacancy_id) DO UPDATE SET (name, employer_id, url, salary) = "
                                 f"(excluded.name, excluded.employer_id, excluded.url, excluded.salary)",
                                 (v.vacancy_id, v.name, v.employer_id, v.url, v.salary))
