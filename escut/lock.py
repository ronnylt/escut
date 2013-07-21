
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

    def __init__(self, redis):
        self.__redis = redis

    def lock(self, resource, lifetime):
        self.__redis.set("lock:%s" % resource, 1, ex=lifetime, nx=True)

    def release(self, resource, token):
        pass

    def renew(self, resource, token, lifetime):
        pass

    def get_lifetime(self, resource):
        return self.__redis.ttl("lock:%s" % resource)
