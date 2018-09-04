/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2017
-----------------------------------------------------------------------------*/

{
    const ID = Symbol("cocktail.ui.Action.ID");
    const POSITION = Symbol("cocktail.ui.Action.POSITION");

    cocktail.ui.Action = class Action {

        constructor(id, position = null) {
            this[ID] = id;
            this[POSITION] = position;
        }

        get id() {
            return this[ID];
        }

        get iconURL() {
            return null;
        }

        get min() {
            return null;
        }

        get max() {
            return null;
        }

        get position() {
            return this[POSITION];
        }

        set position(value) {
            this[POSITION] = value;
        }

        get translationPrefix() {
            return "cocktail.ui.actions";
        }

        get translationKey() {
            return `${this.translationPrefix}.${this[ID]}`;
        }

        translate() {
            return cocktail.ui.translations[this.translationKey];
        }

        get shortcut() {
            return cocktail.ui.translations[this.translationKey + ".shortcut"];
        }

        matches(actionBar) {
            return true;
        }

        getState(context) {

            let selectionSize = context.selection.length;

            let min = this.min;
            if (min !== null && selectionSize < min) {
                return "disabled";
            }

            let max = this.max;
            if (max !== null && selectionSize > max) {
                return "disabled";
            }

            return "visible";
        }

        createEntry() {
            return this.entryClass.create();
        }

        get entryClass() {
            return cocktail.ui.ActionListButton;
        }

        invoke(context) {
        }
    }
}

