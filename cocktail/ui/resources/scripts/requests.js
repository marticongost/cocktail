/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

cocktail.ui.request = function (params) {

    let xhr = new XMLHttpRequest();

    let promise = new Promise(function (resolve, reject) {

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status <= 299) {
                resolve(xhr);
            }
            else {
                reject(new cocktail.ui.RequestError(xhr));
            }
        }

        xhr.onerror = function () {
            reject(xhr);
        }

        let url = params.url;

        if (params.parameters) {
            let urlBuilder = URI(url);
            for (let key in params.parameters) {
                urlBuilder.removeSearch(key);
                urlBuilder.addSearch(key, params.parameters[key]);
            }
            url = urlBuilder.toString();
        }

        xhr.open(params.method || "GET", url);

        let data = params.data;
        let headers = params.headers || {};

        if (typeof(data) == "object") {
            data = JSON.stringify(data);
            headers["Content-Type"] = "application/json";
        }

        for (let key in headers) {
            xhr.setRequestHeader(key, headers[key]);
        }

        if (params.responseType) {
            xhr.responseType = params.responseType;
        }

        if (cocktail.csrfprotection) {
            cocktail.csrfprotection.setupRequest(xhr);
        }

        xhr.send(data);
    });

    promise.xhr = xhr;
    return promise;
}

cocktail.ui.RequestError = class RequestError {

    constructor(xhr) {
        this.xhr = xhr;
    }

    toString() {
        return "Request error"
    }
}

