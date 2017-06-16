/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         June 2017
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.ui.sorting", {

    compare(a, b) {
        if (a > b) {
            return 1;
        }
        else if (a < b) {
            return -1;
        }
        return 0;
    },

    localeCompare(a, b, locale = null) {
        return a.localeCompare(b, locale || cocktail.getLanguage());
    },

    sort(values, key = null, comparator = null) {
        if (!key) {
            let items = Array.from(values);
            items.sort(comparator);
            return items;
        }
        else {
            if (typeof(key) == "string") {
                let prop = key;
                key = (item) => item[prop];
            }
            let items = Array.from(values, (item) => [key(item), item]);
            if (!comparator) {
                comparator = this.compare;
            }
            items.sort((a, b) => comparator(a[0], b[0]));
            return Array.from(items, (item) => item[1]);
        }
    },

    localeSort(values, key = null, locale = null) {
        return this.sort(values, key, (a, b) => this.localeCompare(a, b, locale));
    }
});

