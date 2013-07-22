
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
        resource = self.get_argument('resource')
        lifetime = self.get_argument('lifetime')
        token = self.get_argument('token')

        result = self.lock_manager.renew(resource, token, lifetime)

        if result == 0:
            self.send_error(status_code=404, message="lock not found")
        elif result == 1:
            self.set_status(200)
            self.write("ok=>%s" % lifetime )
        elif result == 2:
            self.send_error(status_code=403, message="invalid lock token")
        elif result == 3:
            self.send_error(status_code=404, message="lock not found")


    def delete(self, resource):
        lock = self.lock_manager.release(resource)
        if lock:
            self.set_status(204)
        else:
            self.send_error(status_code=404, message="lock not found")