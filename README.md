# Инструкция по установке


### 1) Установить локальное окружение
```shell
$ python3 -m venv venv
$ source venv/Scripts/activate # Для Windows: venv/bin/activate
```

### 2) Установить зависимости
```shell
$ pip install -r requirements.txt
```

### 3) Укажите свой API token в Telegram
echo "<Ваш API token>" >> http_api.txt

### 4) Запуск
```shell
$ nohup python3 main.py &
```