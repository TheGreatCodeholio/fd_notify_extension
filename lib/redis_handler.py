# Python 3 Core Libraries
import datetime
import time
import json

# Python 3 Third Party Libraries
import redis

# Python 3 Project Libraries
import etc.config as config


class RedisCache:
    def __init__(self):
        self.r = redis.Redis(
            host='localhost',
            port=6379)

    def add_update_flag_to_redis(self, service, status):
        working = {"status": status}
        self.r.hset("fire_calls_" + service, "status", working)

    def get_flag_from_redis(self):
        data = self.r.hget("fire_calls", "status")
        result = json.loads(data)
        if result:
            return result
        else:
            return None

    def add_call_to_redis(self, service, call_tone_name, call_tone_data, call_mp3_url, call_mp3_path):
        call_data = {"call_tone_name": call_tone_name, "call_tone_data": call_tone_data, "call_mp3_url": call_mp3_url,
                     "call_mp3_path": call_mp3_path, "call_time": time.time(),
                     "call_department_number": call_tone_data["department_number"]}
        self.r.hset("fire_calls_" + service, call_tone_name, json.dumps(call_data))

    def get_single_call(self, service, call_tone_name):
        call = self.r.hget("fire_calls_" + service, call_tone_name)
        result = json.loads(call)
        if result:
            return result
        else:
            return None

    def get_all_call(self, service):
        result = self.r.hgetall("fire_calls_" + service)
        if result is not None:
            return result
        else:
            return None

    def delete_single_call(self, service, call_tone_name):
        self.r.hdel("fire_calls_" + service, call_tone_name)

    def delete_all_calls(self, service):
        self.r.delete("fire_calls_" + service)

    def add_warn_to_redis(self, warning_data):
        self.r.hset("noaa_warn", warning_data["warn_id"], json.dumps(warning_data))

    def get_warn_from_redis(self, warn_id):
        data = self.r.hget("noaa_warn", warn_id)
        if data is not None:
            return json.loads(data)
        else:
            return False

    def get_all_warn_from_redis(self):
        data = self.r.hgetall("noaa_warn")
        if data is not None:
            return data
        else:
            return False

    def rem_warn_from_redis(self, warn_id):
        self.r.hdel("noaa_warn", warn_id)
