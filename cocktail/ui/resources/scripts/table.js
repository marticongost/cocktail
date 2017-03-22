/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2017
-----------------------------------------------------------------------------*/

cocktail.ui.dataBound(cocktail.ui.Table);

cocktail.ui.Table.define({

    [cocktail.ui.INITIALIZE]() {
        this.dataState = "pending";
        this.columnsReady = false;
        this.headingsRow.style.width =  `calc(100% - ${cocktail.getScrollbarWidth()}px)`;
    },

    member: new cocktail.ui.Property({
        set: function (instance, value) {
            this.setValue(instance, value);
            this.visibleColumns = new Set(value.members());
        }
    }),

    languages: new cocktail.ui.Property({
        getDefault: function () {
            return [];
        }
    }),

    visibleColumns: null,

    update() {

        let table = this;
        this.dataState = "loading";

        if (!this.columnsReady) {
            this.createColumns();
            this.columnsReady = true;
        }

        this.dataSource
            .load()
            .then(function (data) {
                table.setRows(data);
                table.dataState = "loaded";
            })
            .catch(function () {
                table.dataState = "failed";
            });
    },

    createColumns() {
        for (let member of this.member.members()) {
            let languages = member.translated ? this.languages : [null];
            for (let language of languages) {
                let heading = this.createHeading(member, language);
                this.headingsRow.appendChild(heading);
            }
        }
    },

    createHeading(member, language = null) {
        let heading = this.Heading();
        heading.member = member;
        heading.language = language;
        heading.setAttribute("data-column", member.name);
        heading.label.innerHTML = member.translate();
        if (language) {
            heading.languageLabel.innerHTML = language; // TODO: translate this
        }
        else {
            heading.languageLabel.style.display = "none";
        }
        return heading;
    },

    setRows(records) {
        for (let record of records) {
            let row = this.createRow(record);
            this.body.appendChild(row);
        }
    },

    createRow(record) {
        let row = document.createElement("tr");
        for (let member of this.member.members()) {
            let languages = member.translated ? this.languages : [null];
            for (let language of languages) {
                let cell = this.createCell(record, member, language);
                row.appendChild(cell);
            }
        }
        return row;
    },

    createCell(record, member, language) {

        let cell = document.createElement("td");
        cell.member = member;
        cell.language = language;
        cell.setAttribute("data-column", member.name);

        // Render the value using a custom component, if available, or fall
        // back to a string reprensetation
        let value = this.dataSource.getValue(record, member, language);
        let displayFactory = member[cocktail.ui.DISPLAY];

        if (displayFactory) {
            let display = displayFactory();
            display.object = record;
            display.member = member;
            display.language = language;
            display.value = value;
            cell.appendChild(display);
            display.update();
        }
        else {
            cell.innerHTML = member.translateValue(value);
        }

        return cell;
    }
});

