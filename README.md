HyperLogLog
===========

Imagine you have a big-ol' data set and you want to know how many distinct
elements there are in it.  This is also called the cardinality of the data set.

My first attempt would be something like this:

```python
def cardinality(data_set):
    return len(set(data_set))
```

This would work fine (and has the advantage of giving an exact answer) except
when the data set is truly "big-ol'".  If the data set doesn't even come close
to fitting in memory on our computer, the problem becomes a fair bit more
difficult.

It turns out if we relax the accuracy by a few percent, we can do some cool
things.  This is where HyperLogLog comes in.


Explain How!
------------

### The Kernel

The key idea powering HyperLogLog is that if you get a large set of randomly
distributed data, the probability of seeing a binary number that ends in x
zeroes is `2^x`.  So the probability of seeing a number that ends in a `0`
is 50%.  The probability of seeing a number that ends in `00` is 25%.  `000`
is 12.5%, and so on.

So if we scan through our data set (which at this point is just a series of
numbers) and we see a binary number that ends in `0000`, and no numbers that
end in more zeroes, we can reasonably estimate that the set has 16 unique
numbers in it, since on average 1 / 16 numbers ends in four zeroes.

### But what if our data set isn't randomly distributed integers?

**Hash functions to the rescue!**

The second key idea is that a good hash function maps any inputs to what
appears to be (and for us, is) a set of randomly distributed values.

This could also have the added benefit of shrinking your data.  If your data
set is made up of 10MB .jpgs or something like that, how all we care about are
the hashes of those .jpgs.

### Take it home

All that was pretty cool, but it only gets us to the nearest power of two and
has a high error rate.  It turns out we can do better.

If we split our data into many randomly divided subsets of that data, count
the-maximum-amount-of-trailing-zeroes-in-the-hash-of-each-value for each
subset, and average them together, we can get much closer.

This process is called "stochastic averaging", and first appears (I think) in
[Flajolet and Martin's Probabilistic Counting Algorithms for Data Base
Applications](http://www.mathcs.emory.edu/~cheung/papers/StreamDB/Probab/1985-Flajolet-Probabilistic-counting.pdf).

There are a couple more technicalities like correcting your estimate if it is
below a certain amount, or if it is very large, or if it smells a little weird.
But it's not too crazy.  The whole algorithm fits comfortably in < 20 lines of
code.

The details and derivations can be found in [HyperLogLog's
whitepaper](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf).


So What Am I Looking at Here?
-----------------------------

I initially got excited about this algorithms due to Nick Johnson's [Damn Cool
Algorithms: Cardinality
Estimation](http://blog.notdot.net/2012/09/Dam-Cool-Algorithms-Cardinality-Estimation)
post.

I copied the code from his blogpost into `loglog.py` to test it, and
implemented the full HyperLogLog algorithm in `hyperloglog.py`.  Nick's intent
was to explain the essence of the algorithm, so he didn't add all potentially
confusing bits about range correction, and stuck to LogLog over HyperLogLog,
since arithmetic means are more popular that geometric ones.

There are some helper comparison functions in `compare.py`.


Let's See It in Action!
-----------------------

### Basic Usage

```python
In [1]: from compare import *

In [2]: data = create_set(100000)

In [3]: len(data)
Out[3]: 5152822

In [4]: len(set(data))
Out[4]: 100000

In [5]: hyperloglog(data)
Out[5]: 101398.84190696556
# About 1% error

In [6]: loglog(data)
Out[6]: 97393.92237981079
# About 3% error
```

### Range Correction

We can see the benefits of the small range correction in an example that has
very few elements:

```python
In [7]: small_data = [1, 2, 3, 4, 5, 5, 5, 3]

In [8]: hyperloglog(small_data)
Out[8]: 5.012246913769684

In [9]: loglog(small_data)
Out[9]: 818.0449534051104
```

A difference of ~1% and 16000%.

### More testing!

Being a bit more rigorous, we run 1000 trials of each algorithm on similar data
and get the average absolute percent error:

```python
In [1]: from compare import compare_hyperloglog_and_loglog

In [2]: compare_hyperloglog_and_loglog(num_elements=10000, num_trials=1000)
Out[2]: ('h_err, l_err:', 0.024493629960671007, 0.030072619766436517)

In [3]: compare_hyperloglog_and_loglog(num_elements=100000, num_trials=1000)
Out[3]: ('h_err, l_err:', 0.02438100081135814, 0.032231631635683)
```

So on average, on our toy datasets, where range correction is not needed,
`hyperloglog()` is off by about 2.4%, and `loglog` is off by around 3%.


Bonus
-----

An extra bit of coolness is that this algorithm is trivial to parallelize.

I would imagine some huge (and possibly never-ending) process outputting
elements to a queue, and any number of machines or processes scooping up these
values and building their own bucket-tables (the thing that `hyperloglog()`
refers to as `buckets`), and occasionally merging them together to perform a
periodic estimate of the cardinality of the set they'd seen.


Why?
----

Originally these algorithms were developed for database applications, as you
might have guessed from the title of the first whitepaper -- *Probabilistic
Counting Algorithms for Data Base Applications*.  You could do things like
determining the number of unique queries, or percent unique queries and do all
sorts of fancy optimizations and hand-waving.
