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

$ python download_imagenet_synset.py \
    n01440764_urls.txt
    dataset-imagenet-n01440764
    --jobs 10 --retry 3 --sleep 0
```
