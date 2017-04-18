/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

cocktail.ui.DISPLAY = Symbol("cocktail.ui.DISPLAY");

cocktail.ui.dataSourceConsumer = function (registration) {
    registration.properties["dataSource"] = {};
    registration.properties["dataState"] = {reflected: true};
}

cocktail.ui.DataSource = class DataSource {

    constructor(parameters = null) {
    }

    load(parameters = null) {}

    getValue(object, member, language = null) {
        let value = object[member.name];
        if (member.translated && language) {
            return value ? value[language] : null;
        }
        else {
            return value;
        }
    }
}

cocktail.ui.HTTPDataSource = class HTTPDataSource extends cocktail.ui.DataSource {

    constructor(parameters = null) {
        super(parameters);
        if (parameters) {
            this.url = parameters.url;
        }
    }

    getRequestParameters(parameters = null) {
        if (!parameters) {
            parameters = {};
        }
        parameters.url = this.url;
        parameters.responseType = "json";
        return parameters;
    }

    load(parameters = null) {

        parameters = this.getRequestParameters(parameters);

        return new Promise(function (resolve, reject) {
            cocktail.ui.request(parameters)
                .then(function (request) {
                    resolve(request.response);
                })
                .catch(function (e) {
                    reject(e);
                });
        });
    }
}

