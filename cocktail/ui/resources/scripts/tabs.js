/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         December 2016
-----------------------------------------------------------------------------*/

cocktail.ui.Tabs.define({

    [cocktail.ui.ADD](child) {
        if (cocktail.ui.isInstance(child, cocktail.ui.Tabs.Tab)) {
            this.strip.appendChild(child.button);
            this.content.appendChild(child);
        }
        else {
            this.appendChild(child);
        }
    },

    selectedTab: new cocktail.ui.Property({
        set: function (tabs, tab) {
            if (tabs.selectedTab) {
                tabs.selectedTab.selected = false;
            }
            this.setValue(tabs, tab);
            if (tab) {
                tabs.selectedTab.selected = true;
            }
        }
    })
});

cocktail.ui.Tabs.Tab.define({

    [cocktail.ui.INITIALIZE]() {
        let tab = this;
        this.button.addEventListener("click", function () {
            let tabs = cocktail.ui.closestInstance(this, cocktail.ui.Tabs);
            tabs.selectedTab = tab;
        });
        this.addEventListener("selectedChanged", function () {
            this.button.selected = this.selected;
            if (this.selected && !this.revealed) {
                this.revealed = true;
                cocktail.ui.trigger(this, "tabRevealed");
            }
        });
        if (this.selected === null) {
            this.selected = false;
        }
    },

    selected: new cocktail.ui.BooleanAttribute(),
    revealed: false
});

cocktail.ui.Tabs.Tab.Button.define({
    selected: new cocktail.ui.BooleanAttribute()
});

