
import tornado.web

class LockHandler(tornado.web.RequestHandler):
    @property
    def lock_manager(self):
        return self.application.lock_manager

    def post(self):
        resource = self.get_argument('resource')
        lifetime = self.get_argument('lifetime')
        ttl = self.lock_manager.get_lifetime(resource)

        if ttl > 0:
            self.write(str(ttl))
        else:
            self.lock_manager.lock(resource, lifetime)
            self.set_status(201)

    def put(self):
        pass

    def delete(self, resource):
        lock = self.lock_manager.release(resource)
        if lock:
            self.set_status(204)
        else:
            self.send_error(status_code=404, message="lock not found")