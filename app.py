import os
from flask import Flask, render_template
import praw
import matplotlib.pyplot as plt
import datetime

app = Flask(__name__)

# Set up Reddit API using environment variables
reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT")
)

SUBREDDIT_NAME = "Conservative"

@app.route("/")
def home():
    try:
        subreddit = reddit.subreddit(SUBREDDIT_NAME)
        top_posts = subreddit.top(time_filter="day", limit=5)

        post_titles = []
        post_scores = []
        comment_counts = []

        for post in top_posts:
            post_titles.append(post.title[:50] + ("..." if len(post.title) > 50 else ""))
            post_scores.append(post.score)
            comment_counts.append(post.num_comments)

            try:
                post.comments.replace_more(limit=0)
            except Exception as e:
                print(f"Comment error: {e}")

        # Chart 1: Upvotes
        plt.figure(figsize=(10, 5))
        plt.barh(post_titles, post_scores, color='blue')
        plt.xlabel("Upvotes")
        plt.title("Top 5 Posts by Upvotes")
        plt.tight_layout()
        try:
            plt.savefig("static/upvotes_chart.png")
        except Exception as e:
            print(f"Failed to save upvotes chart: {e}")
        plt.close()

        # Chart 2: Comments
        plt.figure(figsize=(10, 5))
        plt.barh(post_titles, comment_counts, color='green')
        plt.xlabel("Comments")
        plt.title("Top 5 Posts by Comment Count")
        plt.tight_layout()
        try:
            plt.savefig("static/comments_chart.png")
        except Exception as e:
            print(f"Failed to save comments chart: {e}")
        plt.close()

        return render_template("index.html", updated=datetime.datetime.now())

    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
