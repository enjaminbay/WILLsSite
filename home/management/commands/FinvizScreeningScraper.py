from finviz.screener import Screener
import datetime as dt
import time
import json
from itertools import combinations, permutations



def main():
    count = 0
    KEYS = [
        ['Market Cap.', 'Nano (under $50mln)'],
        ['Sector', 'Utilities'],
        ['P/E', 'High (>50)'],
        ['PEG', 'High (>2)'],
        ['InsiderTransactions', 'Very Positive (>20%)'],
        ['Earnings Date', 'This Month'],
        ['Performance', 'Month +50%'],
        ['RSI (14)', 'Oversold (10)'],
        ['Gap', 'Down 20%'],
        ['Pattern', 'Head & Shoulders Inverse'],
        ['Target Price', '50% Below Price'],
        ['Return on Investment', 'Very Negative (<-10%)'],
        ['Return on Assets', 'Very Negative (<-15%)'],
        ['Beta', 'Over 4']
    ]

    dict_all_filters = Screener.load_filter_dict()
    unique_combinations = make_filter_pairs(dict_all_filters, KEYS)

    for filterPair in unique_combinations:
        print(filterPair)
    print("number of pairs is", len(unique_combinations))

    dataDict = scrape_finviz(unique_combinations)
    make_file(dataDict)

def make_file(dataDict):
    print(dataDict)
    newDict = {}
    date1 = (str(dt.date.today()) + ".json")
    newDict[str(date1)] = dataDict

    print(dt.date.today())

    with open(date1, "a") as outfile:
        json.dump(dataDict, outfile)

def scrape_finviz(unique_combinations):
    dataDict = {}
    for r in range(len(unique_combinations)):
        filters = unique_combinations[r]
        try:
            time.sleep(0.1)
            stock_list = Screener(filters=filters, rows=20, table='Performance', order='-MarketCap')
            dataDict[str(filters)] = {}
            scraped_stocks = list()
            for stock in stock_list[0:len(stock_list)]:
                # dataDict[str(filters)][stock['Ticker']] = float(stock['Price'])
                scraped_stocks.append(stock['Ticker'])
            print(filters)
            print(scraped_stocks)
            dataDict[str(filters)] = scraped_stocks
            print("pair number", r + 1)
        except Exception as e:
            print("EXCEPTION OCCURED - the error was", e)
            try:
                stock_list = Screener(filters=filters, table='Performance', order='-MarketCap')
                dataDict[str(filters)] = {}
                scraped_stocks = list()
                for stock in stock_list[0:len(stock_list)]:
                    # dataDict[str(filters)][stock['Ticker']] = float(stock['Price'])
                    scraped_stocks.append(stock['Ticker'])
                print(filters)
                print(scraped_stocks)
                dataDict[str(filters)] = scraped_stocks
                print("pair number", r + 1)
            except Exception:
                print("NO DATA AVAILABLE")
                pass
    return dataDict

def make_filter_pairs(dict_all_filters, KEYS):
    categories = []
    realFilters = []
    for i in range(len(KEYS)):
      endIndex = (list(dict_all_filters[KEYS[i][0]].keys()).index(KEYS[i][1]))
      categories.append(list(dict_all_filters[KEYS[i][0]].keys())[:endIndex+1])

    for i in range(len(categories)):
      categories[i].remove('Any')


    for j in range (len(categories)):
      for p in range (len(categories[j])):
        categories[j][p] = dict_all_filters[KEYS[j][0]][categories[j][p]]

    categories_combos = []
    combos = combinations(categories,2)
    combos_list1 = list(combos)
    categories_combos += combos_list1

    unique_combinations = []
    for y in range(len(categories_combos)):
      permut = permutations(categories_combos[y][0], 1)
      for comb in permut:
        zipped = list(map(list,zip(comb, categories_combos[y][1])))
        unique_combinations.append(list(zipped)[0])
    return unique_combinations







main()