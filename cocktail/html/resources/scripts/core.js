
var cocktail = {};
cocktail.__initCallbacks = [];
cocktail.__clientModels = {};
cocktail.__autoId = 0;

cocktail.init = function (param) {
    
    if (param && (param instanceof Function)) {
        cocktail.__initCallbacks.push(param);
    }
    else {
        jQuery(document.body).addClass("scripted");
        var callbacks = cocktail.__initCallbacks;
        for (var i = 0; i < callbacks.length; i++) {
            callbacks[i](param || document.body);
        }
    }
}

cocktail._clientModel = function (modelId, partId /* optional */) {
    var model = this.__clientModels[modelId];
    if (!model) {
        model = this.__clientModels[modelId] = {
            html: null,
            params: {},
            code: [],
            parts: {}
        };
    }

    if (partId) {
        var part = model.parts[partId];
        if (!part) {
            part = model.parts[partId] = {
                params: {},
                code: []                
            };
        }
        return part;
    }

    return model;
}

cocktail.requireId = function () {
    return "clientElement" + (this.__autoId++);
}

cocktail.instantiate = function (modelId, params, initializer) {

    var model = this.__clientModels[modelId];

    if (!model || !model.html) {
        throw "Undefined client model '" + modelId + "'";
    }
    
    // Variable replacement
    var html = model.html;

    for (var key in params) {
        var expr = new RegExp("\\$" + key + "\\b", "g");
        html = html.replace(expr, params[key]);
    }

    // Create the instance
    var dummy = document.createElement("div");
    dummy.innerHTML = html;
    var instance = dummy.firstChild;
    instance.id = cocktail.requireId();
    dummy.removeChild(instance);

    if (initializer) {
        initializer.call(instance);
    }

    // Client parameters
    if (model.params) {
        for (var key in model.params) {
            instance[key] = model.params[key];
        }
    }

    // Client code
    if (model.code) {
        (function () {
            for (var i = 0; i < model.code.length; i++) {
                eval(model.code[i]);
            }
        }).call(instance);
    }

    // Nested parts
    for (var partId in model.parts) {
        var part = model.parts[partId];
        var partInstance = jQuery("#" + partId, instance).get(0);
        partInstance.id = cocktail.requireId();

        // Parameters
        if (part.params) {
            for (var key in part.params) {
                partInstance[key] = part.params[key];
            }
        }

        // Code
        if (part.code) {
            (function () {
                for (var i = 0; i < part.code.length; i++) {
                    eval(part.code[i]);
                }
            }).call(partInstance);
        }
    }

    // Behaviors
    cocktail.init(instance);

    return instance;
}

cocktail.getLanguage = function () {
    return this.__language;
}

cocktail.setLanguage = function (language) {
    this.__language = language;
}

cocktail.setLanguages = function (languages) {
    this.__languages = languages
}

cocktail.getLanguages = function () {
    return this.__languages;
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
                translation = translation.replace(new RegExp("%\\(" + i + "\\)s"), params[i]);
            }
        }
    }
    
    return translation;
}

cocktail.__dialogBackground = null;

cocktail.showDialog = function (content) {

    if (!cocktail.__dialogBackground) {
        cocktail.__dialogBackground = document.createElement("div")
        cocktail.__dialogBackground.className = "dialog-background";
    }
    document.body.appendChild(cocktail.__dialogBackground);
    
    var $content = jQuery(content);
    $content.addClass("dialog");
    jQuery(document.body)
        .addClass("modal")
        .append($content);
}

cocktail.closeDialog = function () {
    // We use a custom remove function because jQuery.remove()
    // clears event handlers
    function remove() { this.parentNode.removeChild(this); };
    jQuery("body > .dialog-background").each(remove);
    jQuery("body > .dialog").each(remove);
    jQuery(document.body).removeClass("modal");
}

cocktail.createElement = function (tag, name, type) {

    if (jQuery.browser.msie) {
        var html = "<" + tag;
        if (name) {
            html += " name='" + name + "'";
        }
        if (type) {
            html += " type='" + type + "'";
        }
        html += ">";
        return document.createElement(html);
    }
    else {
        var element = document.createElement(tag);
        element.name = name;
        element.type = type;
        return element
    }
}

