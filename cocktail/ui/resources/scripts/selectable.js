/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2017
-----------------------------------------------------------------------------*/

{
    const PREV_CLICK_ELEMENT = Symbol();
    const PREV_CLICK_TIME = Symbol();

    cocktail.ui.selectable = (cls) => class Selectable extends cls {

        static get componentProperties() {
            return {
                selectedElements: {
                    reflected: false,
                    normalization: cocktail.sets.normalize,
                    changedCallback: function (oldValue, newValue) {
                        let [added, removed] = cocktail.sets.addedRemoved(oldValue, newValue);
                        if (added.size || removed.size) {
                            let item;
                            for (item of removed) {
                                item.removeAttribute("selected");
                            }
                            for (item of added) {
                                item.setAttribute("selected", "");
                            }
                            if (added.size) {
                                this.selectionCursor = item;
                            }
                            cocktail.ui.trigger(this, "selectionChanged", {
                                added: added,
                                removed: removed
                            });
                        }
                    }
                },
                selectionType: {
                    type: "string",
                    reflected: true
                },
                selectionAxis: {
                    type: "string",
                    reflected: true
                },
                selectionCursor: {
                    reflected: false
                },
                selectableEntriesSelector: {
                    type: "string",
                    reflected: true
                },
                activationType: {
                    type: "string",
                    reflected: true
                },
                activationDoubleClickDelay: {
                    type: "number"
                }
            }
        }

        initialize() {
            super.initialize();

            this.selectionContainer = this;
            this[this.constructor.selectedElements.VALUE] = new Set();
            this.selectionType = "single";
            this.selectionAxis = "vertical";
            this.activationType = "doubleClick";
            this.activationDoubleClickDelay = 300;

            this.addEventListener("click", (e) => {

                if (this.selectionType == "none") {
                    return;
                }

                let target = this.getSelectableElementInPath(e.path);

                if (target) {

                    let multiple = (this.selectionType == "multiple");

                    // Ctrl + click: toggle selection
                    if (multiple && e.ctrlKey) {
                        this.setElementSelected(target, !this.selectedElements.has(target));
                    }
                    // Shift + click: range selection
                    else if (multiple && e.shiftKey) {
                        this.setRangeSelected(
                            this.selectionCursor || this.getFirstSelectableElement(),
                            target,
                            true
                        );
                    }
                    // Regular click: replace selection
                    else {
                        this.selectedElements = [target];
                    }

                    // Double click activation
                    let now = new Date();
                    if (
                        this.activationType == "singleClick"
                        || (
                            this.activationType == "doubleClick"
                            && target == this[PREV_CLICK_ELEMENT]
                            && now - this[PREV_CLICK_TIME] <= this.activationDoubleClickDelay
                        )
                    ) {
                        cocktail.ui.trigger(this, "activated", {selection: [target]});
                    }
                    this[PREV_CLICK_ELEMENT] = target;
                    this[PREV_CLICK_TIME] = now;

                    this.selectionCursor = target;
                    e.preventDefault();
                    e.stopPropagation();
                }
            });

            this.addEventListener("keydown", (e) => {

                if (this.selectionType == "none") {
                    return;
                }

                if (
                    e.which == 13
                    && this.activationType != "none"
                    && this.selectedElements.size
                ) {
                    cocktail.ui.trigger(this, "activated", {selection: Array.from(this.selectedElements)});
                    e.preventDefault();
                    e.stopPropagation();
                }

                let multiple = (this.selectionType == "multiple");

                // Select all (ctrl + a), empty selection (ctrl + shift + a)
                if (e.which == 65 && e.ctrlKey) {
                    if (e.shiftKey) {
                        this.selectedElements = [];
                        this.selectionCursor = null;
                    }
                    else if (multiple) {
                        let elements = this.getSelectableElements();
                        this.selectedElements = elements;
                        this.selectionCursor = elements[elements.length - 1];
                    }
                    e.preventDefault();
                    e.stopPropagation();
                }

                let axis = this.selectionAxis;
                let target, direction;

                // Home
                if (e.which == 36 && !e.ctrlKey && !e.altKey) {
                    target = this.getFirstSelectableElement();
                    direction = (axis == "vertical" ? "up" : "left");
                }
                // End
                else if (e.which == 35 && !e.ctrlKey && !e.altKey) {
                    target = this.getLastSelectableElement();
                    direction = (axis == "vertical" ? "bottom" : "right");
                }
                else {
                    if (axis == "vertical") {
                        // Up
                        if (e.which == 38) {
                            target = this.getPreviousSelectableElement();
                            direction = "up";
                        }
                        // Down
                        else if (e.which == 40) {
                            target = this.getNextSelectableElement();
                            direction = "bottom";
                        }
                    }
                    else if (axis == "horizontal") {
                        // Left
                        if (e.which == 37) {
                            target = this.getPreviousSelectableElement();
                            direction = "left";
                        }
                        // Right
                        else if (e.which == 39) {
                            target = this.getNextSelectableElement();
                            direction = "right";
                        }
                    }
                }

                if (target) {
                    if (multiple && e.ctrlKey) {
                        this.setElementSelected(target, true);
                    }
                    else if (multiple && e.shiftKey) {
                        this.setRangeSelected(this.selectionCursor, target, true);
                    }
                    else {
                        this.selectedElements = [target];
                    }
                    this.selectionCursor = target;
                    target.scrollIntoViewIfNeeded(false);
                    e.preventDefault();
                    e.stopPropagation();
                }
                else if (direction) {
                    cocktail.ui.trigger(this, "keyboardSelectionOverflow", {
                        direction: direction
                    });
                }
            });
        }

        get selectedValues() {
            return Array.from(this.selectedElements, (element) => element.value);
        }

        getSelectableElements() {
            let selector = this.selectableEntriesSelector;
            if (selector) {
                return Array.from(this.selectionContainer.children).filter(
                    (child) => child.matches(selector)
                );
            }
            else {
                return this.selectionContainer.children;
            }
        }

        getFirstSelectableElement() {
            let elements = this.getSelectableElements();
            return elements.length ? elements[0] : null;
        }

        getLastSelectableElement() {
            let elements = this.getSelectableElements();
            return elements.length ? elements[elements.length - 1] : null;
        }

        getNextSelectableElement(element = null) {

            if (!element) {
                element = this.selectionCursor;
            }

            if (element) {
                let selector = this.selectableEntriesSelector;
                let next = element.nextSibling;
                while (next) {
                    if (
                        next.nodeType == 1
                        && (!selector || next.matches(selector))
                    ) {
                        return next;
                    }
                    next = next.nextSibling;
                }
            }
            else {
                return this.getFirstSelectableElement();
            }

            return null;
        }

        getPreviousSelectableElement(element = null) {

            if (!element) {
                element = this.selectionCursor;
            }

            if (element) {
                let selector = this.selectableEntriesSelector;
                let previous = element.previousSibling;
                while (previous) {
                    if (
                        previous.nodeType == 1
                        && (!selector || previous.matches(selector))
                    ) {
                        return previous;
                    }
                    previous = previous.previousSibling;
                }
            }

            return null;
        }

        getSelectableElementInPath(path) {
            for (var i = 0; i < path.length - 2; i++) {
                let element = path[i];
                let container = path[i + 1];
                if (container == this.selectionContainer) {
                    return element;
                }
            }
            return null;
        }

        setElementSelected(element, selected) {
            this.setElementsSelected([element], selected);
        }

        setElementsSelected(elements, selected) {

            let added = new Set();
            let removed = new Set();
            let selectedElements = this.selectedElements;

            for (let element of elements) {
                let wasSelected = selectedElements.has(element);
                if (selected != wasSelected) {
                    if (selected) {
                        element.setAttribute("selected", "");
                        selectedElements.add(element);
                        added.add(element);
                    }
                    else {
                        element.removeAttribute("selected");
                        selectedElements.delete(element);
                        removed.add(element);
                    }
                }
            }

            if (added.size || removed.size) {
                cocktail.ui.trigger(this, "selectionChanged", {
                    added: added,
                    removed: removed
                });
            }
        }

        setRangeSelected(start, end, selected) {
            let range = (
                this.getSelectionRange(start, end, 1)
                || this.getSelectionRange(start, end, -1)
            );
            this.setElementsSelected(range, selected);
        }

        getSelectionRange(start, end, direction = 1) {

            let range = [];
            let element = start;
            let next = this["get" + (direction < 0 ? "Previous" : "Next") + "SelectableElement"];

            while (true) {
                range.push(element);
                if (!element) {
                    return null;
                }
                else if (element === end) {
                    return range;
                }
                element = next.call(this, element);
            }
        }
    }
}

