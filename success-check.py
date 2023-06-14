import os

# Path to the parent directory
parent_dir = 'subreddit-data'

parse_successful = True

failed_subreddits = []

# Iterate over all subdirectories in the parent directory
for subdir in os.listdir(parent_dir):
    subdir_path = os.path.join(parent_dir, subdir)
    # Check if the path is a directory
    if os.path.isdir(subdir_path):
        # Get a list of all files in the subdirectory
        files = os.listdir(subdir_path)
        # Check if there is at least one .json file and one .md file
        if not (any(file.endswith('.json') for file in files) and any(file.endswith('.md') for file in files)):
            failed_subreddits.append(subdir.replace("-r", ""))
            parse_successful = False

if parse_successful:
    print('Scrape was successful!')
else:
    print('Scrape was unsuccessful for subreddits ' + ', '.join([sub.replace('-', '/') for sub in failed_subreddits]) + '. Please try again.')