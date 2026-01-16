class Card:
    def __init__(self, data: dict, variant: int):
        self.variant_id = data.get('id')
        self.card_id = data.get('variants')[variant].get('id')
        self.name = data.get('name')
        self.number = data.get('number')
        self.tcg_playerId = data.get('tcgplayerId')
        self.condition = data.get('variants')[variant].get('condition')
        self.currentPrice = data.get('variants')[variant].get('price')
        self.last_updated = data.get('variants')[variant].get('lastUpdated')
        self.tcg_playerSku_id = data.get('variants')[variant].get('tcgplayerSkuId')
        self.price_change_24h = data.get('variants')[variant].get('priceChange24h')
        self.price_change_7d = data.get('variants')[variant].get('priceChange7d')
        self.price_change_30d = data.get('variants')[variant].get('priceChange30d')
        self.avg_price = data.get('variants')[variant].get('avgPrice')
        self.min_price = data.get('variants')[variant].get('minPrice1y')
        self.max_price = data.get('variants')[variant].get('maxPrice1y')
        self.printing = data.get('variants')[variant].get('printing')

    def to_dict(self) -> dict:
        return {
            "variantId": self.variant_id,
            "cardId": self.card_id,
            "tcgplayerId": self.tcg_playerId,
            "condition": self.condition,
            "currentPrice": self.currentPrice,
            "lastUpdated": self.last_updated,
            "tcgplayerSkuId": self.tcg_playerSku_id,
            "priceChange24hr": self.price_change_24h,
            "priceChange7d": self.price_change_7d,
            "priceChange30d": self.price_change_30d,
            "avgPrice": self.avg_price,
            "minPrice1y": self.min_price,
            "maxPrice1y": self.max_price,
            "name": self.name,
            "number": self.number,
            "printing": self.printing
        }