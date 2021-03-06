Финальное ДЗ представляет собой сервис по индексации страниц Интернет и поиску результатов. Оно является объединением наработок по предыдущим домашним заданиям.


Разрабатываемый сервис состоит из 3х микросервисов:
1. Точка входа в приложение – API
2. Микросервис авторизации, занимающийся авторизацией и валидацией пользователей
3. Краулер, занимающийся обкачкой сайтов


# Микросервис 1. API приложения.
В апи нужно реализовать следующие методы:

## Методы, которые не требуют авторизации:
1. POST /signup - метод регистрации нового пользователя. Принимает email, password, name. В случае успеха возвращает - 200 {“status”: “ok”, “data”: {“token”: “...”, “expire”: <timestamp>}}. Иначе - 4ХХ {“status”: “<текстовый код ошибки>”, “data”: {}}
2. POST /login - метод получения/обновления токена доступа. Принимает email, password. В случае успеха возвращает - 200 {“status”: “ok”, “data”: {“token”: “...”, “expire”: <timestamp>}}. Иначе - см. пункт 1
3. GET /search - метод поиска по обкаченным документам. Принимает q (запрос), limit (не может превышать 100), offset. Возвращает список документом с вхождением “q” - 200 {“status”: “ok”, “data”: [...]}. В случае некорректных параметров - 400 {“status”: “bad_request”, “data”: {}}


## Методы, которые требуют авторизации.
Для вызова этих методов необходимо добавить заголовок X-Token. Значение X-Token необходимо получить из метода /login. Если заголовок не передан - методы ниже должны возвращать ошибку 403 {“status”: “forbidden”, “data”: {}}
1. GET /current - метод, который возвращает текущего пользователя. Возвращает 200 {“status”: “ok”, “data”: {“id”: …, “email”:  …, “name”: …, “created_date”: …, “last_login_date”: …}}
2. POST /index - метод, который ставит задачу краулеру на индексацию домена. Принимает domain. Возвращает - 200 {“status”: “ok”, “data”: {“id”: … }}
3. GET /stat - метод, который возвращает статистику по сайтам пользователя. Возвращает - 200 {“status”: “ok”, “data”: [...]}

# Микросервис 2. Авторизация.
Взаимодействие с микросервисом авторизации должно происходить через брокер сообщений RabbitMQ. 

Необходимо предусмотреть 3 типа запросов-сообщений, которые обрабатывает микросервис:
1. Запрос на регистрацию нового пользователя (signup). В сообщении должны передаваться поля: email, password, name. В ответ должно возвратиться сообщение об успешной регистрации пользователя, иначе - ошибка и ее причина.
2. Запрос на получения токена доступа (login). В сообщении должны передаваться поля: email, password. В ответ должен возвратиться токен доступа и срок его жизни, иначе - ошибка и ее причина.
3. Запрос на проверку токена доступа (validate). В сообщении должен передаваться токен доступа. В ответ должны возвратиться все данные пользователя (из таблицы User), иначе ошибка.
Следует реализовать механизм протухания токена (поле expire_date). Для обновления протухшего токена необходимо повторно сделать запрос login.


# Микросервис 3. Краулер.
Необходимо доработать краулер из ДЗ №3 для работы с несколькими доменами.

Общая схемы работы краулера следующая:

Краулер работает непрерывно, ожидая задачи из брокера сообщений. Задача представляет собой указание краулеру начать обкачу указанного в задаче домена. Если данный сайт уже обкачивался раньше, чем T секунд назад, то задача помечается завершенной и обкачка не происходит. В противном случае начинается процедура обкачки и индексации сайта с заданной максимальной глубиной D.

Индексация, как в ДЗ №3 заключается в очистке скачанного html документа от html разметки и сохранением его в индекс Elasticsearch.

Необходимо учесть, что так как теперь краулер обкачивает не один домен необходимо иметь независимые “внутренние очереди” для каждого обкачиваемого домена, а также следить за RPS на каждый из доменов. Иными словами, нужно обязательно добиваться того, чтобы краулер не простаивал, если есть задачи которые можно выполнять.

Краулер должен по завершении или во время исполнения задачи писать статистику выполнения в БД (см. раздел БД ниже) согласно структуре. Можно добавить любую статистику по желанию. Именно эту статистику должен возвращать сервис API по запросу /stat.

Пример payload задачи на обкачку, которую может ожидать краулер из брокера сообщений:
```json
{
    "type": "index",
    "index": {
        "domain": "python.org",
        "https": true
    }
}
```

# Общение микросервисов

Взаимодействие между микросервисами должно происходить через брокер сообщений RabbitMQ. Над брокером необходимо реализовать интерфейс, аналогичный http запросам.

Рассмотрим на примере запроса validate, к микросервису авторизации: https://gist.github.com/alexopryshko/a0c1d4ad152d3fa5a0bc5ec3a3113805

У микросервиса авторизации должно быть 2 очереди: inbound - очередь входящих сообщений, outbound - очередь ответов. При создании запроса к микросервису, создается задача, ей присваивается уникальный id и она кладется в очередь inbound. Микросервис обрабатывает этот запрос и создает задачу с результатом в outbound очереди с id, равным id задачи из inbound очереди. В свою очередь клиент, который делал запрос к микросервису читает outbound очередь и получает результат по id задачи. Необходимо предусмотреть timeout запроса. В случае возникновения timeout make_request должен вернуть None.

Для реализации подобного механизма может быть использована asyncio.Future с ручным выставлением результата при получении ответа от микросервиса.

Также нужно реализовать интерфейс без ожидания ответа от микросервиса. Рассмотри на примере запроса к crawler: https://gist.github.com/alexopryshko/6ff8fe52f0649d0bd01da6b6fcfeba5e

# БД

В качестве базы данных для хранения пользователей и статистики краулера можно использовать любую современную SQL или NoSQL СУБД (MySQL, PostgreSQL, MongoDB, Redis, Tarantool, ...)

Для взаимодействия с выбранной базой данных необходимо реализовать асинхронную ORM (наподобие разработанной в ДЗ №1). 
Примерная структура БД:

Таблица User:
* id - int
* email - text
* password - text
* name text
* created_date - datetime
* last_login_date - datetime

Таблица Token:
* token - text
* user_id (fk to User) - int
* expire_date - datetime

Таблица CrawlerStats:
* domain - text
* author_id (fk to User) - int
* https - int (0/1)
* time - datetime
* pages_count - int
* avg_time_per_page - float
* max_time_per_page - float
* min_time_per_page - float


# Таблица оценивания
Оцениваемый компонент   | Баллы
----------------------- | -----
API приложения          | 10
Микросервис авторизации | 10
Web-crawler             | 10
Асинхронная ORM         | 10
