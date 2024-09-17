## Документация
Это приложение для парсинга повторов ```.dem``` из CS2.
Программа предназначена для извлечения данных и их записи в excel-файл и/или в Базу Данных, чтобы автоматизировать вывод графики в прямой эфир через приложение VMix.

Данные из повтора записываются в excel-файл  в определенном порядке и на определенную страницу. Эти данные автоматически подтягиваются в приложение VMix через заранее прописанные формулы. Формулы следует записывать на любой странице excel-файла, за исключением листа ```CS2```, который будет каждый раз обновляться.  

Так же у приложения есть возможность добавлять статистику в Базу Данных для того, чтобы результат матча можно было вывести позже.

Перед началом работы приложения в файле ```ConnectToDataBase``` обновите данные для подключения к своей базе банных в функции ```connect_to_database```.
```
mydb = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="user",
                password="password"
                )
```         

```
mydb = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="user",
                password="password",
                database=self.database_name
                )
```

Для успешного вывода данных в эфир, убедитесь, что в папке, где лежит приложение, создан excel-файл ```CS2 stats for stream.xlsx```. Откройте файл, убедитесь, что лист, на котором вы работаете не называется ```CS2```. Пропишите на листе формулы для связывания ячеек таблицы с VMix Data Source.
Если в папке нет файла, он будет создан программой автоматически, но без формул. Если  Вы хотите просто вывести данные в excel-файл, без отправки в эфир, достаточно не создавать файл заранее, приложение сгенерирует результат автоматически.

1. Чтобы начать работу с приложением, запустите файл ```GUI.py```
2. Заполните поле ```'Путь к файлу или название'```. В случае, если данные должны быть занесены или извлечены из Базу Данных, заполните так же поле ```'Дата'``` - вместе с названием оно будет нужно для создания id записи, так как одни и те же команды могут встретиться на турнире несколько раз и сыграть на одних и тех же картах. Чтобы избежать путаницы следует указывать дату и время матча.
Пример названия файла: ```mouz-vs-g2-m1-inferno.dem```. Скачать ```.dem``` файл можно здесь: https://www.hltv.org/matches/2370724/mouz-vs-g2-pgl-cs2-major-copenhagen-2024
3. Выберите, будет ли запись внесена в базу данных или извлечена по названию и дате. Если это не требутся и статистика должна быть выведена на трансляцию без сохранения в Базу Данных, выберите ```Ничего не делать```
4. Выберите, хотите ли вы вывести графику в эфир. Если да, установите галочку у поля ```В эфир```
5. Нажмите ```Ввод```