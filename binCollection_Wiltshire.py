import requests
import json
import datetime
import voluptuous as vol
from datetime import timedelta
from bs4 import BeautifulSoup

valNextBinDay = datetime.datetime.now()
valNextBinDay_Recycling = datetime.datetime.now()
valNextBinDay_Waste = datetime.datetime.now()

configPOSTCODE = 'BA148JQ'

def main():
    Fetch(configPOSTCODE)
    print("Next bin day:\t\t" + str(valNextBinDay.date()))
    print("Next waste:\t\t" + str(valNextBinDay_Waste.date()))
    print("Next recycling:\t\t" + str(valNextBinDay_Recycling.date()))

def fetchAddressList(strPostcode):
    url = 'https://ilforms.wiltshire.gov.uk/WasteCollectionDays/AddressList'
    dataobj = {
        'Postcode': strPostcode
        }

    jsonAddressList = requests.post(url, data = dataobj)
    dictAddressList = json.loads(jsonAddressList.text)
    listProps = dictAddressList.get('Model', {}).get('PostcodeAddresses')
    UPRN = listProps[0].get('UPRN')

    return UPRN

def fetchCollectionList(strMonth, strYear, strPostcode, strUPRN):
    strHTML = postRequest(strMonth, strYear, strPostcode, strUPRN)
    # Filter out relevant information and store in dict
    parsedHTML = BeautifulSoup(strHTML, features="html.parser")

    events = parsedHTML.body.find_all('div', attrs={'class':'rc-event-container'})
    dictBinDays = []
    for event in events:
        strDate = event.next.attrs.get('data-original-datetext')
        #print(strDate)
        strType = event.text
        #print(strType)

        strColour = ""
        if strType in ['Household waste']:
            strColour = ['Grey']
        else:
            strColour = ['Blue','Black']
        
        BinDay = {
            'Date': strDate,
            'Type': strColour
            }
        dictBinDays.append(BinDay)
        #print(dictBinDays)

    #print('.')
    #print(dictBinDays)

    return dictBinDays

def postRequest(strMonth, strYear, strPostcode, strUPRN ):
    url = 'https://ilforms.wiltshire.gov.uk/WasteCollectionDays/CollectionList'
    thisdict = {
        'Month': strMonth,
        'Year': strYear,
        'Postcode': strPostcode,
        'Uprn': strUPRN
    }
    strHTML = requests.post(url, data = thisdict).text
    strHTML = '<html><head></head><body>' + strHTML + '</body></html>'
    return strHTML

def PertinentDays(Dates):
    Days = []
    for i in Dates:
        #print(i.get('Date'))
        collect = datetime.datetime.strptime(i.get('Date'), '%A %d %B, %Y')
        #print(collect)
        today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        #print(today)

        if collect > today:
            # Future
            Days.append(i)
        elif collect == today:
            # Today
            Days.append(i)
        else:
            #Past
            continue
    return Days

def RolloverMonth(Days, Postcode, UPRN):
    strMonth = datetime.datetime.now().month
    strYear = datetime.datetime.now().year
    strMonth += 1
    listDates = fetchCollectionList(strMonth, strYear, Postcode, UPRN)
    listDates = PertinentDays(listDates)
    for i in listDates:
        Days.append(i)

    return Days

def RolloverYear(Days, Postcode, UPRN):
    length = len(Days)
    strMonth = 1
    strYear = datetime.datetime.now().year
    strYear += 1
    listDates = fetchCollectionList(strMonth, strYear, Postcode, UPRN)
    listDates = PertinentDays(listDates)
    for i in listDates:
        Days.append(i)

    return Days

def Fetch(inputPostcode):
    valNextBinDay = datetime.datetime.now()
    valNextBinDay_Recycling = datetime.datetime.now()
    valNextBinDay_Waste = datetime.datetime.now()

    # Fetch first UPRN so we get valid results back
    strUPRN = fetchAddressList(inputPostcode)       

    # Fetch the calendar information for the current month and year
    strMonth = datetime.datetime.now().month
    strYear = datetime.datetime.now().year
    listDates = fetchCollectionList(strMonth, strYear, inputPostcode, strUPRN)

    # Store next days after today
    listDays = PertinentDays(listDates)

    # We ONLY want 2
    length = len(listDays)
    # Trying next month if under
    if length <= 1:
        listDays = RolloverMonth(listDays, inputPostcode, strUPRN)
        length = len(listDays)
    # Try next year if still under
    if length <= 1:
        listDays = RolloverYear(listDays, inputPostcode, strUPRN)
        length = len(listDays)
    # If we don't have more than two now the web service is screwed
    if length > 2:
        listDays = listDays[:2]

    valNextBinDay = datetime.datetime.strptime(listDays[0].get('Date'), '%A %d %B, %Y').replace(hour=0, minute=0, second=0, microsecond=0)
    for i in listDays:
        test = i.get('Type')[0]
        if test in ['Grey']:
            valNextBinDay_Waste = datetime.datetime.strptime(i.get('Date'), '%A %d %B, %Y').replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            valNextBinDay_Recycling = datetime.datetime.strptime(i.get('Date'), '%A %d %B, %Y').replace(hour=0, minute=0, second=0, microsecond=0)

    return 0

main()