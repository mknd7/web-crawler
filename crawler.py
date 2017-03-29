from bs4 import BeautifulSoup
import urllib
from StringIO import StringIO
import gzip
import re

# Takes URL, returns BeautifulSoup object
def get_page(url):
    try:
        # For assuming identity as browser
        # class NewOpener(urllib.FancyURLopener):
        #     version = '''Mozilla/5.0 (X11; Linux i686)
        #                 AppleWebKit/535.2 (KHTML, like Gecko)
        #                 Ubuntu/11.10 Chromium/15.0.874.120
        #                 Chrome/15.0.874.120 Safari/535.2'''
        # op = NewOpener()
        # response = op.open(url)

        response = urllib.urlopen(url)
        if response.info().get('Content-Encoding') == 'gzip':
            # If response is in gzip
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            html = f.read()
        else:
            html = response.read()
        return BeautifulSoup(html, "html.parser")
    except:
        return BeautifulSoup("")

# Gets text and adds keywords to index
def add_page_to_index(index, url, content):
    text = content.get_text()
    # Match any one of the delimiters inside class [...]
    # \s is equivalent to whitespace chars [ \t\n\r\f\v]
    words = re.split('[\s,.;:!?]+', text)
    # Get rid of empty strings in list
    words = filter(None, words)
    for word in words:
        add_to_index(index, word.encode('ascii', 'ignore'), url)

# Returns list of all links from Soup object
def get_all_links(page):
    urls = []
    for link in page.find_all('a'):
        ulink = link.get('href')
        urls.append(ulink.encode('ascii', 'ignore'))
    return urls

# Performs union of two lists; result in first list
def union(p,q):
    for i in q:
        if i not in p:
            p.append(i)

# Adds entry pair to index (dictionary)
# Format of index: {keyword1: [urls], keyword2: [urls]...}
def add_to_index(index, keyword, url):
    keyword = keyword.lower()
    if keyword in index:
        if url not in index[keyword]:
            index[keyword].append(url)
    else:
        index[keyword] = [url]

# Looks up keyword in index, returns list of URLs
def lookup(index, keyword):
    keyword = keyword.lower()
    if keyword in index:
        return index[keyword]
    else:
        return None

# Returns single best URL for given keyword
def lookup_best(index, ranks, keyword):
    urls = lookup(index, keyword)
    if not urls:
        return None
    else:
        best_url = urls[0]
        for url in urls:
            if ranks[url] > ranks[best_url]:
                best_url = url
        return best_url

# Returns list of URLs, ranked
def lookup_all(index, ranks, keyword):
    urls = lookup(index, keyword)
    if not urls:
        return None
    else:
        # Sort list of URLs based on values of ranks dict
        ranked_urls = sorted(urls, key=lambda url: ranks[url], reverse=True)
        return ranked_urls

# Returns true for reciprocal link (with collusion level k)
def is_reciprocal_link(graph, source, destination, k):
    if k == 0:
        return destination == source
    elif k == 1:
        return source in graph[destination]
    else:
        for node in graph[destination]:
            if is_reciprocal_link(graph, source, node, k - 1):
                return True
        return False

# Basic implementation of the Page Rank algorithm
# Returns a dict containing URLs and their ranks
def compute_ranks(graph, k):
    d = 0.8                 # damping factor
    numloops = 10           # timestep

    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages

    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    if not is_reciprocal_link(graph, node, page, k):
                        newrank += (d * (ranks[node] / len(graph[node])))
            newranks[page] = newrank
        ranks = newranks
    return ranks

# Crawls URLs starting from seed page
# Returns index, graph and list of crawled URLs
def crawl(seed, max_depth, max_pages):
    to_crawl = [seed]
    crawled = []
    index = {}              # {word1: [urls], word2: [urls]...}
    graph = {}              # {url1: [outlinks], url2: [outlinks]...}

    next_depth = []
    depth = 0
    pages_crawled = 0

    while to_crawl and depth <= max_depth and pages_crawled <= max_pages:
        # Last URL crawled first
        url = to_crawl.pop()

        if url not in crawled:
            soup = get_page(url)
            add_page_to_index(index, url, soup)

            outlinks = get_all_links(soup)
            graph[url] = outlinks

            # Add new links to list (union)
            union(next_depth, outlinks)
            crawled.append(url)
            pages_crawled += 1

        if not to_crawl:
            # Level done, increment depth
            to_crawl, next_depth = next_depth, []
            depth += 1

    return index, graph, crawled