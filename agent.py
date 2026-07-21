from xdk import Client
from xdk.oauth1_auth import OAuth1
from xdk.posts.models import CreateRequest

class Agent():
    def __init__(
        self,
        ConsumerKey: str,
        ConsumerKeySecret: str,
        AccessToken: str,
        AccessTokenSecret: str
    ):
        self.__auth = OAuth1(
            api_key=ConsumerKey,
            api_secret=ConsumerKeySecret,
            callback="http://localhost:8080/callback",
            access_token=AccessToken,
            access_token_secret=AccessTokenSecret
        )
        self.__client = Client(auth=self.__auth)

    def getLatest(self):
        pass

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