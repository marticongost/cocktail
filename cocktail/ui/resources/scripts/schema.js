/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2017
-----------------------------------------------------------------------------*/

{
    let pkg = cocktail.declare("cocktail.schema");

    let OWNER = Symbol("cocktail.schema.OWNER");
    let NAME = Symbol("cocktail.schema.NAME");
    let MEMBERSHIP_TYPE = Symbol("cocktail.schema.MEMBERSHIP_TYPE");
    let TRANSLATED = Symbol("cocktail.schema.TRANSLATED");
    let MEMBER_MAP = Symbol("cocktail.schema.MEMBER_MAP");
    let BASE = Symbol("cocktail.schema.BASE");
    let TYPE = Symbol("cocktail.schema.TYPE");
    let SOURCE_MEMBER = Symbol("cocktail.schema.SOURCE_MEMBER");
    let ITEMS = Symbol("cocktail.schema.ITEMS");

    pkg.MEMBERS = Symbol("cocktail.schema.MEMBERS");
    pkg.MEMBER_PARAMETERS = Symbol("cocktail.schema.MEMBER_PARAMETERS");

    pkg.membershipTypes = {
        member: Symbol("cocktail.schema.membershipTypes.member")
    }

    cocktail.schema.Member = class Member {

        constructor(parameters = null) {
            this.primary = false;
            this.initialize(parameters);
        }

        initialize(parameters) {
            if (parameters) {
                for (let k in parameters) {
                    this.applyParameter(k, parameters[k]);
                }
                for (let k of Object.getOwnPropertySymbols(parameters)) {
                    this.applyParameter(k, parameters[k]);
                }
            }
        }

        toString() {
            return `${this.constructor.name}(${this.name})`;
        }

        get owner() {
            return this[OWNER];
        }

        get name() {
            return this[NAME];
        }

        get membershipType() {
            return this[MEMBERSHIP_TYPE];
        }

        get schema() {
            if (this.membershipType == pkg.membershipTypes.member) {
                return this.owner;
            }
            else {
                return null;
            }
        }

        get sourceMember() {
            return this[SOURCE_MEMBER];
        }

        get originalMember() {
            let member = this;
            while (member[SOURCE_MEMBER]) {
                member = member[SOURCE_MEMBER];
            }
            return member;
        }

        get translationKey() {
            let schema = this.schema;
            if (schema) {
                return schema.translationKey + ".members." + this[NAME];
            }
            else {
                return this[NAME];
            }
        }

        applyParameter(key, value) {
            if (key == "name") {
                this[NAME] = value;
            }
            else {
                this[key] = value;
            }
        }

        serializeValue(value) {
            if (value === null || value === undefined) {
                return "";
            }
            else {
                return String(value);
            }
        }

        parseValue(value) {
            return value;
        }

        getPossibleValues(obj = null) {
            if (this.enumeration) {
                return this.enumeration;
            }
            else if (this.dataSource) {
                return new Promise((resolve, reject) => {
                    this.dataSource.load()
                        .then((data) => resolve(data.records))
                        .catch((error) => reject(error));
                });
            }
            else {
                return null;
            }
        }

        translate(suffix = "") {
            let translation = cocktail.ui.translations[this.translationKey + suffix];
            if (translation) {
                return translation;
            }
            else if (this[SOURCE_MEMBER]) {
                return this[SOURCE_MEMBER].translate(suffix);
            }
            return "";
        }

        translateValue(value) {
            if (value === undefined || value === null || value === "") {
                return this.translate(".none");
            }
            else {
                return value;
            }
        }

        copy(parameters = null) {

            let copy = new this.constructor();

            for (let key of Reflect.ownKeys(this)) {
                if (!parameters || !(key in parameters)) {
                    this.copyAttribute(copy, key, this[key], parameters);
                }
            }

            copy[SOURCE_MEMBER] = this;

            if (parameters) {
                for (let key of Reflect.ownKeys(parameters)) {
                    this.copyAttribute(copy, key, parameters[key], parameters);
                }
            }

            return copy;
        }

        copyAttribute(copy, key, value, parameters) {
            if (key == "name") {
                copy[NAME] = value;
            }
            else if (key != OWNER && key != MEMBERSHIP_TYPE) {
                copy[key] = value;
            }
        }

        getDefaultValue(object = null, locale = null) {
            let value = this.defaultValue;
            if (value instanceof Function) {
                value = value.call(this, object);
            }
            return value;
        }
    }

    cocktail.schema.Member.prototype.descriptive = false;
    cocktail.schema.Member.prototype.translated = false;

    cocktail.schema.Schema = class Schema extends cocktail.schema.Member {

        static declare(parameters) {
            let schema = new cocktail.schema.Schema(parameters);
            cocktail.setVariable(schema.name, schema);
            return schema;
        }

        initialize(parameters) {
            this[MEMBER_MAP] = new Map();
            super.initialize(parameters);
        }

        applyParameter(key, value) {
            if (key == "base") {
                this[BASE] = value;
            }
            else if (key == "members") {
                for (let name in value) {
                    let member = value[name];
                    member[NAME] = name;
                    this.addMember(member);
                }
            }
            else {
                super.applyParameter(key, value);
            }
        }

        get base() {
            return this[BASE];
        }

        *members(recursive = true) {
            if (recursive) {
                let base = this[BASE];
                if (base) {
                    yield* base.members();
                }
            }
            yield* this[MEMBER_MAP].values();
        }

        getMember(name) {
            let member = null;
            for (let schema = this; !member && schema; schema = schema[BASE]) {
                member = this[MEMBER_MAP].get(name);
            }
            return member;
        }

        requireMember(name) {
            let member = this.getMember(name);
            if (!member) {
                throw new cocktail.schema.MemberNotFoundError(this, name);
            }
            return member;
        }

        addMember(member) {

            let currentOwner = member[OWNER];
            if (currentOwner) {
                throw new pkg.MemberRelocationError(member, currentOwner, this);
            }

            let name = member[NAME];
            if (!name) {
                throw new pkg.AnonymousMemberError(member, this);
            }

            if (this[MEMBER_MAP].has(name)) {
                throw new pkg.DuplicateMemberNameError(member, this);
            }

            member[OWNER] = this;
            member[MEMBERSHIP_TYPE] = pkg.membershipTypes.member;
            this[MEMBER_MAP].set(name, member);

            if (member.primary) {
                this.primaryMember = member;
            }

            if (member.descriptive) {
                this.descriptiveMember = member;
            }

            return member;
        }

        translateValue(value) {
            if (value && this.descriptiveMember) {
                let descriptiveValue = value[this.descriptiveMember.name];
                if (descriptiveValue && this.descriptiveMember.translated) {
                    descriptiveValue = descriptiveValue[cocktail.getLanguage()];
                }
                return this.descriptiveMember.translateValue(descriptiveValue);
            }
            else {
                return super.translateValue(value);
            }
        }

        copyAttribute(copy, key, value, parameters) {
            if (key == MEMBER_MAP) {

                let members = parameters && parameters[pkg.MEMBERS] || this.members();
                let memberParameters = parameters ? parameters[pkg.MEMBER_PARAMETERS] : null;

                for (let sourceMember of members) {

                    if (typeof(sourceMember) == "string") {
                        sourceMember = this.requireMember(sourceMember)
                    }

                    let targetMember;

                    if (sourceMember.schema === this) {
                        let params = memberParameters && memberParameters[sourceMember.name];
                        targetMember = sourceMember.copy(params);
                    }
                    else {
                        targetMember = sourceMember;
                    }

                    copy.addMember(targetMember);
                }
            }
            else if (key != BASE && key != "descriptiveMember") {
                super.copyAttribute(copy, key, value, parameters);
            }
        }

        getDefaultValue(object = null, locale = null) {
            return this.defaults();
        }

        defaults(object = null, locales = null) {
            if (!object) {
                object = {};
            }
            if (!locales) {
                locales = cocktail.ui.locales;
            }
            for (let member of this.members()) {
                let value;
                if (member.translated) {
                    value = {};
                    for (let locale of locales) {
                        value[locale] = member.getDefaultValue(object, locale);
                    }
                }
                else {
                    value = member.getDefaultValue(object);
                }
                object[member.name] = value;
            }
            return object;
        }
    }

    cocktail.schema.Schema.prototype.descriptiveMember = null;

    cocktail.schema.Boolean = class Boolean extends cocktail.schema.Member {

        getPossibleValues(obj = null) {
            let values = super.getPossibleValues(obj);
            return (values === null) ? [true, false] : values;
        }

        parseValue(value) {
            if (value == "true") {
                return true;
            }
            else if (value == "false") {
                return false;
            }
            else if (value == "null") {
                return null;
            }
            else {
                return undefined;
            }
        }

        serializeValue(value) {
            if (value === null) {
                return "null";
            }
            else if (value === undefined) {
                return "";
            }
            else {
                return value ? "true" : "false";
            }
        }

        translateValue(value) {
            if (value !== null && value !== undefined) {
                return cocktail.ui.translations[
                    "cocktail.schema.Boolean.instance." + (value ? "true" : "false")
                ];
            }
            else {
                return super.translateValue(value);
            }
        }
    }

    cocktail.schema.String = class String extends cocktail.schema.Member {
    }

    cocktail.schema.Number = class Number extends cocktail.schema.Member {

        constructor(parameters = null) {
            super(parameters);
            if (parameters) {
                this.min = parameters.min === undefined ? null : parameters.min;
                this.max = parameters.max === undefined ? null : parameters.max;
            }
            else {
                this.min = null;
                this.max = null;
            }
        }
    }

    cocktail.schema.Integer = class Integer extends cocktail.schema.Number {

        parseValue(value) {
            value = parseInt(value);
            return isNaN(value) ? undefined : value;
        }

        getPossibleValues(obj = null) {
            let values = super.getPossibleValues(obj);
            if (values === null) {
                if (this.min !== null && this.max !== null) {
                    values = [];
                    for (var i = this.min; i <= this.max; i++) {
                        values.push(i);
                    }
                }
            }
            return values;
        }
    }

    cocktail.schema.Float = class Float extends cocktail.schema.Number {

        parseValue(value) {
            value = parseFloat(value);
            return isNaN(value) ? undefined : value;
        }
    }

    cocktail.schema.Reference = class Reference extends cocktail.schema.Member {

        get type() {
            let type = this[TYPE];
            if (typeof(type) == "string") {
                type = cocktail.getVariable(type);
                this[TYPE] = type;
            }
            return type;
        }

        set type(value) {
            this[TYPE] = value;
        }

        translateValue(value) {

            if (value && this.type) {
                return this.type.translateValue(value);
            }

            return super.translateValue(value);
        }

        serializeValue(value) {
            if (!value) {
                return "";
            }
            else {
                return value[this.type.primaryMember.name];
            }
        }

        getPossibleValues(obj = null) {
            let values = super.getPossibleValues(obj);
            if (!values) {
                const type = this.type;
                if (type && type.dataSource) {
                    values = new Promise((resolve, reject) => {
                        type.dataSource.load()
                            .then((data) => resolve(data.records))
                            .catch((error) => reject(error));
                    });
                }
            }
            return values;
        }
    }

    cocktail.schema.Collection = class Collection extends cocktail.schema.Member {

        get items() {
            return this[ITEMS];
        }

        set items(value) {
            if (typeof(value) == "string") {
                value = new cocktail.schema.Reference({type: value});
            }
            this[ITEMS] = value;
        }

        translateValue(value) {
            if (this.items && value) {
                let items = [];
                for (let item of value) {
                    items.push(this.items.translateValue(item));
                }
                return items.join(", ");
            }
            else {
                return super.translateValue(value);
            }
        }

        parseValue(value) {
            if (value) {
                return Array.from(
                    this.splitValue(value),
                    item => this.items.parseValue(item)
                );
            }
            else {
                return [];
            }
        }

        serializeValue(value) {
            if (!value) {
                return "";
            }
            return this.joinValue(
                Array.from(value, item => this.items.serializeValue(item))
            );
        }

        splitValue(value) {
            return value.split(/\s+/);
        }

        joinValue(value) {
            if (!(value instanceof Array)) {
                value = Array.from(value);
            }
            return value.join(" ");
        }

        getDefaultValue(object = null, locale = null) {
            let defaultValue = super.getDefaultValue(object, locale);
            if (defaultValue === undefined) {
                defaultValue = [];
            }
            return defaultValue;
        }
    }

    cocktail.schema.Locale = class Locale extends cocktail.schema.String {

        constructor(parameters = null) {
            if (!parameters) {
                parameters = {};
            }
            if (parameters.enumeration === undefined) {
                parameters.enumeration = cocktail.ui.locales;
            }
            super(parameters);
        }

        translateValue(value) {
            if (value) {
                return cocktail.ui.translations["cocktail.locales." + value];
            }
            else {
                return super.translateValue(value);
            }
        }
    }

    cocktail.schema.MemberReference = class MemberReference extends cocktail.schema.Member {

        constructor(parameters = null) {
            super(parameters);
        }

        getPossibleValues(obj = null) {
            let values = super.getPossibleValues(obj);
            if (!values && this.sourceSchema) {
                values = new Set(this.sourceSchema.members());
            }
            return values;
        }

        parseValue(value) {

            if (!value) {
                return null;
            }

            if (!this.sourceSchema) {
                return undefined;
            }

            return this.sourceSchema.getMember(value);
        }

        serializeValue(value) {
            if (value) {
                value = value.name;
            }
            return value;
        }

        translateValue(value) {
            if (value) {
                return value.translate();
            }
            return super.translateValue(value);
        }
    }

    cocktail.schema.getLocales = function (object, schema) {
        for (let member of schema.members()) {
            if (member.translated) {
                let value = object[member.name];
                if (value && typeof(value) == "object") {
                    return Object.keys(value);
                }
            }
        }
        return null;
    }

    cocktail.schema.setLocales = function (object, schema, locales) {
        for (let member of schema.members()) {
            if (member.translated) {
                let value = object[member.name];
                if (value === undefined || value === null) {
                    value = {};
                }
                if (typeof(value) == "object") {
                    let [added, removed] = cocktail.sets.addedRemoved(Object.keys(value), locales);
                    for (let locale of removed) {
                        delete value[locale];
                    }
                    for (let locale of added) {
                        value[locale] = member.getDefaultValue(object, locale);
                    }
                }
            }
            else if (member instanceof cocktail.schema.Collection) {
                if (member.items && member.items instanceof cocktail.schema.Reference && member.items.type) {
                    let value = object[member.name];
                    if (value) {
                        for (let item of value) {
                            cocktail.schema.setLocales(item, member.items.type, locales);
                        }
                    }
                }
            }
            else if (member instanceof cocktail.schema.Reference && member.type) {
                let value = object[member.name];
                if (value && typeof(value) == "object") {
                    cocktail.schema.setLocales(value, member.type, locales);
                }
            }
        }
    }

    cocktail.schema.Error = class Error {
    }

    cocktail.schema.DuplicateMemberNameError = class DuplicateMemberNameError extends cocktail.schema.Error {

        constructor(member, schema) {
            this.member = member;
            this.schema = schema;
        }

        toString() {
            return `${this.schema} already contains a member called ${this.member.name}`;
        }
    }

    cocktail.schema.AnonymousMemberError = class AnonymousMemberError extends cocktail.schema.Error {

        constructor(member, schema) {
            super();
            this.member = member;
            this.schema = schema;
        }

        toString() {
            return `Can't add ${this.member} to ${this.schema}, the member has no name`;
        }
    }

    cocktail.schema.DuplicateMemberNameError = class DuplicateMemberNameError extends cocktail.schema.Error {

        constructor(member, schema) {
            super();
            this.member = member;
            this.schema = schema;
        }

        toString() {
            return `${this.schema} already contains a member called ${this.member.name}`;
        }
    }

    cocktail.schema.MemberRelocationError = class MemberRelocationError extends cocktail.schema.Error {

        constructor(member, schema) {
            super();
            this.member = member;
            this.schema = schema;
        }

        toString() {
            return `Can't move ${this.member} to ${this.schema}, it is already part of a schema`;
        }
    }

    cocktail.schema.MemberNotFoundError = class MemberNotFoundError extends cocktail.schema.Error {

        constructor(schema, memberName) {
            super();
            this.schema = schema;
            this.memberName = memberName;
        }

        toString() {
            return `${this.schema} contains no member with name "${this.memberName}"`;
        }
    }
}

