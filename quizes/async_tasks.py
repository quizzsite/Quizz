import asyncio
import functools

SECOND = 1
MINUTE = 60*SECOND
HOUR = 60*MINUTE
DAY = 24*HOUR
WEEK = 7*DAY

INFINITY = float("inf")

async def periodic(func, seconds):
    while True:
        await asyncio.sleep(seconds)
        func()

def stop():
    task.cancel()

def run_task(*args, **kwargs):
    def adecorator(func):
        global run_time
        run_time = kwargs.get("run_time")
        func = func
        s = kwargs.get("s") or 0
        m = kwargs.get("m") or 0
        h = kwargs.get("h") or 0
        d = kwargs.get("d") or 0
        w = kwargs.get("w") or 0
        time = s*SECOND+m*MINUTE+h*HOUR+d*DAY+w*WEEK
        def wrapper(*args, **kwargs):
            global task
            loop = asyncio.get_event_loop()
            loop.call_later(INFINITY, stop)
            task = loop.create_task(periodic(func=func, seconds=time))
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
 
        return wrapper
 
    return adecorator
