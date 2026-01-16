
from urllib import response
from supabase import create_client, Client, create_async_client
class Supabase:
    def __init__(self, key: str):
        self.supabase: Client | None = None
        self.supabase_key = key  # store it!
    
    async def connect(self):
        self.supabase = await create_async_client('https://nfptsmxkovgtuymzeydg.supabase.co', self.supabase_key)
    
    async def insert_cards(self, card_data: list[dict]) -> None:
        await self.supabase.table('Cards').insert(card_data).execute()

    async def upsert_cards(self, card_data: list[dict]) -> None:
        await self.supabase.table('Cards').upsert(card_data).execute()
    
    async def find_card(self, name: str, condition: str) -> list[dict]:
        response = await self.supabase.table('Cards').select('*').eq('name', name).eq('condition', condition).execute()
        if response.data:
            return response.data
        return []