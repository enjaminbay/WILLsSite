import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os.path
from .forms import MyForm
from .SMAstrategy import spikeTest, SMAcrossOver

def home_page(request):
    form = MyForm(request.POST or None)
    AverageROI = ''
    successRate = ''
    buySellDict = ''
    if request.method == 'POST':
        if form.is_valid():
            Ticker = form.cleaned_data['Ticker']
            Ticker = Ticker.upper()
            SMAlength = form.cleaned_data['SMAlength']

            FULLdata = spikeTest(Ticker, 1000, 0, timePeriod=SMAlength)
            data = FULLdata['Data']['SMA20']['rawData']
            priceData = FULLdata['Other']['TotalPrices']

            buySellDict, successRate, AverageROI = SMAcrossOver(data, priceData)

            for date in buySellDict:
                print(date, buySellDict[date])

            print("Success Rate ==> ", successRate)
            print("Average ROI ==> ", AverageROI)
    return render(request, 'home/home_page.html', {'buySellDict':buySellDict,
                                                   'successRate':successRate,
                                                   'AverageROI':AverageROI,
                                                   'form':form
                                                   })

