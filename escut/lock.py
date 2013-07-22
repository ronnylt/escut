
import uuid
import datetime


class Lock:
    resource = None
    lifetime = None
    created = None
    token = None

    def __init__(self, resource, lifetime):
        self.resource = resource
        self.lifetime = lifetime
        self.created = datetime.datetime.now()
        self.token = str(uuid.uuid4()).replace('-', '')


class LockManager:

    __redis = None
    __release_script = None
    __renew_script = None

    def __init__(self, redis):
        self.__redis = redis
        self.__release_script = self.__register_release_script()
        self.__renew_script = self.__register_renew_script()

    def lock(self, resource, lifetime):
        self.__redis.set("lock:%s" % resource, 1, ex=lifetime, nx=True)

    def release(self, resource, token):
        return self.__release_script(keys=["lock:%s" % resource], args=[token])

    def renew(self, resource, token, lifetime):
        return self.__renew_script(keys=["lock:%s" % resource], args=[token, lifetime])

    def get_lifetime(self, resource):
        return self.__redis.ttl("lock:%s" % resource)

    def __register_release_script(self):
        script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
        """
        return self.__redis.register_script(script)

    def __register_renew_script(self):
        script = """
            local current_value = redis.call("GET", KEYS[1])

            if current_value == ARGV[1] then
                -- 1 if the timeout was set.
                -- 0 if key does not exist or the timeout could not be set.
                return redis.call("EXPIRE", KEYS[1], ARGV[2])
            elseif not current_value == nil then
                return 2
            else
                return 3
            end
        """
        return self.__redis.register_script(script)