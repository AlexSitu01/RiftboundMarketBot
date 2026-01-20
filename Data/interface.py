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
        self.price_change_24h = data.get('variants')[variant].get('priceChange24hr')
        self.price_change_7d = data.get('variants')[variant].get('priceChange7d')
        self.price_change_30d = data.get('variants')[variant].get('priceChange30d')
        self.avg_price = data.get('variants')[variant].get('avgPrice')
        self.min_price = data.get('variants')[variant].get('minPrice30d')
        self.max_price = data.get('variants')[variant].get('maxPrice30d')
        self.printing = data.get('variants')[variant].get('printing')
        self.price_history = data.get('variants')[variant].get('priceHistory', [])
        self.trend_slope_30d = data.get('variants')[variant].get('trendSlope30d')

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
            "minPrice30d": self.min_price,
            "maxPrice30d": self.max_price,
            "name": self.name,
            "number": self.number,
            "printing": self.printing,
            "priceHistory": self.price_history,
            "trendSlope30d": self.trend_slope_30d
            
        }