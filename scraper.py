import urllib.request
from bs4 import BeautifulSoup, SoupStrainer

def href_filter(link):
    if not link.has_attr('href'):
        return False
    if ':' in link['href']:
        return False
    if not link['href'].startswith('/wiki/'):
        return False
    return True

def scrape_page(url):
    # query the url and return raw html to page
    with urllib.request.urlopen('https://en.wikipedia.org' + url) as response:
        links = BeautifulSoup(response.read(), parse_only=SoupStrainer('a'),features="html.parser")
        href_links = list(link['href'] for link in links if href_filter(link))
        href_link_set = list(set(href_links))
        href_link_set.sort()
        return href_link_set

def main():
    scrape_page('/wiki/History')

if __name__ == '__main__':
    main()
