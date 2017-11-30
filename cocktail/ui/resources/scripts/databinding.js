/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

// Member annotations
{
    cocktail.ui.addAnnotations = Symbol.for("cocktail.ui.addAnnotations");
    cocktail.ui.removeAnnotations = Symbol.for("cocktail.ui.removeAnnotations");

    const CACHE = new WeakMap();

    cocktail.ui.getMemberTypes = function (memberType) {
        let memberTypeStr = CACHE.get(memberType);
        if (!memberTypeStr) {
            let memberTypeList = [];
            while (memberType !== cocktail.schema.Member) {
                memberTypeList.push(memberType.name);
                memberType = Object.getPrototypeOf(memberType);
            }
            memberTypeStr = memberTypeList.join(" ");
            CACHE.set(memberType, memberTypeStr);
        }
        return memberTypeStr;
    }
}

cocktail.schema.Member.prototype[cocktail.ui.addAnnotations] = function (element) {
    element.setAttribute("member", this.name);
    element.setAttribute("memberType", cocktail.ui.getMemberTypes(this.constructor));
}

cocktail.schema.Member.prototype[cocktail.ui.removeAnnotations] = function (element) {
    element.removeAttribute("member");
    element.removeAttribute("memberType");
}

cocktail.schema.Collection.prototype[cocktail.ui.addAnnotations] = function (element) {
    cocktail.schema.Member.prototype[cocktail.ui.addAnnotations].call(this, element);
    if (this.items) {
        element.setAttribute("itemsType", cocktail.ui.getMemberTypes(this.items.constructor));
    }
}

cocktail.schema.Collection.prototype[cocktail.ui.removeAnnotations] = function (element) {
    cocktail.schema.Member.prototype[cocktail.ui.removeAnnotations].call(this, element);
    element.removeAttribute("itemsType");
}

// DataBinding
{
    const MEMBER = Symbol("cocktail.ui.DataBinding.MEMBER");
    const OBJECT = Symbol("cocktail.ui.DataBinding.OBJECT");
    const LANGUAGE = Symbol("cocktail.ui.DataBinding.LANGUAGE");
    const INDEX = Symbol("cocktail.ui.DataBinding.INDEX");
    const PARENT = Symbol("cocktail.ui.DataBinding.PARENT");
    const VALUE = Symbol("cocktail.ui.DataBinding.VALUE");

    cocktail.ui.DataBinding = class DataBinding {

        constructor(object, member, language = null, index = null, value = undefined) {

            if (!member) {
                throw new cocktail.ui.InvalidDataBindingError(
                    "Can't create a data binding without specifying a member"
                );
            }

            this[OBJECT] = object;
            this[MEMBER] = member;
            this[LANGUAGE] = language;
            this[INDEX] = index;
            this[VALUE] = (value === undefined) ? this.getValue(language, index) : value;
        }

        get object() {
            return this[OBJECT];
        }

        get member() {
            return this[MEMBER];
        }

        get language() {
            return this[LANGUAGE];
        }

        get index() {
            return this[INDEX];
        }

        get parent() {
            return this[PARENT];
        }

        get value() {
            return this[VALUE];
        }

        getValue(language = null, index = null) {
            let object = this[OBJECT];
            if (object === undefined) {
                return undefined;
            }
            return this[MEMBER].getObjectValue(object, language, index);
        }

        childBinding(object, member, language = null, index = null, value = undefined) {
            let child = new this.constructor(object, member, language, index, value);
            child[PARENT] = this;
            return child;
        }

        memberBinding(member, language = null, value = undefined) {
            return this.childBinding(this[VALUE], member, language, null, value);
        }

        itemBinding(index, item = undefined) {
            return this.childBinding(this[VALUE], this[MEMBER].items, null, index, item);
        }
    }
}

cocktail.ui.InvalidDataBindingError = class InvalidDataBindingError {

    constructor(message) {
        this.message = message;
    }

    toString() {
        return this.message;
    }
}

