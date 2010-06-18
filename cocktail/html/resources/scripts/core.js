
var cocktail = {};
cocktail.__initCallbacks = [];
cocktail.__clientModels = {};
cocktail.__autoId = 0;
cocktail.__iframeId = 0;
cocktail.__bindings = [];
cocktail.__bindingId = 0;

cocktail.init = function (param) {
    
    if (param && (param instanceof Function)) {
        cocktail.__initCallbacks.push(param);
    }
    else {
        var root = param || document.body;
        jQuery(document.body).addClass("scripted");
        var callbacks = cocktail.__initCallbacks;
        for (var i = 0; i < callbacks.length; i++) {
            callbacks[i](root);
        }
        cocktail.applyBindings(root);
    }
}

cocktail.applyBindings = function (root) {
    if (window.console) {
        console.log("Applying bindings");
    }
    for (var i = 0; i < cocktail.__bindings.length; i++) {
        cocktail.__bindings[i].apply(root);
    }
}

cocktail.bind = function (/* varargs */) {

    if (arguments.length == 1) {
        var binding = arguments[0];
    }
    else if (arguments.length <= 3) {
        var binding = {
            selector: arguments[0],
            behavior: arguments[1],
            children: arguments.length == 3 ? arguments[3] : null
        }
    }
    else {
        throw "Invalid binding parameters";
    }
    
    if (binding.children) {
        if (binding.children instanceof Array) {
            for (var i = 0; i < binding.children.length; i++) {
                binding.children[i].parent = binding;
                var child = cocktail.bind(binding.children[i]);
                binding.children[i] = child;
            }
        }
        else {
            var children = [];
            for (var selector in binding.children) {
                var child = cocktail.bind({
                    selector: selector,
                    behavior: binding.children[selector],
                    parent: binding
                });
                children.push(child);
            }
            binding.children = children;
        }
    }

    binding.id = cocktail.__bindingId++;

    if (!binding.parent) {
        cocktail.__bindings.push(binding);
    }

    binding.apply = function (root) {
        var $root = jQuery(root || document.body);
        var $matches = $root.find(binding.selector);        
        if ($root.is(binding.selector)) {
            $matches = $root.add($matches);
        }
        $matches.each(function () {
            if (binding.children) {
                for (var i = 0; i < binding.children.length; i++) {
                    binding.children[i].apply(this);
                }
            }
            if (!this._cocktail_bindings) {
                this._cocktail_bindings = {};
            }
            if (!this._cocktail_bindings[binding.id]) {
                var $element = jQuery(this);
                if (root && binding.name) {
                    root[binding.name] = this;
                    root["$" + binding.name] = $element;
                }
                this._cocktail_bindings[binding.id] = true;
                if (window.console) {
                    console.log(
                        'Applying binding "' + binding.selector
                        + '" #' + binding.id
                        + " to <" + this.tagName + " id='" + this.id + "' class='" + this.className + "'>"
                    );
                }
                binding.behavior.call(this, $element, jQuery(root));
            }
        });
    }
    return binding;
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

cocktail.loadElement = function (element, url, callback) {
    
    var pos = url.indexOf(" ");
    var fragment = "*";
    
    if (pos != -1) {
        fragment = url.substr(pos);
        url = url.substr(0, pos);
    }

    var container = document.createElement("div");

    jQuery.get(url, function (data) {
        cocktail.updateElement(element, data, fragment);
        if (callback) {
            callback.apply(element);
        }
    });
}

cocktail.submit = function (params) {

    var iframe = document.createElement("iframe");
    iframe.name = "cocktail_iframe" + cocktail.__iframeId++;
    iframe.style.position = "absolute";
    iframe.style.left = "-2000px";
    document.body.appendChild(iframe);
    iframe.onload = function () {
        var doc = (this.contentWindow || this.contentDocument);
        doc = doc.document || doc;
        if (params.targetElement) {
            cocktail.updateElement(
                params.targetElement,
                doc.documentElement.innerHTML,
                params.fragment || "body > *"
            );
        }
        iframe.parentNode.removeChild(iframe);
        if (params.callback) {
            params.callback.call(params.form, params, doc);
        }
    }
    params.form.target = iframe.name;
    params.form.submit();
}

cocktail.updateElement = function (element, data, fragment) {

    var container = document.createElement("div");
    var $container = jQuery(container);
    container.innerHTML = data;

    var newElement = $container.find(fragment).get(0);
    newElement.parentNode.removeChild(newElement);

    // Assign CSS classes
    element.className = newElement.className;

    // Copy children
    jQuery(element)
        .empty()
        .append(newElement.childNodes);

    // TODO: add new resources, client params, translations, etc

    // Re-apply behaviors
    cocktail.applyBindings();
}
