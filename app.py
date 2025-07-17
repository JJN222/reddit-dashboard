import os
from flask import Flask, render_template, request
import praw
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import datetime

app = Flask(__name__)

# Set up Reddit API using environment variables
reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent=os.environ.get("REDDIT_USER_AGENT")
)

SUBREDDIT_NAME = "Conservative"

TOPIC_KEYWORDS = {
    "Trump": ["trump", "donald", "maga", "45th president"],
    "Biden": ["biden", "joe", "hunter", "bidens"],
    "Obama": ["obama", "barack"],
    "Clinton": ["clinton", "hillary", "bill clinton"],
    "Epstein": ["epstein", "ghislaine", "client list", "pedophile island"],
    "DOJ/FBI": ["doj", "fbi", "justice department", "comey", "wray"],
    "Congress": ["house", "senate", "congress", "speaker"],
    "Elections": ["election", "ballots", "mail-in"],
    "Mainstream Media": ["cnn", "msnbc", "nyt", "fake news"],
    "Big Tech": ["twitter", "facebook", "meta", "google", "youtube"],
}

def detect_topics(text):
    topics = set()
    text_lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.add(topic)
    return list(topics)

@app.route("/")
def home():
    try:
        selected_tag = request.args.get("tag")

        subreddit = reddit.subreddit(SUBREDDIT_NAME)
        posts = list(subreddit.top(time_filter="day", limit=25))

        post_data = []
        topic_upvotes = defaultdict(int)
        topic_counts = Counter()

        for post in posts:
            title = post.title
            text = post.selftext or ""
            topics = detect_topics(title + " " + text)

            try:
                post.comments.replace_more(limit=0)
                top_comment_obj = post.comments[0] if post.comments else None
                top_comment = {
                    "body": top_comment_obj.body[:200] + ("..." if len(top_comment_obj.body) > 200 else ""),
                    "upvotes": top_comment_obj.score
                } if top_comment_obj else None
            except Exception as e:
                print(f"Comment fetch error: {e}")
                top_comment = None

            post_data.append({
                "title": title,
                "upvotes": post.score,
                "comments": post.num_comments,
                "created": datetime.datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                "author": str(post.author),
                "flair": post.link_flair_text,
                "text": text[:300] + ("..." if len(text) > 300 else ""),
                "url": f"https://reddit.com{post.permalink}",
                "topics": topics,
                "top_comment": top_comment
            })

            for topic in topics:
                topic_upvotes[topic] += post.score
                topic_counts[topic] += 1

        # 🔍 Filter by selected topic
        if selected_tag:
            post_data = [p for p in post_data if selected_tag in p["topics"]]

        # 📊 Chart: Top Topics by Upvotes
        if topic_upvotes:
            fig, ax = plt.subplots(figsize=(10, 5))
            tags, upvotes = zip(*sorted(topic_upvotes.items(), key=lambda x: x[1], reverse=True)[:10])
            ax.barh(tags, upvotes)
            ax.set_title("Top Topics by Upvotes")
            ax.invert_yaxis()
            plt.tight_layout()
            if not os.path.exists("static"):
                os.makedirs("static")
            plt.savefig("static/upvotes_chart.png")
            plt.close()

        return render_template("index.html", posts=post_data, tags=sorted(TOPIC_KEYWORDS.keys()), selected_tag=selected_tag, updated=datetime.datetime.now())

    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)