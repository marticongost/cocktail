/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2017
-----------------------------------------------------------------------------*/

{
    const ID = Symbol("cocktail.ui.Action.ID");

    cocktail.ui.Action = class Action {

        constructor(id) {
            this[ID] = id;
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

        translate() {
            return cocktail.ui.translations["cocktail.ui.actions." + this[ID]];
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

        invoke(context) {
        }
    }
}

