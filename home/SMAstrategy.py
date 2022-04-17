import time
import pandas as pd
from pandas import DataFrame as df
import requests
from datetime import timedelta
import traceback

def TAdataRequest(Function, Ticker, timePeriod, dataKey, timeFrame='daily', full='No'):
    success = False
    time_passed = 0
    while success == False:
        try:
            Function = Function.upper()
            FunctionData = Function + 'data'
            if timePeriod != 'No' and full == 'No':
                url = 'https://www.alphavantage.co/query?function=' + Function + '&symbol=' + Ticker + '&interval='+timeFrame+'&time_period=' + str(
                    timePeriod) + '&series_type=close&apikey=HZ0SGS5ODH8JP1K2'
            elif timePeriod == 'No' and full == 'No':
                url = 'https://www.alphavantage.co/query?function=' + Function + '&symbol=' + Ticker + '&interval='+timeFrame+'&series_type=close&apikey=HZ0SGS5ODH8JP1K2'
            elif timePeriod == 'No' and full == 'Yes':
                url = 'https://www.alphavantage.co/query?function=' + Function + '&symbol=' + Ticker + '&interval='+timeFrame+'&series_type=close&outputsize=full&apikey=HZ0SGS5ODH8JP1K2'
            else:
                url = 'https://www.alphavantage.co/query?function=' + Function + '&symbol=' + Ticker + '&interval='+timeFrame+'&time_period=' + str(
                    timePeriod) + '&series_type=close&outputsize=full&apikey=HZ0SGS5ODH8JP1K2'

            r = requests.get(url)
            FunctionData = r.json()
            FunctionData = FunctionData[dataKey]
            try:
                firstKey = list(FunctionData.keys())[0]
                firstKeyFix = firstKey[:firstKey.index(' ')]
                FunctionData[firstKeyFix] = FunctionData[firstKey]
                FunctionData.pop(firstKey)
            except Exception as e:
                pass

            success = True
            return FunctionData
        except Exception as e:
            print(traceback.format_exc())
            print('Error in TAdataRequest -->', e)
            time_passed += 5
            time.sleep(5)
            print(Function, time_passed, " seconds have passed")

def spikeTest(Ticker, amountOfTradingDays, minimumChange, VolatilityCheck=False, timeFrame='daily', timePeriod=20):
    # Get Historical data For indicators
    indicatorData = dict()
    if timeFrame == 'daily':
        Adjusted_data = TAdataRequest(Function='TIME_SERIES_DAILY_ADJUSTED', Ticker=Ticker, timePeriod='No',
                                       dataKey='Time Series (Daily)', full='Yes')
    elif timeFrame == 'weekly':
        Adjusted_data = TAdataRequest(Function='TIME_SERIES_WEEKLY_ADJUSTED', Ticker=Ticker, timePeriod='No',
                                      dataKey='Weekly Adjusted Time Series')

    def smaPercentages(smaType_list):
        dataClean = dict()
        for date in list(smaType_list.keys()):
            dataClean[date] = dict()
            dataClean[date]['SMA'] = str(round(100 * (float(smaType_list[date]['SMA']) / float(
                Adjusted_data[date]['5. adjusted close']) - 1), 3))
        return dataClean

    sma20_data = TAdataRequest(Function='SMA', Ticker=Ticker, timePeriod=timePeriod, dataKey='Technical Analysis: SMA', timeFrame=timeFrame)
    sma20_data = smaPercentages(sma20_data)

    indicatorData["SMA20"] = [sma20_data, 'SMA']

    if amountOfTradingDays <= len(Adjusted_data.keys()):
        DateOfAmountOfDays = list(Adjusted_data.keys())[amountOfTradingDays + 1]
        consideredDays = list(Adjusted_data.keys())[:amountOfTradingDays + 1]
    elif amountOfTradingDays > len(Adjusted_data.keys()):
        TotalDays = list(Adjusted_data.keys())
        DateOfAmountOfDays = TotalDays[-1]
        consideredDays = list(Adjusted_data.keys())
    closeData = dict()
    closeData['5. adjusted close'] = dict()
    for date in consideredDays:
        closeData['5. adjusted close'][date] = float(Adjusted_data[date]['5. adjusted close'])
    closeData = df.from_dict(closeData)

    ADJcloseData = df.to_dict(closeData)['5. adjusted close']

    # convert from price of stock to the percent change day to day
    percentData = closeData.pct_change()
    # shifting everything up one becuase I am considering the values of indicators for the day BEFORE they go up a given amount...so each value is actually the next days change
    percentData = percentData.shift(periods=-1)
    percentData = percentData.drop(labels=consideredDays[0], axis=0)
    dataSorted = df.to_dict(percentData.sort_values(ascending=False, by='5. adjusted close'))['5. adjusted close']


    newDataSorted = dataSorted
    kickOut = list()

    if len(kickOut) != len(dataSorted):
        try:
            averageGain = dict()
            for date in newDataSorted.keys():
                averageGain[pd.to_datetime(str(date)).strftime('%Y-%m-%d')] = dict()
                averageGain[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]['Indicators'] = dict()
                def averageGainCreation(date, averageGain, data, specialIndicatorName, specialKey):
                    # Use special key for indicators like SMA50 vs SMA 200 because the only difference is the timePeriod
                    try:
                        averageGain[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]['Indicators'][specialIndicatorName] \
                        = round(float(data[pd.to_datetime(str(date)).strftime('%Y-%m-%d')][specialKey]), 2)
                    except:
                        averageGain[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]['Indicators'][specialIndicatorName] \
                            = 0
                    return averageGain

                for indicator in indicatorData.keys():
                    averageGainCreation(date, averageGain, data=indicatorData[indicator][0], specialIndicatorName=indicator,
                                        specialKey=indicatorData[indicator][1])


                averageGain[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]['Other'] = dict()

                averageGain[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]['Other']['Change'] \
                    = round(float(dataSorted[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]) * 100, 2)

                cleanData = df.to_dict(closeData)['5. adjusted close']
                averageGain[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]['Other']['Price'] \
                    = cleanData[pd.to_datetime(str(date)).strftime('%Y-%m-%d')]

            answers = dict()
            answers['Data'] = dict()

            def plugIndicatorsIntoAnswers(answers, rawData, rawDataWithoutKey, specialIndicatorName, specialKey):
                if specialKey != 'SMA':
                    try:
                        answers['Data'][specialIndicatorName] = dict()
                        # RAW data is wrong...passing all data taken from API query including other ones. Like all MACD, all Bollinger bands etc
                        answers['Data'][specialIndicatorName]['rawData'] = rawDataWithoutKey
                        answers['Data'][specialIndicatorName]['totalRawData'] = rawData
                    except:
                        print(traceback.format_exc())
                        error = 'no data greater than ' + str(minimumChange) + '%'
                        answers['Data'][specialIndicatorName]['rawData'] = error
                        answers['Data'][specialIndicatorName]['totalRawData'] = error
                    return answers
                else:
                    try:
                        answers['Data'][specialIndicatorName] = dict()
                        answers['Data'][specialIndicatorName]['rawData'] = rawDataWithoutKey
                        answers['Data'][specialIndicatorName]['totalRawData'] = rawData
                    except:
                        print(traceback.format_exc())
                        error = 'no data greater than ' + str(minimumChange) + '%'
                        answers['Data'][specialIndicatorName]['rawData'] = error
                        answers['Data'][specialIndicatorName]['totalRawData'] = error
                    return answers

            # looking through the indicators in one date of averageGain
            for indicator in averageGain[list(averageGain.keys())[0]]['Indicators'].keys():
                mainList = list()
                for date in averageGain:
                    mainList.append(averageGain[date]['Indicators'][indicator])

                data = indicatorData[indicator][0]
                rawDataWithoutKey = dict(data)
                specialKey = indicatorData[indicator][1]
                for date in rawDataWithoutKey:
                    rawDataWithoutKey[date] = rawDataWithoutKey[date][specialKey]
                answers = plugIndicatorsIntoAnswers(answers, rawData=data, rawDataWithoutKey=rawDataWithoutKey, specialIndicatorName=indicator,
                                                    specialKey=specialKey)


            changeList = list()
            for date in averageGain:
                changeList.append(averageGain[date]['Other']['Change'])

            answers['Other'] = dict()

            answers['Other']['TotalPrices'] = ADJcloseData

            answers['Other']['TotalChanges'] = df.to_dict(percentData)['5. adjusted close']

            answers['Other']['DataOfInstancesPriceChange'] = newDataSorted

            answers['Other']['StartDate'] = DateOfAmountOfDays

            answers['Other']['NumberOfInstancesWithALargerMagnitudePercentChangeThanMinimumChange'] = len(
                averageGain.keys())

            answers['Other']['NumberOfConsideredInstances'] = len(answers['Other']['TotalChanges'])

            answers['Other']['MinimumChange'] = minimumChange

            return answers
        except Exception as e:
            print(traceback.format_exc())
            pass
    else:
        answers = dict()
        answers['Number of instances with a larger magnitude percent change than minimum change'] = "There is no data that work with what you inputed at the top of the page"
        # my view will just input error for each of these
        return answers

def SMAcrossOver(data, priceData):
    buySellDict = dict()
    lastItem = list(priceData.keys())[0]
    try:
        dateList = list(data.keys())[:list(data.keys()).index(lastItem)]
    except:
        dateList = list(data.keys())

    for i in range(len(dateList)-1):
        if float(data[dateList[i]]) < 0 and float(data[dateList[i+1]]) > 0:
            buySellDict[dateList[i]] = dict()
            buySellDict[dateList[i]]['Long/Short'] = 'Long'
            buySellDict[dateList[i]]['price'] = priceData[dateList[i]]
        elif float(data[dateList[i]]) > 0 and float(data[dateList[i+1]]) < 0:
            buySellDict[dateList[i]] = dict()
            buySellDict[dateList[i]]['Long/Short'] = 'Short'
            buySellDict[dateList[i]]['price'] = priceData[dateList[i]]


    crossDates = list(buySellDict.keys())
    current = ''
    last = ''
    for i in range(len(crossDates)-1):
        if i == 0:
            current = buySellDict[crossDates[i]]
            buySellDict.pop(crossDates[0])
            crossDates = crossDates[1:]
        elif i == len(crossDates)-1:
            last = buySellDict[crossDates[len(crossDates)-1]]
            buySellDict.pop(crossDates[len(crossDates)-1])
            crossDates = crossDates[:-1]
        elif i != 0:
            amountOfDaysSinceLastCross = dateList.index(crossDates[i]) - dateList.index(crossDates[i-1])
            buySellDict[crossDates[i]]['AmountOfDaysHeld'] = amountOfDaysSinceLastCross
            PL = round(
                    100 * (buySellDict[crossDates[i-1]]['price'] - buySellDict[crossDates[i]]['price']) /
                    buySellDict[crossDates[i]]['price'], 2)

            if buySellDict[crossDates[i]]['Long/Short'] == 'Short':
                buySellDict[crossDates[i]]['gainLoss'] = -PL
                if PL <= 0:
                    buySellDict[crossDates[i]]['Success'] = 'Yes'
                elif PL > 0:
                    buySellDict[crossDates[i]]['Success'] = 'No'
            elif buySellDict[crossDates[i]]['Long/Short'] == 'Long':
                buySellDict[crossDates[i]]['gainLoss'] = PL
                if PL >= 0:
                    buySellDict[crossDates[i]]['Success'] = 'Yes'
                elif PL < 0:
                    buySellDict[crossDates[i]]['Success'] = 'No'




    amountSuccess = 0
    ToRemove = []
    for date in buySellDict:

        try:
            if buySellDict[date]['Success'] == 'Yes':
                amountSuccess += 1
        except KeyError:
            # must remove the last item of the dictionary
            ToRemove.append(date)
    buySellDict.pop(ToRemove[0])
    successRate = round(100*amountSuccess/len(buySellDict),2)

    count = 0
    totalPL = 0
    for date in buySellDict:
        count += 1
        totalPL += buySellDict[date]['gainLoss']
    AverageROI = round(totalPL/count,2)

    return buySellDict, successRate, AverageROI


# FULLdata = spikeTest(stock, 1000, 0, timePeriod=20)
# data = FULLdata['Data']['SMA20']['rawData']
# priceData = FULLdata['Other']['TotalPrices']
#
# buySellDict, successRate, AverageROI = SMAcrossOver(data, priceData)
#
# for date in buySellDict:
#     print(date, buySellDict[date])
#
# print("Success Rate ==> ", successRate)
# print("Average ROI ==> ", AverageROI)