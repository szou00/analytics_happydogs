import datetime

now = datetime.datetime.now()
print(now)
delta = datetime.timedelta(days=1)
oneDayAgo = now-delta

print(oneDayAgo.timestamp())