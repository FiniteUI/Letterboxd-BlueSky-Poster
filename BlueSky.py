from atproto import Client, models
from bs4 import BeautifulSoup
import requests

class BlueSky:
    def __init__(self, username, password):
        self.client = Client()
        self.client.login(username, password)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.client

    def post(self, contents):
        self.client.send_post(contents)

    def post_with_link_embed(self, contents, link):
        title, description, thumbnail = self.get_embed_details(link)

        embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                title=title,
                description=description,
                uri=link,
                thumb=thumbnail,
            )
        )

        self.client.send_post(text = contents, embed = embed)

    def get_embed_details(self, link):
        title = ''
        description = ''
        thumbnail = None

        response = requests.get(link)
        response.raise_for_status()
        data = BeautifulSoup(response.text, "html.parser")

        title_tag = data.find("meta", property="og:title")
        if title_tag:
            title = title_tag['content']

        description_tag = data.find("meta", property="og:description")
        if description_tag:
            description = description_tag["content"]
        
        image_tag = data.find("meta", property="og:image")
        if image_tag:
            img_url = image_tag["content"]
            if "://" not in img_url:
                img_url = link + img_url
            response = requests.get(img_url)
            response.raise_for_status()

            thumbnail = self.client.upload_blob(response.content).blob
        
        return title, description, thumbnail