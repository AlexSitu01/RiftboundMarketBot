import asyncio
from concurrent.futures import ThreadPoolExecutor
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
    executor = ThreadPoolExecutor(max_workers=5)  # reuse threads

    def __init__(self, api_key, supabase_key: str):
        self.api_key = api_key
        self.supabase = Supabase(supabase_key)

    async def connect(self):
        await self.supabase.connect()
    
    def __add_to_database(self, card_data: list[dict]) -> None:
        self.executor.submit(lambda: asyncio.run(self.supabase.upsert_cards(card_data)))

    # Fetch and update cards from the JustTCG API
    def update_cards(self) -> None:
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

            if len(batch) >= 500:
                self.__add_to_database(batch)
                batch.clear()

            offset += 20
            time.sleep(base_delay)

        if batch:
            self.__add_to_database(batch)

    async def find_card(self, name: str, condition: str) -> list[dict]:
        return await self.supabase.find_card(name, condition)