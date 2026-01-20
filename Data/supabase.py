
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
        print(f"Upserting {len(card_data)} cards")
        await self.supabase.table('Cards').upsert(card_data).execute()
    
    async def find_card(self, name: str, condition: str) -> list[dict]:
        response = await (
            self.supabase
            .table('Cards')
            .select('*')
            .ilike('name', f'%{name}%')
            .ilike('condition', f'%{condition}%')
            .limit(10)
            .execute()
        )

        return response.data or []
    
    async def followCard(self, cardId: str, discUserId: str):
        try:
            response = await self.supabase.table("UserCards").upsert({
                "cardId": cardId, 
                "discUserId": discUserId
            }).execute()
            return response
        except Exception as e:
            print(f"Error following card: {e}")
            return None
        
    async def unfollowCard(self, cardId: str, discUserId: str):
        try:
            response = await self.supabase.table("UserCards").delete().eq(
                "cardId", cardId
            ).eq(
                "discUserId", discUserId
            ).execute()
            return response
        except Exception as e:
            print(f"Error unfollowing card: {e}")
            return None
        
    async def getUserCards(self):
        try:
            response = await self.supabase.table("UserCards").select("*").execute()
            return response.data
        except Exception as e:
            print(f'Error getting UserCards')
            return []
        
    async def findCardById(self, cardId: str):
        try:
            response = await self.supabase.table("Cards").select("*").eq("cardId", cardId).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting card by id")