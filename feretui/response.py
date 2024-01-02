class Response:
    def __init__(
        self,
        body: str,
        content_type: str = 'text/html',
        status_code: int = 200,
        headers: dict = None
    ):
        if headers is None:
            headers = {}

        self.body = body
        self.content_type = content_type
        self.status_code = status_code
        self.headers = headers
