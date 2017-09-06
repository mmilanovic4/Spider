from bs4 import BeautifulSoup
import requests
import sys
import threading
import urllib

def get_page_source(url):
	r = requests.get(url)

	if r.status_code != 200:
		return False
	# end

	if len(r.headers['content-type'].split('text/html')) < 2:
		return False
	# end

	return r.text
# end

class Spider:

	def __init__(self, homepage):
		self.links = set()
		self.crawled = set()

		self.homepage = homepage
		self.links.add(homepage)

		self.lock = threading.Lock()
		self.crawl()
	# end

	def start_workers(self):
		t1 = threading.Thread(target=self.job, name='S1')
		t2 = threading.Thread(target=self.job, name='S2')
		t3 = threading.Thread(target=self.job, name='S3')
		t4 = threading.Thread(target=self.job, name='S4')

		t1.start()
		t2.start()
		t3.start()
		t4.start()

		t1.join()
		t2.join()
		t3.join()
		t4.join()
	# end

	def job(self):
		while True:
			if not self.crawl():
				break
			# end
		# end
		print('%s мртав!' % threading.current_thread().name)
	# end

	def crawl(self):
		with self.lock:
			if len(self.links) == 0:
				return False
			else:
				link = self.links.pop()
				self.crawled.add(link)
			# end
		# end

		print('%s: %s' % (threading.current_thread().name, link))
		html = get_page_source(link)

		if not html:
			pass
		else:
			self.gather_links(html)
		# end

		return True
	# end

	def gather_links(self, html):
		bs = BeautifulSoup(html, 'lxml')
		for link in bs.findAll('a'):

			if 'href' not in link.attrs:
				continue
			# end

			link = urllib.parse.urljoin(self.homepage, link.attrs['href'])
			if len(link.split(self.homepage)) < 2:
				continue
			# end

			if link in self.crawled:
				continue
			# end

			self.links.add(link)
		# end
	# end

# end

if len(sys.argv) != 2:
	print('Правилна употреба: python3 spider.py [URL]')
	sys.exit()
# end

url = sys.argv[1]
parsed = urllib.parse.urlparse(url)

if parsed.netloc == '':
	print('Задати URL није валидан!')
	sys.exit()
# end

output = parsed.netloc.replace('.', '_') + '.txt'
print('Излазни фајл:', output)

if parsed.scheme not in ['http', 'https']:
	parsed.scheme = 'http'
# end

homepage = parsed.scheme + '://' + parsed.netloc
spider = Spider(homepage)

try:
	spider.start_workers()
except:
	pass
finally:
	links = sorted(spider.crawled)

	with open(output, 'w') as fw:
		for link in links:
			fw.write(link + '\n')
		# end
	# end

	print('Крај!')
# end

