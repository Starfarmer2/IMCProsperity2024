from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import pandas as pd
import string

def find_acceptable_price(df):
    # price = 921.2061
    # price += 4.0231 * df['TRANSPORT_FEES'].iloc[-338] + 2.8198 * df['EXPORT_TARIFF'].iloc[-773] - 6.5970 * df['IMPORT_TARIFF'].iloc[-1] + 2.1720 * df['HUMIDITY'].iloc[-230]
    price = 750
    price += 2.3 * df['HUMIDITY'].iloc[-230]
    return price 

class Trader:
    def run(self, state: TradingState):
        observations = state.observations.conversionObservations["ORCHIDS"]
        if state.traderData == "":
            df = pd.DataFrame(columns=['timestamp', 'TRANSPORT_FEES', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY', 'SOUTH_BID', 'SOUTH_ASK', 'POSITION', 'PRICE'])
        else:
            df = pd.read_json(state.traderData)

        new_row_df = pd.DataFrame([{'TRANSPORT_FEES': observations.transportFees, 'EXPORT_TARIFF': observations.exportTariff, 'IMPORT_TARIFF': observations.importTariff, 'SUNLIGHT': observations.sunlight, 'HUMIDITY': observations.humidity, 'SOUTH_BID': observations.bidPrice, 'SOUTH_ASK': observations.askPrice, 'POSITION': state.position, 'PRICE': df['PRICE'].iloc[-1] if len(df) > 0 else 0}])
                                    
        df = pd.concat([df, new_row_df], ignore_index=True)

        traderData = df.to_json(orient='records', lines=False)

        if (state.timestamp <= 776*100):
            return {}, 0, traderData
        # for column in df.columns:
        #     df[column] = state.observations[column]
        # new_row = pd.DataFrame(state, index=[0])
        # df = pd.concat([df, new_row], ignore_index=True)
        

				# Orders to be placed on exchange matching engine
        result = {}
        conversions = 0

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = find_acceptable_price(df)
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

            

            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) < acceptable_price - 10:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
                    df['POSITION'].iloc[-1] += -best_ask_amount
                    df['PRICE'].iloc[-1] = best_ask
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > acceptable_price + 10:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
                    df['POSITION'].iloc[-1] += best_bid_amount
                    df['PRICE'].iloc[-1] = best_bid
            
            result[product] = orders


            # Conversion
            # Sell
            if df['POSITION'] > 0 and df['TRANSPORT_FEES'].iloc[-1] + df['EXPORT_TARIFF'].iloc[-1] + 2 < df['SOUTH_BID'].iloc[-1] - df['PRICE'].iloc[-1]:
                conversions += df['POSITION']

            # Buy
            if df['POSITION'] < 0 and df['TRANSPORT_FEES'].iloc[-1] + df['IMPORT_TARIFF'].iloc[-1] + 2 < df['PRICE'].iloc[-1] - df['SOUTH_ASK'].iloc[-1]:
                conversions -= df['POSITION']
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        
				# Sample conversion request. Check more details below. 


        return result, conversions, traderData