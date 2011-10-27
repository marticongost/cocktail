#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import OrderedDict
from cocktail.schema import Reference, RelationMember
from cocktail.persistence.persistentobject import PersistentClass

def delete_dry_run(item, visited = None):
    """Determines what would happend if the object was deleted: which
    objects would be cascade deleted, or which other objects would block
    the whole delete operation.
    """
    # Cycle prevention
    if visited is None:
        visited = set()
    elif item in visited:
        return
    else:
        visited.add(item)

    node = {"item": item, "cascade": OrderedDict(), "blocking": OrderedDict()}

    for member in item.__class__.ordered_members():
        if (
            isinstance(member, RelationMember)
            and member.related_type
            and isinstance(member.related_type, PersistentClass)
        ):
            # Blocking
            if member.block_delete:
                value = item.get(member)
                if value:
                    if isinstance(member, Reference):
                        value = (value,)
                    node["blocking"][member] = value

            # Cascade delete
            elif item._should_cascade_delete(member):
                value = item.get(member)
                
                if value:
                    if isinstance(member, Reference):
                        value = (value,)                    
                    
                    cascade_nodes = []
                    
                    for descendant in value:
                        cascade_node = delete_dry_run(descendant, visited)
                        if cascade_node is not None:
                            cascade_nodes.append(cascade_node)

                    if cascade_nodes:
                        node["cascade"][member] = cascade_nodes

    return node

