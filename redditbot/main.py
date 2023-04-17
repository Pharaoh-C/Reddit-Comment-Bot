import json
import os
import openai
import praw
import requests
import time

# Reddit
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
USERNAME = 'your_username'
PASSWORD = 'your_password'
USER_AGENT = 'your_user_agent'

# NASA
NASA_API = 'your_nasa_api'
NASA_HTTP = 'https://api.nasa.gov/planetary/apod'



#########################################################################################                                                                                        #

# to access to the Bot account
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     username=USERNAME,
                     password=PASSWORD,
                     user_agent=USER_AGENT)

subreddit = reddit.subreddit('your_subreddit_name')
#########################################################################################

#########################################################################################


#########################################################################################
post_id = ""

last_comment_time = time.time()

test_data = {}

answered_comments = {}

try:
    with open("comment_id.json", "r") as data_file:
        answered_comments = json.load(data_file)
except FileNotFoundError:
    with open("comment_id.json", "w") as data_file:
        json.dump(answered_comments, data_file, indent=4)
except json.decoder.JSONDecodeError:
    data = {}

while True:
    new_comments = subreddit.comments(params={"after": last_comment_time})

    for comment in new_comments:
        # update the newest comment
        if comment.created_utc > last_comment_time:
            last_comment_time = comment.created_utc
    # for answer /nasa
        if '/nasa' in comment.body.lower():
            # if not already answered
            if comment.id not in answered_comments:
                # parameters that necessary for APO request
                parameters = {
                    "api_key": NASA_API,
                    "hd": True
                }

                # getting data from API
                response = requests.get(NASA_HTTP, params=parameters)
                response.raise_for_status()
                data = response.json()

                # creating png url
                image_url = data["hdurl"]

                # answer the comment
                comment.reply('NASA Image of the Day: ' + image_url)

                # to add answered comment to dictionary
                answered_comments[comment.id] = {
                    "Post ID": comment.parent_id.split("_")[1],
                    "Comment ID": comment.id
                }

                # open JSON in append mode
                with open("comment_id.json", "a") as data_file:
                    if os.stat("comment_id.json").st_size == 0:
                        test_data = {}

                    test_data.update(answered_comments)
                    with open("comment_id.json", "w") as data_file:
                        json.dump(answered_comments, data_file, indent=4)

        # for answer /install
        if '/install' in comment.body.lower():
            post = comment.parent()
            post_id = post.id
            if comment.id not in answered_comments:
                if post.media:
                    video_url = post.media['reddit_video']['fallback_url']
                    comment.reply('Video URL: ' + video_url)
                else:
                    comment.reply("Can't install this.")
                    # to add answered comment to dictionary
                answered_comments[comment.id] = {
                    "Post ID": post_id,
                    "Comment ID": comment.id
                }
                # open JSON in append mode
                with open("comment_id.json", "a") as data_file:
                    if os.stat("comment_id.json").st_size == 0:
                        test_data = {}

                    test_data.update(answered_comments)
                    with open("comment_id.json", "w") as data_file:
                        json.dump(answered_comments, data_file, indent=4)


    # update every 10 minutes
    time.sleep(60*10)
#########################################################################################
