# Scripts for downloading ImageNet images

## Files and copyright

- `download_imagenet_synset.py`

   - (c) 2014, [Seiya Toku](http://beam2d.net), https://github.com/beam2d/imagenet_downloader
   - (c) 2014, [Emmanuel Benazera](http://juban.free.fr), https://github.com/beniz/imagenet_downloader
   - (c) 2016, [Anton Lokhmotov](http://dividiti.com)

- `list_imagenet_synsets.py`
   - (c) 2016, [Anton Lokhmotov](http://dividiti.com)

## List ImageNet categories

To list all ImageNet synsets (categories):

```
$ python list_imagenet_synsets.py   \
    [--lower LOWER] [--upper UPPER] \
    [--downloaded-only]
```

## Download ImageNet URLs

### Download all URLs (not recommended)

To download a single file with all ImageNet IDs and URLs:
```
$ wget http://image-net.org/imagenet_data/urls/imagenet_fall11_urls.tgz
$ du imagenet_fall11_urls.tgz
335M    imagenet_fall11_urls.tgz
$ tar xvzf imagenet_fall11_urls.tgz
1.1G    fall11_urls.txt
```

Filter out URLs for a particular category:
```
$ grep n01440764 fall11_urls > n01440764_urls.txt
```

The resulting file contains pairs (ID, URL), as expected by the original
`download_imagenet_synset.py` script.

### Download URLs for a particular category

To download a file with ImageNet URLs for a particular category:

```
$ wget -O n01440764_urls.txt
    http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n01440764
$ python download_imagenet_synset.py \
    n01440764_urls.txt
    dataset-imagenet-n01440764
    --jobs 10 --retry 3 --sleep 0
```

The resulting file contains URLs only. The `download_imagenet_synsets.py`
script has been modified to handle this case as well.

## Download images for a given category

```
$ python download_imagenet_synset.py \
    n01440764_urls.txt
    dataset-imagenet-n01440764
    --jobs 10 --retry 3 --sleep 0
```

## CK support

When downloading a new synset, a new local repository is created via a CK
command sequence roughly equivalent to the following shell command sequence:

```
$ ck add repo:imagenet-n01440764 --quiet
```

Then, individual images can be:

- registered:

```
$ ck add imagenet-n01440764:dataset:9981 \
    --tags=imagenet,n01440764,9981,http://dividiti.com
$ ck find imagenet-n01440764:dataset:9981
/home/anton/CK/imagenet-n01440764/dataset/9981
```

- searched through by a combination of tags:
```
$ ck search dataset:* --tags=imagenet,n01440764
imagenet-n01440764:dataset:9981
$ ck search dataset:* --tags=imagenet,http://dividiti.com
imagenet-n01440764:dataset:9981
```

- inspected (printing the contents of `meta.json` and `desc.json`):
```
$ ck load imagenet-n01440764:dataset:9981 --min
{
  "dict": {
    "tags": [
      "imagenet",
      "n01440764",
      "9981",
      "http://dividiti.com"
    ]
  },
  "desc": {}
}
```

- updated:
```
$ cp n01440764_9981.jpg `ck find imagenet-n01440764:dataset:9981`
$ ck update imagenet-n01440764:dataset:9981 @@dict
{
  "dataset_files": [
    "n01440764_9981.jpg"
  ]
}

Entry 9981 (c52d8c8b1f54b879, /home/anton/CK/imagenet-n01440764/dataset/9981) updated successfully!
$ ck load imagenet-n01440764:dataset:9981 --min
{
  "dict": {
    "dataset_files": [
      "n01440764_9981.jpg"
    ],
    "tags": [
      "imagenet",
      "n01440764",
      "9981",
      "http://dividiti.com"
    ]
  },
  "desc": {}
}
```

- cleaned:
```
$ ck rm imagenet-unknown:dataset:* --force &&
  ck rm repo:imagenet-unknown --force &&
  rm -rf ~/CK/imagenet-unknown/
```

- and more...
