# Reddit-Data-Scraper

Reddit Data Scraper is a distributed computing-based scraper designed to automatically scrape data from multiple subreddits. Its primary objective is to enable efficient data retrieval from Reddit before any potential changes in the Reddit API that might increase the cost of data acquisition.

Usage:

1. Clone the repository and navigate to the project directory.

2. Install the required dependencies by running the following command:
```pip install -r requirements.txt```

3. Open the subreddits.txt file and add as many subreddits as you want to scrape below the comment with one subreddit line per name.The names should be case-sensitive. Note that the subreddit names should be valid and existing subreddits.

4. Run the script by executing the following command:
```python scraper.py```
The script will automatically scrape data from all the subreddits specified in the subreddits.txt file using distributed computing. It will save the data in the subreddit-data directory. The data will be stored in separate subdirectories for each subreddit.
Note: If you want to skip already parsed subreddits add '--skip-parsed' at the end of the aforementioned command.

5. Remove all subreddits from the subreddits.txt file. Keep the comment.

6. Commit your changes, including the updated scraper.py file.

7. Create a pull request (PR) with your changes, mentioning the subreddits you have scraped and any additional modifications you made.

8. Your PR will be reviewed, and if everything is in order, it will be merged into the main repository.

Note: Don't worry about errors that appear. However, Error 403 means that specific subreddit is private. Also, it may say Compute Failed. Don't worry the scraper still worked and correctly added files.