#!/usr/bin/python3
#
# Spider v1.0

import requests
import sys
import threading
import time
import urllib
from bs4 import BeautifulSoup


def timer(func):
	if not callable(func):
		return False
	# end

	def wrapper(*args, **kwargs):
		t0 = time.time()
		func(*args, **kwargs)

		tt = time.time() - t0
		print('Total running time: %.2f seconds.\n' % tt)
	# end

	return wrapper
# end


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


def sorted_set_to_file(data, output_file):
	data = sorted(data)

	with open(output_file, 'w') as fw:
		for row in data:
			fw.write(row + '\n')
		# end
	# end
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

	def start_workers(self, total=8):
		threads = []

		for x in range(1, 1 + total):
			t = threading.Thread(target=self.job, name='S' + str(x))
			t.daemon = True
			t.start()
			threads.append(t)
		# end

		for t in threads:
			t.join()
		# end
	# end

	def job(self):
		while True:
			if not self.crawl():
				break
			# end
		# end
		print('%s is dead!' % threading.current_thread().name)
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

		if html is not False:
			self.gather_links(html)
		# end

		return True
	# end

	def gather_links(self, html):
		bs = BeautifulSoup(html, 'lxml')
		for link in bs.find_all('a'):

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


def usage():
	print('Usage: python3 spider.py [URL]\n')
# end


@timer
def main():
	print('Spider v1.0\n')

	if len(sys.argv) != 2:
		usage()
		sys.exit(2)
	# end

	url = sys.argv[1]
	parsed = urllib.parse.urlparse(url)

	if not hasattr(parsed, 'scheme') or parsed.scheme not in ['http', 'https']:
		print('Invalid URL: scheme missing\n')
		sys.exit(2)
	# end

	if parsed.netloc == '':
		print('Invalid URL: netloc missing\n')
		sys.exit(2)
	# end

	homepage = parsed.scheme + '://' + parsed.netloc
	print('Target: %s' % homepage)

	output_file = parsed.netloc.replace('.', '_') + '.txt'
	print('Results will be saved to: %s \n' % output_file)

	try:
		spider = Spider(homepage)
		spider.start_workers()
	except KeyboardInterrupt:
		print('')
	finally:
		if 'spider' in locals() and hasattr(spider, 'crawled'):
			sorted_set_to_file(spider.crawled, output_file)
		# end
		print('END!')
	# end
# end

if __name__ == '__main__':
	main()
# end

