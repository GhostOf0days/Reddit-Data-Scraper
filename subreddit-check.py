import requests

# Open the file and read the subreddit names
with open('subreddits.txt', 'r', encoding='utf-8') as f:
    subreddits = [line.strip() for line in f if not line.startswith('#')]

# List to hold names of failed subreddits
failed_subreddits = []

# Iterate over each subreddit
for subreddit in subreddits:
    # Send a GET request to the subreddit URL
    response = requests.get(f'https://www.reddit.com/r/{subreddit}', headers = {'User-agent': 'Mozilla/5.0'})

    # Check if the status code is not 200
    if response.status_code != 200:
        failed_subreddits.append(subreddit)

# Print the failed subreddits
if failed_subreddits:
    print('The following subreddits do not exist: ' + ', '.join(failed_subreddits))
else:
    print('All subreddits exist.')
