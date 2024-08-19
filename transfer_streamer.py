import tweepy
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def create_api():

    auth = tweepy.OAuthHandler("YGPP8hPJkPYORFE1Ng1UChwjB",
                               "V7k8BGt8vY7GSGhK6c26LMUQKyNDv9HvkhzsElCv3T4UL6djVy")
    auth.set_access_token("1304501171449737216-exR7VDevY82Xbsxn8DAa2HUmvMHVIo",
                          "L3j7LTtYAwGcad1fnrfAYWHteY2GZ3LkrvfPa0Hm4Xxxn")
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


class FavRetweetListener(tweepy.StreamListener):
    def __init__(self, api):
        super().__init__(api)
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        logger.info(f"Processing tweet id {tweet.id}")
        if tweet.in_reply_to_status_id is not None or \
            tweet.user.id == self.me.id:
            # This tweet is a reply or I'm its author so, ignore it
            return
        if not tweet.favorited:
            # Mark it as Liked, since we have not done it yet
            try:
                tweet.favorite()
            except Exception as e:
                logger.error("Error on fav", exc_info=True)
        if not tweet.retweeted:
            # Retweet, since we have not retweeted it yet
            try:
                tweet.retweet()
            except Exception as e:
                logger.error("Error on fav and retweet", exc_info=True)

    def on_error(self, status):
        logger.error(status)


def main(keywords):
    api = create_api()
    tweets_listener = FavRetweetListener(api)
    stream = tweepy.Stream(api.auth, tweets_listener)
    stream.filter(track=keywords, languages=["en"])


if __name__ == "__main__":
    main(["Python", "Tweepy"])
