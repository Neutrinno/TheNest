# TheNest
## Содержание
- [Описание](#описание)
- [Установка](#установка)
- [Технологический стек](#технологии)
- [Лицензия](#лицензия)

## Описание

**TheNest** — это приложение для автоматизированного распределения студентов по местам в общежитиях, основанное на их рейтинге (баллах) и предпочтениях. Платформа упрощает процесс заселения, учитывая как академические достижения студентов, так и их личные пожелания по выбору общежитий и соседей.

### Основные функции TheNest:

1. **Регистрация студента**: 
   Каждый студент может создать личный кабинет на платформе для управления процессом заселения.

2. **Подача заявки**: 
   Студенты могут подать заявку на заселение, указав предпочтения по общежитию и потенциальным соседям.

3. **Отслеживание статуса заявки**: 
   Система позволяет в реальном времени отслеживать статус рассмотрения заявки.

4. **Управление заявкой**: 
   Возможна отмена или изменение поданной заявки в любое время до заселения.

5. **Информация о заселении**: 
   После успешного распределения студенты могут получить информацию о месте проживания и соседях.

## Установка

Пошаговая инструкция по установке всех необходимых компонентов для запуска проекта. Например:

1. Клонируйте репозиторий:

    ```bash
    https://github.com/Neutrinno/TheNest.git
    ```

2. Перейдите в директорию проекта:

    ```bash
    cd TheNest
    ```

3. Создайте виртуальное окружение (если необходимо) и активируйте его:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

4. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

## Технологический стек

В проекте используются следующие технологии:
- **Python** — основной язык программирования для разработки бэкенда.
- **FastAPI** — веб-фреймворк для создания серверной части приложения.
- **PostgreSQL** — реляционная база данных для хранения информации о студентах, их заявках и распределениях.
- **Jinja** — шаблонизатор для языка программирования Python.

   Основные библиотеки:
- **Alembic** — инструмент для управления миграциями базы данных в проектах с использованием SQLAlchemy. Позволяет отслеживать изменения в структуре базы данных и применять их последовательно.
- **SQLAlchemy** — популярная ORM (Object Relational Mapper) для Python, позволяющая взаимодействовать с реляционными базами данных через объектно-ориентированный подход.
- **Pydantic** — библиотека для валидации данных и сериализации на основе аннотаций типов Python. Используется в FastAPI для валидации входных данных и работы с моделями.
- **FastAPI Users** — готовое решение для управления пользователями в FastAPI, предоставляющее функционал регистрации, аутентификации и авторизации пользователей.
