from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = ""
key = ""

supabase = create_client(url, key)


def login(email, password):
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def register(email, password):
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })


def get_user():
    return supabase.auth.get_user()