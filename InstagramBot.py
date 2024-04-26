import time
import json
import logging
#from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from persist_activity import SavedComment
import config


class InstagramBot:
    comments_made = 0
    comments_skipped_because_could_not_find = 0

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=930,820")
        # chrome_options.add_argument("--start-maximized")  # Maximize the Chrome window
        # Use webdriver_manager to automatically download and manage the ChromeDriver
        # add undetected_chromedriver here 
        self.driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def login(self, email, password):
        # Open Instagram
        self.driver.get("https://www.instagram.com/")
        # Wait for the login elements to become available
        wait = WebDriverWait(self.driver, 10)
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))

        # Find the login elements and enter email and password
        email_field.send_keys(email)
        password_field.send_keys(password)

        # Submit the login form
        password_field.send_keys(Keys.RETURN)

        # Wait for the login process to complete (you may need to adjust the delay based on your internet speed)
        time.sleep(config.DEFAULT_DELAY_SECONDS)

    def scrape_hashtag_posts(self, hashtag):
        # Open Instagram and navigate to the hashtag page
        self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
        time.sleep(8)
        # Wait for the posts to load
        wait = WebDriverWait(self.driver, 10)
        # most_recent = self.driver.find_element(By.XPATH, '//div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/article/div[2]/div')
        main_element = self.driver.find_element(By.TAG_NAME, 'main')
        article_element = main_element.find_element(By.TAG_NAME, 'article')
        
        # Scrape the most recent posts from the hashtag
        posts = article_element.find_elements(By.TAG_NAME, "a")

        links = []
        for post in posts:
            # Retrieve the href attribute value
            href = post.get_attribute("href")
            # Process each href as needed
            links.append(href)
        
        return links
    
    def scrape_usernames(self, links):
        usernames = []
        for link in links:
            self.driver.get(link)
            time.sleep(3)
            # Wait for the username element to load
            wait = WebDriverWait(self.driver, 10)
            username_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div[1]/div/div[2]/div/div[1]/header/div[2]/div[1]/div[1]/div/div/span/div/div/a')))
            # Extract the username text
            username = username_element.text
            usernames.append(username)
        
        # Remove duplicate usernames
        usernames = list(set(usernames))
        
        return usernames
    
    def send_dm(self, usernames, message, delay_time):
        # Go to the Instagram Direct Inbox
        self.driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(3)

        # Check if the notification pop-up is displayed
        notification_popup = self.driver.find_element(By.XPATH, '//div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]')
        if notification_popup.is_displayed():
            notification_popup.click()
            time.sleep(2)

       
        for username in usernames:
             # Click the 'New Message' button
            new_message_button = self.driver.find_element(By.XPATH, '//div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/div/div/div/div[1]/div/div[1]/div/div[1]/div[2]/div/div')
            new_message_button.click()
            time.sleep(2)

            # Wait for the recipient input field to become available
            wait = WebDriverWait(self.driver, 10)
            recipient_input = wait.until(EC.presence_of_element_located((By.XPATH, '//div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div[2]/input')))

            # Type each username and press Enter to add as a recipient
            recipient_input.send_keys(username)
            time.sleep(1)
            recipient_input.send_keys(Keys.ENTER)
            time.sleep(1)

            
            select_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div')))
            select_button.click()
            time.sleep(2)

            # Wait for the next button to become clickable
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[4]/div')))

            # Click the Next button to proceed to the message input
            next_button.click()
            time.sleep(3)

            # Create an instance of ActionChains
            actions = ActionChains(self.driver)
            actions.send_keys(message)
            actions.send_keys(Keys.RETURN)
            # Perform the actions
            actions.perform()

            time.sleep(delay_time)
        
        self.driver.quit()


    def comment_on_posts(self, links, comment, delay_time) -> None:
        wait = WebDriverWait(self.driver, 30)
        for link in links:
            # Open each post link
            if not self.has_already_been_commented_on(link):
                self.driver.get(link)
                time.sleep(2)

                # Find the comment input field
                comment_xpath_1 = 'textarea[aria-label="Add a comment…"]'
                comment_xpath_2 = "//div[@role='button' and .//*[contains(text(), 'Comment')]]"
                try:
                    comment_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, comment_xpath_1)))
                except Exception as e:
                    logging.warning(f'Exception {e}')
                    logging.warning('could not find comment element xpath ' + comment_xpath_1 + ' skipping the current post')
                    self.comments_skipped_because_could_not_find += 1
                    continue
                    #try:
                    #    comment_button = wait.until(EC.presence_of_element_located((By.XPATH, comment_xpath_2)))
                    #    comment_button.click()
                    #except Exception as e:
                    #    logging.error('could not find other comment element xpath ' + comment_xpath_2 + ' skipping the current link')
                    #    continue

                comment_input.click()
                time.sleep(1)

                # Create an instance of ActionChains
                actions = ActionChains(self.driver)
                actions.send_keys(comment)
                actions.send_keys(Keys.RETURN)
                # Perform the actions
                actions.perform()
                self.comments_made += 1
                saved_comment = SavedComment(text=comment, hyperlink=link)
                saved_comment.save()

                time.sleep(delay_time)

    def has_already_been_commented_on(self, link: str):
        saved_comments : list = SavedComment.select().where(SavedComment.hyperlink == link)
        already_commnented_on =  len(saved_comments) > 0
        return already_commnented_on

    def ignore_save_your_login_info(self):
        wait = WebDriverWait(self.driver, 30)
        xpath_string = "//div[@role='button' and contains(text(), 'Not now')]"
        not_now_button = wait.until(EC.presence_of_element_located((By.XPATH, xpath_string)))
        not_now_button.click()
        
    def ignore_turn_on_notifications(self):
        buttons = self.driver.find_elements(By.TAG_NAME, 'button')
        not_now_buttons = [but for but in buttons if but.text == 'Not Now']
        if 0 == len(not_now_buttons):
            logging.info('No Not Now buttons. Assuming theres no Turn On Notifications Dialogue.')
            return
        elif 1 == len(not_now_buttons):
            logging.debug('Selecting Not Now for Turn on Notifications')
        else:
            logging.warning('More than One \'Not Now\' buttons. Using the first one.')
        not_now_buttons[0].click()

    def next_debug_step(self):
        print('nothing to do exactly. Just debug/develop activity.')

    def quit(self):
        logging.info('quitting selenium driver session.')
        self.driver.quit()


