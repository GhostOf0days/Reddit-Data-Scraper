import requests
import json
import os
import re
import argparse
from dask.distributed import Client
from dask import delayed
from collections import deque

DATA_DIRECTORY = 'subreddit-data'
PROXIES_FILE = 'proxies.txt'

def get_proxies():
    proxies = []
    with open(PROXIES_FILE, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                proxies.append(line)
    return proxies

def parse_about(subreddit, proxies):
    url = f'https://www.reddit.com/r/{subreddit}/about.json'
    url_rules = f'https://www.reddit.com/r/{subreddit}/about/rules.json'
    headers = {'User-agent': 'Reddit Data Scraper'}
    proxies = {'https': proxies}
    response = requests.get(url, headers=headers, proxies=proxies)
    response_rules = requests.get(url_rules, headers=headers, proxies=proxies)

    if response.ok and response_rules.ok:
        data = response.json()['data']
        rules_data = response_rules.json()['rules']
        rules = [rule['short_name'] + ': ' + rule['description'] for rule in rules_data]
        about_data = {
            'name': data['display_name'],
            'subscribers': data['subscribers'],
            'created_utc': data['created_utc'],
            'description': data['public_description'],
            'rules': rules
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
            author = child['data']['author']
            replies = child['data']['replies']
            if replies and 'data' in replies:
                reply_comments = parse_comments_recursive(replies['data'], level=level+1)
                comments.append({'level': level, 'comment': comment, 'score': score, 'author': author, 'replies': reply_comments})
            else:
                comments.append({'level': level, 'comment': comment, 'score': score, 'author': author})
    return comments

def parse_comments(subreddit, post_id, proxies):
    url = f'https://www.reddit.com/r/{subreddit}/comments/{post_id}.json'
    headers = {'User-agent': 'Reddit Data Scraper'}
    proxies = {'https': proxies}
    response = requests.get(url, headers=headers, proxies=proxies)
    
    if response.ok:
        data = response.json()
        comments = parse_comments_recursive(data[1]['data'])
        return comments
    else:
        print(f'Error {response.status_code}')
        return None

def parse_top(subreddit, proxies):
    urlTemplate = 'https://www.reddit.com/r/{}/top.json?limit=100&t=all'
    headers = {'User-agent': 'Reddit Data Scraper'}
    url = urlTemplate.format(subreddit)

    proxies_queue = deque(proxies)  # Initialize a deque object with the proxies
    proxies = {'https': proxies_queue[0]}  # Use the first proxy from the deque
    print(f"Using proxy: {proxies}")

    response = requests.get(url, headers=headers, proxies=proxies)
    
    if response.ok:
        data = response.json()['data']
        posts = []

        post_count = 0  # Initialize the post count

        for post in data['children']:
            postData = post['data']
            postID = postData['id']
            score = postData['score']
            postTitle = postData['title']
            author = postData['author']
            date = postData['created_utc']
            post_url = f"https://www.reddit.com/r/{subreddit}/comments/{postID}"
            postText = postData.get('selftext', '')  # Get post content/description

            all_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', postText)
            media_file_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'webm']
            media_urls = [url for url in all_urls if any(url.endswith(ext) for ext in media_file_extensions)]
            other_urls = [url for url in all_urls if url not in media_urls]

            media_url = postData.get('url') if postData['is_video'] or 'preview' in postData else None
            if media_url:
                media_urls.append(media_url)

            comments = parse_comments(subreddit, postID, proxies)

            posts.append({'id': postID, 'score': score, 'title': postTitle,
                          'author': author, 'date': date, 'url': post_url, 
                          'media_urls': media_urls, 'other_urls': other_urls, 
                          'postText': postText, 'comments': comments})
            
            post_count += 1  # Increment the post count

            if post_count % 25 == 0:  # Rotate the proxies after every 25 posts
                proxies_queue.append(proxies_queue.popleft())
                proxies = {'https': proxies_queue[0]}  # Use the first proxy from the deque
                print(f"Switched to proxy: {proxies}")

        return posts
    else:
        print(f'Error {response.status_code}')
        return None

def parse(subreddit, after='', proxies=None):
    urlTemplate = 'https://www.reddit.com/r/{}.json?{}'
    headers = {'User-agent': 'Reddit Data Scraper'}
    params = '' if not after else 'after=' + after
    url = urlTemplate.format(subreddit, params)

    proxies_queue = deque(proxies)  # Initialize a deque object with the proxies
    proxies = {'https': proxies_queue[0]}  # Use the first proxy from the deque
    print(f"Using proxy: {proxies}")

    response = requests.get(url, headers=headers, proxies=proxies)
    
    if response.ok:
        data = response.json()['data']
        posts = []

        post_count = 0  # Initialize the post count

        for post in data['children']:
            postData = post['data']
            postID = postData['id']
            score = postData['score']
            postTitle = postData['title']
            author = postData['author']
            date = postData['created_utc']
            post_url = f"https://www.reddit.com/r/{subreddit}/comments/{postID}"
            postText = postData.get('selftext', '')  # Get post content/description

            all_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', postText)
            media_file_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'webm']
            media_urls = [url for url in all_urls if any(url.endswith(ext) for ext in media_file_extensions)]
            other_urls = [url for url in all_urls if url not in media_urls]

            media_url = postData.get('url') if postData['is_video'] or 'preview' in postData else None
            if media_url:
                media_urls.append(media_url)

            comments = parse_comments(subreddit, postID, proxies)

            posts.append({'id': postID, 'score': score, 'title': postTitle,
                          'author': author, 'date': date, 'url': post_url, 
                          'media_urls': media_urls, 'other_urls': other_urls, 
                          'postText': postText, 'comments': comments})
            
            post_count += 1  # Increment the post count

            if post_count % 25 == 0:  # Rotate the proxies after every 25 posts
                proxies_queue.append(proxies_queue.popleft())
                proxies = {'https': proxies_queue[0]}  # Use the first proxy from the deque
                print(f"Switched to proxy: {proxies}")

        return posts, data['after']
    else:
        print(f'Error {response.status_code}')
        return None, None
    
def write_about(subreddit, data):
    subreddit_dir = os.path.join(DATA_DIRECTORY, f'r-{subreddit}')
    if not os.path.exists(subreddit_dir):
        os.makedirs(subreddit_dir)

    about_file = os.path.join(subreddit_dir, 'about.md')
    with open(about_file, 'w', encoding='utf-8') as f:
        f.write(f'# About r/{data["name"]}\n\n')
        f.write(f'Subscribers: {data["subscribers"]}\n\n')
        f.write(f'Created UTC: {data["created_utc"]}\n\n')
        if data["description"]:
            f.write(f'Description:\n\n{data["description"]}\n\n')
        if data["rules"]:
            f.write('Rules:\n\n')
            for rule in data['rules']:
                f.write(f'{rule}\n\n')

def write_to_json(subreddit, post_id, data, proxy):
    subreddit_dir = os.path.join(DATA_DIRECTORY, f'r-{subreddit}')
    if not os.path.exists(subreddit_dir):
        os.makedirs(subreddit_dir)

    with open(os.path.join(subreddit_dir, f'{post_id}.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# This is a wrapper function for everything a single subreddit has to do
@delayed
def process_subreddit(subreddit, proxies=None):
    about_data = parse_about(subreddit, proxies)
    if about_data:
        write_about(subreddit, about_data)
        print(f'About data for subreddit {subreddit} written to about.md')
                
    top_posts = parse_top(subreddit, proxies)
    if top_posts:
        for post in top_posts:
            print(f'Data for top post {post["id"]} in subreddit {subreddit} written to JSON')

    after = ''
    
    while True:
        posts, after = parse(subreddit, after, proxies)
        if not posts or after is None:
            break
        for post in posts:
            write_to_json(subreddit, post['id'], post)
            print(f'Data for post {post["id"]} in subreddit {subreddit} written to JSON')

def main():
    parser = argparse.ArgumentParser(description='Reddit Data Scraper')
    parser.add_argument('--skip-parsed', action='store_true', help='Skip parsing subreddits that have already been parsed')
    args = parser.parse_args()

    client = Client()  # set up local cluster
    print(client)
    
    proxies = get_proxies()
    
    results = []
    with open('subreddits.txt', 'r', encoding='utf-8') as file:
        subreddits = [line.strip() for line in file if line.strip() and not line.strip().startswith("#")]
        for subreddit in subreddits:
            if args.skip_parsed:
                subreddit_dir = os.path.join(DATA_DIRECTORY, f'r-{subreddit}')
                if os.path.exists(subreddit_dir):
                    print(f'Skipping subreddit {subreddit} as it has already been parsed')
                    continue
            proxy = proxies.pop(0) if proxies else None
            result = process_subreddit(subreddit, proxy)
            if result is not None:  # Check if the result is not None
                results.append(result)
    
    if results:  # Check if the results list is not empty
        total = delayed(sum)(results)  # aggregate with a sum function
        total.compute()  # execute

if __name__ == '__main__':
    main()