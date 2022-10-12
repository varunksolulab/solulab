import re
import datetime as dt
import sys
import time
from time import sleep

import requests as requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import urllib.request
import datetime


from packaging.requirements import URL
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as foptions
options = foptions()
options.add_argument('--headless')

# profile = webdriver.FirefoxProfile("/Users/apple/Library/Application Support/Firefox/Profiles/0ur7nimh.default-release-11")
# gecko_path="/Users/apple/doc/Git/geckodriver/geckodriver"
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
driver.maximize_window()

def location_res(result):
    '''Function to extract location from Indeed search result'''

    tag = result.find(name='div', attrs={'class': 'companyLocation'})  # find appropriate tag
    try:
        if re.search("<", tag.text):  # helps clean the data; extract text instead of html code
            return tag.find(name='div', attrs={'class': 'companyLocation'}).text
        else:
            return tag.text
    except:
        return 'NaN'


def company_res(result):
    '''Function to extract company name from Indeed search result'''

    tag = result.find(name='span', attrs={'class': 'companyName'})  # find appropriate tag
    try:  # First try statement accounts for whether there is any company at all
        try:  # Second try statement accounts for whether there any nested tags
            return tag.find('a').text
        except:      
            return tag.text
    except:
        return 'NaN'


def job_res(result):
    '''Function to extract job title'''

    try:  # Accounts for missing job title
        tag = result.find(name='a', attrs={'class': 'jcs-JobTitle css-jspxzf eu4oa1w0'})
        job = tag.text
        return job
    except:
        return 'NaN'


def salary_res(result):
    '''Function to extract salary'''
    try:
        tag = result.find(name='div',
                          attrs={'class': 'heading6 tapItem-gutter metadataContainer noJEMChips salaryOnly'})
        if tag.find(name='div', attrs={
            'class': 'metadata estimated-salary-container'}):  # Try statement is especially important for this function since most results don't have a salary
            tag2 = tag.find(name='div', attrs={'class': 'metadata estimated-salary-container'})
            tag3 = tag2.find(name='span', attrs={'class': 'estimated-salary'})
            tag4 = tag3.find('span')
            return tag4.text
        else:
            tag2 = tag.find(name='div', attrs={'class': 'metadata salary-snippet-container'})
            tag3 = tag2.find(name='div', attrs={'class': 'attribute_snippet'})
            return tag3.text

    except:
        return 'NaN'


def job_description(result):
    try:
        JD_link_list = []
        tag = result.find(name='a', attrs={'class': 'jcs-JobTitle css-jspxzf eu4oa1w0'})['href']
        if tag:
            try:
                if tag.__contains__('jk='):
                    hrefs = tag.split("jk=")
                    url_href = "https://www.indeed.com/viewjob?jk=" + hrefs[1]
                elif tag.__contains__('/company/'):
                    url_href = "https://www.indeed.com" + tag

            except:
                url_href = "https://www.indeed.com/viewjob?jk=" + hrefs[0]
            driver.execute_script(f"location.href='{url_href}';")
            time.sleep(6)
            html = driver.page_source
            soup_ = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
            tag2 = soup_.find(name='div', attrs={'id': 'jobDescriptionText'})
            if tag2.find('div'):
                job_desc = tag2.find('div').text
            else:
                job_desc = tag2.text
            JD_link_list.append(job_desc)
            tag3 = soup_.find(name='div', attrs={'class': 'icl-u-xs-hide icl-u-lg-block icl-u-lg-textCenter'})
            if tag3 is not None:
                link = tag3.find('a')['href']
            else:
                link = 'NaN'

            JD_link_list.append(link)
            return JD_link_list
        else:
            tag = result.find(name='div',attrs={'class':'jobsearch-jobDescriptionText'})
            job_desc = tag.text
            JD_link_list.append(job_desc)
            JD_link_list.append('NaN')
            return JD_link_list
    except:
        JD_link_list.append('NaN')
        JD_link_list.append('NaN')
        return JD_link_list

def Posted_Date(result):
    try:
        Today = datetime.datetime.today()
        tag = result.find(name='span',attrs={'class':'date'})
        posted_date = tag.text
        date_ = re.findall(r'\d+', posted_date)
        d = datetime.timedelta(days=int(date_[0]))
        a = Today - d
        Published_Date = a.strftime('%Y-%m-%d')
        return Published_Date
    except:
        Published_Date = 'NaN'
        return Published_Date



def all_funcs(search):
    '''
    This function iterates through each result on a single Indeed.com results
    page then applies the four functions above to extract the relevant
    information. It takes a search argument in order to also keep track of the
    search term used, since location can give a different value than the actual
    city or location searched.'''

    entries = []
    Today = datetime.datetime.today()
    for result in search.find_all(name='div', attrs={'class': 'job_seen_beacon'}):
        result_data = []
        result_data.append(job_res(result))
        result_data.append(company_res(result))
        result_data.append(location_res(result))
        result_data.append(salary_res(result))
        P_DATE = Posted_Date(result)
        if P_DATE:
            result_data.append(P_DATE)
        JD_LINK = job_description(result)
        for i in JD_LINK:
            result_data.append(i)
        One_MONTH = Today - datetime.timedelta(days=int(30))
        # result_data.append(search)
        if P_DATE !='NaN':
            if One_MONTH < datetime.datetime.strptime(P_DATE, '%Y-%m-%d'):
                entries.append(result_data)
            else:
                continue
    print(entries)
    return entries


def scrape(cities_list, max=10):
    max_results_per_city = max
    results = []  # Empty list that will contain all results
    a = dt.datetime.now()  # Start time of process
    print(a)
    for job in jobs:
        for city in cities_list:  # Iterate through cities
            for start in range(0, max_results_per_city, 5):  # Iterate through results pages
                url = "https://www.indeed.com/jobs?q="+job+"&l=" + city + "&start=" + str(start)
                driver.execute_script(f"location.href='{url}';")
                time.sleep(6)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
                data = all_funcs(soup)  # use functions from before to extract all job listing info
                for i in range(len(data)):  # add info to results list
                    results.append(data[i])
                sleep(1)
        #     print(city + " DONE")
        #     print("Elapsed time: " + str(dt.datetime.now() - a))  # Update user on progress

        # b = dt.datetime.now()
        # c = b - a
        # print(c)


    # Turn results list into dataframe
    df = pd.DataFrame(results, columns=['Job Title', 'Company', 'Location', 'Salary','Posted Date', 'Job Description',
                                        'Company URL'])

    name = str(dt.datetime.now())
    df.to_csv(f'./csvs/indeed_ethereum.csv')  # Save data


cities = ['Alabama',
'Alaska',
'Arizona',
'Arkansas',
'California',
'Colorado',
'Connecticut',
'Delaware',
'Florida',
'Georgia',
'Hawaii',
'Idaho',
'Illinois',
'Indiana',
'Iowa',
'Kansas',
'Kentucky',
'Louisiana',
'Maine',
'Maryland',
'Massachusetts',
'Michigan',
'Minnesota',
'Mississippi',
'Missouri',
'Montana',
'Nebraska',
'Nevada',
'New+Hampshire',
'New+Jersey',
'New+Mexico',
'New+York',
'North+Carolina',
'North+Dakota',
'Ohio',
'Oklahoma',
'Oregon',
'Pennsylvania',
'Rhode+Island',
'South+Carolina',
'South+Dakota',
'Tennessee',
'Texas',
'Utah',
'Vermont',
'Virginia',
'Washington',
'West+Virginia',
'Wisconsin',
'Wyoming']

jobs = ['Ethereum%20Developer', 'Blockchain%20Developer%20-%20Solidity/Ethereum',
    'Sr.%20Blockchain%20Engineer%20(Ganache)', 'Solidity%20Developer', 'Remote%20Blockchain%20Engineer%20(Ethereum/Solidity)', 'Smart%20Contract%20Developer', 
    'Fullstack%20Blockchain%20Developer', 'Blockchain%20Developer%20-%20Integration%20&%20Support', 'Research%20Engineer', 
    'Game%20Developer%20-%20Crypto%20/%20Blockchain%20/%20DeFi', 'Senior%20Smart%20Contract%20Dev', 'Senior%20Backend%20Developer',
     'Blockchain%20Engineer%20-%20Ethereum/Hyperledger', 'Ethereum%20Software%20Engineer', 'Blockchain%20(Solidity)%20Expert', 
     'Solidity%20Developer%20-%20DeFi', 'EOS/Graphene%20Blockchain%20Developer', 'Frontend%20Engineer%20-%20Blockchain%20Product',
      'Blockchain%20Developer%20/%20NFT', 'Senior%20Blockchain%20Engineer', 'Blockchain%20Engineer%20:%20rust/golang', 
      'Senior%20Golang%20Blockchain%20Protocol%20Developer', 'Consultant%20-%20Hyperledger%20Fabric%20Blockchain', 
      'Blockchain%20Developer%20-%20Ethereum/Hyperledger', 'Blockchain%20Developer%20-%20Hyperledger%20Fabric%20developer', 
      'Blockchain%20Engineer%20-%20Ethereum/Hyperledger', 'Blockchain%20Architect', 'Hyperledger%20Fabric%20Adminstrator%20(Remote-PAN%20India)', 
      'Senior%20Blockchain%20Engineer%20-%20Solidity/Smart%20Contract', 'Blockchain%20Developer%20Consultant%20(Associate/Senior)', 
      'Senior%20Blockchain%20Software%20Developer', 'Senior%20Blockchain%20Business%20Analyst', 'Core%20Blockchain%20Engineer%20at%20Cosmos%20SDK',
       'Senior%20Architect%20�%20Blockchain%20and%20Enterprise%20Ethereum']


scrape(cities)
driver.close()