/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2017
-----------------------------------------------------------------------------*/

{
    cocktail.ui.selectable = (cls) => class Selectable extends cls {

        static get componentProperties() {
            return {
                selectedElements: {
                    reflected: false,
                    normalization: cocktail.sets.normalize,
                    changedCallback: function (oldValue, newValue) {
                        let [added, removed] = cocktail.sets.addedRemoved(oldValue, newValue);
                        if (added.size || removed.size) {
                            for (let item of removed) {
                                item.removeAttribute("selected");
                            }
                            for (let item of added) {
                                item.setAttribute("selected", "");
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
                }
            }
        }

        initialize() {
            super.initialize();

            this.selectionContainer = this;
            this[this.constructor.selectedElements.VALUE] = new Set();
            this.selectionType = "single";
            this.selectionAxis = "vertical";

            this.addEventListener("click", (e) => {

                if (this.selectionType == "none") {
                    return;
                }

                let target = this.getSelectableElementInPath(e.path);

                if (target) {
                    let multiple = (this.selectionType == "multiple");
                    if (multiple && e.ctrlKey) {
                        this.setElementSelected(target, !this.selectedElements.has(target));
                    }
                    else if (multiple && e.shiftKey) {
                        this.setRangeSelected(
                            this.selectionCursor || this.getFirstSelectableElement(),
                            target,
                            true
                        );
                    }
                    else {
                        this.selectedElements = [target];
                    }
                    this.selectionCursor = target;
                    e.preventDefault();
                }
            });

            this.addEventListener("keydown", (e) => {

                if (this.selectionType == "none") {
                    return;
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
                    return false;
                }

                let target;

                // Home
                if (e.which == 36) {
                    target = this.getFirstSelectableElement();
                }
                // End
                else if (e.which == 35) {
                    target = this.getLastSelectableElement();
                }
                else {
                    let axis = this.selectionAxis;
                    if (axis == "vertical") {
                        // Up
                        if (e.which == 38) {
                            target = this.getPreviousSelectableElement();
                        }
                        // Down
                        else if (e.which == 40) {
                            target = this.getNextSelectableElement();
                        }
                    }
                    else if (axis == "horizontal") {
                        // Left
                        if (e.which == 37) {
                            target = this.getPreviousSelectableElement();
                        }
                        // Right
                        else if (e.which == 39) {
                            target = this.getNextSelectableElement();
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
                }
            });
        }

        getSelectableElements() {
            return this.selectionContainer.children;
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
                let next = element.nextSibling;
                while (next) {
                    if (next.nodeType == 1) {
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
                let previous = element.previousSibling;
                while (previous) {
                    if (previous.nodeType == 1) {
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

