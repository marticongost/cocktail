
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

cocktail.requireId = function (element) {
    if (!element) {
        return "clientElement" + (this.__autoId++);
    }
    else {
        return element.id || (element.id = "clientElement" + (this.__autoId++));
    }
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

    // If the instance has been inserted into the document by the callback,
    // page-wide bindings (note that IE creates new elements with a parentNode
    // of type DOCUMENT_FRAGMENT!)
    if (instance.parentNode && instance.parentNode.nodeType != 11) {
        cocktail.init();
    }
    // If the instance hasn't been inserted yet, limit bindings to the 
    // instances itself
    else {
        cocktail.init(instance);
    }

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

cocktail.center = function (element) {
    var windowWidth = window.innerWidth || document.documentElement.clientWidth;
    var windowHeight = window.innerHeight || document.documentElement.clientHeight;
    element.style.left = (windowWidth / 2 - element.offsetWidth / 2) + "px";
    element.style.top = (windowHeight / 2 - element.offsetHeight / 2) + "px";
}

cocktail.closeDialog = function () {
    // We use a custom remove function because jQuery.remove()
    // clears event handlers
    function remove() { this.parentNode.removeChild(this); };
    jQuery("body > .dialog-background").each(remove);
    jQuery("body > .dialog")
        .each(remove)
        .trigger("dialogClosed");
    jQuery(document.body).removeClass("modal");
}

cocktail.createElement = function (tag, name, type) {

    if (jQuery.browser.msie && Number(jQuery.browser.version) < 9) {
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

    function processReceivedContent(data, textStatus, request) {
        params.data = data;
        params.textStatus = textStatus;
        params.request = request;
        cocktail._updateElement(params);
        if (params.callback) {
            params.callback.call(params.element, params);
        }
        cocktail.init(params.element);
    }

    if (params.method == "get" || !params.method) {
        jQuery.get(params.url, processReceivedContent);
    }
    else if (params.method == "post") {
        jQuery.post(params.url, params.postData, processReceivedContent);
    }
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

        // Restore controls disabled by the 'disableForm' option
        if (params.disabledControls) {
            params.disabledControls.removeAttr("disabled");
        }
        
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
    
    // Disable all form controls for the duration of the submit operation
    if (params.disableForm) {
        var $form = jQuery(params.form);
        params.disabledControls = (
            $form.find("input")
            .add($form.find("button"))
            .add($form.find("textarea"))
            .add($form.find("select"))
            .not("[disabled]")
        );
        params.disabledControls.attr("disabled", "disabled");
    }
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
    
    if (source) {

        // Assign CSS classes
        target.className = source.className;

        // Copy children
        if (params.updateContent || params.updateContent === undefined) {
            jQuery(target).html(jQuery(source).html());
        }
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
            if (source && source.id) {
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

if (!jQuery.fn.reverse) {
    jQuery.fn.reverse = [].reverse;
}

// Add a :focus selector
jQuery.extend(jQuery.expr[':'], {
    focus: function(element) { 
        return element == document.activeElement; 
    }
});

cocktail.findPrevious = function (element, filter /* optional */) {
    
    var $iterator = jQuery(element);

    while ($iterator.length) {
        var $prev = $iterator.prev();
        
        while ($prev.length) {
            if (!filter || $prev.filter(filter).length) {
                return $prev.get(0);
            }
            $descendants = $prev.find("*");
            if (filter) {
                $descendants = $descendants.filter(filter);
            }
            if ($descendants.length) {                
                return $descendants.last().get(0);
            }
            $prev = $prev.prev();
        }

        $iterator = $iterator.parent();
        
        if ($iterator.length) {
            if (!filter || $iterator.filter(filter).length) {
                return $iterator.get(0);
            }
        }
    }
}

cocktail.findNext = function (element, filter /* optional */) {
    
    var $iterator = jQuery(element);

    while ($iterator.length) {
        
        var $next = $iterator;
        var first = true;

        while ($next.length) {

            if (!first) {
                var $descendants = $next.find("*");
                if (filter) {
                    $descendants = $descendants.filter(filter);
                }
                if ($descendants.length) {
                    return $descendants.get(0);
                }
            }
            first = false;

            var $next = $next.next();
            if (!filter || $next.filter(filter).length) {
                return $next.get(0);
            }
        }

        $iterator = $iterator.parent();
        
        if ($iterator.length) {
            if (!filter || $iterator.filter(filter).length) {
                return $iterator.get(0);
            }
        }
    }
}

cocktail.isVisible = function (element, recursive) {
    
    var $element = jQuery(element);    
    if ($element.css("visibility") == "hidden" 
        || $element.css("display") == "none") {
        return false;
    }
    
    if (recursive && element.parentNode && element != document.body) {
        return cocktail.isVisible(element.parentNode, true);
    }
    
    return true;    
}

cocktail.acceptsFocus = function (element) {
    return ("tabIndex" in element) && element.tabIndex != -1 && cocktail.isVisible(element, true);
}

cocktail.focusNext = function (item) {

    var origin = item || jQuery(":focus").get(0);
    var focusable = function () { return cocktail.acceptsFocus(this); }

    if (origin) {
        target = cocktail.findNext(origin, focusable);
    }

    if (!target) {
        target = jQuery(document.body).find(focusable).get(0);
    }

    if (target) {
        target.focus();
    }
}

cocktail.focusPrevious = function (item) {

    var target;
    var origin = item || jQuery(":focus").get(0);
    var focusable = function () { return cocktail.acceptsFocus(this); }
    
    if (origin) {
        target = cocktail.findPrevious(origin, focusable);
    }

    if (!target) {
        target = jQuery(document.body).find(focusable).last().get(0);
    }

    if (target) {
        target.focus();
    }
}

cocktail.declare = function (dottedName) {
    var obj;
    var parts = dottedName.split(".");
    var visitedParts = [];
    var container = window;

    for (var i = 0; i < parts.length; i++) {
        visitedParts.push(parts[i]);
        obj = container[parts[i]];
        if (!obj) {
            obj = {};
            container[parts[i]] = obj;
        }
        obj.__dottedName__ = visitedParts.join(".");
        obj.__name__ = parts[i];
        obj.__container__ = container;
        if (obj.toString == Object.prototype.toString) {
            obj.toString = function () { return this.__dottedName__; }
        }
        container = obj;
    }
    return obj;
}

cocktail.setVariable = function (dottedName, value) {
    var parts = dottedName.split(".");
    var name = parts.pop();
    var container = parts.length ? cocktail.declare(parts.join(".")) : window;
    container[name] = value;
}

// Implement support for the 'autofocus' HTML 5 attribute
jQuery(function () {
    var supportsAutofocus = "autofocus" in document.createElement('input');
    if (!supportsAutofocus) {
        jQuery("[autofocus]").first().focus();
    }
});

// Allow AJAX calls to redirect the browser
jQuery(function () {
    jQuery("body").bind("ajaxComplete", function (e, request, settings) {
        var redirect = request && request.getResponseHeader("Ajax-Redirect");
        if (redirect) {
           window.location = redirect;
        };
    });
});

