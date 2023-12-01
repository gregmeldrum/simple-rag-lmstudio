import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Set for storing already visited urls
visited_urls = set()

data_directory = "./content"

def get_page_content(url):
    """
    Returns the content of the webpage at `url`
    """
    response = requests.get(url)
    return response.text

def get_all_links(content, domain):
    """
    Returns all valid links on the page
    """
    soup = BeautifulSoup(content, "html.parser")
    links = soup.find_all("a")
    valid_links = []

    for link in links:
        href = link.get('href')
        if href != None and not href.startswith("..") and href != "#" and not href.startswith("#"):
            if href.startswith("http"):
                if href.startswith(domain):
                    print("Following", href)
                    valid_links.append(href)
            else:

                print("Following", strip_after_last_hash(href))
                valid_links.append(domain + '/' + strip_after_last_hash(href))
    return valid_links

def strip_after_last_hash(url):
    """
    Strips off all characters after the last "#" in `url`,
    if "#" does not have a "/" character before it.
    """
    hash_index = url.rfind('#')
    if hash_index > 0 and url[hash_index - 1] != '/':
        return url[:hash_index]
    else:
        return url

def write_to_file(url, content):
    """
    Write the content to a text file with the name as the URL
    """
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    filename = data_directory + '/' + url.replace('/', '_').replace(':', '_') + '.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        lines = content.split('\n')
        non_blank_lines = [line for line in lines if line.strip() != '']
        f.write('\n'.join(non_blank_lines))

def scrape(url, depth):
    """
    Scrapes the webpage at `url` up to a certain `depth`
    """
    scheme = urlparse(url).scheme # Get the scheme
    domain = urlparse(url).netloc # Get base domain
    path = os.path.dirname(urlparse(url).path) # Get base path excluding the last part

    print("URL", url)
    if depth == 0 or url in visited_urls:
        return

    visited_urls.add(url)

    print(f"Scraping: {url}")
    content = get_page_content(url)
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()
    write_to_file(url, text)

    links = get_all_links(content, scheme + "://" + domain + path)

    for link in links:
        scrape(link, depth - 1)
