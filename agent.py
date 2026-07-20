from xdk import Client
from xdk.oauth1_auth import OAuth1

class Agent:
    def __init__(
        self,
        ConsumerKey,
        ConsumerKeySecret,
        AccessToken,
        AccessTokenSecret
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