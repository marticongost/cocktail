#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""

def split_view_name(name):
    
    pos = name.rfind(".")

    if pos == -1:
        raise ValueError("Unqualified template name: " + name)

    pkg_name = name[:pos]
    item_name = name[pos + 1:]
    
    if not pkg_name or not item_name:
        raise ValueError("Wrong template name: %s" % name)
    
    return pkg_name, item_name

def get_view_full_name(name):
    pos = name.rfind(".")
    pos2 = name.rfind(".", 0, pos)
    return name[:pos2] + name[pos:]

