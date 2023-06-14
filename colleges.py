import requests
import csv

# URL of the CSV file
url = 'https://raw.githubusercontent.com/karlding/college-subreddits/master/data/colleges.csv'

# Send HTTP request to the URL and save the response
response = requests.get(url)

# Decode the response text
decoded_content = response.content.decode('utf-8')

# Read the CSV data
csv_reader = csv.reader(decoded_content.splitlines(), delimiter=',')

# Open the file to append the subreddit names
with open('subreddits.txt', 'a', encoding = 'utf-8') as f:
    # Skip header row
    next(csv_reader)
    counter = 0
    # Iterate over each row in the CSV file
    for row in csv_reader:
        counter += 1
        # Append the subreddit name to the file
        if counter > 15:
            f.write('# ')
        f.write(row[2] + '\n')  # assuming the subreddit is in the third column