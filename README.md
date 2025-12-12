
# Autocalendar

Human-friendly event title parser for natural language input (Russian).

`autocalendar` converts short, informal event descriptions into a structured,
timezone-aware representation suitable for calendars, reminders, and planners.

---

## ✨ Features

- Natural language date & time parsing (RU)
- Explicit date formats: `DD.MM`
- Relative dates: `завтра`, `сегодня`, weekdays (`понедельник`)
- Time-only fallback: `15:30`
- Money extraction: `1200р`, `10€`, `$5`
- Timezone-aware datetimes (`zoneinfo`)
- Deterministic behavior
- Core logic fully covered by tests

---

## 🚀 Quick Start

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from autocalendar.parsing import parse_event_title

now = datetime(2025, 12, 12, 10, 0, tzinfo=ZoneInfo("Europe/Amsterdam"))

event = parse_event_title(
    "Кино 1200р завтра 20:00",
    now=now,
    tz=ZoneInfo("Europe/Amsterdam"),
)

print(event)
````

**Output:**

```text
ParsedEvent(
  raw='Кино 1200р завтра 20:00',
  title='Кино',
  dt=2025-12-13 20:00+01:00,
  d=2025-12-13,
  t=20:00,
  price=MoneyValue(amount=1200, currency='RUB'),
  leftovers=''
)
```

---

## 📦 API

### `parse_event_title`

```python
parse_event_title(
    text: str,
    *,
    now: datetime,
    tz: ZoneInfo,
    language: str = "ru",
) -> ParsedEvent
```

Parses a human-readable event title into a structured representation.

#### Parameters

* **`text`** — raw user input
* **`now`** — reference datetime (must be timezone-aware)
* **`tz`** — target timezone (`zoneinfo.ZoneInfo`)
* **`language`** — parsing language (`ru` supported)

#### Returns

`ParsedEvent`

---

### `ParsedEvent`

| Field       | Type                 | Description                    |
| ----------- | -------------------- | ------------------------------ |
| `raw`       | `str`                | Original input                 |
| `title`     | `str`                | Cleaned event title            |
| `dt`        | `datetime \| None`   | Full datetime (timezone-aware) |
| `d`         | `date \| None`       | Date component                 |
| `t`         | `time \| None`       | Time component                 |
| `price`     | `MoneyValue \| None` | Extracted money value          |
| `leftovers` | `str`                | Unparsed remainder             |

---

### `MoneyValue`

| Field      | Type      | Description                         |
| ---------- | --------- | ----------------------------------- |
| `amount`   | `Decimal` | Numeric value                       |
| `currency` | `str`     | Currency code (`RUB`, `EUR`, `USD`) |

---

## 🧪 Testing

Run all parser tests:

```bash
python -m autocalendar.tests.test_parse_event_title
```

Covered scenarios:

* explicit dates (`13.12 09:00`)
* relative dates (`завтра`)
* weekdays (`в понедельник`)
* time-only input (`15:45`)
* money + datetime (`1200р завтра`)
* input without datetime

Tests act as a **formal specification** of parser behavior.

---

## 🧭 Design Principles

* **Explicit formats > NLP**
  (`DD.MM` has priority over fuzzy parsing)

* **Deterministic behavior**
  Same input + same `now` → same output

* **Pipeline architecture**
  `normalize → extract datetime → extract money → cleanup`

* **Tests as documentation**
  If a case matters — it must be covered by a test

---

## ⚠️ Known Limitations

* Russian language only
* No duration parsing (`2 часа`)
* No recurrence (`каждый вторник`)
* No time ranges (`с 10 до 12`)
* No location parsing

These features are intentionally out of scope for v0.x.

---

## 📂 Project Structure

```text
autocalendar/
├── parsing/
│   ├── parser.py
│   ├── datetime_extractor.py
│   ├── money_extractor.py
│   ├── cleanup.py
│   ├── normalize.py
│   └── types.py
├── tests/
│   └── test_parse_event_title.py
├── config.py
└── __init__.py
```

---

## 📄 License

MIT License
