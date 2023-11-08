# Importing required packages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

# Chromedriver path
c_path = r"C:\Users\gonda\Downloads\chromedriver-win64\chromedriver-win64\chromedriver"

# Creating a webdriver variable
driver = webdriver.Chrome(c_path)

# Search parameters
position = 'data analyst'
location = 'hyderabad'

# Headers for user-agent
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Constructing URL
url = f'https://www.naukri.com/excel-jobs-in-{location}?k={position}&l={location}'

# Navigating to the URL
driver.get(url)

# Wait for some time to allow the page to load
time.sleep(5)  # You can adjust the sleep time as needed

# Getting the page source after navigation
sitedata = driver.page_source

# Parsing the HTML using BeautifulSoup
soup = BeautifulSoup(sitedata, 'html.parser')

# Waiting time
driver.implicitly_wait(10)

# Finding the number of jobs found
n_element = driver.find_element(By.CLASS_NAME, 'styles_count-string__DlPaZ')
tot_no_of_jobs = n_element.text.split()[-1]
print(f'Total {tot_no_of_jobs} jobs found for the current search!')

# Number of jobs displayed per page
jobs_per_page = 20

# Creating a DataFrame to store the data
df_columns = ['Company Name', 'Job Title', 'Experience', 'Salary', 'Location', 'Description', 'Job Link', 'Tags', 'Posted']
data = pd.DataFrame(columns=df_columns)

# Iterate through all pages
for start in range(2, 16):  # Limited loop for 5 pages for fetching data
    page_url = f"{url}-{start}"
    driver.get(page_url)

    time.sleep(7)

    # Extracting information from the current page using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all job containers on the page
    job_containers = soup.find_all('div', class_='srp-jobtuple-wrapper')

    # Loop through each job container and extract information
    for job_container in job_containers:
        # Navigate to the 'row1' div
        job_title_div = job_container.find('div', class_='row1')
        job_title = job_title_div.find('a', class_='title') if job_title_div else None  # Find job title within 'row1' div

        company_name = job_container.find('a', class_='comp-name')
        exp = job_container.find('span', class_='exp-wrap')
        sal = job_container.find('span', class_='sal-wrap ver-line')
        location = job_container.find('span', class_='loc-wrap ver-line')  # this is only a preview of the description on the home screen job card
        description = job_container.find('span', class_='job-desc ni-job-tuple-icon ni-job-tuple-icon-srp-description')
        link = job_title_div.find('a', class_='title')['href'] if job_title_div else None
        posted = job_container.find('span', class_='job-post-day')

        tags_div = job_container.find('div', class_='row5')
        tags = tags_div.find('ul', class_='tags-gt')

        # Check if tags is not None before proceeding
        if tags:
            # Extracting text content from tags and joining into a comma-separated string
            tags_string = ', '.join(tag.text.title() for tag in tags.find_all('li', class_='dot-gt'))
        else:
            tags_string = None

        data = data.append({
            'Job Title': job_title.text if job_title else None,
            'Company Name': company_name.text if company_name else None,
            'Experience': exp.text if exp else None,
            'Salary': sal.text if sal.text else None,
            'Location': location.text if location.text else None,
            'Description': description.text if description else None,
            'Job Link': link if link else None,
            'Posted': posted.text.strip() if posted.text.strip() else None,
            'Tags': tags_string
        }, ignore_index=True)

    #printing data for checking any error in internal / subsequent pages 
    #print(data)

# Exporting data to Excel
data.to_excel('naukri.xlsx')

# Quit the webdriver
driver.quit()