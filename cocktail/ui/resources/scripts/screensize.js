/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         October 2019
-----------------------------------------------------------------------------*/

{
    const SIZE_MAP = Symbol();
    const ATTRIBUTE = Symbol();
    const SMALLEST_SIZE = Symbol();
    const BIGGEST_SIZE = Symbol();
    const CURRENT_SIZE = Symbol();
    const NEXT = Symbol();
    const PREV = Symbol();
    const RESIZE_LISTENER = Symbol();
    const PROPERTIES = Symbol();

    cocktail.ui.Sizes = class Sizes {

        constructor(sizesMap, attribute) {
            this[SIZE_MAP] = {};
            this[SMALLEST_SIZE] = null;
            this[BIGGEST_SIZE] = null;
            this[PROPERTIES] = new WeakMap();
            this[ATTRIBUTE] = attribute;
            for (let name in sizesMap) {
                this.addSize(name, sizesMap[name]);
            }
        }

        getSize(name) {
            return this[SIZE_MAP][name];
        }

        get smallestSize() {
            return this[SMALLEST_SIZE];
        }

        get biggestSize() {
            return this[BIGGEST_SIZE];
        }

        *ascending(selector = null) {
            if (this[SMALLEST_SIZE]) {
                for (let size of this[SMALLEST_SIZE].ascending()) {
                    if (!selector || size.matches(selector)) {
                        yield size;
                    }
                }
            }
        }

        *descending(selector = null) {
            if (this[BIGGEST_SIZE]) {
                for (let size of this[BIGGEST_SIZE].descending()) {
                    if (!selector || size.matches(selector)) {
                        yield size;
                    }
                }
            }
        }

        addSize(name, maxWidth) {

            const size = new cocktail.ui.Size(name, maxWidth);
            size[PREV] = this[BIGGEST_SIZE];

            if (this[BIGGEST_SIZE]) {
                if (this[BIGGEST_SIZE].max === null || maxWidth !== null && maxWidth <= this[BIGGEST_SIZE].max) {
                    throw `Size thresholds should be in ascending order; ${this[BIGGEST_SIZE].name} has a greater width than ${name}`;
                }
                this[BIGGEST_SIZE][NEXT] = size;
            }
            else {
                this[SMALLEST_SIZE] = size;
            }

            this[BIGGEST_SIZE] = size;
            this[SIZE_MAP][name] = size;
            return size;
        }

        getSizeOfWindow(wnd = null) {
            return this.getSizeForMeasure((wnd || window).innerWidth);
        }

        getSizeForMeasure(measure) {
            if (this[SMALLEST_SIZE]) {
                for (let size of this.ascending()) {
                    if (size.maxWidth === null || measure < size.maxWidth) {
                        return size;
                    }
                }
            }
            return null;
        }

        monitorWindow(wnd = null) {
            if (!wnd) {
                wnd = window;
            }
            if (!wnd[RESIZE_LISTENER]) {
                const setSize = (previousSize, newSize) => {
                    wnd[CURRENT_SIZE] = newSize;
                    cocktail.ui.trigger(wnd, "sizeChanged", {
                        previousSize,
                        newSize
                    });
                    if (this[ATTRIBUTE]) {
                        wnd.document.body.setAttribute(this[ATTRIBUTE], newSize.name);
                    }
                }
                setSize(null, this.getSizeOfWindow(wnd));
                wnd[RESIZE_LISTENER] = wnd.addEventListener("resize", (e) => {
                    const previousSize = wnd[CURRENT_SIZE];
                    const newSize = this.getSizeOfWindow(wnd);
                    if (newSize !== previousSize) {
                        setSize(previousSize, newSize);
                    }
                });
            }
        }

        stopMonitoringWindow(wnd = null) {
            if (!wnd) {
                wnd = window;
            }
            if (wnd[RESIZE_LISTENER]) {
                wnd.removeEventListener(wnd[RESIZE_LISTENER]);
                wnd[RESIZE_LISTENER] = null;
            }
        }

        adapt(element, properties) {

            const props = this[PROPERTIES].get(element);

            if (!props) {
                this[PROPERTIES].set(element, properties);
                this.monitorWindow(element.ownerDocument.defaultView);
                element.addWindowListener("sizeChanged", (e) => {
                    this.applyPerSizeProperties(
                        element,
                        this[PROPERTIES].get(element),
                        e.detail.newSize
                    );
                    cocktail.ui.trigger(element, "sizeAdaptation", {
                        previousSize: e.detail.previousSize,
                        newSize: e.detail.newSize
                    });
                });
            }
            else {
                Object.assign(props, properties);
            }
            const wnd = element.ownerDocument.defaultView;
            const newSize = this.getSizeOfWindow(wnd);
            this.applyPerSizeProperties(element, properties);
            cocktail.ui.trigger(element, "sizeAdaptation", {
                previousSize: null,
                newSize
            });
        }

        applyPerSizeProperties(element, perSizeProperties, size = null) {
            if (!size) {
                size = this.getSizeOfWindow(element.ownerDocument.defaultView);
            }
            for (let key in perSizeProperties) {
                const perSizeValues = perSizeProperties[key];
                for (let sizeSelector in perSizeValues) {
                    if (size.matches(sizeSelector)) {
                        const value = perSizeValues[sizeSelector];
                        element[key] = value;
                        break;
                    }
                }
            }
        }
    }

    const NAME = Symbol();
    const MAX_WIDTH = Symbol();

    cocktail.ui.Size = class Size {

        constructor(name, maxWidth) {
            this[NAME] = name;
            this[MAX_WIDTH] = maxWidth;
            this[NEXT] = null;
            this[PREV] = null;
        }

        get name() {
            return this[NAME];
        }

        get minWidth() {
            return this[PREV] ? this[PREV].maxWidth + 1 : 0;
        }

        get maxWidth() {
            return this[MAX_WIDTH];
        }

        get previousSize() {
            return this[PREVIOUS];
        }

        get nextSize() {
            return this[NEXT];
        }

        matches(selector) {
            return (
                selector == this[NAME]
                || selector == "any"
            );
        }

        *descending(includeSelf = true) {
            let size = this;
            if (!includeSelf) {
                size = size[PREV];
            }
            while (size) {
                yield size;
                size = size[PREV];
            }
        }

        *ascending(includeSelf = true) {
            let size = this;
            if (!includeSelf) {
                size = size[NEXT];
            }
            while (size) {
                yield size;
                size = size[NEXT];
            }
        }
    }
}

