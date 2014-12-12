
import pprint
import urllib.parse

import org.wayround.carafe.carafe
import org.wayround.wsgi.server


class TestCarafeApp:

    def __init__(self):

        self.carafe_app = \
            org.wayround.carafe.carafe.Carafe(self.router_entry)

        self.wsgi_server = \
            org.wayround.wsgi.server.CompleteServer(
                self.carafe_app.target_for_wsgi_server
                )

        self.router = \
            org.wayround.carafe.carafe.Router(self.default_router_target)

        self.router.add('GET', [('fm', 'index')], self.index)
        self.router.add('GET', [('fm', 'index2')], self.index2)

        return

    def router_entry(self, wsgi_environment, response_start):
        return self.router.wsgi_server_target(wsgi_environment, response_start)

    def start(self):
        self.wsgi_server.start()
        return

    def wait(self):
        self.wsgi_server.wait()
        return

    def default_router_target(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return a(wsgi_environment, response_start, 'default')

    def index(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return a(wsgi_environment, response_start, 'index')

    def index2(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return a(wsgi_environment, response_start, 'index2')


def a(e, s, name):

    s(
        '200',
        [('Content-Type', 'text/plain;charset=UTF8')]
        )

    res = """\
name: {}
e:
{}
pi:
{}
qs:
{}
""".format(
        name,
        pprint.pformat(e),
        urllib.parse.unquote(e['PATH_INFO']),
        urllib.parse.parse_qs(urllib.parse.unquote(e['QUERY_STRING']))
        )

    print(res)

    return [bytes(res, 'utf-8')]

b = TestCarafeApp()
b.start()
b.wait()
