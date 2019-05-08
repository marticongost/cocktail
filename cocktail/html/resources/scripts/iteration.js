/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2018
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.iteration");

cocktail.iteration.first = function (iterable, predicate, notFound = undefined) {
    for (let item of iterable) {
        if (predicate(item)) {
            return item;
        }
    }
    return notFound;
}

