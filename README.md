# Reddit-Data-Scraper

Reddit Data Scraper is a distributed computing-based scraper designed to automatically scrape data from multiple subreddits. Its primary objective is to enable efficient data retrieval from Reddit before any potential changes in the Reddit API that might increase the cost of data acquisition.

Please note there are two scraper files, scraper.py and scraper-with-proxy-rotation.py. Currently, scraper-with-proxy-rotation.py is broken, but its purpose is proxy rotation. Proxy rotation is essentially when you rotate a queue of proxies (with format ip:port) after every x number of requests and ensure your request uses the first item in the queue to prevent rate limiting.

Usage:

1. Clone the repository and navigate to the project directory.

2. Install the required dependencies by running the following command:
```pip install -r requirements.txt```

3. Open the subreddits.txt file and add as many subreddits as you want to scrape below the comment with one subreddit line per name. The names should be case-sensitive. Save the file. Note that the subreddit names should be valid and existing subreddits.

4. Check if the subreddits exist by running the following command:
```python subreddit-check.py```

5. Remove non-existent subreddits.

6. (Optional) Run add-subreddits-from-directory.py if you would like previously parsed subreddits to be reparsed.

7. (Optional) If you would like to use proxy rotation, open the proxies.txt file and add your proxies below the comment with one proxy per line in the form of ip:port. Save the file. Make sure your proxies are valid.

8. Run the script by executing the following command (For proxy rotation, run 'python scraper-wth-proxy-rotation.py'):
```python scraper.py```
The script will automatically scrape data from all the subreddits specified in the subreddits.txt file using distributed computing. It will save the data in the subreddit-data directory. The data will be stored in separate subdirectories for each subreddit.
Note: If you want to skip already parsed subreddits that are also in subreddits.txt, add '--skip-parsed' at the end of the aforementioned command.

9. Run success-check py by executing the following command:
```python success-check.py```
If any subreddits were unsuccessfully scraped, remove all subreddits from the subreddits.txt file, keeping the comment, and restart from step 3 for the unsuccessful subreddits.

10. Remove all subreddits from the subreddits.txt file. Keep the comment.

11. Commit your changes, but do not commit changes to subreddits.txt and proxies.txt.

12. Create a pull request (PR) with your changes, mentioning the subreddits you have scraped and any additional modifications you made.

13. Your PR will be reviewed, and if everything is in order, it will be merged into the main repository.

Note: Don't worry about errors that appear. However, Error 403 means that specific subreddit is private. Remove that subreddit and rerun the parser for the other ones. Also, it may say Compute Failed. Don't worry the scraper still worked and correctly added files. Also, less distribution by scraping less subreddits at a time means more scraping power for each subreddit. As for