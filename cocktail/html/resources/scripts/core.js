
var cocktail = {};
cocktail.__initCallbacks = [];

cocktail.init = function (callback) {
    if (callback) {
        cocktail.__initCallbacks.push(callback);
    }
    else {
        var callbacks = cocktail.__initCallbacks;
        for (var i = 0; i < callbacks.length; i++) {
            callbacks[i]();
        }
    }
}

cocktail.getLanguage = function () {
    return this.__language;
}

cocktail.setLanguage = function (language) {
    this.__language = language;
}

cocktail.__text = {};

cocktail.setTranslation = function (key, value) {
    this.__text[key] = value;
}

cocktail.translate = function (key, params) {
    
    var translation = this.__text[key];
    
    if (translation) {
        if (translation instanceof Function) {
            translation = translation.call(this, params || []);
        }
        else if (params) {
            for (var i in params) {
                translation = translation.replace(new RegExp("%(" + i + ")s"), params[i]);
            }
        }
    }
    
    return translation;
}
