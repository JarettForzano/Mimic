from supabase import create_client, Client

# inits supabase and retrieves the client for further probing
def init(env):
    url = env.retrieve("SUPA_URL")
    key = env.retrieve("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    return supabase

