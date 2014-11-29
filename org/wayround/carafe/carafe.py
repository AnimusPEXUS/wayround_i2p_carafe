

"""
I was mutch disapointed by BottlePy: Bottle class instances are nailed to
module. So I writed this module
"""

import logging
import urllib.parse

import org.wayround.utils.path


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
    """

    def __init__(self, response_start, output_encoding='utf-8'):
        self._response_start = response_start
        self._output_encoding = output_encoding
        return

    def __call__(self, status, response_headers, exc_info=None):
        return ResponseStartResultWrapper(
            self._response_start(status, response_headers, exc_info),
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

    def __call__(self, wsgi_environment, response_start):

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
