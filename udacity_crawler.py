# Original code for the Web Crawler project done
# as part as Udacity's CS101X Intro to CS course

def get_page(url):
    try:
        import urllib
        return urllib.urlopen(url).read()
    except:
        return ""

def add_page_to_index(index, url, content):
    words = content.split()
    for word in words:
        add_to_index(index, word, url)

def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

def union(p, q):
    for i in q:
        if i not in p:
            p.append(i)

def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10

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
                    newrank += (d * (ranks[node] / len(graph[node])))
            newranks[page] = newrank
        ranks = newranks
    return ranks

index, graph, pages = crawl('http://www.udacity.com/cs101x/index.html')
ranks = compute_ranks(graph)
print index

def crawl(seed):
    tocrawl = [seed]
    crawled = []
    graph = {}
    index = {}
    while tocrawl:
        url = tocrawl.pop()
        if url not in crawled:
            html = get_page(url)
            add_page_to_index(index, url, html)
            outlinks = get_all_links(html)
            graph[url] = outlinks
            union(tocrawl, outlinks)
            crawled.append(url)
    return index, graph, crawled