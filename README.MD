Мониторинг появления отзывов на товары в маркетплейсе  
(Analysis of feedback on products in a marketplace)
=
Проект по настройке регулярного сбора данных из внешнего источника c API в базу данных облачного провайдера. Визуализация данных в [Yandex DataLens](https://cloud.yandex.ru/ru/services/datalens).  
`Yandex Cloud`, `Airflow`, `PostgreSQL`, `Yandex DataLens`

Мониторинг появления отзывов на товары из маркейтплейса - демонстрация дашборда.
## Архитектура проекта 
![архитектура проекта](https://github.com/bubussh/DE-API-PRODUCT/assets/93825972/ef54680f-1eb9-4cc8-8dbf-97a53c32dd7e)  
DAG *"dag_product_project"* отвечает за ежедневное получение данных из системы источника и запись этих данных в таблицу count_feedbacks.  Поля таблицы:
* date  - дата (logical date of dag run);
* id - артикул товара;
* salepriceu - цена;
* feedbacks - количество отзывов.  

DAG *"dag_dynamic_calculations"* отвечает за ежедневное вычисление количества новых отзывов по каждому артикулу.
Поля таблицы:
* date  - дата; 
* id - артикул товара;
* new_feedbacks - количество новых отзывов.

Для визуализации данных в Yandex DataLens используется sql-запрос, который получает данные из таблицы dynamic_feedbacks за последние 7 дней по 3 артикула, у которых за последние 7 дней отзывов больше всего.  
`СКОПИРОВАТЬ SQL-ЗАПРОС из Yandex DataLens в отдельный файл и приложить к проекту.
`

## Используемые технологии и продукты
- [Airflow](https://airflow.apache.org/) - регулярный сбор данных с API внешнего источника, обработка и загрузка данных в БД.
- [Yandex Managed Service for PostgreSQL](https://cloud.yandex.ru/ru/services/managed-postgresql) - СУБД для хранения и обработки данных.
- [Yandex DataLens](https://cloud.yandex.ru/ru/services/datalens) - Облачный сервис для визуалиции данных и бизнес-аналитики.

## Проект
### Настройка проекта
Для работы проекта необходимы:
* Экземпляр СУБД PostgreSQL в Yandex Cloud для хранения данных.  
    1. Для подключению к кластеру из интернета необходимо включить опцию **Публичный доступ**:  
*Хосты -> Редактировать хост -> Публичный доступ*  
    2. Включить опцию **Доступ из DataLens**.
* Apache Airflow Setup:
    1. Создаем виртуальное окружение  
        `venv`
    2. Задаем переменную окружения AIRFLOW_HOME - путь, где будут лежать все конфигурационные файлы.  
        `export AIRFLOW_HOME=~/airflow`
    3. Устанавливаем Airflow с constraints file (в проекте Python 3.11 и Airflow 2.8.3)  
        `pip install 'apache-airflow==2.8.3' --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.3/constraints-3.11.txt"`
    4. Инициализируем базу данных Airflow (по умолчанию используется SQLite).  
        `airflow migrate`
    5. В проекте в качестве бэкенда для хранения метаданных Airflow используется PostgreSQL. Создаем базу данных и пользователя c помощью консольной утилиты *psql* (локально). 
        ```sql
        CREATE DATABASE airflow_db;  
        CREATE USER airflow_user WITH PASSWORD 'password';
        GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;
        -- PostgreSQL 15 requires additional privileges:
        \c airflow_db;
        GRANT ALL ON SCHEMA public TO airflow_user;
        ```
    6. Изменить значения параметров в конфигурационном файле AIRFLOW_HOME/airflow.cfg 
        ```
        sql_alchemy_conn = postgresql+psycopg2://<user>:<password>@<host>/<db>
        load_examples = False
        load_default_connections = False
        executor = LocalExecutor
        ```
    7. Для использования подзапроса SQL в качестве источника в Yandex DataLens необходимо включить опцию *Уровень доступа SQL запросов -> Разрешить подзапросы в датасетах при создании и редактировании* при создании и редактировании подключения.
## Визуализация данных в DataLens
