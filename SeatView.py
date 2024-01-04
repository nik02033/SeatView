import smtplib
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
is_class_open = None

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
        return None
    except TimeoutException:
        print("Timed out waiting for the elements to be present.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(3)  # Wait for 3 seconds before closing the browser
        return None

def send_email_body(class_number, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Gmail SMTP port for TLS
    smtp_security = 'TLS'  # Use 'TLS' for Gmail
    sender_email = 'Email'  # Replace with your Gmail address
    app_password = 'Pass'  # Replace with the generated App Password
    recipient_email = 'Email'  # Replace with the recipient's email address
    subject = f" {body}"

    try:
        mail = smtplib.SMTP(smtp_server, smtp_port)
        mail.ehlo()
        if smtp_security == 'TLS':
            mail.starttls()
        mail.login(sender_email, app_password)
        
        message = f"Subject: {subject}\n\n{body}"

        mail.sendmail(sender_email, recipient_email, message)
        mail.close()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def monitor_class_availability(class_number, check_interval=300):
    global is_class_open
    while True:
        open_seats = get_open_seats(class_number)
        if open_seats is not None:
            if is_class_open is None:
                # First run, set the initial state
                is_class_open = open_seats > 0
                send_initial_email(class_number, is_class_open)
            elif open_seats > 0 and not is_class_open:
                # Class opened up
                is_class_open = True
                send_email(class_number, open_seats, "opened")
            elif open_seats == 0 and is_class_open:
                # Class closed
                is_class_open = False
                send_email(class_number, open_seats, "closed")
        time.sleep(check_interval)
    
def send_initial_email(class_number, is_open):
    status = "open" if is_open else "closed"
    body = f"The class {class_number} is currently {status}. We will notify you when the status changes."
    send_email_body(class_number, body)

def send_email(class_number, open_seats, status):
    if status == "opened":
        body = f"The class {class_number} has just opened up with {open_seats} available seats."
    elif status == "closed":
        body = f"The class {class_number} has closed with no available seats."
    send_email_body(class_number, body)

#Example usage
class_number = '30139'  # Replace with the class number you want to search for
monitor_class_availability(class_number)
