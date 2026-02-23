from datetime import datetime, timedelta, date

# Task 1
def Task1():
    current_date = datetime.now()
    delta = timedelta(days=5)
    new = current_date - delta
    print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
    print(f"Date 5 days ago: {new.strftime('%Y-%m-%d')}")

# Task 2
def Task2():
    today = date.today()
    delta = timedelta(days=1)
    yesterday = today - delta
    tomorrow = today + delta
    print(f"Today: {today}")
    print(f"Yesterday: {yesterday}")
    print(f"Tomorrow: {tomorrow}")

# Task 3
def Task3():
    now = datetime.now()
    now_no_ms = now.replace(microsecond=0)
    print(f"Original: {now}")
    print(f"Without microseconds: {now_no_ms}")

# Task 4
def Task4():
    now = datetime.now()
    now_no_ms = now.replace(microsecond=0)
    b_day = datetime(2007, 9, 21, 22, 48, 39)
    difference = now_no_ms - b_day
    seconds_diffs = difference.total_seconds()
    print(f"Start: {now_no_ms}")
    print(f"End: {b_day}")
    print(f"Difference in seconds: {int(seconds_diffs)} seconds")