from typing import List
import argparse
import json
from config import logging
import random

import InstagramBot

def load_credentials() -> dict:
    with open('creds.json', 'r') as f:
        stuff = f.read()
        creds = json.loads(stuff)
        return creds
    
def load_comments(args: argparse.ArgumentParser) -> List[str]:
    # TODO: use args for if args.comments, then load comments, otherwise return empty list.
    with open('comments.txt', 'r') as f:
        comments = f.readlines()
        return comments

def load_hash_tags(args: argparse.ArgumentParser) -> List[str]:
    # TODO: utilize argument parser.
    with open('hash_tags.txt', 'r') as f:
        hash_tags = f.readlines()
        return hash_tags

def run(args: argparse.ArgumentParser):
    credentials = load_credentials()
    comments = load_comments(args)
    hash_tags = load_hash_tags(args)

    # Login steps
    bot = InstagramBot.InstagramBot()
    logging.info("Logging in to " + credentials['username'])
    bot.login(email=credentials['username'], password=credentials['password'])
    
    bot.ignore_save_your_login_info()
    # TODO: Verify login
    logging.info('logged in.')
    bot.ignore_turn_on_notifications()

    logging.warning('ASSUMING THAT WE WILL BE MAKING COMMENTS')
    for hash_tag in hash_tags:
        post_links = bot.scrape_hashtag_posts(hash_tag)
        for link in post_links:
            comment = random.choice(comments)
            bot.comment_on_posts([link], comment, 5)

    logging.info(f"total comments made during run {bot.comments_made}")
    logging.info("total comments skipped because the Comment element could not be found {bot.comments_skipped_because_could_not_find}")
    bot.quit()









    