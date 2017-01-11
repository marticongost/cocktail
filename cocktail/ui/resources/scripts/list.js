/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2017
-----------------------------------------------------------------------------*/

cocktail.ui.List.define({
    value: new cocktail.ui.Property(),
    member: new cocktail.ui.Property(),
    language: new cocktail.ui.Property(),
    update: function () {
        while (this.firstChild) {
            this.removeChild(this.firstChild);
        }
        if (this.value) {
            for (let item of this.value) {
                let entry = this.createEntry(item);
                this.appendChild(entry);
            }
        }
    },
    createEntry: function (item) {
        let entry = this.Entry();
        entry.item = item;
        entry.innerHTML = this.translateItem(item);
        return entry;
    },
    translateItem: function (item) {
        return this.member.items.translateValue(item);
    }
});

