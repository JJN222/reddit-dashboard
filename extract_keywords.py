import praw
from collections import Counter
import re

# Replace with your Reddit credentials
reddit = praw.Reddit(
    client_id="3-HcG4Imphx9YgIlTMj4gA",
    client_secret="xVcRzgog4A4FZoNMDyVHR2yAlqbCCA",
    user_agent="script:reddit-keyword-analyzer:v1.0 (by u/Ruhtorikal)"
)

# Common stopwords to ignore
stopwords = {
    'the', 'and', 'to', 'of', 'a', 'in', 'is', 'on', 'for', 'with', 'that',
    'at', 'by', 'from', 'this', 'it', 'as', 'an', 'are', 'be', 'was', 'but',
    'or', 'not', 'if', 'they', 'has', 'have', 'had', 'about', 'you', 'will',
    'just', 'up', 'out', 'we', 'all', 'who', 'what', 'so', 'their', 'how',
    'can', 'our', 'would', 'do', 'does', 'been'
}

# Get top 100 post titles from today
subreddit = reddit.subreddit("Conservative")
titles = [post.title for post in subreddit.top(limit=100, time_filter='day')]

# Clean and split words
words = []
for title in titles:
    title = re.sub(r"[^\w\s]", "", title.lower())  # remove punctuation
    words.extend(title.split())

# Filter and count
filtered = [word for word in words if word not in stopwords and len(word) > 2]
counts = Counter(filtered)

# Show top 50 keywords
print("\nTop Keywords:\n")
for word, count in counts.most_common(50):
    print(f"{word}: {count}")

