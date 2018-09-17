#!/usr/bin/python3
#
# Multi-threaded website crawler written in Python.

import argparse
import lxml.html as lh
import requests
import sys
import threading
import time
import urllib.parse as up


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
	headers = {
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'
	}

	try:
		r = requests.get(url, headers=headers)

		if r.status_code != 200:
			return False
		# end

		if len(r.headers['content-type'].split('text/html')) < 2:
			return False
		# end

		return r.text
	except:
		return False
	# end
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

	def start_workers(self, total=16):
		threads = []

		for x in range(1, 1 + total):
			t = threading.Thread(target=self.job, name='S' + str(x).zfill(2))
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

		try:
			self.gather_links(html)
		except:
			pass
		# end

		return True
	# end

	def gather_links(self, html):
		doc = lh.fromstring(html)
		for link in doc.xpath('//a'):

			if 'href' not in link.attrib:
				continue
			# end

			link = up.urljoin(self.homepage, link.attrib['href'])
			if len(link.split(self.homepage)) < 2:
				continue
			# end

			with self.lock:
				if link in self.crawled:
					continue
				# end
				self.links.add(link)
			# end
		# end
	# end

# end


@timer
def main():
	parser = argparse.ArgumentParser(
		description='Multi-threaded website crawler written in Python.'
	)
	parser.add_argument(
		'-u',
		'--url',
		action='store',
		dest='url',
		help='Target website',
		required=True
	)

	args = parser.parse_args()
	parsed_url = up.urlparse(args.url)

	if not hasattr(parsed_url, 'scheme') or parsed_url.scheme not in ['http', 'https']:
		print('Invalid URL: scheme missing\n')
		sys.exit(2)
	# end

	if parsed_url.netloc == '':
		print('Invalid URL: netloc missing\n')
		sys.exit(2)
	# end

	homepage = parsed_url.scheme + '://' + parsed_url.netloc
	print('Target: %s' % homepage)

	output_file = parsed_url.netloc.replace('.', '_') + '.txt'
	print('Results will be saved to: %s \n' % output_file)

	try:
		spider = Spider(homepage)

		# Collect some queue links so threads won't die immediately
		for _ in range(10):
			spider.crawl()
		# end

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
