import requests
from bs4 import BeautifulSoup

# The URL of the pharmacy
url = "https://onlinefamilypharmacy.com/"

try:
    print("Connecting to the website...")
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # This pulls the text out of the website
    data = soup.get_text(separator='\n', strip=True)

    # This creates the file that was "missing"
    with open("pharmacy_data.txt", "w", encoding="utf-8") as f:
        f.write(data)
    
    print("Success! 'pharmacy_data.txt' has been created on your Desktop.")

except Exception as e:
    print(f"Error: {e}")    