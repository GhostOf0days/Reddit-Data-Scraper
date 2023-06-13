import requests
import json
import os

SUBREDDITS = ['emotions']  # Add subreddits to scrape as strings here (e.g. 'artificial')
DATA_DIRECTORY = 'subreddit-data'

def parse_about(subreddit):
    url = f'https://www.reddit.com/r/{subreddit}/about.json'
    headers = {'User-agent': 'Reddit Data Scraper'}
    response = requests.get(url, headers=headers)

    if response.ok:
        data = response.json()['data']
        about_data = {
            'name': data['display_name'],
            'subscribers': data['subscribers'],
            'created_utc': data['created_utc'],
            'description': data['public_description']
        }
        return about_data
    else:
        print(f'Error {response.status_code}')
        return None

def parse_comments_recursive(data, level=0):
    comments = []
    for child in data['children']:
        if 'body' in child['data']:
            comment = child['data']['body']
            score = child['data']['score']
            replies = child['data']['replies']
            if replies and 'data' in replies:
                reply_comments = parse_comments_recursive(replies['data'], level=level+1)
                comments.append({'level': level, 'comment': comment, 'score': score, 'replies': reply_comments})
            else:
                comments.append({'level': level, 'comment': comment, 'score': score})
    return comments

def parse_comments(subreddit, post_id):
    url = f'https://www.reddit.com/r/{subreddit}/comments/{post_id}.json'
    headers = {'User-agent': 'Reddit Data Scraper'}
    response = requests.get(url, headers=headers)
    
    if response.ok:
        data = response.json()
        comments = parse_comments_recursive(data[1]['data'])
        return comments
    else:
        print(f'Error {response.status_code}')
        return None

def parse(subreddit, after=''):
    urlTemplate = 'https://www.reddit.com/r/{}.json?{}'
    headers = {'User-agent': 'Reddit Data Scraper'}
    params = '' if not after else 'after=' + after
    url = urlTemplate.format(subreddit, params)

    response = requests.get(url, headers=headers)
    
    if response.ok:
        data = response.json()['data']
        posts = []
        for post in data['children']:
            postData = post['data']
            postID = postData['id']
            score = postData['score']
            postTitle = postData['title']
            author = postData['author']
            date = postData['created_utc']
            url = postData.get('url_overridden_by_dest')
            media_url = postData.get('url') if postData['is_video'] or 'preview' in postData else None
            comments = parse_comments(subreddit, postID)
            posts.append({'id': postID, 'score': score, 'title': postTitle,
                          'author': author, 'date': date, 'url': url, 'media_url': media_url, 'comments': comments})
        return posts, data['after']
    else:
        print(f'Error {response.status_code}')
        return None, None
    
def write_about(subreddit, data):
    subreddit_dir = os.path.join(DATA_DIRECTORY, f'r-{subreddit}')
    if not os.path.exists(subreddit_dir):
        os.makedirs(subreddit_dir)

    about_file = os.path.join(subreddit_dir, 'about.md')
    with open(about_file, 'w') as f:
        f.write(f'# About r/{data["name"]}\n\n')
        f.write(f'Subscribers: {data["subscribers"]}\n\n')
        f.write(f'Created UTC: {data["created_utc"]}\n\n')
        f.write(f'Description:\n\n{data["description"]}\n')

def write_to_json(subreddit, post_id, data):
    subreddit_dir = os.path.join(DATA_DIRECTORY, f'r-{subreddit}')
    if not os.path.exists(subreddit_dir):
        os.makedirs(subreddit_dir)

    with open(os.path.join(subreddit_dir, f'{post_id}.json'), 'w') as f:
        json.dump(data, f, indent=4)

def main():
    for subreddit in SUBREDDITS:

        about_data = parse_about(subreddit)
        if about_data:
            write_about(subreddit, about_data)
            print(f'About data for subreddit {subreddit} written to about.md')
        after = ''

        while True:
            posts, after = parse(subreddit, after)
            if not posts or after is None:
                break
            for post in posts:
                write_to_json(subreddit, post['id'], post)
                print(f'Data for post {post["id"]} in subreddit {subreddit} written to JSON')

if __name__ == '__main__':
    main()