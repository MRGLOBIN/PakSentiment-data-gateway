import asyncio

import asyncpraw
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["config/settings.toml", "config/.secrets.toml"],
    environments=True,
    envvar_prefix="PAKSENTIMENT"
)

async def fetch_reddit_posts(tag):
    reddit = asyncpraw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent=settings.REDDIT_USER_AGENT
    )

    subreddit = await reddit.subreddit('pakistan')
    async for post in subreddit.hot(limit=3):
        print("------------------------------")
        print(f"{post.title}")
        print(post.selftext)
        print("AUTHOR: ", post.author)
        print("------------------------------")

    await reddit.close()
 


asyncio.run(fetch_reddit_posts('tag'))
