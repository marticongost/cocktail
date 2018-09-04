/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2017
-----------------------------------------------------------------------------*/

cocktail.ui.COPY_VALUE = Symbol("cocktail.ui.COPY_VALUE");

cocktail.ui.copyValue = function (value) {

    if (
        value === null
        || value === undefined
        || value === true
        || value === false
    ) {
        return value;
    }

    if (typeof(value) == "object") {

        let copyMethod = value[cocktail.ui.COPY_VALUE];

        if (copyMethod) {
            return copyMethod.call(value);
        }
        else {
            return Object.assign({}, value);
        }
    }

    return value;
}

Date.prototype[cocktail.ui.COPY_VALUE] = function () {
    return new Date(this);
}

RegExp.prototype[cocktail.ui.COPY_VALUE] = function () {
    return new RegExp(this);
}

Array.prototype[cocktail.ui.COPY_VALUE] = function () {
    let copy = [];
    for (let item of this) {
        copy.push(cocktail.ui.copyValue(item));
    }
    return copy;
}

Set.prototype[cocktail.ui.COPY_VALUE] = function () {
    let copy = new Set();
    for (let item of this) {
        copy.add(cocktail.ui.copyValue(item));
    }
    return copy;
}

Map.prototype[cocktail.ui.COPY_VALUE] = function () {
    let copy = new Map();
    for (let item of this) {
        copy.set(
            cocktail.ui.copyValue(item[0]),
            cocktail.ui.copyValue(item[1])
        );
    }
    return copy;
}

