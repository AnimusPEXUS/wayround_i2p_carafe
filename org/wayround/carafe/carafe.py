

"""
I was mutch disapointed by BottlePy: Bottle class instances are nailed to
module. So I writed this module
"""

import logging
import fnmatch
import urllib.parse
import copy

import org.wayround.utils.path
import org.wayround.http.message


class Route:

    """
    path_settings:
        must be list of 3-tuples. those tuple values have folloving meanings:
            0 - path segment matching method: 're', 'fm', True
                if this == True, this Route (first one found with True) will
                    supercide all other Routes for current path segment.
            1 - pattern. for True this value is not used.
                    if 0 == 'fm', this value simply a string - file mask
                    if 0 == 're', this value must be compiled regexp, or
                        string which will be compiled into regexp
            2 - name. name frough which resolved value will be available for
                target. None - if this availability isn't needed

    method: can be any str or list of strs
        None - disables matching
        True - any method accepted

    target - must be callable, which accepts folloving parameters:
        wsgi_environment, response_start - just passed from wsgi server
        route_result - dict (which can be empty) with keys corresponding
            to 2 values in path_settings
    """

    def __init__(
            self,
            method,
            path_settings,
            target
            ):

        if not callable(target):
            raise TypeError("`target' must be callable")

        self.target = target

        if type(method) != list:
            method = [method]

        for i in method:
            if type(i) != str:
                raise ValueError(
                    "invalid value of `method'"
                    )

        for i in range(len(method)):
            method[i] = method[i].strip().upper()

        self.method = method

        if path_settings is None:
            path_settings = [(True, None, 'path')]

        for i in path_settings:
            if not i[0] in ['re', 'fm', True]:
                raise ValueError(
                    "invalid segment match method: {}".format(i[0])
                    )

        for i in range(len(path_settings) - 1, -1 - 1):
            ii = path_settings[i]

            if ii[0] == 're':
                if type(ii[1]) == str:

                    i2 = (ii[0], re.compile(ii[1]), ii[2])

                    path_settings[i] = i2

        self.path_settings = path_settings

        # TODO: find way to check all `re' values are compiled

        return


class Router:

    def __init__(self, default_target):
        """
        default_target is same as target in Route class
        """
        if not callable(default_target):
            raise TypeError("`default_target' must be callable")
        self.routes = []
        self.default_target = default_target
        return

    def add(self, method, path_settings, target):
        """
        Simply creates Route and appends it to self.routes

        read Route class docs for parameters meaning
        """
        self.routes.append(Route(method, path_settings, target))
        return

    def wsgi_server_target(self, wsgi_environment, response_start):
        """
        Searches route in self.routes and passes found target wsgi_environment,
        response_start and route_result. explanation for route_result is in
        Route class.

        result from ranning this method is simply passed from target to carafe
        calling fuctionality. see Carafe class for explanations to this.
        """
        route_result = {}

        if wsgi_environment['PATH_INFO'] == '/':
            splitted_path_info = []
        else:
            splitted_path_info = wsgi_environment['PATH_INFO'].split('/')

        target = self.default_target

        path_segment_to_check_position = 0

        filter_result = copy.copy(self.routes)

        for i in range(len(splitted_path_info)):

            if len(filter_result) == 0:
                break

            filter_result = _filter_routes_by_segment(
                splitted_path_info[i],
                filter_result,
                i
                )
            if (len(filter_result) == 1
                and
                filter_result[0].path_settings[i][0] == True
                ):
                break

        if len(filter_result) != 0:
            target = filter_result[0].target

        if target is None:
            target = self.default_target

        return target(wsgi_environment, response_start, route_result)


def _filter_routes_by_segment(
        actual_segment_value,
        routes_lst,
        routes_segment_index
        ):

    ret = []

    for i in routes_lst:
        ret.append(i)

    for i in range(len(ret) - 1, -1, -1):
        ii = ret[i]

        if routes_segment_index >= len(ii.path_settings) - 1:
            del ret[i]

    true_path_found_atonce = False
    for i in ret:
        if i.path_settings[routes_segment_index][0] == True:
            true_path_found_atonce = True
            ret = [i]
            break

    if not true_path_found_atonce:

        for i in range(len(ret) - 1, -1, -1):
            ii = ret[i]

            match = False
            meth = ii.path_settings[routes_segment_index][0]
            if meth == 're':
                if ii.path_settings[routes_segment_index][1].match(
                        actual_segment_value
                        ):
                    match = True
            elif meth == 'fm':

                if fnmatch.fnmatch(
                        actual_segment_value,
                        ii.path_settings[routes_segment_index][1]
                        ):
                    match = True
            else:
                pass

            if not match:
                del ret[i]

    return ret


class _EnvironWSGIHandler:

    def __init__(self, environ_handler):
        if not isinstance(environ_handler, EnvironHandler):
            raise TypeError("invalid type")
        self._environ_handler = environ_handler
        return

    @property
    def version(self):
        return self._environ_handler['wsgi.version']

    @property
    def url_scheme(self):
        return self._environ_handler['wsgi.url_scheme']

    @property
    def input(self):
        return self._environ_handler['wsgi.input']

    @property
    def errors(self):
        return self._environ_handler['wsgi.errors']

    @property
    def multithread(self):
        return self._environ_handler['wsgi.multithread']

    @property
    def multiprocess(self):
        return self._environ_handler['wsgi.multiprocess']

    @property
    def run_once(self):
        return self._environ_handler['wsgi.run_once']


class EnvironHandler:

    def __init__(self, environ, encoding='utf-8'):
        if not isinstance(environ, dict):
            raise TypeError("`environ' must be dict")
        self._environ = environ
        self._encoding = encoding
        self.wsgi = _EnvironWSGIHandler(self)
        return

    def get_original(self):
        return self._environ

    def __getitem__(self, key):
        self._environ.get(name, None)

    def __len__(self):
        return len(self._environ)

    def __repr__(self):
        return repr(self._environ)

    def __str__(self):
        return str(self._environ)

    @property
    def request_method(self):
        return self['REQUEST_METHOD']

    @property
    def script_name(self):
        return self['SCRIPT_NAME']

    @property
    def path_info(self):
        return self['PATH_INFO']

    def get_path_info_splitted(self):
        return org.wayround.utils.path.split(self.path_info)

    @property
    def query_string(self):
        return self['QUERY_STRING']

    def parse_qs(self, *args, **kwargs):
        return urllib.parse.parse_qs(
            self.query_string,
            *args,
            **kwargs
            )

    def parse_qsl(self, *args, **kwargs):
        return urllib.parse.parse_qsl(
            self.query_string,
            *args,
            **kwargs
            )

    @property
    def content_type(self):
        return self['CONTENT_TYPE']

    @property
    def content_length(self):
        return self['CONTENT_LENGTH']

    @property
    def server_name(self):
        return self['SERVER_NAME']

    @property
    def server_port(self):
        return self['SERVER_PORT']

    @property
    def server_protocol(self):
        return self['SERVER_PROTOCOL']


class CarafeIterableIterator:

    def __init__(self, iterator, output_encoding='utf-8'):
        self._iterator = iterator
        self._stop_flag = False
        self.output_encoding = output_encoding
        return

    def __iter__(self):
        for i in self._iterator.__iter__():

            if self._stop_flag:
                if hasattr(self._iterator, 'stop'):
                    getattr(self._iterator, 'stop')()
                    break

            i_t = type(i)

            i_r = None

            if i_t == bytes:
                i_r = res

            elif i_t == str:
                i_r = bytes(res, self.output_encoding)

            else:
                raise TypeError(
                    "iterator `{}' returned invalid value".format(
                        self._iterator
                        )
                    )

            yield i_r

        return

    def stop(self):
        self._stop_flag = True
        return


class ResponseStartWrapper:

    """
    Wrapper for response_start function provided by WSGI server

    It transparantly converts strs to bytes

    This callable wrapper is mimics standard WSGI response_start callable,
    but adds some incompatible things:
        * status (in distinct to WSGI, where it must be str with code and
          reason) can be just int or string with code but without reason.
          in such a case, the reason is taken from Python standard
          http.client.responses dictionary

    """

    def __init__(self, response_start, output_encoding='utf-8'):
        self._response_start = response_start
        self._output_encoding = output_encoding
        return

    def __call__(self, status, response_headers, exc_info=None):

        if type(status) == int:
            status = str(status)

        status_code = None
        status_reason = None

        status_splitted = status.strip().split(' ')

        status_splitted_l = len(status_splitted)

        if status_splitted_l not in range(1, 3):
            raise ValueError("Invalid `status' value")

        status_code = int(status_splitted[0])

        if status_splitted_l > 1:
            status_reason = status_splitted[1]

        status_format_res = org.wayround.http.message.format_status(
            status_code,
            status_reason
            )

        return ResponseStartResultWrapper(
            self._response_start(
                status_format_res,
                response_headers,
                exc_info
                ),
            self._output_encoding
            )


class ResponseStartResultWrapper:

    def __init__(self, response_start_result, output_encoding='utf-8'):
        self._response_start_result = response_start_result
        self._output_encoding = output_encoding
        return

    def __call__(self, data):
        raise Exception("This data return method is deprecated. Don't use it!")
        if isinstance(data, str):
            data = bytes(data, self._output_encoding)
        return self._response_start_result(data)


class Carafe:

    def __init__(self, carafe_app, output_encoding='utf-8'):
        """
        carafe_app - must be callable which has
            (wsgi_environment, response_start) parameters.

            wsgi_environment - is wrapped with EnvironHandler class, which does
                not do any changes to dictionary, but only provides handy
                attributes. moreover EnvironHandler behaves like a mapping
                object. original dict is returned with get_original() method if
                needed.

            response_start - is wrapped with special class, which, when called,
                raises exception as deprecation mesure

            carafe_app must return bytes, str, list of bytes or strs, or
            iterable. if iterable is returned, it is converted with other
            internal iterable which is converts returned strs into bytes.
        """
        self.carafe_app = carafe_app
        self.output_encoding = output_encoding
        return

    def target_for_wsgi_server(self, wsgi_environment, response_start):

        ret = None

        try:
            res = self.carafe_app(
                wsgi_environment,
                ResponseStartWrapper(response_start)
                )

        except Exception as e:
            # TODO: check status correctness
            response_start('500 Error', [], e)
            ret = [b'Internal Server Error']
            logging.exception("Error calling `{}'".format(self.carafe_app))
        else:

            res_t = type(res)

            if res_t == bytes:
                ret = [res]

            elif res_t == str:
                ret = [bytes(res, self.output_encoding)]

            elif res_t == list:
                ret = []
                for i in res:
                    i_t = type(i)
                    if i_t == bytes:
                        ret.append(i)

                    elif i_t == str:
                        ret.append(bytes(i, self.output_encoding))

                    else:
                        raise ValueError(
                            "if list is returned it bust contain strs or bytes"
                            )
            elif hasattr(res, '__iter__'):
                if not callable(res):
                    raise ValueError("invalid iterator returned")

                if hasattr(res, 'stop'):
                    if not callable(getattr(res, 'stop')):
                        raise Exception(
                            "returned iteratable has invalid 'stop' method"
                            )

                ret = CarafeIterableIterator(res_iter, self.output_encoding)

            else:
                raise TypeError("some invalid data type returned")

        return ret
