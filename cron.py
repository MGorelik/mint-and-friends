from crontab import CronTab

cron = CronTab(user='username')
job = cron.new(command='python kick_canary.py')
job.day.every(1)

cron.write()