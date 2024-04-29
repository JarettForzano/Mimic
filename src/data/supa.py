from supabase import create_client, Client

# inits supabase and retrieves the client for further probing
def init(url, key):
    supabase: Client = create_client(url, key)

    return supabase

# Pushes the context data to the databse
def pushContext(called_at, json):
    return

# pulls all of the data from the databse when given the users id
def pullContext(id):
    return

# pushes the user's phone number into the databse when called, expected format probably "1234563333"
def pushUser(number):
    return

# pulls the user id when given the phone number, to check if has called before
def pullUser(number):
    return

# pulls the context data when given the id of the user
def pullContextData(id):
    return

# pulls the context date of called when given the id of the user (will be the most recent one)
def pullContextDate(id):
    return