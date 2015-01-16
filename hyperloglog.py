from math import log

import hashlib


def hash(x):
    x = str(x)
    h = hashlib.sha1(x)
    hex_ = h.hexdigest()
    return int(hex_, base=16)

def rightmost_binary_1_position(num):
  """The (number of trailing zeroes in the binary representation of num) + 1"""
  i = 0
  while (num >> i) & 1 == 0:
      i += 1
  return i + 1

def hyperloglog(numbers, bits_for_bucket_index=10):
    """Estimate the number of unique elements in `numbers`.

    Average error is < 3%.

    4 <= bits_for_bucket_index <= 16

    Poor variable-naming is due to my trying to stay as close to the
    notation used by the whitepaper as reasonable. : )

    http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
    http://www.mathcs.emory.edu/~cheung/papers/StreamDB/Probab/1985-Flajolet-Probabilistic-counting.pdf

    """
    bucket_count = 2 ** bits_for_bucket_index
    buckets = [0] * bucket_count

    # Set up the data for "stochastic averaging"
    for v in numbers:
        hash_integer = hash(v)
        i = hash_integer & (bucket_count - 1)
        w = hash_integer >> bits_for_bucket_index
        buckets[i] = max(buckets[i], rightmost_binary_1_position(w))

    a_m = .7213 / (1 + 1.079 / bucket_count)
    # Do the stochastic averaging.
    E = a_m * bucket_count ** 2 * sum(2 ** (-Mj) for Mj in buckets) ** (-1)
    # Small-range correction
    if E < (5 / 2.0 * bucket_count):
        V = len([b for b in buckets if b == 0])
        if V:
            E = bucket_count * log(bucket_count / float(V))
    # Large-range correction
    elif E > (1 / 30.0) * 2 ** 32:
        E = -(2 ** 32) * log(1 - (E / 2 ** 32))
    return E
