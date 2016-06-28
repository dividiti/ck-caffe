#e!/usr/bin/env python
# Copyright (c) 2014 Seiya Tokui
# Copyright (c) 2014 Emmanuel Benazera
# Copyright (c) 2016 Anton Lokhmotov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import imghdr
import Queue
import os
import socket
import sys
import tempfile
import threading
import time
import urllib2
import glob
import ck.kernel as ck

def download(url, timeout, retry, sleep, verbose=False):
    """Downloads a file at given URL."""
    count = 0
    while True:
        try:
            f = urllib2.urlopen(url, timeout=timeout)
            if f is None:
                raise Exception('Cannot open URL {0}'.format(url))
            content = f.read()
            f.close()
            break
        except urllib2.HTTPError as e:
            if 500 <= e.code < 600:
                if verbose:
                    sys.stderr.write('Error: HTTP with code {0}\n'.format(e.code))
                count += 1
                if count > retry:
                    if verbose:
                        sys.stderr.write('Error: too many retries on {0}\n'.format(url))
                    raise
            else:
                if verbose:
                    sys.stderr.write('Error: HTTP with code {0}\n'.format(e.code))
                raise
        except urllib2.URLError as e:
            if isinstance(e.reason, socket.gaierror):
                count += 1
                time.sleep(sleep)
                if count > retry:
                    if verbose:
                        sys.stderr.write('Error: too many retries on {0}\n'.format(url))
                    raise
            else:
                if verbose:
                    sys.stderr.write('Error: URLError {0}\n'.format(e))
                raise
        #except Exception as e:
        #    if verbose:
        #        sys.stderr.write('Error: unknown during download: {0}\n'.format(e))
    return content

def imgtype2ext(typ):
    """Converts an image type given by imghdr.what() to a file extension."""
    if typ == 'jpeg':
        return 'jpg'
    if typ is None:
        raise Exception('Cannot detect image type')
    return typ

def make_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def download_list(list_file,
                  timeout=10,
                  retry=10,
                  num_jobs=1,
                  sleep_after_dl=1,
                  verbose=False,
                  offset=0,
                  msg=1):
    """Try to download all images whose URLs are listed in 'list_file'
    and register them with Collective Knowledge.

    The file is expected to have lines in either of the forms:

    a) <category>_<index> <url>

    Example:
    n04515003_4421  http://www.danheller.com/images/Europe/CzechRepublic/Prague/Misc/upright-bass-n-piano.jpg

    That is, the WordNet ID of a category ("category" for short)
    concatenated with a unique index, followed by a URL.

    The downloaded image will be added to a local CK repository called
    "imagenet-<category>" as a dataset entry called "<index>",
    tagged with "imagenet", <category>, <index>, <url>.

    b) <url>
    http://www.danheller.com/images/Europe/CzechRepublic/Prague/Misc/upright-bass-n-piano.jpg

    The downloaded image with be added to a local CK repository called
    "imagenet-unknown" as a dataset with a unique random index,
    tagged with "imagenet" and <url>.
    """

    #make_directory(out_dir)

    count_total = 0
    with open(list_file) as list_in:
        for i, l in enumerate(list_in):
            pass
        count_total = i + 1
    count_total -= offset

    sys.stderr.write('Total: {0}\n'.format(count_total))

    num_jobs = max(num_jobs, 1)

    entries = Queue.Queue(num_jobs)
    done = [False]

    counts_fail = [0 for i in xrange(num_jobs)]
    counts_success = [0 for i in xrange(num_jobs)]

    def producer():
        count = 0
        with open(list_file) as list_in:
            for line in list_in:
                if count >= offset:
                    sep = None; max_split = 1
                    prefix_url = line.strip().split(sep, max_split)
                    if len(prefix_url) == 2: # prefix and URL
                        prefix = prefix_url[0]
                        url = prefix_url[1]
                        category_index = prefix.split('_', max_split)
                        if len(category_index) == 2: # category and index
                            category = category_index[0]
                            index = category_index[1]
                        elif len(category_index) == 1: # category only
                            category = category_index[0]
                            index = count
                        else:
                            if verbose:
                                sys.stderr.write('Error: Invalid line: {0}\n'.format(line))
                    elif len(prefix_url) == 1: # URL only
                        url = prefix_url[0]
                        category = "unknown"
                        index = count
                    else:
                        if verbose:
                            sys.stderr.write('Error: Invalid line: {0}\n'.format(line))
                    entries.put((category, index, url), block=True)
                count += 1

        entries.join()
        done[0] = True

    def consumer(i):
        while not done[0]:
            try:
                category, index, url = entries.get(timeout=1)
            except:
                continue

            try:
                # Try adding a CK repository for this category.
                repo_uoa = 'local'; module_uoa = 'repo'; data_uoa = 'imagenet-%s' % category
                r=ck.access({
                    'action':'add',
                    'repo_uoa':repo_uoa,
                    'module_uoa':module_uoa,
                    'data_uoa':data_uoa
                })
                if r['return']>0:
                    # If already exists, give a warning rather than an error.
                    if r['return']==16:
                        if verbose:
                            sys.stdout.write ("CK info: repository for category \'%s\' already exists.\n" % category)
                    else:
                        if verbose:
                            sys.stderr.write ("CK error: %s\n" % r['error'])
                        counts_fail[i] += 1
                        continue

                # Get the CK repository for this category.
                # FIXME: "ck add --help" says that it returns
                # "Output from the 'create_entry' function".
                # It may be possible to extract the repo uoa for this category
                # from it but it's unclear what it contains...
                r=ck.access({
                    'action':'search',
                    'repo_uoa':repo_uoa,
                    'module_uoa':module_uoa,
                    'data_uoa':data_uoa
                })
                if r['return']>0:
                    if verbose:
                        sys.stderr.write ("CK error: %s\n" % r['error'])
                    counts_fail[i] += 1
                    continue
                if len(r['lst'])!=1:
                    if verbose:
                        sys.stderr.write ("CK error: %d repositories found, expected 1\n" % len(r['lst']))
                    counts_fail[i] += 1
                    continue
                
                # Search for an image by the given category URL.
                # (Ignore the index as it may not be unique.)
                repo_uoa=r['lst'][0]['data_uoa']
                module_uoa='dataset'
                tags='imagenet,%s,%s' % (category,url)
                r=ck.access({
                    'action':'search',
                    'repo_uoa':repo_uoa,
                    'module_uoa':module_uoa,
                    'tags':tags
                })
                if r['return']>0:
                    if verbose:
                        sys.stderr.write ("CK error: %s\n" % r['error'])
                    counts_fail[i] += 1
                    continue
                if len(r['lst'])>0:
                    # If already exists, give a warning rather than an error.
                    if verbose:
                        sys.stdout.write ("CK info: image at \'%s\' already downloaded\n" % url)
                    counts_success[i] += 1
                    entries.task_done()
                    continue
                
                # Add the given image to the repository for this category. 
                data_uoa=str(index).zfill(9)
                r=ck.access({
                    'action':'add',
                    'repo_uoa':repo_uoa,
                    'module_uoa':module_uoa,
                    'data_uoa':data_uoa,
                    'tags':tags
                })
                if r['return']>0:
                    if verbose:
                        sys.stderr.write ("CK error: %s\n" % r['error'])
                    counts_fail[i] += 1
                    continue
                # FIXME: "ck add --help" says that it returns
                # "Output from the 'create_entry' function".
                # It may be possible to extract the repo uoa for this category
                # from it but it's unclear what it contains...
                r=ck.access({
                    'action':'search',
                    'repo_uoa':repo_uoa,
                    'module_uoa':module_uoa,
                    'data_uoa':data_uoa
                })
                if r['return']>0:
                    if verbose:
                        sys.stderr.write ("CK error: %s\n" % r['error'])
                    counts_fail[i] += 1
                    continue
                if len(r['lst'])!=1:
                    if verbose:
                        sys.stderr.write ("CK error: %d dataset entries found, expected 1\n" % len(r['lst']))
                    counts_fail[i] += 1
                    continue

                # Download the image into the image dataset directory.
                directory = r['lst'][0]['path']
                content = download(url, timeout, retry, sleep_after_dl)
                ext = imgtype2ext(imghdr.what('', content))
                name = '{0}.{1}'.format(category, ext)
                path = os.path.join(directory, name)
                with open(path, 'w') as f:
                    f.write(content)

                # Download the image category description.
                words_url = "http://www.image-net.org/api/text/wordnet.synset.getwords?wnid=%s" % category
                content = download(words_url, timeout, retry, sleep_after_dl)
                all_words = content.split("\n")

                # Update the image metadata.
                info={}
                info['dataset_files'] = [ name ]
                info['dataset_words'] = [ word for word in all_words if word != ""]
                r=ck.access({
                    'action':'update',
                    'repo_uoa':repo_uoa,
                    'module_uoa':module_uoa,
                    'data_uoa':data_uoa,
                    'dict':info
                })
                if r['return']>0:
                    if verbose:
                        sys.stderr.write ("CK error: %s\n" % r['error'])
                    counts_fail[i] += 1
                    continue

                counts_success[i] += 1
                time.sleep(sleep_after_dl)

            except Exception as e:
                counts_fail[i] += 1
                if verbose:
                    sys.stderr.write('Error: {0} / {1}: {2}\n'.format(category, url, e))

            entries.task_done()

    def message_loop():
        if verbose:
            delim = '\n'
        else:
            delim = '\r'

        while not done[0]:
            count_success = sum(counts_success)
            count = count_success + sum(counts_fail)
            rate_done = count * 100.0 / count_total
            if count == 0:
                rate_success = 0
            else:
                rate_success = count_success * 100.0 / count
            sys.stderr.write(
                '{0} / {1} ({2: 2.2f}%) done, {3} / {0} ({4: 2.2f}%) succeeded                    {5}'.format(
                    count, count_total, rate_done, count_success, rate_success, delim))

            time.sleep(msg)

    producer_thread = threading.Thread(target=producer)
    consumer_threads = [threading.Thread(target=consumer, args=(i,)) for i in xrange(num_jobs)]
    message_thread = threading.Thread(target=message_loop)

    producer_thread.start()
    for t in consumer_threads:
        t.start()
    message_thread.start()

    # Explicitly wait to accept SIGINT
    try:
        while producer_thread.isAlive():
            time.sleep(1)
    except:
        sys.exit(1)

    producer_thread.join()
    for t in consumer_threads:
        t.join()
    message_thread.join()

    sys.stderr.write('\ndone\n')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('list', help='ImageNet list file')
    p.add_argument('--jobs', '-j', type=int, default=1,
                   help='Number of parallel threads to download')
    p.add_argument('--timeout', '-t', type=int, default=10,
                   help='Timeout per image in seconds')
    p.add_argument('--retry', '-r', type=int, default=10,
                   help='Max count of retry for each image')
    p.add_argument('--sleep', '-s', type=float, default=1,
                   help='Sleep after download each image in second')
    p.add_argument('--verbose', '-v', action='store_true',
                   help='Enable verbose messages')
    p.add_argument('--offset', '-o', type=int, default=0,
                   help='Which line to start from in ImageNet list file')
    p.add_argument('--msg', '-m', type=int, default=1,
                   help='Logging message every x seconds')
    args = p.parse_args()

    download_list(args.list,
                  timeout=args.timeout, retry=args.retry,
                  num_jobs=args.jobs, verbose=args.verbose,
                  offset=args.offset, msg=args.msg)
