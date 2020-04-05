import pymongo

"""
   Variables that contain user credentials for Twitter API as well as
   client for local MongoDB database.
    Intructions:
    - paste your own Twitter credentials into the empty strings.
    - when finished, save and rename this file as config.py (important!)
"""

### TWITTER CREDENTIALS ###
CONSUMER_API_KEY = "shz1Bk2Pzo376o4WTe31WSlPY"
CONSUMER_API_SECRET = "BBq8GSbmRfMnR5GqgABFQ8ZX4LKBzOcAhuyLB6Ll4CzvFyvGLf"
ACCESS_TOKEN = "79029087-ZRWxNEgj0sH107hSED6G3ElRTZZ6bLrCLQ1so7Ejl"
ACCESS_TOKEN_SECRET = "VGh9iKCJocbVvC73w1MGxb0DCFDyFOQyYVWONXsasA0cH"

### CONNECTING TO LOCAL MONGODB ###
LOCAL_CLIENT = pymongo.MongoClient()
