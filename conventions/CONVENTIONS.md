# Соглашения по написанию кода

## TL;DR

**Стиль:**
- `match\case` для работы со слабоструктурированными данными
- `str | None`, `list[int]` — современный синтаксис type hints (PEP 604)
- Не используйте `from __future__ import annotations` (Python 3.13+)
- Type hints обязательны для публичных API
- Говорящие имена переменных и функций
- Аббревиатуры: `HTTPClient` в классах, `http_client` в переменных/функциях
- Именованные константы вместо magic numbers
- Comprehensions для простых преобразований, явные циклы для сложных
- NamedTuple для функций с несколькими возвращаемыми значениями
- f-strings для форматирования
- Избегайте рефлексии (`getattr`, `hasattr`) — используйте явные схемы

**Структура:**
- Pydantic модели для валидации объявляются в `models`
- `StrEnum` для строковых констант
- Кастомные исключения в `errors.py`
- Структурное логирование через `logger`

**Ошибки:**
- Ловите конкретные исключения, не `except Exception`
- Никогда не используйте bare `except:`

**Чистота:**
- Комментарии объясняют «почему», не «что»
- `pathlib.Path` вместо `os.path`

---

## Подробные объяснения

Основано на книге "Python — К вершинам мастерства" (Luciano Ramalho). Ниже — практические рекомендации для опытных разработчиков с пояснениями и контекстом применения.

### Содержание

- [Стиль](#стиль-1)
  - [1. Match case для работы со слабоструктурированными данными](#1-match-case-для-работы-со-слабоструктурированными-данными)
  - [2. Современные type hints](#2-современные-type-hints)
  - [3. Не используйте from future import annotations](#3-не-используйте-from-future-import-annotations)
  - [4. Type hints обязательны](#4-type-hints-обязательны)
  - [5. Говорящие имена](#5-говорящие-имена)
  - [6. Аббревиатуры и числа в именах](#6-аббревиатуры-и-числа-в-именах)
  - [7. Нет magic numbers](#7-нет-magic-numbers)
  - [8. Comprehensions](#8-comprehensions)
  - [9. Деструктуризация](#9-деструктуризация)
  - [10. NamedTuple для множественных возвратов](#10-namedtuple-для-множественных-возвратов)
  - [11. f-strings для форматирования](#11-f-strings-для-форматирования)
  - [12. Минимум рефлексии](#12-минимум-рефлексии)
- [Структура](#структура-1)
  - [13. Pydantic модели](#13-pydantic-модели)
  - [14. Enum'ы](#14-enumы)
  - [15. Кастомные ошибки](#15-кастомные-ошибки)
  - [16. Logger](#16-logger)
- [Ошибки](#ошибки-1)
  - [17. Конкретные исключения](#17-конкретные-исключения)
  - [18. Избегайте bare except](#18-избегайте-bare-except)
- [Чистота](#чистота-1)
  - [19. Осмысленные комментарии](#19-осмысленные-комментарии)
  - [20. pathlib для путей](#20-pathlib-для-путей)

---

### Стиль

#### 1. Match case для работы со слабоструктурированными данными

Pattern matching (Python 3.10+) — мощный инструмент для диспетчеризации по типам и структурному сопоставлению данных. Также эффективен при работе с классами: можно одновременно проверить тип и деструктурировать атрибуты. Применяйте его вместо цепочек `isinstance`, когда нужно ветвление по типам или извлечение данных из объектов.

В отдельных случаях, когда условие очень простое, `isinstance` может быть использован.

Антипаттерн (базовые типы):
```python
def process_data(data):
    if isinstance(data, dict):
        return data.get("value", 0)
    elif isinstance(data, list):
        return len(data)
    elif isinstance(data, str):
        return data.upper()
    else:
        return None
```

Рекомендуется:
```python
def process_data(data):
    match data:
        case dict(value=v):
            return v
        case list() as lst:
            return len(lst)
        case str() as s:
            return s.upper()
        case _:
            return None
```

Антипаттерн (с классами):
```python
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    status: str
    data: dict


class ErrorResponse(BaseModel):
    status: str
    error: str
    code: int


def handle_response(response):
    if isinstance(response, SuccessResponse):
        status = response.status
        data = response.data
        return f"Success: {data}"
    elif isinstance(response, ErrorResponse):
        error = response.error
        code = response.code
        return f"Error {code}: {error}"
    else:
        return "Unknown response"
```

Рекомендуется (match на классах с деструктуризацией):
```python
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.enums import Status


def handle_response(response):
    match response:
        case SuccessResponse(status=Status.OK, data=data):
            return f"Success: {data}"
        case ErrorResponse(error=error, code=code) if code >= HTTP_500_INTERNAL_SERVER_ERROR:
            # Guard для дополнительных условий
            return f"Server error {code}: {error}"
        case ErrorResponse(error=error, code=code):
            return f"Client error {code}: {error}"
        case _:
            return "Unknown response"
```

Преимущества match case с классами:
- Одновременная проверка типа и деструктуризация атрибутов
- Поддержка guards (дополнительные условия через `if`)
- Явная структура диспетчеризации — легче читать и поддерживать
- Работает с dataclasses, Pydantic, обычными классами

#### 2. Современные type hints

Используйте синтаксис PEP 604 для объединений (`str | None`) и встроенные обобщённые коллекции (`list[str]`, `dict[str, int]`). Для параметров функций предпочтительнее абстракции `typing` (`Sequence[str]`, `Mapping[str, int]`), чтобы не привязывать контракт к конкретной реализации.

Антипаттерн:
```python
from typing import List, Dict, Optional, Union


def process_items(items: List[str], cache: Dict[str, int]) -> Optional[str]:
    result: Union[str, int] = items[0] if items else 0
    return str(result) if isinstance(result, str) else None
```

Рекомендуется:
```python
from typing import Sequence, Mapping


def process_items(items: Sequence[str], cache: Mapping[str, int]) -> str | None:
    first: str | None = next(iter(items), None)
    return first
```

#### 3. Не используйте from future import annotations

В Python 3.13+ отложенная оценка аннотаций реализована нативно (PEP 649), поэтому импорт `from __future__ import annotations` больше не нужен и не должен использоваться. В более ранних версиях (3.7-3.12) этот импорт был полезен для разрешения forward references и циклических зависимостей типов, но в 3.13+ это поведение встроено по умолчанию.

Антипаттерн:
```python
from __future__ import annotations

from typing import Sequence


class Node:
    def __init__(self, value: int, children: list[Node] | None = None):
        self.value = value
        self.children = children or []
```

Рекомендуется (Python 3.13+):
```python
from typing import Sequence


class Node:
    def __init__(self, value: int, children: list[Node] | None = None):
        self.value = value
        self.children = children or []
```

Причины отказа от `from __future__ import annotations`:
- В Python 3.13+ это избыточно — нативная поддержка работает лучше
- Упрощается код — меньше импортов
- Соответствие современным стандартам Python

#### 4. Type hints обязательны

Аннотации обязательны для публичных API: они документируют контракт и помогают статическому анализатору ловить несоответствия на границах модулей. Внутренние функции аннотируйте по мере необходимости.

Антипаттерн:
```python
class UserService:
    def get_user(self, user_id):
        return self.db.query(user_id)

    def create_user(self, data):
        return self.db.insert(data)
```

Рекомендуется:
```python
from app.models.user import User, UserCreate


class UserService:
    def get_user(self, user_id: int) -> User | None:
        return self.db.query(user_id)

    def create_user(self, data: UserCreate) -> User:
        return self.db.insert(data)
```

#### 5. Говорящие имена

Имена должны передавать семантику, а не форму. Лишние символы в имени дешевле времени чтения и неверных интерпретаций.

Антипаттерн:
```python
def calc(x, y, z):
    r = []
    for i in x:
        if i > y and i < z:
            r.append(i)
    return r
```

Рекомендуется:
```python
def filter_in_range(
    numbers: list[float],
    min_value: float,
    max_value: float
) -> list[float]:
    filtered_numbers = []

    for number in numbers:
        if min_value < number < max_value:
            filtered_numbers.append(number)

    return filtered_numbers
```

Вариант (comprehension):
```python
def filter_in_range(
    numbers: list[float],
    min_value: float,
    max_value: float
) -> list[float]:
    return [num for num in numbers if min_value < num < max_value]
```

#### 6. Аббревиатуры и числа в именах

Единообразное оформление аббревиатур и чисел в именах улучшает читаемость и соответствие PEP 8.

**Аббревиатуры в CamelCase:**
- Используйте все заглавные буквы для всей аббревиатуры

```python
# Рекомендуется
class HTTPClient:
    pass

class APIHandler:
    pass

class XMLParser:
    pass

# Антипаттерн
class HttpClient:  # смешанный регистр
    pass
```

**Аббревиатуры в snake_case:**
- Используйте только строчные буквы

```python
# Рекомендуется
http_address = "localhost"
api_key = "secret"
xml_content = "<root/>"

# Антипаттерн
HTTP_address = "localhost"  # не константа, не должно быть заглавных
Api_Key = "secret"  # не CamelCase
```

**Числа в именах:**
- Не используйте лишнее подчеркивание перед числом

```python
# Рекомендуется
http2_protocol = "HTTP/2"
base64_encoder = encoder
ipv6_address = "::1"

# Антипаттерн
http_2_protocol = "HTTP/2"  # лишнее подчеркивание
base_64_encoder = encoder
ipv_6_address = "::1"
```

#### 7. Нет magic numbers

Именуйте пороги, коэффициенты и таймауты. Это фиксирует доменную семантику и снижает риск регрессий.

Антипаттерн:
```python
def calculate_price(base_price: float) -> float:
    if base_price > 1000:
        return base_price * 0.85
    return base_price * 1.1
```

Рекомендуется:
```python
PREMIUM_DISCOUNT_THRESHOLD = 1000
PREMIUM_DISCOUNT_RATE = 0.85
STANDARD_TAX_RATE = 1.1


def calculate_price(base_price: float) -> float:
    if base_price > PREMIUM_DISCOUNT_THRESHOLD:
        return base_price * PREMIUM_DISCOUNT_RATE
    return base_price * STANDARD_TAX_RATE
```

#### 8. Comprehensions

Comprehensions уместны для простых преобразований. Если вложенность > 2 уровней или несколько ветвлений — используйте явные циклы/функции.

Рекомендуется:
```python
# Простое преобразование
user_ids = [user.id for user in users]

# С условием
active_users = [user for user in users if user.is_active]

# Dict comprehension
user_map = {user.id: user.name for user in users}

# Flatten с двумя уровнями
all_tags = [tag for place in places for tag in place.tags]
```

Антипаттерн:
```python
# Чрезмерная вложенность — используйте функцию
result = [
    item.value
    for group in groups
    for subgroup in group.items
    for item in subgroup.data
    if item.is_valid
]

# Сложная логика — используйте явный цикл
filtered = [
    process_item(item) if item.type == "A" else transform_item(item)
    for item in items
    if validate(item) and check_permission(item)
]
```

#### 9. Деструктуризация

Распаковка повышает выразительность и уменьшает обращения по индексам/ключам. Используйте `match` для декларативного извлечения.

Антипаттерн:
```python
point = (3, 5)
x = point[0]
y = point[1]

config = {"host": "localhost", "port": 8080}
host = config["host"]
port = config["port"]
```

Рекомендуется:
```python
x, y = point
host, port = config["host"], config["port"]

# Или с pattern matching
match config:
    case {"host": host, "port": port}:
        print(f"Connecting to {host}:{port}")
```

#### 10. NamedTuple для множественных возвратов

Когда функция возвращает несколько значений, используйте `NamedTuple` вместо обычного кортежа. Это делает код самодокументируемым и позволяет обращаться к элементам по имени, а не по индексу.

Антипаттерн:
```python
def get_user_stats(user_id: int) -> tuple[int, float, bool]:
    posts_count = get_posts_count(user_id)
    average_rating = calculate_rating(user_id)
    is_verified = check_verification(user_id)
    return posts_count, average_rating, is_verified

# Вызов — непонятно, что означает каждое значение
count, rating, verified = get_user_stats(123)
# Или хуже — обращение по индексу
stats = get_user_stats(123)
if stats[2]:  # Что такое stats[2]?
    print(f"User has {stats[0]} posts")
```

Рекомендуется:
```python
from typing import NamedTuple


class UserStats(NamedTuple):
    posts_count: int
    average_rating: float
    is_verified: bool


def get_user_stats(user_id: int) -> UserStats:
    posts_count = get_posts_count(user_id)
    average_rating = calculate_rating(user_id)
    is_verified = check_verification(user_id)
    return UserStats(
        posts_count=posts_count,
        average_rating=average_rating,
        is_verified=is_verified
    )

# Вызов — явно и понятно
stats = get_user_stats(123)
if stats.is_verified:
    print(f"User has {stats.posts_count} posts")

# Или с деструктуризацией
stats = get_user_stats(123)
match stats:
    case UserStats(is_verified=True, posts_count=count):
        print(f"Verified user has {count} posts")
```

Преимущества NamedTuple:
- Самодокументирование кода — сразу видно, что возвращается
- Доступ по имени вместо индексов — меньше ошибок
- Поддержка деструктуризации и pattern matching
- Неизменяемость (immutable) — безопасность

#### 11. f-strings для форматирования

f-strings быстрее и безопаснее альтернатив. Используйте спецификаторы формата и отладочный синтаксис `name=` (3.8+).

Антипаттерн:
```python
name = "Alice"
age = 30
message = "User %s is %d years old" % (name, age)
message2 = "User {} is {} years old".format(name, age)
message3 = "User {name} is {age} years old".format(name=name, age=age)
```

Рекомендуется:
```python
message = f"User {name} is {age} years old"

# Форматирование чисел
price = 49.99
formatted = f"Price: ${price:.2f}"

# Выравнивание
for i, item in enumerate(items):
    print(f"{i:3d}: {item:>20s}")

# Отладочный вывод
value = 42
print(f"{value=}")  # value=42
```

#### 12. Минимум рефлексии

Избегайте динамического доступа к атрибутам/ключам, когда возможна явная схема. Это улучшает проверяемость и автодополнение.

Антипаттерн:
```python
class ConfigParser:
    def get_value(self, obj, path: str):
        parts = path.split(".")
        result = obj
        for part in parts:
            if hasattr(result, part):
                result = getattr(result, part)
            else:
                return None
        return result
```

Рекомендуется (Pydantic):
```python
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    host: str
    port: int
    username: str


class Config(BaseModel):
    database: DatabaseConfig
    debug: bool = False


# Теперь доступ типобезопасный
config = Config(database={"host": "localhost", "port": 5432, "username": "admin"})
print(config.database.host)
```

### Структура

#### 13. Pydantic модели

Все модели объявляются внутри модуля `models`.

Модели описывают контракт на границе слоёв. Валидация — на входе/выходе сервисов. Используйте `ConfigDict`.

```python
# app/models/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    is_active: bool = True
```

#### 14. Enum'ы

Используйте `StrEnum` для значений, сериализуемых в JSON/БД. Явно задавайте строки, не полагайтесь на `auto()`.

```python
# app/enums.py
from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Использование
user_role = UserRole.ADMIN
assert user_role == "admin"
```

#### 15. Кастомные ошибки

Определяйте специфичные исключения в `errors.py`.

```python
# app/errors.py
class BaseAPIError(Exception):
    """Базовый класс для всех ошибок API"""
    def __init__(self, message: str, code: ErrorCode):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(BaseAPIError):
    """Ресурс не найден"""
    def __init__(self, resource: str, resource_id: str | int):
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            code=ErrorCode.NOT_FOUND
        )


class ValidationError(BaseAPIError):
    """Ошибка валидации данных"""
    def __init__(self, field: str, value: str, reason: str):
        super().__init__(
            message=f"Invalid value '{value}' for field '{field}': {reason}",
            code=ErrorCode.ValidationError
        )
```

#### 16. Logger

Логируйте события с контекстом (структурно), чтобы упрощать агрегацию и трассировку. Не форматируйте строки вручную — используйте контекст логгера.

```python
from app.logger import logger

logger.debug(...)
```

### Ошибки

#### 17. Конкретные исключения

Ловите только те исключения, которые можете корректно обработать. Не замалчивайте ошибки.

Антипаттерн:
```python
try:
    result = int(user_input)
    data = load_json_file(f"data_{result}.json")
except Exception:
    return None
```

Рекомендуется:
```python
try:
    result = int(user_input)
except ValueError:
    raise ValidationError("user_input", user_input, "must be a valid integer")

try:
    data = load_json_file(f"data_{result}.json")
except FileNotFoundError:
    logger.warning(f"Data file for {result} not found, using defaults")
    data = get_default_data()
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in data_{result}.json: {e}")
    raise DataCorruptionError(f"data_{result}.json")
```

#### 18. Избегайте bare except

Голый `except:` перехватывает системные исключения (например, `KeyboardInterrupt`) и затрудняет остановку/диагностику.

Антипаттерн:
```python
try:
    process_data()
except:
    pass
```

Если действительно нужно поймать всё прикладное:
```python
try:
    process_data()
except Exception as e:  # не ловит системные исключения
    logger.error(f"Unexpected error: {e}", exc_info=True)
```

Предпочтительно — конкретные исключения:
```python
try:
    process_data()
except (ValueError, TypeError) as e:
    logger.error(f"Data processing error: {e}")
    return default_result
```

### Чистота

#### 19. Осмысленные комментарии

Комментируйте намерения, инварианты, компромиссы и нестандартные решения. Не дублируйте очевидное поведение кода.

Антипаттерн:
```python
# Увеличиваем счётчик на 1
counter += 1

# Проверяем, больше ли x чем y
if x > y:
    # Возвращаем x
    return x
```

Рекомендуется:
```python
# Пропускаем заголовок при подсчёте строк данных
counter += 1

# Используем экспоненциальный backoff для избежания
# перегрузки внешнего API при массовых ошибках
delay = min(2 ** retry_count, MAX_RETRY_DELAY)

# ВАЖНО: не используем стандартный json.loads, т.к.
# API возвращает числа как строки для сохранения точности
data = parse_json_with_decimal(response.text)
```

#### 20. pathlib для путей

`pathlib` даёт переносимость, удобные операции и явные типы. Используйте вместо `os.path` и ручных строковых манипуляций.

Антипаттерн:
```python
import os

config_path = os.path.join(os.path.dirname(__file__), "..", "config", "app.yaml")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = yaml.load(f)
```

Рекомендуется:
```python
from pathlib import Path

config_path = Path(__file__).parent.parent / "config" / "app.yaml"
if config_path.exists():
    config = yaml.safe_load(config_path.read_text())

# Другие полезные методы
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Поиск файлов
for json_file in data_dir.glob("*.json"):
    process_file(json_file)

# Работа с расширениями
file_path = Path("document.txt")
new_path = file_path.with_suffix(".md")
```