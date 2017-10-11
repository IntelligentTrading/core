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
