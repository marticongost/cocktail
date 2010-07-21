
var cocktail = {};
cocktail.__initialized = false;
cocktail.__clientModels = {};
cocktail.__autoId = 0;
cocktail.__iframeId = 0;
cocktail.__bindings = [];
cocktail.__bindingId = 0;
cocktail.__clientParams = {};
cocktail.__clientCode = {};

cocktail.init = function (root) {
    
    if (!cocktail.__initialized) {
        cocktail.__initialized = true;
        jQuery(document.body).addClass("scripted");
    }
    
    root = root || document.body;

    // Set server supplied parameters
    var remainingParams = {};

    for (var id in cocktail.__clientParams) {
        var target = cocktail._findById(root, id);
        var params = cocktail.__clientParams[id];
        if (target) {
            for (var key in params) {
                target[key] = params[key];
            }
        }
        else {
            remainingParams[id] = params;
        }
    }

    cocktail.__clientParams = remainingParams;

    // Apply server supplied code
    var remainingCode = {};

    for (var id in cocktail.__clientCode) {
        var target = cocktail._findById(root, id);
        var code = cocktail.__clientCode[id];
        if (target) {
            for (var i = 0; i < code.length; i++) {
                code[i].call(target);
            }
        }
        else {
            remainingCode[id] = code;
        }
    }

    cocktail.__clientCode = remainingCode;

    // Apply bindings
    for (var i = 0; i < cocktail.__bindings.length; i++) {
        cocktail.__bindings[i].apply(root);
    }
}

cocktail._findById = function (root, id) {
    return (root.id == id) ? root : jQuery(root).find("#" + id).get(0);
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

    binding.toString = function () {
        return "Binding #" + this.id + " \"" + this.selector + "\"";
    }

    binding.find = function (root) {
        if (!root) {
            var body = root = document.body;
        }
        else {
            var body = root.ownerDocument.body;
        }

        var $root = jQuery(root);
        
        if (root == body) {
            var $matches = jQuery(body).find(binding.selector);
        }
        else {
            var $matches = jQuery(root).find("*").filter(binding.selector);
        }

        if ($root.is(binding.selector)) {
            $matches = $root.add($matches);
        }

        return $matches;
    }

    binding.apply = function (root) {
        this.find(root).each(function () {
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

        // Close the dialog when pressing the Escape key
        jQuery(document).keyup(function (e) {
            if (e.keyCode == 27) {
                cocktail.closeDialog();
            }
        });

        jQuery(cocktail.__dialogBackground).click(cocktail.closeDialog);
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

cocktail.update = function (params) {

    if (params.nodeType) {
        params = {element: params};
    }

    if (!params.url) {
        params.url = location.href;
    }

    jQuery.get(params.url, function (data) {
        params.data = data;
        cocktail._updateElement(params);
        if (params.callback) {
            params.callback.call(params.element, params);
        }
        cocktail.init(params.element);
    });
}

cocktail.prepareBackgroundSubmit = function (params) {

    var iframe = document.createElement("iframe");
    iframe.name = "cocktail_iframe" + cocktail.__iframeId++;
    iframe.style.position = "absolute";
    iframe.style.left = "-2000px";
    document.body.appendChild(iframe);

    iframe.onload = function () {
        var doc = (this.contentWindow || this.contentDocument);
        doc = doc.document || doc;
        if (params.targetElement) {
            cocktail._updateElement({
                element: params.targetElement,
                data: doc.documentElement.innerHTML,
                fragment: params.fragment || "body > *"
            });
        }
        iframe.parentNode.removeChild(iframe);
        if (params.callback) {
            params.callback.call(params.form, params, doc);
        }
        if (params.targetElement) {
            cocktail.init(params.targetElement);
        }
    }

    params.form.target = iframe.name;
}
    
cocktail.submit = function (params) {
    cocktail.prepareBackgroundSubmit(params);
    params.form.submit();
}

cocktail.__htmlBodyRegExp = /<body(\s[^>]*)?/;
cocktail.CLIENT_ASSETS_MARK = "// cocktail.html client-side setup";

cocktail._updateElement = function (params) {

    var bodyHTML = params.data;
    var bodyStart = params.data.search(cocktail.__htmlBodyRegExp);
    if (bodyStart != -1) {
        bodyStart += params.data.match(cocktail.__htmlBodyRegExp)[0].length;
        var bodyEnd = params.data.indexOf("</body>", bodyStart);
        bodyHTML = params.data.substring(bodyStart, bodyEnd);
    }

    params.$container = jQuery("<div>").html(bodyHTML);
    var target = params.element;
    var source = params.$container.find(params.fragment || "*").get(0);
    
    // Assign CSS classes
    target.className = source.className;

    // Copy children
    if (params.updateContent || params.updateContent === undefined) {
        jQuery(target).html(jQuery(source).html());
    }

    // Copy client parameters and code
    if (params.updateAssets || params.updateAssets === undefined) {

        var clientAssets = null;
        var scriptStart = params.data.indexOf(cocktail.CLIENT_ASSETS_MARK)
        if (scriptStart != -1) {
            scriptStart += cocktail.CLIENT_ASSETS_MARK.length;
            var scriptEnd = params.data.indexOf("</script>", scriptStart);
            if (scriptEnd != -1) {
                clientAssets = params.data.substring(scriptStart, scriptEnd);
            }
        }

        if (clientAssets) {
            eval(clientAssets);
            if (source.id) {
                if (!target.id) {
                    target.id = source.id;
                }
                else if (target.id != source.id) {
                    // Parameters
                    var newClientParams = cocktail.__clientParams[source.id] || {};
                    var clientParams = cocktail.__clientParams[target.id]
                                   || (cocktail.__clientParams[target.id] = {});
                    for (var key in newClientParams) {
                        clientParams[key] = newClientParams[key];
                    }

                    // Code
                    var newCode = cocktail.__clientCode[source.id] || [];
                    var code = cocktail.__clientCode[target.id]
                           || (cocktail.__clientCode[target.id] == []);
                    for (var i = 0; i < newCode.length; i++) {
                        code.push(newCode[i]);
                    }
                }
            }
        }
        // TODO: add new resources, translations, etc
    }
}
