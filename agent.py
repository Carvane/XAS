from xdk import Client
from xdk.oauth1_auth import OAuth1
from xdk.posts.models import CreateRequest

from openai import OpenAI

from typing import List, Dict, Optional

class AI():
    def __init__(
        self,
        OpenaiSecretKey
    ):
        self.__clientAI = OpenAI(api_key=OpenaiSecretKey)
    def generateResponse(self, prompt: str):
        response = self.__clientAI.responses.create(
            model="gpt-5.4-nano",
            tools=[{"type": "web_search"}],
            instructions="",
            input=prompt,
#            conversation=???
        )
        return response
        

class Agent(AI):
    def __init__(
        self,
        ConsumerKey: str,
        ConsumerKeySecret: str,
        AccessToken: str,
        AccessTokenSecret: str,
        OpenaiSecretKey: str
    ):
        self.__auth = OAuth1(
            api_key=ConsumerKey,
            api_secret=ConsumerKeySecret,
            callback="http://localhost:8080/callback",
            access_token=AccessToken,
            access_token_secret=AccessTokenSecret
        )
        self.__client = Client(auth=self.__auth)
        super().__init__(OpenaiSecretKey)

    def getLatest(self, users: List[str]) -> Optional[Dict]:
        if not users:
            return None

        query = (
            "(" + " OR ".join([f"from:{u}" for u in users]) + ") "
            "-is:retweet -is:reply -is:quote"
        )

        for page in self.__client.posts.search_recent(
            query=query,
            max_results=10,
            tweet_fields=["author_id", "created_at"],
            expansions=["author_id"],
            user_fields=["username"]
        ):
            if page.data:
                users_map = {}
                includes = getattr(page, 'includes', None)
                if includes:
                    if isinstance(includes, dict):
                        users_list = includes.get('users', [])
                    else:
                        users_list = getattr(includes, 'users', [])

                    for u in users_list:
                        uid = u.id if hasattr(u, 'id') else u.get('id')
                        uname = u.username if hasattr(u, 'username') else u.get('username')
                        if uid and uname:
                            users_map[uid] = uname

                post = page.data[0]

                post_id = post.id if hasattr(post, 'id') else post.get('id')
                text = post.text if hasattr(post, 'text') else post.get('text')
                author_id = post.author_id if hasattr(post, 'author_id') else post.get('author_id')
                created_at = post.created_at if hasattr(post, 'created_at') else post.get('created_at')

                username = users_map.get(author_id, str(author_id))

                return {
                    "mess": text,
                    "postId": str(post_id),
                    "author": username,
                    "date": created_at
                }
            break

        return None

    def getHighestRated(self):
        pass

    def postCreate(
            self,
            message: str
        ):
        response = self.__client.posts.create(
            body=CreateRequest(text=message)
        )
        return response