import os
import time
import smtplib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tee_time_checker.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load configuration from environment variables
def load_config():
    config = {
        "TEE_TIMES_USERNAME": os.getenv("TEE_TIMES_USERNAME", ""),
        "TEE_TIMES_PASSWORD": os.getenv("TEE_TIMES_PASSWORD", ""),
        "EMAIL_FROM": os.getenv("EMAIL_FROM", ""),
        "EMAIL_TO": os.getenv("EMAIL_TO", ""),
        "GMAIL_APP_PASSWORD": os.getenv("GMAIL_APP_PASSWORD", ""),
        "ALERT_TIMES": os.getenv("ALERT_TIMES", "")
    }
    return config

TWILIGHT_SCHEDULE = [
    (datetime(2024, 1, 2), datetime(2024, 1, 15), "12:30pm"),
    (datetime(2024, 1, 31), datetime(2024, 3, 9), "1:00pm"),
    (datetime(2024, 3, 10), datetime(2024, 4, 7), "2:00pm"),
    (datetime(2024, 4, 8), datetime(2024, 5, 5), "2:30pm"),
    (datetime(2024, 5, 6), datetime(2024, 8, 11), "3:00pm"),
    (datetime(2024, 8, 12), datetime(2024, 9, 8), "2:30pm"),
    (datetime(2024, 9, 9), datetime(2024, 9, 29), "2:00pm"),
    (datetime(2024, 9, 30), datetime(2024, 11, 2), "1:30pm"),
    (datetime(2024, 11, 3), datetime(2025, 1, 1), "12:00pm"),
]

def get_twilight_start_time(date):
    for start_date, end_date, twilight_time in TWILIGHT_SCHEDULE:
        if start_date <= date <= end_date:
            return twilight_time
    return None


# Example usage:
config = load_config()
username = config["TEE_TIMES_USERNAME"]
password = config["TEE_TIMES_PASSWORD"]
email_from = config["EMAIL_FROM"]
email_to = config["EMAIL_TO"]
gmail_app_password = config["GMAIL_APP_PASSWORD"]
alert_times = config["ALERT_TIMES"]

# Parse alert times
alert_start_time, alert_end_time = alert_times.split('-')
alert_start_time = datetime.strptime(alert_start_time.strip(), "%H:%M").time()
alert_end_time = datetime.strptime(alert_end_time.strip(), "%H:%M").time()

# Log loaded configuration
logger.info(f"Loaded configuration: {config}")
logger.info(f"Alert Time Range: {alert_start_time} - {alert_end_time}")

# Function to log in and navigate to the tee times page for 0-3 days
def login_and_navigate_0_3():
    logger.info("Starting login and navigation process for 0-3 days")

    # Set up Firefox options
    firefox_options = Options()
    firefox_options.add_argument("-headless")
    driver = webdriver.Firefox(options=firefox_options)
                 
    login_url = "https://foreupsoftware.com/index.php/booking/19347#/login"
    teetimes_url = "https://foreupsoftware.com/index.php/booking/19347/1487#/teetimes"

    # Login process
    driver.get(login_url)
    time.sleep(5)

    username_field = driver.find_element(By.ID, 'login_email')
    password_field = driver.find_element(By.ID, 'login_password')
    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)

    # Navigate to the tee times page
    driver.get(teetimes_url)
    time.sleep(5)

    book_now_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Non Resident (0 - 3 Days)')]"))
    )
    book_now_button.click()
    time.sleep(5)

    logger.info("Login and navigation successful for 0-3 days")
    return driver

# Function to log in and navigate to the tee times page for 4-90 days
def login_and_navigate_4_90():
    logger.info("Starting login and navigation process for 4-90 days")

    # Set up Firefox options
    firefox_options = Options()
    firefox_options.add_argument("-headless")
    driver = webdriver.Firefox(options=firefox_options)

    login_url = "https://foreupsoftware.com/index.php/booking/19347#/login"
    teetimes_url = "https://foreupsoftware.com/index.php/booking/19347/1487#/teetimes"

    # Login process
    driver.get(login_url)
    time.sleep(5)

    username_field = driver.find_element(By.ID, 'login_email')
    password_field = driver.find_element(By.ID, 'login_password')
    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    time.sleep(5)

    # Navigate to the tee times page
    driver.get(teetimes_url)
    time.sleep(5)

    book_now_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Non Resident (4 - 90 Days)')]"))
    )
    book_now_button.click()
    time.sleep(5)

    logger.info("Login and navigation successful for 4-90 days")
    return driver

# Function to get tee times
def get_tee_times(driver):
    logger.info("Getting tee times")
    tee_times = {}

    try:
        datepicker_days = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'datepicker-days'))
        )

        # Get the current month and year from the datepicker
        month_year_text = datepicker_days.find_element(By.CLASS_NAME, 'datepicker-switch').text.strip().split()
        month, year = month_year_text[0], month_year_text[1]

        # Find available days
        day_elements = datepicker_days.find_elements(By.XPATH, ".//td[contains(@class, 'day') and not(contains(@class, 'old')) and not(contains(@class, 'disabled'))]")

        # Loop through available days
        for i in range(len(day_elements)):
            datepicker_days = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'datepicker-days'))
            )
            day_elements = datepicker_days.find_elements(By.XPATH, ".//td[contains(@class, 'day') and not(contains(@class, 'old')) and not(contains(@class, 'disabled'))]")

            # Click on a day to retrieve tee times
            day_elements[i].click()
            time.sleep(2)

            # Re-get month and year in case it changes
            month_year_text = datepicker_days.find_element(By.CLASS_NAME, 'datepicker-switch').text.strip().split()
            month, year = month_year_text[0], month_year_text[1]
            active_day_element = datepicker_days.find_element(By.XPATH, ".//td[contains(@class, 'active')]")
            day = active_day_element.text.strip()

            date = f"{month} {day}, {year}"
            day_of_week = datetime.strptime(date, "%B %d, %Y").strftime("%A")
            date_with_day = f"{day_of_week} {date}"
            date_obj = datetime.strptime(date, "%B %d, %Y")
            twilight_start_time = get_twilight_start_time(date_obj)

            # Now check for both "booking-start-time-label" and "booking-slot-details"
            try:
                booking_start_time_labels = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'booking-start-time-label'))
                )

                booking_slot_details = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'booking-slot-details'))
                )

                daygolf_tee_times = []
                twilight_tee_times = []

                for label, slot in zip(booking_start_time_labels, booking_slot_details):
                    time_str = label.text

                    holes = slot.find_element(By.CLASS_NAME, 'booking-slot-holes').text.strip()
                    players = slot.find_element(By.CLASS_NAME, 'booking-slot-players').text.strip()
                    details = f"Holes: {holes}, Players: {players}"

                    time_only = time_str.split(" ")[0] 

                    try:
                        time_obj = datetime.strptime(time_only, "%I:%M%p")
                    except ValueError as ve:
                        logger.error(f"Error parsing time '{time_only}': {ve}")
                        continue

                    hour_as_int = int(time_obj.strftime("%H"))
                    time_str_24 = time_obj.strftime("%H:%M")
                    twilight_time = get_twilight_start_time(date_obj)

                    if twilight_start_time and datetime.strptime(time_str_24, "%H:%M") >= datetime.strptime(twilight_start_time, "%I:%M%p"):
                        twilight_tee_times.append(f"{time_str} - {details}")
                    else:
                        daygolf_tee_times.append(f"{time_str} - {details}")


                # Add to tee_times dictionary
                tee_times[date_with_day] = {
                    "daygolf": daygolf_tee_times,
                    "twilight": twilight_tee_times
                }

            except Exception as e:
                logger.error(f"No booking start time labels or slot details found for {date_with_day}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error retrieving tee times: {e}")

    logger.info("Tee times retrieval successful")
    return tee_times

# Function to compare tee times and find new ones
def compare_tee_times(previous, current, alert_start_time, alert_end_time):
    new_tee_times = {}

    # Log the alert time range for troubleshooting
    logger.info(f"Alert Time Range: {alert_start_time} - {alert_end_time}")
    def is_within_time_range(time_str, start_time, end_time):

        time_only = time_str.split(" ")[0]
        try:
            time_obj = datetime.strptime(time_only, "%I:%M%p").time()
            return start_time <= time_obj <= end_time
        except ValueError as e:
            logger.error(f"Error parsing time '{time_only}': {e}")
            return False


    for date, times in current.items():
        if date not in previous:
            new_daygolf_times = [time_str for time_str in times["daygolf"] if is_within_time_range(time_str, alert_start_time, alert_end_time)]
            new_twilight_times = [time_str for time_str in times["twilight"] if is_within_time_range(time_str, alert_start_time, alert_end_time)]

            if new_daygolf_times or new_twilight_times:
                new_tee_times[date] = {
                    "daygolf": new_daygolf_times,
                    "twilight": new_twilight_times
                }
        else:
            new_daygolf_times = list(set(times["daygolf"]) - set(previous[date]["daygolf"]))
            new_twilight_times = list(set(times["twilight"]) - set(previous[date]["twilight"]))

            alert_daygolf_times = [time_str for time_str in new_daygolf_times if is_within_time_range(time_str, alert_start_time, alert_end_time)]
            alert_twilight_times = [time_str for time_str in new_twilight_times if is_within_time_range(time_str, alert_start_time, alert_end_time)]

            if alert_daygolf_times or alert_twilight_times:
                new_tee_times[date] = {
                    "daygolf": alert_daygolf_times,
                    "twilight": alert_twilight_times
                }

                # Log tee times within the alert time range
                logger.info(f"Tee times within the alert time range for {date}:")
                if alert_daygolf_times:
                    logger.info("Daygolf Tee Times:")
                    for tee_time in alert_daygolf_times:
                        logger.info(tee_time)
                if alert_twilight_times:
                    logger.info("Twilight Tee Times:")
                    for tee_time in alert_twilight_times:
                        logger.info(tee_time)

    return new_tee_times

# Function to send email
def send_email(new_tee_times):
    logger.info("Sending email with new tee times")

    from_address = email_from
    to_address = email_to.split(',')

    subject_days = ", ".join(new_tee_times.keys())

    subject = f"New Tee Times - Torrey Pines South - {subject_days}"

    body = "New Tee Times:\n\n"

    for date, times in new_tee_times.items():
        body += f"Date: {date}\n"
        if times["daygolf"]:
            body += "Daygolf Tee Times:\n"
            for tee_time in times["daygolf"]:
                body += f"{tee_time}\n"
        if times["twilight"]:
            body += "Twilight Tee Times:\n"
            for tee_time in times["twilight"]:
                body += f"{tee_time}\n"
        body += "\n"

    if not new_tee_times:
        body += "No new tee times available.\n"

    msg = MIMEMultipart()
    msg['From'] = "Golf Tee Time Bot"  # Change the sender name here
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, gmail_app_password)
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

# Main loop to run every 10 minutes
previous_tee_times = {}

while True:
    try:
        # Check tee times for 0-3 days
        driver_0_3 = login_and_navigate_0_3()
        current_tee_times_0_3 = get_tee_times(driver_0_3)
        driver_0_3.quit()

        logger.info("All available tee times for 0-3 days:")
        for date, times in current_tee_times_0_3.items():
            logger.info(f"Date: {date}")
            if times["daygolf"]:
                logger.info("Daygolf Tee Times:")
                for tee_time in times["daygolf"]:
                    logger.info(tee_time)
            if times["twilight"]:
                logger.info("Twilight Tee Times:")
                for tee_time in times["twilight"]:
                    logger.info(tee_time)

        new_tee_times_0_3 = compare_tee_times(previous_tee_times, current_tee_times_0_3, alert_start_time, alert_end_time)

        if new_tee_times_0_3:
            logger.info("New Tee Times for 0-3 days:")
            for date, times in new_tee_times_0_3.items():
                logger.info(f"Date: {date}")
                if times["daygolf"]:
                    logger.info("Daygolf Tee Times:")
                    for tee_time in times["daygolf"]:
                        logger.info(tee_time)
                if times["twilight"]:
                    logger.info("Twilight Tee Times:")
                    for tee_time in times["twilight"]:
                        logger.info(tee_time)

            send_email(new_tee_times_0_3)
        else:
            logger.info("No new tee times available for 0-3 days.")

        previous_tee_times.update(current_tee_times_0_3)

        # Check tee times for 4-90 days
        driver_4_90 = login_and_navigate_4_90()
        current_tee_times_4_90 = get_tee_times(driver_4_90)
        driver_4_90.quit()

        logger.info("All available tee times for 4-90 days:")
        for date, times in current_tee_times_4_90.items():
            logger.info(f"Date: {date}")
            if times["daygolf"]:
                logger.info("Daygolf Tee Times:")
                for tee_time in times["daygolf"]:
                    logger.info(tee_time)
            if times["twilight"]:
                logger.info("Twilight Tee Times:")
                for tee_time in times["twilight"]:
                    logger.info(tee_time)

        new_tee_times_4_90 = compare_tee_times(previous_tee_times, current_tee_times_4_90, alert_start_time, alert_end_time)

        if new_tee_times_4_90:
            logger.info("New Tee Times for 4-90 days:")
            for date, times in new_tee_times_4_90.items():
                logger.info(f"Date: {date}")
                if times["daygolf"]:
                    logger.info("Daygolf Tee Times:")
                    for tee_time in times["daygolf"]:
                        logger.info(tee_time)
                if times["twilight"]:
                    logger.info("Twilight Tee Times:")
                    for tee_time in times["twilight"]:
                        logger.info(tee_time)

            send_email(new_tee_times_4_90)
        else:
            logger.info("No new tee times available for 4-90 days.")

        previous_tee_times.update(current_tee_times_4_90)

        time.sleep(600)  # Wait for 10 minutes (600 seconds) before running the script again
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        time.sleep(600)  # Wait for 10 minutes before retrying
