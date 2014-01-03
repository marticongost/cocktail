#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

# Adapted from a script by Martin Pool, original found at
# http://mail.python.org/pipermail/python-list/1999-December/018519.html
_suffixes_by_base = {
    2: [
        (1<<60L, 'EiB'),
        (1<<50L, 'PiB'),
        (1<<40L, 'TiB'),
        (1<<30L, 'GiB'),
        (1<<20L, 'MiB'),
        (1<<10L, 'KiB'),
        (1, 'bytes')
    ],
    10: [
        (10 ** 18, 'EB'),
        (10 ** 15, 'PB'),
        (10 ** 12, 'TB'),
        (10 ** 9, 'GB'),
        (10 ** 6, 'MB'),
        (10 ** 3, 'KB'),
        (1, 'bytes')
    ]
}

def format_bytes(n, base = 10):
    """Return a string representing the greek/metric suffix of an amount of
    bytes.
    
    @param n: An amount of bytes.
    @type n: int

    @return: The metric representation of the given quantity of bytes.
    @rtype: str
    """
    try:
        suffixes = _suffixes_by_base[base]
    except KeyError:
        raise ValueError(
            "Can't format bytes with base %s; must be either 2 or 10"
            % base
        )

    for factor, suffix in suffixes:
        if n > factor:
            break

    return str(int(n/factor)) + suffix

