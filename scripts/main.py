from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

# Setup Chrome browser with auto driver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Fullscreen

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Go to Foodpanda Karachi restaurants page
driver.get("https://www.foodpanda.pk/restaurants/city/karachi")

# Wait for full page load
time.sleep(8)


prev_height = 0
scroll_round = 0
stuck_counter = 0
MAX_STUCK = 10  # give 6 chances
MAX_SCROLLS = 150  # max rounds to avoid infinite loop

while scroll_round < MAX_SCROLLS:
    scroll_round += 1
    print(f"Scrolling round {scroll_round}...")

    # Send multiple PAGE_DOWN keys to simulate real user scrolling
    for _ in range(3):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    vendor_tiles = soup.select('a[data-testid^="vendor-tile"]')
    current_height = len(vendor_tiles)

    print(f"Found vendor tiles: {current_height}")

    if current_height == prev_height:
        stuck_counter += 1
        print(f"No increase detected ({stuck_counter}/{MAX_STUCK})")
        if stuck_counter >= MAX_STUCK:
            print("Reached end. Stopping scroll.")
            break
    else:
        stuck_counter = 0  # Reset if growth detected

    prev_height = current_height

# Save full page HTML for later extraction
with open("page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("HTML saved to 'page.html'")
driver.quit()