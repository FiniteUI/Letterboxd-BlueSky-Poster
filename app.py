import feedparser
from ConfigurationFile import ConfigurationFile
from BlueSky import BlueSky
from datetime import datetime
from time import mktime, sleep
import os
import dotenv

def run():
    print('Process starting. Initializing...')

    #grab settings
    valid = True

    #if we are running on docker, envs are supplied directly. If not, we load the file
    from_docker = os.getenv('DOCKER')
    if from_docker is None:
        print("Running locally...")
        dotenv.load_dotenv()
    else:
        print("Running in Docker...")

    letterboxd_account = os.getenv('LETTERBOXD_ACCOUNT')
    if letterboxd_account == '' or letterboxd_account is None:
        valid = False
        print("Error: Required key [LETTERBOXD_ACCOUNT] missing from configuration file [.env]")

    bluesky_user = os.getenv('BLUESKY_USERNAME')
    if bluesky_user == '' or bluesky_user is None:
        valid = False
        print("Error: Required key [BLUESKY_USERNAME] missing from configuration file [.env]")

    bluesky_app_password = os.getenv('BLUESKY_APP_PASSWORD')
    if bluesky_app_password == '' or bluesky_app_password is None:
        valid = False
        print("Error: Required key [BLUESKY_APP_PASSWORD] missing from configuration file [.env]")

    if valid:
        print('Configuration is valid.')
        process_loop(letterboxd_account, bluesky_user, bluesky_app_password)
    else:
        print('Could not run due to missing keys. Aborting program...')

def process_loop(letterboxd_account, bluesky_user, bluesky_app_password):
    print('Starting process loop...')

    #load registry file
    registry = ConfigurationFile('registry')

    while True:
        print("Checking for new entries...")

        #now grab rss feed
        rss_url = f'https://letterboxd.com/{letterboxd_account}/rss'
        rss_feed = feedparser.parse(rss_url)

        #grab last post
        last_post = registry.getValue('last_post', None)
        if last_post is None:
            last_post = datetime.now().astimezone()
            registry.setValue('last_post', last_post)
        else:
            last_post = datetime.fromisoformat(last_post)
        print(f'Last Post Timestamp: {last_post}')

        #check for any new diary entries on letterboxd
        posted = False
        for item in rss_feed.entries:
            item_date = datetime.strptime(item.published, '%a, %d %b %Y %H:%M:%S %z')
            if item_date > last_post:
                print('New Entry Found...')
                posted = True
                post_text = f'Just watched {item.letterboxd_filmtitle} ({item.letterboxd_filmyear}) and rated it {item.letterboxd_memberrating}/5 on Letterboxd:'
                registry.setValue('last_post_contents', post_text)

                print(f'Sending post: [{post_text}]')
                send_post(post_text, item.link, bluesky_user, bluesky_app_password)

                registry.setValue('total_posts', registry.getValue('total_posts', 0) + 1)
            else:
                break

        if posted:
            registry.setValue('last_post', datetime.now())

        registry.setValue('last_process', datetime.now())
        print("Process complete. Waiting...")

        sleep(300)

def send_post(text, embed, bluesky_user, bluesky_app_password):
    with BlueSky(bluesky_user, bluesky_app_password) as bs:
        bs.post_with_link_embed(text, embed)

    return text

#run program
if __name__ == '__main__':
    run()