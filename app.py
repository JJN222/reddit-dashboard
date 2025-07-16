from flask import Flask, render_template, request
import praw
import datetime
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

app = Flask(__name__)

reddit = praw.Reddit(
    client_id="3-HcG4Imphx9YgIlTMj4gA",
    client_secret="xVcRzgog4A4FZoNMDyVHR2yAlqbCCA",
    user_agent="script:reddit-sentiment-analyzer:v1.0 (by u/Ruhtorikal)"
)

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
    selected_tag = request.args.get("tag")

    subreddit = reddit.subreddit("Conservative")
    posts = subreddit.top(limit=50, time_filter='day')  # Top 50 posts today

    post_data = []
    topic_counts = Counter()
    topic_upvotes = defaultdict(int)

    for post in posts:
        title = post.title
        text = post.selftext or ""
        topics = detect_topics(title + " " + text)

        if selected_tag and selected_tag not in topics:
            continue

        top_comments = []
        post.comments.replace_more(limit=0)
        for comment in post.comments[:3]:
            top_comments.append({
                "body": comment.body[:200] + ("..." if len(comment.body) > 200 else ""),
                "upvotes": comment.score
            })

        post_info = {
            "title": title,
            "upvotes": post.score,
            "comments": post.num_comments,
            "created": datetime.datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            "author": str(post.author),
            "flair": post.link_flair_text,
            "text": text[:300] + ("..." if len(text) > 300 else ""),
            "url": f"https://reddit.com{post.permalink}",
            "topics": topics,
            "top_comments": top_comments
        }

        post_data.append(post_info)

        for topic in topics:
            topic_counts[topic] += 1
            topic_upvotes[topic] += post.score

    # Chart 1: Post Count per Topic
    if topic_counts:
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        tags1, counts1 = zip(*topic_counts.most_common(10))
        ax1.barh(tags1, counts1)
        ax1.set_title("Number of Top Posts per Topic")
        ax1.invert_yaxis()
        plt.tight_layout()
        if not os.path.exists("static"):
            os.makedirs("static")
        plt.savefig("static/post_count_chart.png")
        plt.close()

    # Chart 2: Total Upvotes per Topic
    if topic_upvotes:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        tags2, counts2 = zip(*sorted(topic_upvotes.items(), key=lambda x: x[1], reverse=True)[:10])
        ax2.barh(tags2, counts2)
        ax2.set_title("Total Upvotes per Topic")
        ax2.invert_yaxis()
        plt.tight_layout()
        plt.savefig("static/upvotes_chart.png")
        plt.close()

    return render_template("index.html", posts=post_data, tags=sorted(TOPIC_KEYWORDS.keys()), selected_tag=selected_tag)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

