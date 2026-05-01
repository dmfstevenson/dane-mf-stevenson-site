import http.server
import urllib.parse
import requests
import webbrowser
import threading

CLIENT_ID = input("LinkedIn Client ID: ").strip()
CLIENT_SECRET = input("LinkedIn Client Secret: ").strip()
REDIRECT_URI = "http://localhost:8000/callback"
SCOPE = "w_member_social openid profile"

auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={urllib.parse.quote(SCOPE)}"
)

code = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global code
        if '/callback' in self.path:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code = params.get('code', [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Done! You can close this tab.")
            threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        pass

print("\nOpening LinkedIn in your browser...")
webbrowser.open(auth_url)

server = http.server.HTTPServer(('localhost', 8000), CallbackHandler)
server.serve_forever()

if code:
    r = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    tokens = r.json()

    profile = requests.get(
        'https://api.linkedin.com/v2/userinfo',
        headers={'Authorization': f"Bearer {tokens.get('access_token', '')}"}
    )
    person_id = profile.json().get('sub', 'ERROR')

    print("\n========== ADD THESE AS GITHUB SECRETS ==========")
    print(f"LINKEDIN_CLIENT_ID:     {CLIENT_ID}")
    print(f"LINKEDIN_CLIENT_SECRET: {CLIENT_SECRET}")
    print(f"LINKEDIN_REFRESH_TOKEN: {tokens.get('refresh_token', 'NOT RETURNED - see note below')}")
    print(f"LINKEDIN_PERSON_ID:     {person_id}")
    print("=================================================")
    print("\nNote: if refresh_token is blank, re-run with a fresh LinkedIn app and ensure")
    print("the app has the 'Share on LinkedIn' product enabled.")
