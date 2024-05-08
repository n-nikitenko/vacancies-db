# vacancies-db

Цель проекта заключается в получении данных о десяти
 компаниях и их вакансиях с сайта hh.ru и сохранении этой информации в базу данных Postgres.

## Установка и использование

Для работы программы необходимо установить зависимости, указанные в файле  pyproject.toml:
- для первичной установки:

  ```poetry install```
- для обновления:

  ```poetry update```


Для работы с базой данных необходимо создать файл `.env` с параметрами доступа к базе данных PostgresSQL. Пример содержимого файла:

```
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432
POSTGRES_DB=postgres

```
