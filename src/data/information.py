import os
from dotenv import load_dotenv

# Have to gather all the env variables but I dont want to constantly call load dotenv to get all api keys, just need to do it once
class ENV:
    def __init__(self):
        load_dotenv()

    def retrieve(env): # Makes life easier
        return os.getenv(env)
    