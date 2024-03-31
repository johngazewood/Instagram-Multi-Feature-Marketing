#!/usr/bin/env python3

import argparse
import customtkinter
import logging

from InstagramBot import InstagramBot
import ui_app
import headless_app

def set_logging():
    logging.basicConfig(level=logging.INFO)

def get_args():
    parser = argparse.ArgumentParser(description="Instagram Bot")

    parser.add_argument("-c", "--comment", action="store_true", help="Comment on posts")
    parser.add_argument("-d", "--dm", action="store_true", help="Send direct messages")
    parser.add_argument("-ht", "--hashtag", help="Hashtag to scrape posts from")
    parser.add_argument("-cm", "--message", help="Comment or message to post")
    parser.add_argument("-del", "--delay", type=int, default=5, help="Delay in seconds between actions")
    parser.add_argument("-ui", "--user_interface", type=bool, default=False)
    
    args = parser.parse_args()
    return args

def main():
    set_logging()
    args = get_args()

    if args.user_interface:
        app: customtkinter.CTk = ui_app.create_ui_app(args)
        app.mainloop()
    else:
        logging.info('running headless')
        headless_app.run(args)


if __name__ == "__main__":
    main()

