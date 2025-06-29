import http.server
import socketserver
import urllib.parse
from typing import Dict
from tracker import add_food, reset, get_totals, parse_micros_string

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
        Calories: <input name='calories' type='number' step='any'><br>
        Carbs: <input name='carbs' type='number' step='any'><br>
        Protein: <input name='protein' type='number' step='any'><br>
        Fat: <input name='fat' type='number' step='any'><br>
        Micros (key=value comma or space separated): <input name='micros'><br>
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
            args.calories = float(params.get('calories', ['0'])[0] or 0)
            args.carbs = float(params.get('carbs', ['0'])[0] or 0)
            args.protein = float(params.get('protein', ['0'])[0] or 0)
            args.fat = float(params.get('fat', ['0'])[0] or 0)
            micro_str = params.get('micros', [''])[0]
            args.micro = []
            micros = parse_micros_string(micro_str)
            # convert dict to list for add_food
            args.micro = [f"{k}={v}" for k,v in micros.items()]
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
