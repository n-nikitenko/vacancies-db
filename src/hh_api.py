import copy
import json
from typing import List

import requests
from colorama import Fore, Style


class HeadHunterAPI:
    """
        Класс для работы с API HeadHunter
    """

    __base_url: str
    __headers: dict
    __params: dict
    __vacancies: list

    def __init__(self):
        self.__base_url = 'https://api.hh.ru/vacancies'
        self.__headers = {'User-Agent': 'HH-User-Agent'}
        self.__params = {'text': '', 'page': 0, 'per_page': 100}
        self.__vacancies = []

    def get_vacancies(self, employers: List[dict]) -> list:
        """получает список вакансий, опубликованных заданными компаниями (из списка employers)"""

        self.__vacancies.clear()
        self.__params['employer_id'] = list([list(e.keys())[0] for e in employers])
        self.__params['page'] = 0
        self.__params['currency'] = 'RUR'
        pages = 20
        while self.__params.get('page') < pages:
            try:
                response = requests.get(self.__base_url, headers=self.__headers, params=self.__params, timeout=1)
            except requests.exceptions.Timeout as e:
                print(f"{Fore.YELLOW}Истекло время ожидания ответа сервера. Попробуйте позже.")  # todo: уточнить
                # бизнес-логику
                print(Style.RESET_ALL)
                return copy.deepcopy(self.__vacancies)
            else:
                if response.status_code == 200:
                    response_json = response.json()
                    pages = response_json['pages']
                    vacancies = response_json['items']
                    self.__vacancies.extend(vacancies)
                    self.__params['page'] += 1
                else:  # todo: уточнить бизнес-логику
                    return copy.deepcopy(self.__vacancies)
        return copy.deepcopy(self.__vacancies)
