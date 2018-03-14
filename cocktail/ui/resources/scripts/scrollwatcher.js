/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

{
    let TARGET = Symbol("cocktail.ui.ScrollWatcher.TARGET");
    let TRIGGERED = Symbol("cocktail.ui.ScrollWatcher.TRIGGERED");

    cocktail.ui.ScrollWatcher = class ScrollWatcher {

        constructor(target = null, callback = null, threshold = 1.0) {
            this[TRIGGERED] = false;
            this.listener = (e) => this.check();
            this.target = target;
            this.threshold = threshold;
            this.callback = callback;
        }

        check() {
            if (!this[TRIGGERED] && this.callback && this.matchesThreshold()) {
                this[TRIGGERED] = true;
                this.callback();
            }
        }

        matchesThreshold() {
            let scrollOffset = this.getScrollOffset();
            let scrollSize = this.getScrollSize();
            let contentSize = this.getContentSize();
            return scrollOffset >= contentSize - scrollSize * this.threshold;
        }

        getScrollOffset() {
            return this.target.scrollTop;
        }

        getScrollSize() {
            return this.target.offsetHeight;
        }

        getContentSize() {
            return this.target.scrollHeight;
        }

        get target() {
            return this[TARGET];
        }

        set target(element) {
            if (this[TARGET]) {
                this.disconnect();
            }
            if (element) {
                this[TARGET] = element;
                element.addEventListener("scroll", this.listener);
            }
        }

        get triggered() {
            return this[TRIGGERED];
        }

        reset() {
            this[TRIGGERED] = false;
        }

        disconnect() {
            this[TARGET].removeEventListener(this.listener);
            this[TARGET] = null;
        }
    }
}

