from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = ""
key = ""

supabase = create_client(url, key)


def get_authenticated_client(session):
    """Atualiza o cliente com a sessão do usuário logado para respeitar o RLS."""
    supabase.auth.set_session(session.access_token, session.refresh_token)
    return supabase