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
            resolve(xhr);
        }

        xhr.onerror = function () {
            reject(xhr);
        }

        xhr.open(params.method || "GET", params.url);

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

