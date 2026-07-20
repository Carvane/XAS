def calcRating(
        views: int,
        reposts: int,
        likes: int,
        bookmarks: int,
        replies: int,
):
    return (
        views * 0.01 +
        reposts * 100 +
        likes * 10 +
        bookmarks * 1000 +
        replies * 100        
    )


#print(calcRating(views=1000, reposts=1, likes=5, bookmarks=10, replies=5)) #test