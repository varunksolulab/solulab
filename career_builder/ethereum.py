import datetime
import math
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

from packaging.requirements import URL


def location_res(result):
    '''Function to extract location from Indeed search result'''

    tag = result.find(name='div', attrs={'class': 'data-details'})  # find appropriate tag
    try:
        tag2 = tag.select('span:nth-child(2)')
        location = tag2[0].text
        return location
    except:
        return 'NaN'


def company_res(result):
    '''Function to extract company name from Indeed search result'''

    tag = result.find(name='div', attrs={'class': 'data-details'})  # find appropriate tag
    try:  # Second try statement accounts for whether there any nested tags
        tag2 = tag.select('span:nth-child(1)')
        Name = tag2[0].text
        return Name
    except:
        return 'NaN'


def job_res(result):
    '''Function to extract job title'''

    try:  # Accounts for missing job title
        tag = result.find(name='div', attrs={'class': 'data-results-title dark-blue-text b'})
        job = tag.text
        return job
    except:
        return 'NaN'


def salary_res(result):
    '''Function to extract salary'''
    try:
        tag = result.find(name='div', attrs={'class': 'data-snapshot'})
        tag2 = tag.select('div:nth-child(2)')
        Salary = tag2[0].text
        if Salary.__contains__("$"):
            return Salary
        else:
            return 'NaN'
    except:
        return 'NaN'

def Date_Published(result):
    try:
        Today = datetime.datetime.today()
        tag = result.find(name ='div',attrs={'class':'col-2 layout-results'})
        tag2 = tag.find(name ='div',attrs={'class':'col big col-mobile-inline'})
        tag3 = tag2.find(name ='div',attrs={'class':'data-results-publish-time'})
        date_ = tag3.text
        date_ = re.findall(r'\d+', date_)
        d = datetime.timedelta(days=int(date_[0]))
        a = Today - d
        return a.strftime('%Y-%m-%d')
    except:
        return 'NaN'


def job_description(result):
    try:
        tag = result.find(name='a', attrs={'class': 'data-results-content block job-listing-item'})['href']
        url_href = "https://www.careerbuilder.com" + tag
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
        response = requests.get(url_href,headers=headers)
        html = response.text
        soup_ = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
        tag2 = soup_.find(name='div', attrs={'class': 'col big col-mobile-full jdp-left-content'})
        job_desc = tag2.text
        return job_desc
    except:
        return 'NaN'


def all_funcs(search):
    '''
    This function iterates through each result on a single Indeed.com results
    page then applies the four functions above to extract the relevant
    information. It takes a search argument in order to also keep track of the
    search term used, since location can give a different value than the actual
    city or location searched.'''

    entries = []
    Today = datetime.datetime.today()
    One_MONTH = Today - datetime.timedelta(days=int(30))
    for result in search.find_all(name='li', attrs={'class': 'data-results-content-parent relative'}):
        result_data = []
        P_DATE = Date_Published(result)
        if P_DATE !='NaN':
            if P_DATE:
                if One_MONTH < datetime.datetime.strptime(P_DATE, '%Y-%m-%d'):
                    result_data.append(job_res(result))
                    result_data.append(company_res(result))
                    result_data.append(location_res(result))
                    result_data.append(salary_res(result))
                    result_data.append(P_DATE)
                    result_data.append(job_description(result))
                    result_data.append('Career Builder')
                    # result_data.append(search)
                    entries.append(result_data)
                else:
                    continue


    return entries


def scrape(cities_list,job_list, max=50):
    max_results_per_city = max
    page_no = math.ceil(max/25)
    results = []  # Empty list that will contain all results
    a = dt.datetime.now()  # Start time of process
    print(a)

    for job in job_list:
        for city in cities_list:  # Iterate through cities
            for start in range(page_no):  # Iterate through results pages
                url = "https://www.careerbuilder.com/jobs?keywords="+ job +"&location=" + city + "&page_number=" + str(start+1)
                try:
                    html = urllib.request.urlopen(url).read()
                except:
                    continue
                soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
                data = all_funcs(soup)  # use functions from before to extract all job listing info
                for i in range(len(data)):  # add info to results list
                    results.append(data[i])
                sleep(1)
            print(city + " DONE")
            print("Elapsed time: " + str(dt.datetime.now() - a))  # Update user on progress

        b = dt.datetime.now()
        c = b - a
        print(c)

        print(job + "Done")
        print("Elapsed time: " + str(dt.datetime.now() - a))
    d= dt.datetime.now()
    time_taken = d-a
    print(time_taken)

    # Turn results list into dataframe
    df = pd.DataFrame(results, columns=['Job Title', 'Company', 'Location', 'Salary','Publishing Date', 'Job Description', 'Source'])

    name = str(dt.datetime.now())
    df.to_csv(f'csvs/CareerBuilder_ethereum.csv')  # Save data


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
'Wyoming'
]

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

scrape(cities,jobs)
