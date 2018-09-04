/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2017
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.arrays");

cocktail.arrays.equal = function (a, b) {
    if (a.length != b.length) {
        return false;
    }
    for (var i = 0; i < a.length; i++) {
        if (a[i] !== b[i]) {
            return false;
        }
    }
    return true;
}

cocktail.arrays.commonPrefix = function (a, b) {

    let i = 0;
    let prefix = [];

    while (i < a.length && i < b.length && a[i] === b[i]) {
        i++;
    }

    return a.slice(0, i);
}

cocktail.arrays.normalize = function (collection) {
    return collection instanceof Array ? collection : Array.from(collection);
}

cocktail.declare("cocktail.sets");

cocktail.sets.normalize = function (collection) {
    return collection instanceof Set ? collection : new Set(collection);
}

cocktail.sets.equal = function (a, b) {

    a = cocktail.sets.normalize(a);
    b = cocktail.sets.normalize(b);

    if (a.size != b.size) {
        return false;
    }

    for (let item of a) {
        if (!b.has(item)) {
            return false;
        }
    }

    return true;
}

cocktail.sets.isSubset = function (a, b) {

    a = cocktail.sets.normalize(a);
    b = cocktail.sets.normalize(b);

    for (let item of a) {
        if (!b.has(item)) {
            return false;
        }
    }

    return true;
}

cocktail.sets.isSuperset = function (a, b) {

    a = cocktail.sets.normalize(a);
    b = cocktail.sets.normalize(b);

    for (let item of b) {
        if (!a.has(item)) {
            return false;
        }
    }

    return true;
}

cocktail.sets.addedRemoved = function (oldSet, newSet) {
    oldSet = cocktail.sets.normalize(oldSet);
    newSet = cocktail.sets.normalize(newSet);
    return [
        cocktail.sets.difference(newSet, oldSet),
        cocktail.sets.difference(oldSet, newSet)
    ];
}

cocktail.sets.update = function (set, items) {
    for (let item of items) {
        set.add(item);
    }
}

cocktail.sets.intersectionUpdate = function (set, items) {
    items = cocktail.sets.normalize(items);
    for (let item of set) {
        if (!items.has(item)) {
            set.delete(item);
        }
    }
}

cocktail.sets.differenceUpdate = function (set, items) {
    for (let item of items) {
        set.delete(item);
    }
}

cocktail.sets.union = function (a, b) {
    let union = new Set(a);
    for (let item of b) {
        union.add(item);
    }
    return union;
}

cocktail.sets.intersection = function (a, b) {
    let intersection = new Set();
    for (let item of a) {
        if (b.has(item)) {
            intersection.add(item);
        }
    }
    return intersection;
}

cocktail.sets.difference = function (a, b) {
    a = cocktail.arrays.normalize(a);
    b = cocktail.sets.normalize(b);
    return new Set(a.filter((item) => !b.has(item)));
}

