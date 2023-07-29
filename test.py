import time


def export_time_to_HMS(time_data: float):
    time_data = int(time_data)
    h = int(time_data / 3600)
    time_data %= 3600
    m = int(time_data / 60)
    time_data %= 60
    s = time_data
    result = ""
    if h >= 10:
        result += str(h)
    else:
        result += "0" + str(h)
    result += ":"
    if m >= 10:
        result += str(m)
    else:
        result += "0" + str(m)
    result += ":"
    if s >= 10:
        result += str(s)
    else:
        result += "0" + str(s)
    return result


sumTime = 0

for i in range(1000):
    st = time.time()
    if i == 0:
        average_time = sumTime
    else:
        average_time = sumTime / i
    allTime = average_time * (1000 - i - 1)
    print(f"{allTime}", end="\r")
    time.sleep(0.1)
    ed = time.time()
    sumTime += ed - st
