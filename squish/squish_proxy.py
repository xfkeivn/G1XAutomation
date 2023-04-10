from Pyro5.api import Proxy, locate_ns


class SquishProxy:

    def __init__(self,target_ip, ssh_private_key,attachable_app_name):
        self.target_ip = target_ip
        self.ssh_private_key = ssh_private_key
        self.attachable_app_name = attachable_app_name
        self.proxy = None

    def create_proxy(self):
        with locate_ns(host='127.0.0.1') as ns:
            for router, router_uri in ns.list(prefix="gx1.development.squish_server").items():
                print("found router: %s" % router)
                self.proxy = Proxy(router_uri)
                return True
        return False

    def connect(self):
        return self.proxy.connect()

    def disconnect(self):
        return self.proxy.disconnect()

    def list_drag(self, gobj, offset):
        return self.proxy.list_drag(gobj,offset)

    def mouse_tap(self, gobj):
        return self.proxy.mouse_tap(gobj)

    def mouse_wheel(self, gobj, steps):
        return self.proxy.mouse_wheel(gobj,steps)

    def mouse_wheel_screen(self, x, y, steps):
        return self.proxy.mouse_wheel_screen(x,y,steps)

    def long_mouse_drag(self, gobj, steps):
        return self.proxy.long_mouse_drag(gobj,steps)

    def mouse_click(self, gobj):
        return self.proxy.mouse_click(gobj)

    def mouse_xy(self, x, y):
        return self.proxy.mouse_xy(x,y)

    def long_mouse_click(self, gobj, x, y):
        return self.proxy.long_mouse_click(gobj,x,y)

    def screen_save(self, path_to_save):
        return self.proxy.screen_save(path_to_save)

    def get_gobj_text(self, gobj):
        return self.proxy.get_gobj_text(gobj)


if __name__ == "__main__":
    proxy = SquishProxy("192.168.80.130",r"C:\Users\xuf\.ssh\bsci","gx1")
    proxy.create_proxy()
    proxy.connect()

    proxy.disconnect()
