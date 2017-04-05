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
    pkg.EXCLUDE = Symbol("cocktail.schema.EXCLUDE");

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
            while (source = member[SOURCE_MEMBER]) {
                member = source;
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

        translate() {
            let translation = cocktail.ui.translations[this.translationKey];
            if (translation) {
                return translation;
            }
            else if (this[SOURCE_MEMBER]) {
                return this[SOURCE_MEMBER].translate();
            }
            return "";
        }

        translateValue(value) {
            if (value === undefined) {
                return "";
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
            if (key != OWNER && key != MEMBERSHIP_TYPE) {
                copy[key] = value;
            }
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
            if (this.descriptiveMember) {
                let descriptiveValue = value[this.descriptiveMember.name];
                if (descriptiveValue && this.descriptiveMember.translated) {
                    descriptiveValue = descriptiveValue[cocktail.getLanguage()];
                }
                return this.descriptiveMember.translateValue(descriptiveValue);
            }
            else {
                return this.name;
            }
        }

        copyAttribute(copy, key, value, parameters) {
            if (key == MEMBER_MAP) {
                let membersParameters = parameters ? parameters[pkg.MEMBERS] : null;
                let implicitCopy = parameters ? parameters[pkg.IMPLICIT_COPY] : !membersParameters;

                for (let member of this.members()) {
                    let memberParameters = membersParameters ? membersParameters[member.name] : null;
                    if (memberParameters == pkg.EXCLUDE) {
                        continue;
                    }
                    if (memberParameters || implicitCopy) {
                        let memberCopy = member.copy(memberParameters);
                        copy.addMember(memberCopy);
                    }
                }
            }
            else if (key != BASE && key != "descriptiveMember") {
                super.copyAttribute(copy, key, value, parameters);
            }
        }
    }

    cocktail.schema.Schema.prototype.descriptiveMember = null;

    cocktail.schema.Boolean = class Boolean extends cocktail.schema.Member {

        translateValue(value) {
            return cocktail.ui.translations[
                "cocktail.schema.Boolean.instance." + (value ? "true" : "false")
            ];
        }
    }

    cocktail.schema.String = class String extends cocktail.schema.Member {
    }

    cocktail.schema.Number = class Number extends cocktail.schema.Member {
    }

    cocktail.schema.Integer = class Integer extends cocktail.schema.Number {
    }

    cocktail.schema.Float = class Float extends cocktail.schema.Number {
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
            if (this.type && typeof(value) == "object") {
                return this.type.translateValue(value);
            }
            else {
                super.translateValue(value);
            }
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
            this.member = member;
            this.schema = schema;
        }

        toString() {
            return `Can't add ${this.member} to ${this.schema}, the member has no name`;
        }
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
}

