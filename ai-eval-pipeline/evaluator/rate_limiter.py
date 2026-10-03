import asyncio
import time


class AsyncRateLimiter:
    def __init__(self, max_requests: int, period: float):
        self.max_requests = max_requests
        self.period = period

        self.timestamps = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        while True:
            async with self.lock:
                now = time.monotonic()

                # Remove timestamps outside the window
                self.timestamps = [
                    timestamp
                    for timestamp in self.timestamps
                    if now - timestamp < self.period
                ]

                if len(self.timestamps) < self.max_requests:
                    self.timestamps.append(now)
                    return

                oldest = self.timestamps[0]
                wait_time = self.period - (now - oldest)

            await asyncio.sleep(wait_time)