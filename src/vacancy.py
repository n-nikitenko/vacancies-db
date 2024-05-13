from typing import List


class Vacancy:
    """Класс для работы с вакансиями."""

    __v_id: str
    __name: str
    __salary: int
    __employer_id: str
    __employer_name: str
    __url: str

    def __init__(self, v_id: str, name: str, employer_id: str, employer_name: str, url: str, salary: int = None, ):
        self.__v_id = v_id
        self.__name = name
        self.__salary = 0 if salary is None else salary
        self.__employer_id = employer_id
        self.__employer_name = employer_name
        self.__url = url

    def __str__(self):
        salary_str = 'зарплата не указана' if self.__salary == 0 else f'зарплата от {self.__salary} руб.'
        employer_str = f', работодатель: {self.__employer_name}'
        url_str = f', ссылка на вакансию: {self.__url}'
        return f"Вакансия: '{self.__name}', {salary_str}{employer_str}{url_str}.\n"

    @property
    def salary(self):
        return self.__salary

    @property
    def name(self):
        return self.__name

    @property
    def vacancy_id(self):
        return self.__v_id

    @property
    def employer_id(self):
        return self.__employer_id

    @property
    def employer_name(self):
        return self.__employer_name

    @property
    def url(self):
        return self.__url

    @classmethod
    def cast_to_object_list(cls, v_json_list: List[dict]) -> List['Vacancy']:
        """преобразует список словарей, содержащих данные о вакансии, полученных с сервера в список объектов вакансий"""

        vacancies: List['Vacancy'] = []
        for v in v_json_list:
            v_id = v.get('id', '')
            name = v.get('name', '')

            salary_obj = v.get('salary')
            salary = salary_obj['from'] if salary_obj is not None else 0

            url = v.get('url')

            employer_obj = v.get('employer')
            employer_name = employer_obj['name']
            employer_id = employer_obj['id']

            vacancies.append(cls(v_id, name, employer_id, employer_name, url, salary))
        return vacancies
