import base64
import json
import typing
from urllib.parse import urlencode

from starlette.background import BackgroundTask
from starlette.datastructures import URL
from starlette.responses import RedirectResponse


# a = base64.b64decode(axial)
# ax = json.loads(a)
class RedirectResponseWraper(RedirectResponse):

    def __init__(
            self,
            url: typing.Union[str, URL],
            status_code: int = 307,
            headers: typing.Optional[typing.Mapping[str, str]] = None,
            background: typing.Optional[BackgroundTask] = None,
            query: typing.Optional[dict] = None
    ) -> None:
        if query is None:
            super().__init__(url, status_code, headers, background)
            return
        else:
            for k, v in query.items():
                if type(v) != int and type(v) != str:
                    query[k] = base64.b64encode(v.json().encode('utf-8'))
                    # query[k] = json.dumps(v)
            query_string = urlencode(query, encoding='utf-8')
            super().__init__(url + '?' + query_string, status_code, headers, background)
