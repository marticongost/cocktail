#-*- coding: utf-8 -*-
u"""Utilities for formatting and parsing memory amounts.

Parts of this module were adapted from a script by Martin Pool:
http://mail.python.org/pipermail/python-list/1999-December/018519.html

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from decimal import Decimal
import re

_memory_expr = re.compile(
    r"^(?P<amount>\d+(\.\d+)?) ?(?P<suffix>[EPTGMK](iB|B)?)?$"
)

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

_sizes_by_suffix = {}

for base, sizes in _suffixes_by_base.iteritems():
    for size, suffix in sizes:
        _sizes_by_suffix[suffix] = size

for size, suffix in _suffixes_by_base[2]:
    _sizes_by_suffix[suffix[0]] = size

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

def parse_bytes(string):
    """Return the number of bytes indicated by the given string."""
    match = _memory_expr.match(string)

    if not match:
        raise ValueError("Can't parse %s: not a valid memory amount" % string)

    amount = Decimal(match.group("amount"))
    suffix = match.group("suffix")

    if suffix:
        amount *= _sizes_by_suffix[suffix]

    return amount

