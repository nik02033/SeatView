import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# Initialize the Chrome browser with Selenium WebDriver
options = Options()
options.headless = False  # Set to True if you don't need a browser UI
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def get_open_seats(class_number):
    try:
        # Go to the class search page
        driver.get('https://catalog.apps.asu.edu/catalog/classes')
        time.sleep(1)  # Wait for the page to load completely

        # Wait for the term dropdown to be present and clickable
        wait = WebDriverWait(driver, 15)
        term_dropdown_element = wait.until(EC.element_to_be_clickable((By.ID, 'term')))

        # Ensure the element is indeed a 'select' element
        if term_dropdown_element.tag_name != "select":
            raise Exception("The located element is not a 'select' element.")

        # Create a Select object for the dropdown and select the term by visible text
        term_select = Select(term_dropdown_element)
        term_select.select_by_visible_text('Spring 2024') 

        # Wait for the search box to be present and enter the class number
        search_box = wait.until(EC.presence_of_element_located((By.ID, 'keyword')))
        search_box.clear()
        search_box.send_keys(class_number)

        # Find the search button and click it
        search_button = driver.find_element(By.ID, 'search-button')
        search_button.click()

        # Wait for the search results to load and for the open seats element to be present
        wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[1]/div/div/div[5]/div/div/div/div[2]/div[12]/div')))

        # Locate the element that contains the number of open seats
        open_seats_element = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[1]/div/div/div[5]/div/div/div/div[2]/div[12]/div')
        open_seats_text = open_seats_element.text.strip()
        open_seats = int(open_seats_text.split(' ')[0])
        return open_seats

    except NoSuchElementException:
        print("Dropdown option 'Spring 2024' does not exist.")
          # Wait for 10 seconds before closing the browser
        return None
    except TimeoutException:
        print("Timed out waiting for the elements to be present.")
        
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(3)  # Wait for 10 seconds before closing the browser
        return None
    
        

# Example usage
class_number = '30429'  # Replace with the class number you want to search for
open_seats = get_open_seats(class_number)
if open_seats is not None and open_seats > 0:
    print(f"There are {open_seats} open seats for class number {class_number}.")
else:
    print("No open seats available or could not retrieve open seats information.")
