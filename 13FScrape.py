#script for scraping 13f.info. got rate throttled - to do - change first part of scrape to selenium...

import time
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException

start_time = time.time()

# read in site map as .xml file and convert to soup
with open('fillingsSiteMap.xml', 'r') as f:
    soup = BeautifulSoup(f, 'xml')
f.close()

#parse soup for all links
links = soup.find_all('loc')
print(links)

#convert links to list
linksList = []
for link in links:
    linksList.append(link.text)
#print(linksList)
#print(len(linksList))

#remove the first 4484 links
linksList = linksList[6577:]


#convert list to dataframe
df = pd.DataFrame(linksList)
print(df)


#add new columns for firm, aum, no1Holding, no1Holding%, no2Holding, no2Holding%, no3Holding, no3Holding%, no4Holding, no4Holding%, no5Holding, no5Holding%
df['firm'] = np.nan
df['aum($000)'] = np.nan
df['no1Holding'] = np.nan
df['no1Name'] = np.nan
df['no1Holding%'] = np.nan
df['no2Holding'] = np.nan
df['no2Name'] = np.nan
df['no2Holding%'] = np.nan
df['no3Holding'] = np.nan
df['no3Name'] = np.nan
df['no3Holding%'] = np.nan
df['no4Holding'] = np.nan
df['no4Name'] = np.nan
df['no4Holding%'] = np.nan
df['no5Holding'] = np.nan
df['no5Name'] = np.nan
df['no5Holding%'] = np.nan
df['no6Holding'] = np.nan
df['no6Name'] = np.nan
df['no6Holding%'] = np.nan
df['no7Holding'] = np.nan
df['no7Name'] = np.nan
df['no7Holding%'] = np.nan
df['no8Holding'] = np.nan
df['no8Name'] = np.nan
df['no8Holding%'] = np.nan
df['no9Holding'] = np.nan
df['no9Name'] = np.nan
df['no9Holding%'] = np.nan
df['no10Holding'] = np.nan
df['no10Name'] = np.nan
df['no10Holding%'] = np.nan



count = 0

#visit each link and scrape the relevant information
#company loop
for link in linksList:

    #request the website and convert to soup
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')


    #find firm name
    firm = soup.find('h1')
    firm = firm.find('a')
    firm = firm.string
    print(firm)

    #find aum
    #def custom filer to find aum. tag name must be dd and string must contain $ sign
    def aumFilter(tag):
        return tag.name == 'dd' and '$' in tag.string
    aum = soup.find(aumFilter)
    aum = str(aum.string)
    print(aum)



    #use selenium to find the table
    #open chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    #navigate to link
    driver.get(link)
    #find the table with the top 5 holdings, but make sure it collects all of the children of the table
    try:
        table = driver.find_element(By.TAG_NAME, 'table')
    except StaleElementReferenceException:
        continue
    except:
        continue
    print(table.text)

    #check if the table contains "There are no holdings"
    if "There are no holdings" in table.text:
        print("skip this firm...")
        continue


    top5Ticker = []
    top5Name = []
    top5Percent = []

    fail = False

    #iterate through the table and find the top 5 holdings and their percentages
    #holdings loop
    print("begin holdings loop")
    for i in range(1,11):
        #add a function to continue the loop if there is no element or if there is a stale element
        #query loop
        for attempt in range(5):
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//tr[' + str(i) + ']/td[1]')))
                top5Ticker += table.find_elements(By.XPATH, '//tr[' + str(i) + ']/td[1]')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//tr[' + str(i) + ']/td[2]')))
                top5Name += table.find_elements(By.XPATH, '//tr[' + str(i) + ']/td[2]')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//tr[' + str(i) + ']/td[6]')))
                top5Percent += table.find_elements(By.XPATH, '//tr[' + str(i) + ']/td[6]')
            # use the check response function from error handler to check if the response is valid
            except TimeoutException:
                print("timeout exception")
                #if it's the fifth attempt, turn fail to true
                if attempt == 4:
                    fail = True
                continue
            except StaleElementReferenceException:
                print("stale element exception")
                if attempt == 4:
                    fail = True
                continue
            except UnexpectedAlertPresentException:
                print("unexpected alert present exception")
                if attempt == 4:
                    fail = True
                continue
            except:
                print("other exception")
                if attempt == 4:
                    fail = True
                continue
            #if the response is valid, break out of the loop
            break


        if fail == True:
            print("could not find element")
            break
        try:
            print(top5Ticker[i-1].text)
            print(top5Name[i-1].text)
            print(top5Percent[i-1].text)
            print('')
        except:
            print("stale element exception")
            break

    if fail == True:
        print("skip this firm...")
        continue

    #add data to dataframe
    df.loc[df[0] == link, 'firm'] = firm
    df.loc[df[0] == link, 'aum'] = aum

    #check if each value is within range; if not, skip
    try:
        df.loc[df[0] == link, 'no1Holding'] = top5Ticker[0].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no1Name'] = top5Name[0].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no1Holding%'] = top5Percent[0].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no2Holding'] = top5Ticker[1].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no2Name'] = top5Name[1].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no2Holding%'] = top5Percent[1].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no3Holding'] = top5Ticker[2].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no3Name'] = top5Name[2].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no3Holding%'] = top5Percent[2].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no4Holding'] = top5Ticker[3].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no4Name'] = top5Name[3].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no4Holding%'] = top5Percent[3].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no5Holding'] = top5Ticker[4].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no5Name'] = top5Name[4].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no5Holding%'] = top5Percent[4].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no6Holding'] = top5Ticker[5].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no6Name'] = top5Name[5].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no6Holding%'] = top5Percent[5].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no7Holding'] = top5Ticker[6].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no7Name'] = top5Name[6].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no7Holding%'] = top5Percent[6].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no8Holding'] = top5Ticker[7].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no8Name'] = top5Name[7].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no8Holding%'] = top5Percent[7].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no9Holding'] = top5Ticker[8].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no9Name'] = top5Name[8].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no9Holding%'] = top5Percent[8].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no10Holding'] = top5Ticker[9].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no10Name'] = top5Name[9].text
    except:
        continue
    try:
        df.loc[df[0] == link, 'no10Holding%'] = top5Percent[9].text
    except:
        continue



    print(df)
    df.to_csv('13fScrape.csv')
    count += 1
    print(count, '13fs scraped, estimated time to completion: ', (len(linksList) - count) * (time.time() - start_time) / count / 60, ' minutes')



