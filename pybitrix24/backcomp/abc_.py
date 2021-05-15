try:
    from abc import ABC
except ImportError:
    ABC = type("ABC")  # a stub for old Python versions
