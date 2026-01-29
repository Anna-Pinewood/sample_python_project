# Python Project Template

Шаблон для Python-проектов с best practices для работы с AI-агентами (Claude Code, Cursor).

## Quick Start

```bash
# 1. Создай виртуальное окружение
uv venv --python 3.12 .venv
source .venv/bin/activate

# 2. Установи зависимости
uv pip install -e ".[dev]"

# 3. Установи pre-commit hooks
pre-commit install
```

## После клонирования

1. **Опиши свой проект** в `CLAUDE.md` — замени описание на своё
2. **Обнови** `docs/status.md` — текущее состояние проекта
3. **Создай** `.env` файл для секретов (см. `.env.example` если есть)
4. **Настрой** `conf/config.yaml` под свой проект

## Команды

```bash
make format   # Форматирование кода
make lint     # Проверка линтерами (ruff + mypy)
make test     # Запуск тестов
make check    # Полная проверка: lint + test
```

## Структура

```
├── CLAUDE.md              # Инструкции для AI-агентов
├── Makefile               # Команды разработки
├── pyproject.toml         # Конфигурация проекта и инструментов
├── .pre-commit-config.yaml
├── conf/                  # Конфигурация
│   └── config.yaml
├── src/                   # Исходный код
├── tests/                 # Тесты
├── docs/                  # Документация
│   └── status.md          # Статус проекта
└── conventions/           # Правила и конвенции
    ├── PROJECT_GUIDE.md   # Архитектура и практики
    └── CONVENTIONS.md     # Python-конвенции
```

## Документация

- [CLAUDE.md](./CLAUDE.md) — точка входа для AI
- [conventions/PROJECT_GUIDE.md](./conventions/PROJECT_GUIDE.md) — практики разработки
- [conventions/CONVENTIONS.md](./conventions/CONVENTIONS.md) — Python-конвенции
