import os
import requests
from bs4 import BeautifulSoup
import json
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    filename='airfoil_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL of the UIUC Airfoil Coordinates Database
base_url = 'https://m-selig.ae.illinois.edu/ads/coord_seligFmt/'

# Directory to save .dat files
dat_directory = '.airfoils'

# Create the directory if it doesn't exist
os.makedirs(dat_directory, exist_ok=True)

try:
    # Fetch the main page
    response = requests.get(base_url)
    response.raise_for_status()
    logger.info(f'Successfully fetched the main page: {base_url}')
except requests.exceptions.HTTPError as http_err:
    logger.error(f'HTTP error occurred while fetching the main page: {http_err}')
    raise
except Exception as err:
    logger.error(f'An error occurred while fetching the main page: {err}')
    raise

# Parse the main page to find links to .dat files
soup = BeautifulSoup(response.text, 'html.parser')
dat_links = soup.find_all('a', href=True)

# Dictionary to store airfoil coordinates
airfoils = {}

# Iterate over all links found
for link in dat_links:
    href = link['href']
    if href.endswith('.dat'):
        # Construct the full URL to the .dat file
        dat_url = urljoin(base_url, href)
        try:
            # Fetch the .dat file
            dat_response = requests.get(dat_url)
            dat_response.raise_for_status()
            logger.info(f'Successfully fetched data for {href}')
        except requests.exceptions.HTTPError as http_err:
            if dat_response.status_code == 404:
                logger.error(f'404 Not Found: {dat_url}')
            else:
                logger.error(f'HTTP error occurred while fetching {dat_url}: {http_err}')
            continue
        except Exception as err:
            logger.error(f'An error occurred while fetching {dat_url}: {err}')
            continue

        # Save the .dat file to the airfoils directory
        dat_file_path = os.path.join(dat_directory, href)
        try:
            with open(dat_file_path, 'wb') as dat_file:
                dat_file.write(dat_response.content)
            logger.info(f'Successfully saved {href} to {dat_file_path}')
        except IOError as e:
            logger.error(f'Failed to write {href} to {dat_file_path}: {e}')
            continue

        # Read the lines of the file
        lines = dat_response.text.splitlines()
        # The first line is the airfoil name
        airfoil_name = lines[0].strip()
        # Initialize a list to hold the coordinates
        coordinates = []
        # Process each subsequent line
        for line in lines[1:]:
            # Skip comment lines
            if line.startswith('#'):
                continue
            # Split the line into x and y components
            parts = line.split()
            if len(parts) == 2:
                try:
                    x, y = float(parts[0]), float(parts[1])
                    coordinates.append([x, y])
                except ValueError:
                    logger.warning(f'Invalid coordinate format in {dat_url}: {line}')
                    continue
        # Store the coordinates in the dictionary
        airfoils[airfoil_name] = coordinates

# Save the dictionary to a JSON file
try:
    with open('airfoils.json', 'w') as json_file:
        json.dump(airfoils, json_file, indent=2)
    logger.info('Successfully saved airfoils data to airfoils.json')
except IOError as e:
    logger.error(f'Failed to write to airfoils.json: {e}')
