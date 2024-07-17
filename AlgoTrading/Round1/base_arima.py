import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any
import numpy as np
import pandas as pd

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[:max_length - 3] + "..."

logger = Logger()

class Trader:

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        result = {}
        conversions = 5
        trader_data = ""

        if (state.traderData == ""):
            price_history_amethyst = np.array([])

            price_history_starfruit = np.array([])
            
        else:
            data = json.loads(state.traderData)


            price_history_amethyst = data['AMETHYSTS']
            price_history_amethyst = np.array(price_history_amethyst)

            price_history_starfruit = data['STARFRUIT']
            price_history_starfruit = np.array(price_history_starfruit)

        def fair_price(product: str, price_history: list[float]=[]) -> int:
            if (product == "AMETHYSTS"):
                return 10000
            if (product == "STARFRUIT"):
                return price_history[-10:-1].mean()
                series = pd.Series(price_history)
                ema = series.ewm(span=10).mean()
                return ema.to_numpy()[-1]


            

        for product in state.order_depths.keys():
            if product == 'AMETHYSTS':
                o_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                fprice = fair_price(product)
                
                if len(o_depth.sell_orders) != 0:
                    best_ask = min(o_depth.sell_orders.keys())
                    best_ask_vol = o_depth.sell_orders[best_ask]

                    if best_ask < fprice:
                        orders.append(Order(product, best_ask, -best_ask_vol))

                if len(o_depth.buy_orders) != 0:
                    best_bid = max(o_depth.buy_orders.keys())
                    best_bid_vol = o_depth.buy_orders[best_bid]

                    if best_bid > fprice:
                        orders.append(Order(product, best_bid, -best_bid_vol))

                result[product] = orders

            if product == 'STARFRUIT' and state.timestamp >= 3000:
                o_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                price = 0
                count = 0.000001

                for Trade in state.market_trades.get(product, []):
                    price += Trade.price * Trade.quantity
                    count += Trade.quantity
                current_avg_market_price = price / count
                
                price_history_starfruit = np.append(price_history_starfruit, current_avg_market_price)

                fprice = fair_price(product,price_history_starfruit)
                
                if len(o_depth.sell_orders) != 0:
                    best_ask = min(o_depth.sell_orders.keys())
                    best_ask_vol = o_depth.sell_orders[best_ask]

                    if best_ask < fprice-10:
                        orders.append(Order(product, best_ask, -best_ask_vol))

                if len(o_depth.buy_orders) != 0:
                    best_bid = max(o_depth.buy_orders.keys())
                    best_bid_vol = o_depth.buy_orders[best_bid]

                    if best_bid > fprice+10:
                        orders.append(Order(product, best_bid, -best_bid_vol))

                result[product] = orders
                

        price_history_amethyst = price_history_amethyst.tolist()
        price_history_starfruit = price_history_starfruit.tolist()
        data = {
            'AMETHYSTS': price_history_amethyst,
            'STARFRUIT': price_history_starfruit,
        }
        trader_data = json.dumps(data)

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data