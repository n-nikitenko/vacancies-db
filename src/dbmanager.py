import psycopg2
from typing import List

from colorama import Fore, Style
from psycopg2 import OperationalError, sql

from src.vacancy import Vacancy


class DBManager:

    def __init__(self, params: dict):
        self.__vacancies_table_name = 'vacancies'
        self.__employers_table_name = 'employers'
        self._connect_to_database(params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn is not None:
            self.conn.close()

    def _connect_to_database(self, params: dict):
        """Подключение к базе данных и создание (в случае их отсутствия)
        таблиц для сохранения данных о компаниях и вакансиях"""

        try:
            self.conn = psycopg2.connect(**params)
            self.cur = self.conn.cursor()
            self._create_tables()
        except OperationalError as e:
            self.conn = None
            print(f"{Fore.RED}Ошибка подключения к базе данных {params['dbname']}:\n", e)
            print(Style.RESET_ALL)
            exit()

    def _create_tables(self):
        with self.conn:
            self.cur.execute(sql.SQL("""
                        CREATE TABLE IF NOT EXISTS {employers} (
                        employer_id VARCHAR(255) PRIMARY KEY,
                        employer_name VARCHAR(255) NOT NULL
                        );
                        """).format(employers=sql.Identifier(self.__employers_table_name)))
            self.conn.commit()
            self.cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {vacancies} (
            vacancy_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            employer_id VARCHAR(255) REFERENCES {employers}(employer_id),
            url VARCHAR(255) NOT NULL,
            salary INT DEFAULT 0
            );
            """).format(vacancies=sql.Identifier(self.__vacancies_table_name),
                        employers=sql.Identifier(self.__employers_table_name)))

    def get_companies_and_vacancies_count(self) -> List[dict]:
        """получает список всех компаний и количество вакансий у каждой компании"""

        with self.conn:
            self.cur.execute(sql.SQL("SELECT employer_name, COUNT(vacancy_id) from {vacancies} "
                                     "JOIN {employers} "
                                     "USING(employer_id) "
                                     "GROUP BY employer_name "
                                     "ORDER BY COUNT(vacancy_id) DESC").format(
                vacancies=sql.Identifier(self.__vacancies_table_name),
                employers=sql.Identifier(self.__employers_table_name)))
            data = self.cur.fetchall()
            vacancies = [{'company_name': d[0], 'count': d[1]} for d in data]
            return vacancies

    def get_all_vacancies(self) -> List[Vacancy]:
        """получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""

        with self.conn:
            self.cur.execute(sql.SQL("SELECT vacancy_id, name, employer_id, employer_name, url, salary FROM {vacancies}"
                                     "JOIN {employers} USING(employer_id)"
                                     "ORDER BY salary DESC;").format(
                vacancies=sql.Identifier(self.__vacancies_table_name),
                employers=sql.Identifier(self.__employers_table_name)))
            data = self.cur.fetchall()
            vacancies = [Vacancy(*d) for d in data]
            return vacancies

    def get_avg_salary(self) -> float:
        """получает среднюю зарплату по вакансиям"""

        with self.conn:
            self.cur.execute(sql.SQL("SELECT AVG(salary) FROM {vacancies}").format(
                vacancies=sql.Identifier(self.__vacancies_table_name)))
            data = self.cur.fetchone()[0]
            return round(data) if data is not None else 0

    def get_vacancies_with_higher_salary(self) -> List[Vacancy]:
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""

        with self.conn:
            self.cur.execute(sql.SQL("SELECT vacancy_id, name, employer_id, employer_name, url, salary "
                                     "FROM {vacancies} JOIN {employers} USING(employer_id) "
                                     "WHERE salary > (SELECT AVG(salary) FROM {vacancies}) "
                                     "ORDER BY salary DESC;").format(
                vacancies=sql.Identifier(self.__vacancies_table_name),
                employers=sql.Identifier(self.__employers_table_name)))
            data = self.cur.fetchall()
            vacancies = [Vacancy(*d) for d in data]
            return vacancies

    def get_vacancies_with_keyword(self, keyword: str) -> List[Vacancy]:
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python"""

        with self.conn:
            self.cur.execute(
                sql.SQL("SELECT vacancy_id, name, employer_id, employer_name, url, salary from {vacancies} "
                        "JOIN {employers} USING(employer_id) "
                        "WHERE LOWER(name) LIKE '%%' || LOWER(%s) || '%%'"
                        "ORDER BY salary DESC;").format(
                    vacancies=sql.Identifier(self.__vacancies_table_name),
                    employers=sql.Identifier(self.__employers_table_name)), (keyword,))
            data = self.cur.fetchall()
            vacancies = [Vacancy(*d) for d in data]
            return vacancies

    def save_companies(self, companies: List[dict]):
        """Сохраняет список компаний в базу данных"""

        with self.conn:
            for c in companies:
                self.cur.execute(sql.SQL("INSERT INTO {employers} (employer_id, employer_name) "
                                         "VALUES (%s, %s)  "
                                         "ON CONFLICT (employer_id) "
                                         "DO UPDATE SET employer_name = EXCLUDED.employer_name;").format(
                    employers=sql.Identifier(self.__employers_table_name)), (list(c.keys())[0], list(c.values())[0]))

    def save_vacancies(self, vacancies: List[Vacancy]):
        """Сохраняет список вакансий в базу данных"""

        with self.conn:
            for v in vacancies:
                query = sql.SQL("INSERT INTO {vacancies} (vacancy_id, name, employer_id, url, salary) "
                                "VALUES (%s, %s, %s, %s, %s)  "
                                "ON CONFLICT (vacancy_id) "
                                "DO UPDATE SET (name, employer_id, url, salary) = "
                                "(excluded.name, excluded.employer_id, excluded.url, excluded.salary);").format(
                    vacancies=sql.Identifier(self.__vacancies_table_name))

                self.cur.execute(query, (v.vacancy_id, v.name, v.employer_id, v.url, v.salary))
