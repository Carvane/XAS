

class Agent:
    def __init__(
        self,
        ConsumerKey,
        ConsumerKeySecret,
        AccessToken,
        AccessTokenSecret
    ):
        self.__ConsumerKey = ConsumerKey
        self.__ConsumerKeySecret = ConsumerKeySecret
        self.__AccessToken = AccessToken
        self.__AccessTokenSecret = AccessTokenSecret

    def getPost(self):
        print("test")