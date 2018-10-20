# A DECORATOR FOR PYTHON THREADING
# http://docs.python.org/2/library/threading.html#thread-objects
# http://stackoverflow.com/questions/18420699/multithreading-for-python-django
from threading import Thread

def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator


def multithread_this_shit(function_def, list_of_params):
    """
    :param function_def: the function to pass params to
    :param list_of_params: list of function params, for multiple-param functions, pass tuples
    :return:
    """

    from multiprocessing.dummy import Pool as ThreadPool

    # make the Pool of workers
    pool = ThreadPool(16)

    # open the urls in their own threads
    # and return the results
    results = pool.map(function_def, list_of_params)

    # close the pool and wait for the work to finish
    pool.close()
    pool.join()

    return results
