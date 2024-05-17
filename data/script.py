import requests
from bs4 import BeautifulSoup
import re
import os

# Verify Rasa installation
try:
    from rasa.nlu.training_data import load_data
    from rasa.nlu.model import Trainer
    from rasa.nlu import config
except ImportError as e:
    print(f"Error importing Rasa modules: {e}")
    print("Please ensure that Rasa is correctly installed.")
    raise

# Function to download a file from GitHub
def download_file_from_github(url, local_path):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    with open(local_path, 'w', encoding='utf-8') as file:
        file.write(response.text)

# URLs of the files on GitHub
config_url = "https://raw.githubusercontent.com/MEADecarb/chat/main/data/config.yml"
nlu_url = "https://raw.githubusercontent.com/MEADecarb/chat/main/data/nlu.md"

# Local paths to save the downloaded files
nlu_local_path = "data/nlu.yml"
config_local_path = "config.yml"

# Ensure the data directory exists
os.makedirs(os.path.dirname(nlu_local_path), exist_ok=True)

# Download the files
download_file_from_github(nlu_url, nlu_local_path)
download_file_from_github(config_url, config_local_path)

# Web scraping functions
def extract_links(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    links = [link for link in links if link.startswith('https://energy.maryland.gov/') or link.startswith('/')]
    links = [link if link.startswith('https://') else 'https://energy.maryland.gov' + link for link in links]
    links = list(set(links))
    return links

def extract_content(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = [p.get_text() for p in soup.find_all('p')]
    content = ' '.join(paragraphs)
    return content

# Start web scraping
STARTING_URL = 'https://energy.maryland.gov/'
all_links = extract_links(STARTING_URL)
all_content = [extract_content(link) for link in all_links]
combined_content = ' '.join(all_content)

# Data Cleaning
cleaned_content = re.sub(r'\s+', ' ', combined_content.strip())

# Load training data
training_data = load_data(nlu_local_path)

# Load configuration
nlu_config = config.load(config_local_path)

# Create a trainer
trainer = Trainer(nlu_config)

# Train the model
interpreter = trainer.train(training_data)

# Save the trained model (optional)
model_directory = trainer.persist('models/', fixed_model_name='nlu')

print("Model training complete and saved to:", model_directory)

# Optionally, you can use the cleaned content for further training or analysis
# For example, you can save the cleaned content to a file
with open('data/cleaned_content.txt', 'w', encoding='utf-8') as file:
    file.write(cleaned_content)

print("Web scraped content saved to data/cleaned_content.txt")
