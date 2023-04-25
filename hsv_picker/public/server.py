import http.server
import socketserver
from os import path

my_host_name = 'localhost'
my_port = 4000
my_folder_path = r'C:\Users\Ian Lai\Documents\GitHub\odyssey_cnn\hsv_picker\public'

home_page_path = 'index.html'


class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        #print(f"Path: {self.getPath()}, Size: {path.getsize(self.getPath())}")
        self.send_header('Content-Length', path.getsize(self.getPath()))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def getPath(self):
        content_path = path.join(my_folder_path, str(self.path).split('?')[0][1:])
        print(content_path)
        return content_path

    def getContent(self, content_path):
        with open(content_path, mode='r', encoding='utf-8') as f:
            content = f.read()
        return bytes(content, 'utf-8')
    
    def do_GET(self):
        self._set_headers()
        self.wfile.write(self.getContent(self.getPath()))


with socketserver.TCPServer(('', my_port), HTTPRequestHandler) as httpd:
    try:
        print("HTTP Server serving at port", my_port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")

    