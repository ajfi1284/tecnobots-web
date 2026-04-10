# supabase_config.py
from supabase import create_client, Client

SUPABASE_URL = "https://plcmjxzmjeiqxhwdstqh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsY21qeHptamVpcXhod2RzdHFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzNDk3NDAsImV4cCI6MjA5MDkyNTc0MH0.KecUalXSJYS2mlBs5_OEM-g80JsF18YbI8N5IWONJKM"

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)