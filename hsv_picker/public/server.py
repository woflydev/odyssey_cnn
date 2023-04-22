import http.server
import socketserver

my_port = 8000


with socketserver.TCPServer(("", my_port), http.server.SimpleHTTPRequestHandler) as httpd:
    print("HTTP server on port", my_port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("Server stopped.")