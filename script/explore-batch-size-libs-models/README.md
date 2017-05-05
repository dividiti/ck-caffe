## Benchmark all Caffe libs and models

To benchmark the Cartesian product of all the Caffe libs and models on the host
platform, run:

```
$ python explore-batch-size-libs-models-benchmarking.py
```

## Convert Jupyter Notebook to Python

The Jupyter Notebook `explore-batch-size-libs-models-analysis.ipynb` can be
converted to a normal Python script and executed via: 

```
$ _explore-batch-size-libs-models-convert.sh
$ ipython explore-batch-libs-models-analysis.py
```

## Clean all experimental data 

To clean all the experimental data with the `explore-batch-size-libs-models`
tag, run:

```
$ _explore-batch-size-libs-models-clobber.sh
```
