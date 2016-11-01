The Jupyter Notebook `explore_batch_size_by_tags.ipynb` generates temporary
files required to benchmark (`gpu_time`) the cross product of all Caffe
installations with all Caffe models.

It can be converted to a normal Python script and executed via:
```
$ _explore_batch_size_by_tags_convert.sh
$ ipython explore_batch_size_by_tags-benchmark.py
```

To remove all the temporary files, run:
```
$ _explore_batch_size_by_tags_clean.sh
```

To remove all the temporary files and experimental data with the `gpu_time`
tag, run:
```
$ _explore_batch_size_by_tags_clobber.sh
```
