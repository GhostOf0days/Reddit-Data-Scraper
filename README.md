# Reddit-Data-Scraper

Reddit Data Scraper is a distributed computing-based scraper designed to automatically scrape data from multiple subreddits. Its primary objective is to enable efficient data retrieval from Reddit before any potential changes in the Reddit API that might increase the cost of data acquisition.

Please note there are two scraper files, scraper.py and scraper-with-proxy-rotation.py. Currently, scraper-with-proxy-rotation.py is broken, but its purpose is proxy rotation. Proxy rotation is essentially when you rotate a queue of proxies (with format ip:port) after every x number of requests and ensure your request uses the first item in the queue to prevent rate limiting.

Usage:

1. Clone the repository and navigate to the project directory.

2. Install the required dependencies by running the following command:
```pip install -r requirements.txt```

3. Open the subreddits.txt file and add as many subreddits as you want to scrape below the comment with one subreddit line per name. The names should be case-sensitive. Note that the subreddit names should be valid and existing subreddits.

4. (Optional) Run add-subreddits-from-directory.py if you would like previously added subreddits to be reparsed.

5. (Optional) If you would like to use proxy rotation, open the proxies.txt file and add your proxies below the comment with one proxy per line in the form of ip:port. Make sure your proxies are valid.

6. Run the script by executing the following command (For proxy rotation, run 'python scraper-wth-proxy-rotation.py'):
```python scraper.py```
The script will automatically scrape data from all the subreddits specified in the subreddits.txt file using distributed computing. It will save the data in the subreddit-data directory. The data will be stored in separate subdirectories for each subreddit.
Note: If you want to skip already parsed subreddits that are also in subreddits.txt, add '--skip-parsed' at the end of the aforementioned command.

7. Remove all subreddits from the subreddits.txt file. Keep the comment.

8. Commit your changes, including the updated scraper.py file.

9. Create a pull request (PR) with your changes, mentioning the subreddits you have scraped and any additional modifications you made.

10. Your PR will be reviewed, and if everything is in order, it will be merged into the main repository.

Note: Don't worry about errors that appear. However, Error 403 means that specific subreddit is private. Also, it may say Compute Failed. Don't worry the scraper still worked and correctly added files.