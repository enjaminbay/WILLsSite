
import json
import pandas as pd
import yfinance as yf
from datetime import date, timedelta



def makeDates():
  dates = []
  for i in range(14):
    if ((date.today()-timedelta(14-i)).weekday() == 5 or (date.today()-timedelta(14-i)).weekday() == 6):
      pass
    else:
      dates.append(date.today() - timedelta(14 - i))
  dates.append(date.today())
  return dates


def openFiles(dataPast):
  with open(dataPast) as f:
    data = json.load(f)
  stocks = []
  for key in data:
    for stock in data:
      stocks.append(stock)
  return data, stocks

def calcIndividualStockPrices(data, dataForStocks,dateTested,SandPprice, dates):
  priceNow = {}
  o = dict()
  for filters in data:
    ticker_list = data[filters]
    o[filters] = {}
    for stock in ticker_list:
      priceThen = round(dataForStocks[stock][dateTested.strftime('%Y-%m-%d')], 4)
      SandPpriceThen = SandPprice[str(dateTested)]
      o[filters][stock] = {}
      for k in range(len(dates)):
        try:
          dt = dates[k]
          r = list()
          r.append(round(dataForStocks[stock][dt.strftime('%Y-%m-%d')], 2))
          priceNow[dt.strftime('%Y-%m-%d')] = r
          t = list()
          if (dateTested < dates[k]):

            SandPpriceChange = round(100 * (float(pd.to_numeric(SandPprice[str(dt)])) - SandPpriceThen) / SandPpriceThen, 4)
            stockPriceChange = round((100 * (float(pd.to_numeric(priceNow[str(dt)])) - priceThen) / priceThen), 4)
            t.append(stockPriceChange + SandPpriceChange)
            w = list()
            for q in range((dt - dateTested).days):
              if ((dateTested + timedelta(q)).weekday() == 5) or ((dateTested + timedelta(q)).weekday() == 6):
                w.append("weekend day!")
            if ((dt - dateTested).days > 0):
              daysSinceTrading = (dt - dateTested).days - len(w)
              o[filters][stock][daysSinceTrading] = t
          else:
            pass
        except KeyError as e:
          pass

  return o

def findPercentGain(o, dateTested):
  percentGainLoss = {}
  for pairFilters in o:
    percentGainLoss[pairFilters] = {}
    for b in range(len(list(o[pairFilters].keys()))):
      daysPastList = list((o[pairFilters][list(o[pairFilters])[b]]).keys())
      for z in range(len(daysPastList)):
        afterNDays = list()
        for stock2 in (o[pairFilters]).keys():
          afterNDays.append((o[pairFilters][stock2][daysPastList[z]]))
        flat_pricesStocks = list()
        for sublist in afterNDays:
          for item in sublist:
            flat_pricesStocks.append(item)
        sum_percentGainLoss = sum(flat_pricesStocks)
        average_percentGainLoss = sum_percentGainLoss / len(list(o[pairFilters]))
        percentGainLoss[pairFilters]["After "+ str(daysPastList[z])+ " Days"] = round(average_percentGainLoss, 2)
  analysisFile = str(dateTested)+"-->GainLoss.json"
  with open(analysisFile, "w") as outfile:
    json.dump(percentGainLoss, outfile)
  print("Exported Gain/Loss Directory to -->", analysisFile)
  #print(percentGainLoss)
  return percentGainLoss

def findStockPrices(dates):
  allStocks = []
  for i in range(len(dates)):
    dataPast = str(dates[i]) + ".json"
    try:
      with open(dataPast) as f:
        data = json.load(f)
      stocks = []
      for key in data:
        for stock in data[key]:
          stocks.append(stock)
      for i in stocks:
        if i not in allStocks:
          allStocks.append(i)
      yf.pdr_override()
    except FileNotFoundError as e:
      print("ERROR WAS -->", e)
      pass

  dataForStocks1 = yf.download(allStocks[0:int((1 / 2) * len(allStocks))], start=(date.today() - timedelta(15)), end=date.today()+timedelta(1))["Close"]
  dataForStocks2 = yf.download(allStocks[int((1 / 2) * len(allStocks)):int(len(allStocks))], start=(date.today() - timedelta(15)), end=date.today()+timedelta(1))["Close"]
  dataForStocks = pd.concat([dataForStocks1, dataForStocks2], axis=1)
  SandPprice = yf.download("^GSPC", start=(date.today() - timedelta(15)), end=date.today() + timedelta(1))['Close']
  return SandPprice, dataForStocks

def whileTesting_StockPrices():
  dataForStocks = pd.read_json('file.json', orient ='split', compression = 'infer')
  SandPprice = yf.download("^GSPC", start=(date.today() - timedelta(15)), end=date.today() + timedelta(1))['Close']
  return dataForStocks, SandPprice

def printData(percentGainLoss):
  pd.set_option("display.max_columns", 20)
  pd.set_option("display.max_colwidth", None)
  GLdf = pd.DataFrame.from_dict(percentGainLoss)

  bestFilters = pd.DataFrame.idxmax(GLdf, axis=1)
  bestFilters1 = bestFilters

  bestFiltersPrices = pd.DataFrame.max(GLdf, axis=1)
  for r in range(len(list(bestFiltersPrices.values))):
    bestFilters1['After '+str(r+1)+" Days"] = bestFilters1['After '+str(r+1)+" Days"]+'  -->  '+str(list(bestFiltersPrices.values)[r])+'%'
  print(bestFilters1)


def whichWorksBest(percentGainLoss):
  findWorkingBest = dict()
  for length in range(len(percentGainLoss[list(percentGainLoss.keys())[1]].keys())):
    for pairFilters in percentGainLoss.keys():
      lengths = list(percentGainLoss[pairFilters].keys())[length]
      findWorkingBest[pairFilters] = percentGainLoss[pairFilters][lengths]


def main():
  dates = makeDates()
  #Use findStockPrices() when actually running the code but its fine to use whileTesting_StockPrices() because its just precalculated and means it wont run every time you run the code
  #SandPprice, dataForStocks = findStockPrices(dates)
  dataForStocks, SandPprice = whileTesting_StockPrices()
  print(dataForStocks)
  for date in dates:
    print("DATA FROM DATE", date)
    dateTested = date
    dataPast = str(date) + ".json"
    try:
      data, stocks = openFiles(dataPast)
      o = calcIndividualStockPrices(data,dataForStocks,dateTested,SandPprice, dates)
      percentGainLoss = findPercentGain(o, dateTested)
      whichWorksBest(percentGainLoss)
    except FileNotFoundError as e:
      print("ERROR WAS -->", e)
      pass

main()


