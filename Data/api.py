import asyncio
import time
import requests
import json
from Data.interface import Card
from Data.supabase import Supabase

class TCG_API:
    BASE_URL = "https://api.justtcg.com/v1/"
    with open('riftbound-set.json', "r") as file:
        data = json.load(file)
    RIFTBOUND_ID = data['id']
    TOTAL_CARDS = data['cards_count']
    

    def __init__(self, api_key, supabase_key: str, loop: asyncio.AbstractEventLoop):
        self.api_key = api_key
        self.supabase = Supabase(supabase_key)
        self.loop = loop
        self._db_futures: list[asyncio.Future] = []

    async def connect(self):
        await self.supabase.connect()
    
    def __add_to_database(self, card_data: list[dict]) -> None:
        future = asyncio.run_coroutine_threadsafe(
            self.supabase.upsert_cards(card_data),
            self.loop
        )

        self._db_futures.append(future)
            
    def wait_for_db_writes(self):
        for future in self._db_futures:
            try:
                future.result()  # blocks thread until done
            except Exception as e:
                print("Supabase upsert failed:", e)

        self._db_futures.clear()
        
    def get_change_field(self, timeframe: str) -> str:
        if timeframe == "day":
            return "priceChange24hr"
        if timeframe == "week":
            return "priceChange7d"
        if timeframe == "month":
            return "priceChange30d"
        raise ValueError("Invalid timeframe. Use: 24h, 7d, or 30d")
        
    def get_price_bucket(self, price: float) -> str | None:
        if price is None:
            return None
        if 0 <= price <= 5:
            return "low"
        if 5.01 <= price <= 20:
            return "mid"
        if price >= 20.01:
            return "high"
        return None

    # Fetch and update cards from the JustTCG API
    def update_cards(self) -> None:
        BATCH_LIMIT = 200
        offset = 0
        batch = []

        base_delay = 0.3          # normal pacing
        max_base_delay = 5.0      # long-term throttle
        backoff = 1               # short-term retry backoff
        count = 0                 # 429 counter

        while offset < self.TOTAL_CARDS:
            response = requests.get(
                f"{self.BASE_URL}/cards",
                headers={"x-api-key": self.api_key},
                params={"game": self.RIFTBOUND_ID, "offset": offset},
                timeout=10
            )

            # --- RATE LIMIT HANDLING ---
            if response.status_code == 429:
                count += 1
                if count > 8:
                    print("Too many 429s, aborting.")
                    break
                retry_after = response.headers.get("Retry-After")
                sleep_time = int(retry_after) if retry_after else backoff

                print(f"429 hit, sleeping {sleep_time}s")

                time.sleep(sleep_time)

                # Increase both backoff AND base delay
                backoff = min(backoff * 2, 30)
                base_delay = min(base_delay * 1.5, max_base_delay)
                continue

            # --- SUCCESS PATH ---
            backoff = 1  # reset retry backoff only
            count = 0    # reset 429 counter
            base_delay = max(0.3, base_delay * 0.9)  # slowly cool down

            if response.status_code in (401, 403):
                print(f"Authentication error: {response.status_code}")
                break

            if response.status_code == 500:
                print(f"Server error at offset {offset}, retrying after 5s")
                time.sleep(5)
                continue

            if response.status_code != 200:
                print(f"Failed at offset {offset}: {response.status_code}")
                offset += 20
                time.sleep(base_delay)
                continue

            # --- PROCESS DATA ---
            cards = response.json().get("data", [])

            for card_data in cards:
                for i in range(len(card_data.get("variants", []))):
                    batch.append(Card(card_data, i).to_dict())

            if len(batch) >= BATCH_LIMIT:
                self.__add_to_database(batch.copy())
                batch.clear()

            offset += 20
            time.sleep(base_delay)

        if batch:
            self.__add_to_database(batch.copy())
            
        # ENSURE ALL WRITES FINISH
        self.wait_for_db_writes()

    async def find_card(self, name: str, condition: str) -> list[dict]:
        return await self.supabase.find_card(name, condition)
    
    async def addCardToFollow(self, card, discUserId: str):
        cardId = card.get("cardId")
        if cardId:
            await self.supabase.followCard(cardId=cardId, discUserId=discUserId)
    
    async def unfollowCard(self, card, discUserId: str):
        cardId = card.get("cardId")
        if cardId:
            await self.supabase.unfollowCard(cardId=cardId, discUserId=discUserId)
            
    async def getFollowCards(self) -> list[dict]:
        userCardsToSend = await self.supabase.getUserCards()
        if userCardsToSend:
            return userCardsToSend
        
    async def findCardById(self, cardId: str) -> dict:
        card = await self.supabase.findCardById(cardId)
        return card
    
    
    async def getSummary(self, timeframe: str = "day") -> list[dict]:
        cards = await self.supabase.getCards()
        result = [[0] * 2 for _ in range(6)]
        
        TIME = self.get_change_field(timeframe)
        
        buckets = {
        "low": [],
        "mid": [],
        "high": [],
        }
        for card in cards:
            price = card.get("currentPrice")
            change = card.get(TIME)

            if price is None or change is None:
                continue

            bucket = self.get_price_bucket(price)
            if bucket:
                buckets[bucket].append(card)

        result = {
            "low": {"gainer": None, "loser": None},
            "mid": {"gainer": None, "loser": None},
            "high": {"gainer": None, "loser": None},
        }

        # Find movers per bucket
        for bucket, bucket_cards in buckets.items():
            if not bucket_cards:
                continue

            # Largest gainer
            result[bucket]["gainer"] = max(
                bucket_cards,
                key=lambda c: c.get(TIME, float("-inf")),
                default=None,
            )

            # Largest loser
            result[bucket]["loser"] = min(
                bucket_cards,
                key=lambda c: c.get(TIME, float("inf")),
                default=None,
            )

        return result
    
    async def unfollowAll(self, discUserId: str):
        await self.supabase.unfollow_all(discUserId)
            