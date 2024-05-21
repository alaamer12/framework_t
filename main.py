class Request:
    def __init__(self, environ):
        self.environ = environ
        self.path = environ.get('PATH_INFO', '/')
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.query_params = {}
        self.parse_query_params()

    def parse_query_params(self):
        query_string = self.environ.get('QUERY_STRING', '')
        params = query_string.split('&')
        for param in params:
            split_param = param.split('=')
            if len(split_param) == 2:
                key, value = split_param
                self.query_params[key] = value


class Response:
    def __init__(self, status_code=200, content_type='text/html'):
        self.status_code = status_code
        self.headers = {'Content-Type': content_type}
        self.body = ''

    def set_body(self, body):
        self.body = body

    def add_header(self, key, value):
        self.headers[key] = value

class SimpleFramework:
    def __init__(self):
        self.routes = {}
        self.middleware = []

    def route(self, path):
        def decorator(handler):
            self.routes[path] = handler
            return handler
        return decorator

    def use(self, middleware):
        self.middleware.append(middleware)

    def handle_request(self, environ):
        request = Request(environ)
        response = Response()

        for middleware in self.middleware:
            middleware(request, response)

        handler = self.routes.get(request.path)
        if handler:
            handler(request, response)
        else:
            self.default_handler(request, response)

        return response

    def default_handler(self, request, response):
        response.status_code = 404
        response.set_body("404 Not Found")

# Middleware example
def logging_middleware(request, response):
    print(f"Request: {request.method} {request.path}")

app = SimpleFramework()

# Add middleware
app.use(logging_middleware)

# Define routes
@app.route("/")
def home(request, response):
    response.set_body("<h1>Hello, World!</h1>")

@app.route("/about")
def about(request, response):
    response.set_body("<h1>About Page</h1>")

# Handle requests
def application(environ, start_response):
    response = app.handle_request(environ)
    start_response(f"{response.status_code} OK", list(response.headers.items()))
    return [response.body.encode()]

# Example usage with WSGI server
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
