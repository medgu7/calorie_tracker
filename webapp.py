import http.server
import socketserver
import urllib.parse
from typing import Dict
from tracker import add_food, reset, get_totals, DEFAULT_CSV

PORT = 8000


def render_index() -> bytes:
    total_calories, total_carbs, total_protein, total_fat, micro_totals = get_totals()
    micro_rows = ''.join(f'<li>{k}: {v}</li>' for k, v in micro_totals.items())
    html = f"""
    <html>
    <head><title>Calorie Tracker</title></head>
    <body>
      <h1>Daily Calorie Tracker</h1>
      <h2>Add Food</h2>
      <form action='/add' method='post'>
        Name: <input name='name'><br>
        <button type='submit'>Add</button>
      </form>

      <h2>Summary</h2>
      <p>Calories: {total_calories}</p>
      <p>Carbs: {total_carbs}g</p>
      <p>Protein: {total_protein}g</p>
      <p>Fat: {total_fat}g</p>
      <ul>{micro_rows}</ul>

      <form action='/reset' method='post'>
        <button type='submit'>Reset</button>
      </form>
    </body>
    </html>
    """
    return html.encode()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(render_index())
        else:
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode()
        params = urllib.parse.parse_qs(body)
        if self.path == '/add':
            class Args:
                pass

            args = Args()
            args.name = params.get('name', [''])[0]
            args.calories = None
            args.carbs = None
            args.protein = None
            args.fat = None
            args.micro = []
            args.csv = str(DEFAULT_CSV)
            add_food(args)
        elif self.path == '/reset':
            reset(None)
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()


if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f'Serving on http://localhost:{PORT}')
        httpd.serve_forever()
