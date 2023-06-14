import os

DATA_DIRECTORY = 'subreddit-data'

def main():
    existing_subreddits = set()

    with open('subreddits.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignore comments
                existing_subreddits.add(line)

    new_subreddits = []

    for item in os.listdir(DATA_DIRECTORY):
        if item.startswith('r-') and os.path.isdir(os.path.join(DATA_DIRECTORY, item)):
            subreddit = item[2:]
            if subreddit not in existing_subreddits:
                new_subreddits.append(subreddit)

    if new_subreddits:
        with open('subreddits.txt', 'a', encoding='utf-8') as file:
            file.write('\n'.join(new_subreddits))
            file.write('\n')

if __name__ == '__main__':
    main()