

"""
I was mutch disapointed by BottlePy: Bottle class instances are nailed to
module. So I writed this module
"""


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

    def __call__(status, response_headers, exc_info=None):

        if isinstance(status, str):
            status = bytes(status, self._output_encoding)

        for i in range(len(response_headers)):

            iv = response_headers[i]

            iv0t = type(iv[0])
            iv1t = type(iv[1])

            if iv0t == str or iv1t == str:
                iv0 = iv[0]
                iv1 = iv[1]

                if iv0t == str:
                    iv0 = bytes(iv0, self._output_encoding)

                if iv1t == str:
                    iv1 = bytes(iv1, self._output_encoding)

                response_headers[i] = iv0, iv1

        return self._response_start(status, response_headers, exc_info)


class Carafe:

    def __init__(self, carafe_app, output_encoding='utf-8'):
        """
        carafe_app - must be callable which has
            (wsgi_environment, response_start) parameters.

            wsgi_environment - is passed strictly from wsgi server.
                You can use helpers in this module to
                simplify wsgi_environment handling.

            response_start - is wrapped with special class, which, when called,
                converts strs parameters to bytes

            carafe_app must return bytes, str, list of bytes or strs, or
            iterable. if iterable is returned, it is converted with other
            internal iterable which is converts returned strs into bytes.
        """
        self.carafe_app = carafe_app
        self.output_encoding = output_encoding
        return

    def __call__(self, wsgi_environment, response_start):

        res = self.carafe_app(
            wsgi_environment,
            ResponseStartWrapper(response_start)
            )

        res_t = type(res)

        ret = None

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
