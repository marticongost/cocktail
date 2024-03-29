/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

cocktail.ui.request = function (params) {

    let xhr;

    const promise = new Promise(function (resolve, reject) {

        function makeRequest() {

            const errorHandler = cocktail.ui.request.errorHandler;

            xhr = new XMLHttpRequest();
            xhr.method = params.method || "GET";
            xhr.url = params.url;
            xhr.data = params.data;

            let headers = params.headers || {};

            if (
                typeof(xhr.data) == "object"
                && !(xhr.data instanceof FormData)
                && !(xhr.data instanceof File)
            ) {
                xhr.data = JSON.stringify(xhr.data);
                headers["Content-Type"] = "application/json";
            }

            if (params.parameters) {
                let urlBuilder = URI(xhr.url);
                for (let key in params.parameters) {
                    urlBuilder.removeSearch(key);
                    urlBuilder.addSearch(key, params.parameters[key]);
                }
                xhr.url = urlBuilder.toString();
            }

            xhr.retry = function () {
                return makeRequest();
            }

            xhr.resolvePromise = function () {
                resolve(this);
            }

            xhr.rejectPromise = function () {
                reject(new cocktail.ui.RequestError(this));
            }

            xhr.onload = function () {
                if (xhr.status >= 200 && xhr.status <= 299) {
                    this.resolvePromise();
                }
                else {
                    this.onerror();
                }
            }

            xhr.onerror = function () {
                if (!errorHandler || errorHandler(this) === false) {
                    this.rejectPromise();
                }
            }

            xhr.open(params.method || "GET", xhr.url);

            for (let key in headers) {
                xhr.setRequestHeader(key, headers[key]);
            }

            if (params.responseType) {
                xhr.responseType = params.responseType;
                if (params.responseType == "json") {
                    xhr.setRequestHeader("Accept", "application/json");
                }
            }

            if (params.progressBar) {
                xhr.addEventListener("progress", (e) => {
                    const percent = Math.min(100, e.loaded / e.total * 100);
                    params.progressBar.value = percent;
                });
            }

            if (cocktail.csrfprotection) {
                cocktail.csrfprotection.setupRequest(xhr);
            }

            xhr.send(xhr.data);
            return xhr;
        }

        makeRequest();
    });

    Object.defineProperty(promise, "xhr", {
        get: () => xhr
    });

    return promise;
}

cocktail.ui.request.addErrorHandler = function (handler) {
    const prevHandler = cocktail.ui.request.errorHandler;
    if (prevHandler) {
        cocktail.ui.request.errorHandler = (xhr) => {
            if (errorHandler(xhr) === false) {
                return prevHandler(xhr);
            }
        }
    }
    else {
        cocktail.ui.request.errorHandler = handler;
    }
}

cocktail.ui.RequestError = class RequestError {

    constructor(xhr) {
        this.xhr = xhr;
    }

    toString() {
        return "Request error"
    }
}

