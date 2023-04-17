import os
import pickle
import hashlib
import asyncio
import aiofiles


class FileCache:
    def __init__(self, func=None, cache_file="cache.pkl", save_interval=10):
        self.func = func
        self.cache_file = cache_file
        self.save_interval = save_interval
        self.call_count = 0

        if not os.path.exists(self.cache_file):
            with open(self.cache_file, "wb") as f:
                pickle.dump({}, f)

        with open(self.cache_file, "rb") as f:
            self.cache_data = pickle.load(f)

    def __call__(self, *args, **kwargs):
        if self.func is None:
            self.func = args[0]
            return self

        if asyncio.iscoroutinefunction(self.func):
            return self.__acall__(*args, **kwargs)

        return self._call(*args, **kwargs)

    def _call(self, *args, **kwargs):
        key = self._generate_key(args, kwargs)

        if key in self.cache_data:
            result = self.cache_data[key]
        else:
            result = self.func(*args, **kwargs)
            self.cache_data[key] = result

        self.call_count += 1
        if self.call_count >= self.save_interval:
            self.save_cache()
            self.call_count = 0

        return result

    async def __acall__(self, *args, **kwargs):
        key = self._generate_key(args, kwargs)

        if key in self.cache_data:
            result = self.cache_data[key]
        else:
            result = await self.func(*args, **kwargs)
            self.cache_data[key] = result

        self.call_count += 1
        if self.call_count >= self.save_interval:
            await self.save_cache_async()
            self.call_count = 0

        return result

    def _generate_key(self, args, kwargs):
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key = pickle.dumps(key_data)
        return hashlib.md5(key).hexdigest()

    def save_cache(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache_data, f)

    async def save_cache_async(self):
        async with aiofiles.open(self.cache_file, "wb") as f:
            await f.write(pickle.dumps(self.cache_data))
