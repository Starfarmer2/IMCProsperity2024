import json
# import collections
# from collections import defaultdict
import numpy as np
import pandas as pd

# class Logger:
#     def __init__(self) -> None:
#         self.logs = ""
#         self.max_log_length = 3750

#     def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
#         self.logs += sep.join(map(str, objects)) + end

#     def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
#         base_length = len(self.to_json([
#             self.compress_state(state, ""),
#             self.compress_orders(orders),
#             conversions,
#             "",
#             "",
#         ]))

#         # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
#         max_item_length = (self.max_log_length - base_length) // 3

#         print(self.to_json([
#             self.compress_state(state, self.truncate(state.traderData, max_item_length)),
#             self.compress_orders(orders),
#             conversions,
#             self.truncate(trader_data, max_item_length),
#             self.truncate(self.logs, max_item_length),
#         ]))

#         self.logs = ""

#     def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
#         return [
#             state.timestamp,
#             trader_data,
#             self.compress_listings(state.listings),
#             self.compress_order_depths(state.order_depths),
#             self.compress_trades(state.own_trades),
#             self.compress_trades(state.market_trades),
#             state.position,
#             self.compress_observations(state.observations),
#         ]

#     def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
#         compressed = []
#         for listing in listings.values():
#             compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

#         return compressed

#     def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
#         compressed = {}
#         for symbol, order_depth in order_depths.items():
#             compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

#         return compressed

#     def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
#         compressed = []
#         for arr in trades.values():
#             for trade in arr:
#                 compressed.append([
#                     trade.symbol,
#                     trade.price,
#                     trade.quantity,
#                     trade.buyer,
#                     trade.seller,
#                     trade.timestamp,
#                 ])

#         return compressed

#     def compress_observations(self, observations: Observation) -> list[Any]:
#         conversion_observations = {}
#         for product, observation in observations.conversionObservations.items():
#             conversion_observations[product] = [
#                 observation.bidPrice,
#                 observation.askPrice,
#                 observation.transportFees,
#                 observation.exportTariff,
#                 observation.importTariff,
#                 observation.sunlight,
#                 observation.humidity,
#             ]

#         return [observations.plainValueObservations, conversion_observations]

#     def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
#         compressed = []
#         for arr in orders.values():
#             for order in arr:
#                 compressed.append([order.symbol, order.price, order.quantity])

#         return compressed

#     def to_json(self, value: Any) -> str:
#         return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

#     def truncate(self, value: str, max_length: int) -> str:
#         if len(value) <= max_length:
#             return value

#         return value[:max_length - 3] + "..."

# logger = Logger()

class Trader:
    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if(buy==0):
                vol *= -1
            tot_vol += vol
            if tot_vol > mxvol:
                mxvol = vol
                best_val = ask
        
        return tot_vol, best_val

    def run(self, state):
        result = {}
        conversions = 0
        trader_data = ""

        if (state.traderData == ""):
            price_history_COCONUT = np.array([])
            price_history_COCONUT_COUPON = np.array([])
            hold_history = np.array([])
            
        else:
            data = json.loads(state.traderData)
            # print(f'data: {data}\n\n\n\n\n')
            # print(' ')
            price_history_COCONUT = np.array([data['COCONUT']])
            price_history_COCONUT_COUPON = np.array([data['COCONUT_COUPON']])
            hold_history = np.array(data['HOLD'])


        # def fair_price(product: str, price_history: list[float]=[]) -> int:
        #     coc_minus_coc_coupon = 
        #     if (product == "COCONUT"):
        #         return 10000
        #     if (product == "COCONUT_COUPON"):
        #         return price_history[-10:-1].mean()
        #         series = pd.Series(price_history)
        #         ema = series.ewm(span=10).mean()
        #         return ema.to_numpy()[-1]

        for product in state.order_depths.keys():
            if product == 'COCONUT':
                o_depth = state.order_depths[product]
                osell = o_depth.sell_orders
                obuy = o_depth.buy_orders

                sell_vol, best_sell_pr = self.values_extract(osell)
                buy_vol, best_buy_pr = self.values_extract(obuy, 1)

                price_history_COCONUT = np.append(price_history_COCONUT, (sell_vol * best_sell_pr + buy_vol * best_buy_pr)/(sell_vol + buy_vol))
            

            if product == 'COCONUT_COUPON':
                o_depth = state.order_depths[product]
                osell = o_depth.sell_orders
                obuy = o_depth.buy_orders

                sell_vol, best_sell_pr = self.values_extract(osell)
                buy_vol, best_buy_pr = self.values_extract(obuy, 1)

                price_history_COCONUT_COUPON = np.append(price_history_COCONUT_COUPON, (sell_vol * best_sell_pr + buy_vol * best_buy_pr)/(sell_vol + buy_vol))

        # Make sure position has product key
        if 'COCONUT' not in state.position.keys():
            state.position['COCONUT'] = 0

        # Make sure position has product key
        if 'COCONUT_COUPON' not in state.position.keys():
            state.position['COCONUT_COUPON'] = 0


        COCONUT_LIMIT = 300
        COCONUT_COUPON_LIMIT = 547

        # print(f'hold_history: {hold_history}')
        # print(f'price_history_COCONUT: {price_history_COCONUT}')

        if (len(hold_history) == 0 or hold_history[-1] == 0): #if not holding
            if np.abs(state.position['COCONUT']) >= COCONUT_LIMIT and np.abs(state.position['COCONUT_COUPON']) >= COCONUT_COUPON_LIMIT:
                hold_history = np.append(hold_history, np.sign(state.position['COCONUT']))
            else:
                hold_history = np.append(hold_history, 0)
        else: #if holding
            if np.abs(state.position['COCONUT']) == 0 and np.abs(state.position['COCONUT_COUPON']) == 0:
                hold_history = np.append(hold_history, 0)
            else:
                hold_history = np.append(hold_history, hold_history[-1])



        STD = 25.49
        ENTRY_THRESHOLD = 1.0 * STD
        EXIT_THRESHOLD = 0.4 * STD

        BETA = 1.824590
        # mean = price_history_COCONUT[-100:-1].mean() - price_history_COCONUT_COUPON[-100:-1].mean() * BETA
        mean = 8841.201392747003
        spread = price_history_COCONUT[-1] - price_history_COCONUT_COUPON[-1] * BETA - mean #COCONUT - COCONUT_COUPON * Beta
        print(f'spread: {spread}')
        if 'COCONUT' in state.position.keys() and 'COCONUT_COUPON' in state.position.keys():
            print(f'COCONUT: {state.position["COCONUT"]}, COCONUT_COUPON: {state.position["COCONUT_COUPON"]}')

        for product in state.order_depths.keys():
            if product == 'COCONUT' and state.timestamp >= 1:
                o_depth = state.order_depths[product]
                orders = []
                
                # Exit
                if 'COCONUT' in state.position.keys() and hold_history[-1] != 0:
                    if (hold_history[-1] < 0 and spread < EXIT_THRESHOLD) or (hold_history[-1] > 0 and spread > -EXIT_THRESHOLD):
                        if hold_history[-1] > 0:
                            if len(o_depth.buy_orders) != 0:
                                print("EXIT, SELL COCONUT")
                                best_bid = max(o_depth.buy_orders.keys())
                                best_bid_vol = o_depth.buy_orders[best_bid]

                                orders.append(Order(product, best_bid, -np.sign(best_bid_vol) * np.minimum(np.abs(best_bid_vol), np.abs(state.position['COCONUT'])) ))
                        else:
                            if len(o_depth.sell_orders) != 0:
                                print("EXIT, BUY COCONUT")
                                best_ask = min(o_depth.sell_orders.keys())
                                best_ask_vol = o_depth.sell_orders[best_ask]

                                orders.append(Order(product, best_ask, -np.sign(best_ask_vol) * np.minimum(np.abs(best_ask_vol), np.abs(state.position['COCONUT'])) ))

                # Entry
                if hold_history[-1] == 0:
                    if spread > ENTRY_THRESHOLD: #sell coconut
                        if len(o_depth.buy_orders) != 0:
                            print("ENTRY, SELL COCONUT")
                            best_bid = max(o_depth.buy_orders.keys())
                            best_bid_vol = o_depth.buy_orders[best_bid]

                            max_sell = COCONUT_LIMIT - np.maximum(-state.position['COCONUT'], 0)
                            orders.append(Order(product, best_bid, -np.sign(best_bid_vol) * np.minimum(np.abs(best_bid_vol), max_sell) )) #sell until position reaches limit

                    
                    if spread < -ENTRY_THRESHOLD: #buy coconut
                        if len(o_depth.sell_orders) != 0:
                            print("ENTRY, BUY COCONUT")
                            best_ask = min(o_depth.sell_orders.keys())
                            best_ask_vol = o_depth.sell_orders[best_ask]

                            max_buy = COCONUT_LIMIT - np.maximum(state.position['COCONUT'], 0)
                            orders.append(Order(product, best_ask, -np.sign(best_ask_vol) * np.minimum(np.abs(best_ask_vol), max_buy) )) #buy until position reaches limit
                result[product] = orders

            if product == 'COCONUT_COUPON' and state.timestamp >= 1:
                o_depth = state.order_depths[product]
                orders = []
                
                # Exit
                if 'COCONUT_COUPON' in state.position.keys() and hold_history[-1] != 0:
                    if (hold_history[-1] > 0 and spread > -EXIT_THRESHOLD) or (hold_history[-1] < 0 and spread < EXIT_THRESHOLD):
                        if hold_history[-1] < 0: #sell coupon
                            if len(o_depth.buy_orders) != 0:
                                best_bid = max(o_depth.buy_orders.keys())
                                best_bid_vol = o_depth.buy_orders[best_bid]

                                orders.append(Order(product, best_bid, -np.sign(best_bid_vol) * np.minimum(np.abs(best_bid_vol), np.abs(state.position['COCONUT_COUPON'])) ))
                        else:
                            if len(o_depth.sell_orders) != 0: #buy coupon
                                best_ask = min(o_depth.sell_orders.keys())
                                best_ask_vol = o_depth.sell_orders[best_ask]

                                orders.append(Order(product, best_ask, -np.sign(best_ask_vol) * np.minimum(np.abs(best_ask_vol), np.abs(state.position['COCONUT_COUPON'])) ))
                
                # Entry
                if hold_history[-1] == 0:
                    if spread < -ENTRY_THRESHOLD: #sell coupon
                        if len(o_depth.buy_orders) != 0:
                            best_bid = max(o_depth.buy_orders.keys())
                            best_bid_vol = o_depth.buy_orders[best_bid]

                            max_sell = COCONUT_COUPON_LIMIT - np.maximum(-state.position['COCONUT_COUPON'], 0)
                            orders.append(Order(product, best_bid, -np.sign(best_bid_vol) * np.minimum(np.abs(best_bid_vol), max_sell)  )) #sell until position reaches limit

                    
                    if spread > ENTRY_THRESHOLD: #buy coupon
                        if len(o_depth.sell_orders) != 0:
                            best_ask = min(o_depth.sell_orders.keys())
                            best_ask_vol = o_depth.sell_orders[best_ask]

                            max_buy = COCONUT_COUPON_LIMIT - np.maximum(state.position['COCONUT_COUPON'], 0)
                            orders.append(Order(product, best_ask, -np.sign(best_ask_vol) * np.minimum(np.abs(best_ask_vol), max_buy) )) #buy until position reaches limit
                result[product] = orders
                

        price_history_COCONUT = price_history_COCONUT.tolist()
        price_history_COCONUT_COUPON = price_history_COCONUT_COUPON.tolist()
        hold_history = hold_history.tolist()
        data = {
            'COCONUT': price_history_COCONUT,
            'COCONUT_COUPON': price_history_COCONUT_COUPON,
            'HOLD': hold_history
        }
        trader_data = json.dumps(data)

        # logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data