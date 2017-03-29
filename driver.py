import crawler

# Initializing seed and maximum depth to crawl
seed = "http://www.udacity.com/cs101x/index.html"
default_depth = 5
default_pages = 50
# Pages linking to themselves (k = 0)
default_collusion_level = 0

index, graph, pages = crawler.crawl(seed, default_depth, default_pages)
ranks = crawler.compute_ranks(graph, default_collusion_level)

print "Pages (URLs visited)"
for p in pages:
    print p

print "\nType"
print "'index' to view entire index"
print "'words' to view all words in index"
print "'ranks' to view page ranks"
print "'query' to search for keyword"
print "'exit' to quit program\n"

while True:
    print ' '
    op = raw_input('-->')
    if op == 'index':
        print index
    elif op == 'words':
        for word in index:
            print word
    elif op == 'ranks':
        # Sort list of tuples based on ranks
        res = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
        for i in res:
            print i
    elif op == 'query':
        print "\nEnter keyword"
        keyword = raw_input('-->')
        print crawler.lookup_all(index, ranks, keyword)
    elif op == 'exit':
        break