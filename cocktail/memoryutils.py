#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

# Adapted from a script by Martin Pool, original found at
# http://mail.python.org/pipermail/python-list/1999-December/018519.html
_size_suffixes = [
    (1<<50L, 'Pb'),
    (1<<40L, 'Tb'), 
    (1<<30L, 'Gb'), 
    (1<<20L, 'Mb'), 
    (1<<10L, 'kb'),
    (1, 'bytes')
]

def format_bytes(n):
    """Return a string representing the greek/metric suffix of an amount of
    bytes.
    
    @param n: An amount of bytes.
    @type n: int

    @return: The metric representation of the given quantity of bytes.
    @rtype: str
    """
    for factor, suffix in _size_suffixes:
        if n > factor:
            break
    return str(int(n/factor)) + suffix

