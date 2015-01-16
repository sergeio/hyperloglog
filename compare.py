import random

from loglog import loglog
from hyperloglog import hyperloglog


def mean_absolute_percentage_error(estimates, true_value):
    """Average error of all the `estimates`."""
    errors = [abs(e - true_value) / float(true_value) for e in estimates]
    return sum(errors) / len(errors)


def compare_hyperloglog_and_loglog(num_elements=100000, num_trials=1000):
    """Compare the errors of HyperLogLog and LogLog on similar data.

    Arguments:
        `num_elements`: The true cardinality of the data set.
        `num_trials`: How many times to repeat the experiment.

    """
    hyper = [hyperloglog(create_set(num_elements)) for _ in xrange(num_trials)]
    log = [loglog(create_set(num_elements)) for _ in xrange(num_trials)]

    h_err = mean_absolute_percentage_error(hyper, num_elements)
    l_err = mean_absolute_percentage_error(log, num_elements)
    return 'h_err, l_err:', h_err, l_err


def create_set(num_unique):
    """Create a set of random values with `num_unique` unique elements."""
    numbers = [random.random() for _ in xrange(num_unique)]
    for i in xrange(len(numbers)):
        repeats = random.randint(1, 10)
        numbers.extend([numbers[i]] * repeats)
    return numbers

###############################################################################


def absolute_error(num_values):
    estimate = hyperloglog((random.random() for _ in xrange(num_values)), 10)
    return abs(num_values - estimate) / (num_values or 1)


def errors(_max=100000, step=1):
    return [absolute_error(num_values) for num_values in xrange(1, _max, step)]
