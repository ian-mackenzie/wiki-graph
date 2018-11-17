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

def wiki_trim_map(link):
    return link[6:]

def scrape_page(url):
    # query the url and return raw html to page
    requestUrl = 'https://en.wikipedia.org/wiki/' + url
    with urllib.request.urlopen(requestUrl) as response:
        links = BeautifulSoup(response.read(), parse_only=SoupStrainer('a'),features="html.parser")
        href_links = list(link['href'] for link in links if href_filter(link))
        href_set = list(set(href_links))
        href_set.sort()
        trim_href_set = map(wiki_trim_map, href_set)
        return trim_href_set

def main():
    scrape_page('History')

if __name__ == '__main__':
    main()
