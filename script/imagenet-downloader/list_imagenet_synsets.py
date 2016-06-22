#!/usr/bin/env python
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
import urllib2
import ck.kernel as ck


def get_downloaded_synsets(repo_uoa='local', module_uoa='repo', data_uoa='imagenet-*'):
    r=ck.access({
        'action':'list',
        'repo_uoa':repo_uoa,
        'module_uoa':module_uoa,
        'data_uoa':data_uoa
    })
    if r['return']>0:
        print ("CK error: %s" % r['error'])
        exit(1)
    synsets = []
    for item in r['lst']:
        synset_uoa = item['data_uoa']
        synset = synset_uoa[len('imagenet-'):]
        synsets.append(synset)
    return synsets


def list_imagenet_synsets(lower, upper, list_downloaded_only=False):
    # http://image-net.org/download-API
    url = 'http://www.image-net.org/api/text/imagenet.synset.obtain_synset_list'
    content = urllib2.urlopen(url).read()
    synsets = content.split('\n')
    downloaded_synsets = get_downloaded_synsets() if list_downloaded_only else []

    count = -1
    for synset in synsets:
        count += 1
        if count < lower:
            continue
        if count > upper:
            break
        if not synset.startswith('n'):
            continue
        if list_downloaded_only:
            if synset in downloaded_synsets:
                print synset
        else:
            print synset


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--lower', '-l', type=int, default=0,
                   help='Lower bound on ImageNet synset index')
    p.add_argument('--upper', '-u', type=int, default=100000,
                   help='Upper bound on ImageNet synset index')
    p.add_argument('--downloaded', '-d', action='store_true',
                   help='List downloaded ImageNet synsets only')
    args = p.parse_args()

    list_imagenet_synsets(args.lower, args.upper, args.downloaded)
