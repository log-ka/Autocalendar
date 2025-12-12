from datetime import date, time

from autocalendar.scheduling.types import Event, ScheduledEvent, TimeSlot
from autocalendar.scheduling.constraints import WorkDay
from autocalendar.scheduling.slots import build_free_slots, can_fit
from autocalendar.scheduling.overflow import handle_overflow
from autocalendar.scheduling.scheduler import autoschedule


# ------------------------
# Утилиты тест-раннера
# ------------------------

def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(
            f"{message}\n"
            f"ОЖИДАЛОСЬ: {expected}\n"
            f"ПОЛУЧЕНО: {actual}"
        )


def assert_true(value, message):
    if value is not True:
        raise AssertionError(message)


def run_test(test_func):
    try:
        test_func()
        print(f"✔ {test_func.__name__}")
        return True
    except AssertionError as e:
        print(f"✖ {test_func.__name__}")
        print(e)
        print("-" * 60)
        return False
    except Exception as e:
        print(f"💥 {test_func.__name__} (НЕОЖИДАННОЕ ИСКЛЮЧЕНИЕ)")
        print(repr(e))
        print("-" * 60)
        return False


# ------------------------
# ТЕСТЫ СЛОТОВ
# ------------------------

def test_build_free_slots_single_fixed_event():
    work_day = WorkDay(start=time(9, 0), end=time(18, 0))

    fixed = [
        ScheduledEvent("Meeting", date(2025, 1, 1), time(12, 0), 60, 1)
    ]

    slots = build_free_slots(fixed, work_day)

    expected = [
        TimeSlot(time(9, 0), time(12, 0)),
        TimeSlot(time(13, 0), time(18, 0)),
    ]

    assert_equal(slots, expected, "Неверные свободные слоты при одном фиксированном событии")


def test_build_free_slots_event_at_day_start():
    work_day = WorkDay(start=time(9, 0), end=time(18, 0))

    fixed = [
        ScheduledEvent("Morning", date(2025, 1, 1), time(9, 0), 60, 1)
    ]

    slots = build_free_slots(fixed, work_day)

    expected = [
        TimeSlot(time(10, 0), time(18, 0))
    ]

    assert_equal(slots, expected, "Событие в начале дня должно сдвигать первый слот")


def test_can_fit_exact_match():
    slot = TimeSlot(time(10, 0), time(11, 0))
    assert_true(can_fit(slot, 60), "Слот ровно под длительность должен подходить")


def test_can_fit_too_long():
    slot = TimeSlot(time(10, 0), time(11, 0))
    assert_true(not can_fit(slot, 61), "Слот не должен вмещать событие больше себя")


# ------------------------
# ТЕСТЫ OVERFLOW
# ------------------------

def test_handle_overflow_moves_date_only():
    event = Event("Task", date(2025, 1, 1), None, 60, 1)
    result = handle_overflow(event)

    assert_equal(
        result.date,
        date(2025, 1, 2),
        "Overflow должен переносить событие на следующий день"
    )

    assert_equal(
        result.time,
        None,
        "Overflow не должен сам назначать время"
    )


# ------------------------
# ТЕСТЫ AUTOSCHEDULE
# ------------------------

def test_autoschedule_simple_order_by_priority():
    work_day = WorkDay(start=time(9, 0), end=time(18, 0))

    events = [
        Event("Low", date(2025, 1, 1), None, 60, 1),
        Event("High", date(2025, 1, 1), None, 60, 3),
    ]

    result = autoschedule(events, work_day)

    assert_equal(result[0].title, "High", "Сначала должно планироваться событие с большим приоритетом")
    assert_equal(result[0].time, time(9, 0), "Первое событие должно начинаться с начала рабочего дня")
    assert_equal(result[1].time, time(10, 0), "Второе событие должно идти следом")


def test_autoschedule_respects_fixed_event_gap():
    work_day = WorkDay(start=time(9, 0), end=time(18, 0))

    events = [
        Event("Fixed", date(2025, 1, 1), time(12, 0), 60, 1),
        Event("Flex", date(2025, 1, 1), None, 60, 2),
    ]

    result = autoschedule(events, work_day)

    flex = next(e for e in result if e.title == "Flex")

    assert_equal(
        flex.time,
        time(9, 0),
        "Гибкое событие должно встать в первый доступный слот ДО фиксированного"
    )


def test_autoschedule_overflow_when_day_is_full():
    work_day = WorkDay(start=time(9, 0), end=time(10, 0))

    events = [
        Event("A", date(2025, 1, 1), None, 60, 2),
        Event("B", date(2025, 1, 1), None, 60, 1),
    ]

    result = autoschedule(events, work_day)

    day1 = [e for e in result if e.date == date(2025, 1, 1)]
    day2 = [e for e in result if e.date == date(2025, 1, 2)]

    assert_equal(len(day1), 1, "В первый день должно влезть только одно событие")
    assert_equal(len(day2), 1, "Второе событие должно быть перенесено на следующий день")


# ------------------------
# ЗАПУСК ВСЕХ ТЕСТОВ
# ------------------------

if __name__ == "__main__":
    tests = [
        test_build_free_slots_single_fixed_event,
        test_build_free_slots_event_at_day_start,
        test_can_fit_exact_match,
        test_can_fit_too_long,
        test_handle_overflow_moves_date_only,
        test_autoschedule_simple_order_by_priority,
        test_autoschedule_respects_fixed_event_gap,
        test_autoschedule_overflow_when_day_is_full,
    ]

    print("\n=== AUTOCALENDAR · ТЕСТЫ АВТОДОПОЛНЕНИЯ ВРЕМЕНИ ===\n")

    passed = 0
    for test in tests:
        if run_test(test):
            passed += 1

    print(f"\nИТОГ: {passed}/{len(tests)} тестов пройдено")
