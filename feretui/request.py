import inspect
import json
import urllib
from typing import Any

from feretui.exceptions import RequestError
from feretui.session import Session


class RequestMethod:
    pass


POST = RequestMethod()
GET = RequestMethod()


class Request:
    POST = POST
    GET = GET

    def __init__(
        self,
        method: RequestMethod = POST,
        body: str = None,
        querystring: str = None,
        headers: dict = None,
        request: Any = None,
        session: Session = None,
    ):
        self.method = method
        self.raw_body = body
        self.raw_querystring = querystring
        self.headers = headers
        self.request = request
        self.session = session

        self.body_validator = None
        self.query_string_validator = None

        self.query = {}
        if querystring:
            self.query = urllib.parse.parse_qs(querystring)

        self.body = {}
        if self.raw_body:
            try:
                self.body = json.loads(self.raw_body)
            except Exception:
                self.body = {}

        if not request:
            raise RequestError('the request of the web server is required')

        if not session:
            raise RequestError('the session is required')

        if not isinstance(session, Session):
            raise RequestError(
                'the session must be an instance of FeretUI Session')

    @property
    def deserialized_body(self) -> dict:
        if not self.body_validator:
            raise RequestError(
                'No schema validator defined for deserialize the body'
            )

        if inspect.isfunction(self.body_validator):
            schema = self.body_validator(self)
        else:
            schema = self.body_validator

        return schema(**self.body)

    @property
    def deserialized_querystring(self) -> dict:
        if not self.query_string_validator:
            raise RequestError(
                'No schema validator defined for deserialize the querystring'
            )

        if inspect.isfunction(self.body_validator):
            schema = self.body_validator(self)
        else:
            schema = self.body_validator

        return schema(**self.query)

    def get_url_from_dict(self, querystring: dict) -> str:
        return f'/?{urllib.parse.urlencode(querystring, doseq=True)}'

    def get_query_string_from_current_url(self) -> dict:
        url = self.headers['Hx-Current-Url']
        url = urllib.parse.urlparse(url)
        return urllib.parse.parse_qs(url.query)
