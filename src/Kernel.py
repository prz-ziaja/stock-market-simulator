import random
import time
import Traders.NoisyTrader as NoisyTrader
import Traders.PrzemekTrader as PrzemekTrader
from Books.MarketOrderBook import MarketOrderBook
import pandas as pd


class Kernel:
    def __init__(self, cb, ind, nn, np, nt, ni):
        self.cb = cb
        self.threads = []

        self.num_noisy_traders = nn
        self.num_Przemek_traders = np
        self.num_trend_traders = nt
        self.num_agents = self.num_noisy_traders + self.num_Przemek_traders + self.num_trend_traders
        self.num_iterations = ni

        self.orderBook = {
            "IBM": MarketOrderBook(),
            #"ABB": MarketOrderBook()
        }
        for i in pd.read_csv('data/AAPL.csv')['Close'][ind:ind+5].to_numpy():# zip([122.78, 122.78, 122.77, 122.65, 122.77], [17.76, 17.78, 17.81, 17.79, 17.81]):
            self.cb.addAveragePrice('IBM', i)
            #self.cb.addAveragePrice('ABB', j)

        # Przemek trader
        for i in range(0, self.num_Przemek_traders):
            portfolio = {"IBM": random.choice([20, 30])}
            self.threads.append(PrzemekTrader.PrzemekTrader(i, self.cb, self.orderBook, random.choice([2, 3, 5, 6]), random.choice([10000, 20000, 30000]), portfolio))

        # Noisy trader
        for i in range(self.num_Przemek_traders, self.num_noisy_traders + self.num_Przemek_traders):
            portfolio = {"IBM": random.choice([10, 20, 40])}
            self.threads.append(NoisyTrader.NoisyTrader(i, self.cb, self.orderBook, random.choice([1, 2, 3, 4]), random.choice([10000, 20000, 50000, 100000]), portfolio))

        # Trend trader
        for i in range(self.num_Przemek_traders+self.num_noisy_traders, self.num_noisy_traders + self.num_Przemek_traders + self.num_trend_traders):
            portfolio = {"IBM": random.choice([10, 20, 40])}
            self.threads.append(NoisyTrader.NoisyTrader(i, self.cb, self.orderBook, random.choice([2, 3, 4]), random.choice([10000, 20000, 40000]), portfolio))

        for t in self.threads:
            t.start()

        progress = list("[" + ("_"*100) + "]")

        for i in range(0, self.num_iterations):
            self.cb.clear_counter()
            self.cb.wakeUpAll()
            is_wait = True
            while is_wait:
                if self.cb.attendance_counter == self.num_agents:
                    self.transactions()
                    is_wait = False
                time.sleep(0.001)
            self.clearOrders()
            progress[int(i / self.num_iterations * 100) + 1] = '*'
            print('\r' + "".join(progress), end='')
        print("")
        self.endSimulation()

    def endSimulation(self):
        for t in self.threads:
            t.stop()
        self.cb.wakeUpAll()
        for t in self.threads:
            t.join()

    def transactions(self):
        for name, market in self.orderBook.items():
            bids = market.getBID()
            asks = market.getASK()

            sumQuantity = 0
            sumPrice = 0
            while True:
                if (not bids) or (not asks):  # nie ma wystarczacej ilosci bidow albo askow
                    break
                elif bids[0].getPrice() < asks[0].getPrice():  # cena kupujacych jest mniejsza od ceny sprzedajacych
                    break
                else:
                    if bids[0].getQuantity() < asks[0].getQuantity():  # sprzedajacy ma więcej akcji od kupujacego
                        self.cb.addMessage(bids[0].getOrderID(), "BUY:" + name + ":" + str(bids[0].getQuantity()))
                        self.cb.addMessage(asks[0].getOrderID(),
                                           "SELL:" + str(int(asks[0].getPrice() * bids[0].getQuantity())))
                        sumQuantity += bids[0].getQuantity()
                        sumPrice += asks[0].price * bids[0].getQuantity()
                        market.changeQuantityASK(asks[0].getQuantity() - bids[0].getQuantity())
                        market.removeBID(market.getBID()[0])

                    elif bids[0].getQuantity() > asks[0].getQuantity():  # kupujacy ma wiecej akcji od sprzedajacego
                        self.cb.addMessage(bids[0].getOrderID(), "BUY:" + name + ":" + str(asks[0].getQuantity()))
                        self.cb.addMessage(asks[0].getOrderID(),
                                           "SELL:" + str(int(asks[0].getPrice()) * asks[0].getQuantity()))
                        sumQuantity += asks[0].getQuantity()
                        sumPrice += asks[0].price * asks[0].getQuantity()
                        market.changeQuantityBID(bids[0].getQuantity() - asks[0].getQuantity())
                        market.removeASK(asks[0])
                    else:  # oboje kupujacy i sprzedajacy maja tyle samo akcji
                        self.cb.addMessage(bids[0].getOrderID(), "BUY:" + name + ":" + str(bids[0].getQuantity()))
                        self.cb.addMessage(asks[0].getOrderID(),
                                           "SELL:" + str(int(asks[0].getPrice()) * bids[0].getQuantity()))
                        sumQuantity += bids[0].getQuantity()
                        sumPrice += asks[0].price * bids[0].getQuantity()
                        market.removeBID(market.getBID()[0])
                        market.removeASK(market.getASK()[0])
            if sumQuantity:
                self.cb.addAveragePrice(str(name), round(sumPrice / sumQuantity, 2))
            else:
                pass
                # self.cb.addAveragePrice(str(name), numpy.nan)

    def clearOrders(self):
        for name, market in self.orderBook.items():
            bids = market.getBID()
            asks = market.getASK()

            for order in bids:
                if abs(order.timestamp-self.cb.time) > 10:
                    self.cb.addMessage(order.traderID, "SELL:" + str(order.price*order.quantity))
                    bids.remove(order)

            for order in asks:
                if abs(order.timestamp-self.cb.time) > 10:
                    self.cb.addMessage(order.traderID, "BUY:" + str(name) + ":" + str(order.quantity))
                    asks.remove(order)

    def drawMarket(self):
        for name, market in self.orderBook.items():
            market.drawOrderBook()

    def returnParams(self):
        return 'NUM_NOISY_TRADER:'+str(self.num_noisy_traders)+'NUM_PRZEMEK_TRADER:'+str(self.num_Przemek_traders)+'NUM_TREND_TRADER:'+str(self.num_trend_traders)+'NUM_OF_ITERATIONS:'+str(self.num_iterations)
