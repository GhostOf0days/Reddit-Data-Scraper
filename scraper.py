import requests
import json
import os
import re
from dask.distributed import Client
from dask import delayed

# Add subreddits to scrape as strings here (e.g. 'artificial') [Remove subreddits from array before commits]
SUBREDDITS = []  
DATA_DIRECTORY = 'subreddit-data'

def parse_about(subreddit):
    url = f'https://www.reddit.com/r/{subreddit}/about.json'
    url_rules = f'https://www.reddit.com/r/{subreddit}/about/rules.json'
    headers = {'User-agent': 'Reddit Data Scraper'}
    response = requests.get(url, headers=headers)
    response_rules = requests.get(url_rules, headers=headers)

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

def parse_top(subreddit):
    urlTemplate = 'https://www.reddit.com/r/{}/top.json?limit=100&t=all'
    headers = {'User-agent': 'Reddit Data Scraper'}
    url = urlTemplate.format(subreddit)

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
            post_url = f"https://www.reddit.com/r/{subreddit}/comments/{postID}"
            postText = postData.get('selftext', '')  # Get post content/description

            all_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', postText)
            media_file_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'webm']
            media_urls = [url for url in all_urls if any(url.endswith(ext) for ext in media_file_extensions)]
            other_urls = [url for url in all_urls if url not in media_urls]

            media_url = postData.get('url') if postData['is_video'] or 'preview' in postData else None
            if media_url:
                media_urls.append(media_url)

            comments = parse_comments(subreddit, postID)

            posts.append({'id': postID, 'score': score, 'title': postTitle,
                          'author': author, 'date': date, 'url': post_url, 
                          'media_urls': media_urls, 'other_urls': other_urls, 
                          'postText': postText, 'comments': comments})
        return posts
    else:
        print(f'Error {response.status_code}')
        return None

# Do the same for parse function as well.
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
            post_url = f"https://www.reddit.com/r/{subreddit}/comments/{postID}"
            postText = postData.get('selftext', '')  # Get post content/description

            all_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', postText)
            media_file_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'webm']
            media_urls = [url for url in all_urls if any(url.endswith(ext) for ext in media_file_extensions)]
            other_urls = [url for url in all_urls if url not in media_urls]

            media_url = postData.get('url') if postData['is_video'] or 'preview' in postData else None
            if media_url:
                media_urls.append(media_url)

            comments = parse_comments(subreddit, postID)

            posts.append({'id': postID, 'score': score, 'title': postTitle,
                          'author': author, 'date': date, 'url': post_url, 
                          'media_urls': media_urls, 'other_urls': other_urls, 
                          'postText': postText, 'comments': comments})
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

def write_to_json(subreddit, post_id, data):
    subreddit_dir = os.path.join(DATA_DIRECTORY, f'r-{subreddit}')
    if not os.path.exists(subreddit_dir):
        os.makedirs(subreddit_dir)

    with open(os.path.join(subreddit_dir, f'{post_id}.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# This is a wrapper function for everything a single subreddit has to do
@delayed
def process_subreddit(subreddit):
    about_data = parse_about(subreddit)
    if about_data:
        write_about(subreddit, about_data)
        print(f'About data for subreddit {subreddit} written to about.md')
                
    # top_posts = parse_top(subreddit)
    # if top_posts:
    #     for post in top_posts:
    #         write_to_json(subreddit, post['id'], post)
    #         print(f'Data for top post {post["id"]} in subreddit {subreddit} written to JSON')

    # after = ''
    
    # while True:
    #     posts, after = parse(subreddit, after)
    #     if not posts or after is None:
    #         break
    #     for post in posts:
    #         write_to_json(subreddit, post['id'], post)
    #         print(f'Data for post {post["id"]} in subreddit {subreddit} written to JSON')

def main():
    client = Client()  # set up local cluster
    print(client)
    
    results = []
    for subreddit in SUBREDDITS:
        result = process_subreddit(subreddit)
        if result is not None:  # Check if the result is not None
            results.append(result)
    
    if results:  # Check if the results list is not empty
        total = delayed(sum)(results)  # aggregate with a sum function
        total.compute()  # execute

if __name__ == '__main__':
    main()