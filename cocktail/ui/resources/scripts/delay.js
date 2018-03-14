/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2017
-----------------------------------------------------------------------------*/

{
    const TIMER = Symbol();

    cocktail.ui.Delay = class Delayable {

        constructor(threshold, callback, cancelCallback = null) {
            this[TIMER] = null;
            this.threshold = threshold;
            this.callback = callback;
            this.cancelCallback = cancelCallback;
        }

        begin() {
            this.cancel();
            this[TIMER] = setTimeout(() => {
                this[TIMER] = null;
                this.callback()
            }, this.threshold);
        }

        cancel() {
            if (this[TIMER]) {
                clearTimeout(this[TIMER]);
                this[TIMER] = null;
                if (this.cancelCallback) {
                    this.cancelCallback();
                }
            }
        }

        get running() {
            return this[TIMER] !== null;
        }
    }
}

