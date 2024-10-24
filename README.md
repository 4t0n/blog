### Описание проекта:

Данное приложение позволяет пользователям:

* Регистрироваться на сайте
* Создавать посты с фотографиями
* Читать и комментировать посты других пользователей

Особенности:
* Админ может снимать посты и категории с публикаций
* Можно создавать посты, которые будут опубликованы в выбранное время

### Stack
* Python;
* Django;
* SQLite;

### Как запустить проект на локальном сервере:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/4t0n/blog.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
