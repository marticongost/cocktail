/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2018
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.dom");

cocktail.dom.iterElementsBackwards = function* (node, jail = null) {
    while (node && node != jail) {
        let prev = node.previousElementSibling;
        while (prev) {
            yield* cocktail.dom.iterDescendantsBackwards(prev);
            yield prev;
            prev = prev.previousElementSibling;
        }
        while ((node = node.parentNode) && node != jail) {
            yield node;
            if (node.previousElementSibling) {
                break;
            }
        }
    }
}

cocktail.dom.iterElementsForward = function* (node, jail = null) {
    while (node && node != jail) {
        yield* cocktail.dom.iterDescendantsForward(node);

        let next = node.nextElementSibling;
        while (next) {
            yield next;
            yield* cocktail.dom.iterDescendantsForward(next);
            next = next.nextElementSibling;
        }

        while ((node = node.parentNode) && node != jail) {
            if (node.nextElementSibling) {
                node = node.nextElementSibling;
                yield node;
                break;
            }
        }
    }
}

cocktail.dom.iterDescendantsBackwards = function* (root) {
    for (let i = root.children.length - 1; i >= 0; i--) {
        const child = root.children[i];
        yield* cocktail.dom.iterDescendantsBackwards(child);
        yield child;
    }
}

cocktail.dom.iterDescendantsForward = function* (root) {
    for (let child of root.children) {
        yield child;
        yield* cocktail.dom.iterDescendantsForward(child);
    }
}

