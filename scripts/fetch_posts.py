import requests
import json
import os
from datetime import datetime

CLIENT_ID = os.environ['LINKEDIN_CLIENT_ID']
CLIENT_SECRET = os.environ['LINKEDIN_CLIENT_SECRET']
REFRESH_TOKEN = os.environ['LINKEDIN_REFRESH_TOKEN']
PERSON_ID = os.environ['LINKEDIN_PERSON_ID']

def get_access_token():
    r = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data={
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    r.raise_for_status()
    return r.json()['access_token']

def fetch_posts(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'LinkedIn-Version': '202308',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    r = requests.get(
        f'https://api.linkedin.com/rest/posts?author=urn%3Ali%3Aperson%3A{PERSON_ID}&q=author&count=5&sortBy=LAST_MODIFIED',
        headers=headers
    )
    r.raise_for_status()
    return r.json().get('elements', [])

def parse_posts(elements):
    posts = []
    for el in elements:
        text = el.get('commentary', '')
        if not text:
            continue
        post_id = el.get('id', '').split(':')[-1]
        timestamp = el.get('publishedAt') or el.get('createdAt', 0)
        date = datetime.fromtimestamp(timestamp / 1000).strftime('%B %d, %Y') if timestamp else ''
        posts.append({
            'text': text[:400] + ('...' if len(text) > 400 else ''),
            'date': date,
            'url': f'https://www.linkedin.com/feed/update/urn:li:share:{post_id}'
        })
    return posts

token = get_access_token()
elements = fetch_posts(token)
posts = parse_posts(elements)

with open('posts.json', 'w') as f:
    json.dump(posts, f, indent=2)

print(f"Saved {len(posts)} posts to posts.json")
