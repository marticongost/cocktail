/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

cocktail.ui.dataSourceConsumer = (cls) => class DataSourceConsumer extends cls {

    static get componentProperties() {
        return {
            dataSource: {},
            dataState: {reflected: true}
        };
    }
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
            this.requiresPOST = parameters.requiresPOST || false;
        }
    }

    getRequestParameters(parameters = null) {

        parameters = Object.assign(
            {
                url: this.url,
                responseType: "json",
                method: this.method
            },
            parameters || {}
        );

        // Convert query string parameters to form data / JSON values
        // when using POST requests
        if (this.requiresPOST) {

            parameters.method = "POST";

            if (!parameters.headers) {
                parameters.headers = {};
            }
            parameters.headers["X-HTTP-Method-Override"] = "GET";

            if (parameters.parameters) {
                if (!parameters.data) {
                    parameters.data = new FormData();
                }
                if (parameters.data instanceof FormData) {
                    for (let k in parameters.parameters) {
                        let v = parameters.parameters[k];
                        if (v instanceof Array) {
                            for (let item of v) {
                                parameters.data.append(k, item);
                            }
                        }
                        else {
                            parameters.data.append(k, v);
                        }
                    }
                }
                else {
                    Object.assign(parameters.data, params.parameters);
                }
                delete parameters.parameters;
            }
        }

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

