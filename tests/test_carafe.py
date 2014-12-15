
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

        self.router.add(
            'GET',
            [
                ('fm', 'index', None),
                ('re', r'\d+', 'digits')],
            self.index_and_digits
            )
        self.router.add(
            'GET',
            [
                ('fm', 'index', None)
                ],
            self.index
            )
        self.router.add(
            'GET',
            [
                ('fm', 'index2', None)
                ],
            self.index2
            )
        self.router.add(
            'GET',
            [
                ('fm', 'index2', None),
                ('path', None, 'path')
                ],
            self.index2_with_path
            )
        self.router.add(
            'GET',
            [
                ('fm', 'index3', None),
                ('path', None, 'path')
                ],
            self.index2_with_path_html
            )

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
        return a(wsgi_environment, response_start, 'default', route_result)

    def index(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return a(wsgi_environment, response_start, 'index', route_result)

    def index2(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return a(wsgi_environment, response_start, 'index2', route_result)

    def index2_with_path(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return a(wsgi_environment, response_start,
                 'index2_with_path', route_result)

    def index2_with_path_html(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return b(wsgi_environment, response_start,
                 'index2_with_path_html', route_result)

    def index_and_digits(
            self,
            wsgi_environment,
            response_start,
            route_result
            ):
        return a(wsgi_environment, response_start,
                 'index_and_digits', route_result)


def a(e, s, name, route_result):

    s(
        '200',
        [('Content-Type', 'text/plain; charset=UTF-8')]
        )

    res = """\
name: {}
e:
{}
pi:
{}
qs:
{}
route_result:
{}
""".format(
        name,
        pprint.pformat(e),
        urllib.parse.unquote(e['PATH_INFO']),
        urllib.parse.parse_qs(urllib.parse.unquote(e['QUERY_STRING'])),
        route_result
        )

    print(res)

    return [bytes(res, 'utf-8')]


def b(e, s, name, route_result):

    s(
        '200',
        [('Content-Type', 'text/html; charset=UTF-8')]
        )

    res = """\
<html>
<head><title>123</title></head>
<body>
name: {}
e:
{}
pi:
{}
qs:
{}
route_result:
{}
</body>
</html>
""".format(
        name,
        pprint.pformat(e),
        urllib.parse.unquote(e['PATH_INFO']),
        urllib.parse.parse_qs(urllib.parse.unquote(e['QUERY_STRING'])),
        route_result
        )

    print(res)

    return [bytes(res, 'utf-8')]

c = TestCarafeApp()
c.start()
c.wait()
