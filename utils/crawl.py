import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
from urllib.request import Request, urlopen
from utils.openai import embedding_request
from csv import writer
import pandas as pd

DATA_URL='processed'
EMBEDDING_FILE = DATA_URL+"/embeddings.csv"
HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'

# Create a directory to store the text files
if not os.path.exists(DATA_URL+"/"):
    os.mkdir(DATA_URL+"/")

if not os.path.exists(EMBEDDING_FILE):
    # If the directory doesn't exist, create it and any necessary intermediate directories
    df = pd.DataFrame(list())
    df.to_csv(EMBEDDING_FILE)

# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])

def get_hyperlinks(url):
    
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        head = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
        }
        with urlopen(Request(url, headers=head)) as response:

            # If the response is not HTML, return an empty list
            if not response.info().get('Content-Type').startswith("text/html"):
                return []
            
            # Decode the HTML
            html = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks


def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif (
                link.startswith("#")
                or link.startswith("mailto:")
                or link.startswith("tel:")
            ):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))

def get_domain(url):
    return urlparse(url).netloc

def crawl(url):

    if(url[len(url) - 1:] == '/'):
        url = url[:-1]
        
    # Parse the URL and get the domain
    local_domain = get_domain(url)

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    if not os.path.exists(DATA_URL+"/"+local_domain+"/"):
            os.mkdir(DATA_URL+"/" + local_domain + "/")

    # While the queue is not empty, continue crawling
    while queue:

        # Get the next URL from the queue
        url = queue.pop()
        print(url) # for debugging and to see the progress

        # Try extracting the text from the link, if failed proceed with the next item in the queue
        try:
            # Save text from the url to a <url>.txt file
            with open(DATA_URL+'/'+local_domain+'/'+url[8:].replace("/", "_") + ".txt", "w", encoding="UTF-8") as f:\
            
                # Get the text from the URL using BeautifulSoup
                soup = BeautifulSoup(requests.get(url).text, "html.parser")

                # Get the text but remove the tags
                text = soup.get_text()

                # If the crawler gets to a page that requires JavaScript, it will stop the crawl
                if ("You need to enable JavaScript to run this app." in text):
                    print("Unable to parse page " + url + " due to JavaScript being required")
            
                # Otherwise, write the text to the file in the text directory
                f.write(text)
        except Exception as e:
            print("Unable to parse page " + url)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, url):
            if link not in seen:
                queue.append(link)
                seen.add(link)

def summarize_url(url):
    crawl(url)
    local_domain = get_domain(url)

    # Get all the text files in the text directory
    for file in os.listdir(DATA_URL+"/" + local_domain + "/"):

        # Open the file and read the text
        with open(DATA_URL+"/" + local_domain + "/" + file, "r", encoding="UTF-8") as f:
            title = file[11:-4].replace('-',' ').replace('_', ' ').replace('#update','')
            embedding_data = embedding_request(text=title)
            file_reference = [
                title,
                DATA_URL+"/" + local_domain + "/" + file,
                embedding_data,
            ]
            with open(EMBEDDING_FILE, "a") as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(file_reference)
                f_object.close()