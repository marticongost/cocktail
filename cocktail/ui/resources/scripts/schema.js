/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2017
-----------------------------------------------------------------------------*/

{
    const pkg = cocktail.declare("cocktail.schema");

    const OWNER = Symbol("cocktail.schema.OWNER");
    const NAME = Symbol("cocktail.schema.NAME");
    const MEMBERSHIP_TYPE = Symbol("cocktail.schema.MEMBERSHIP_TYPE");
    const TRANSLATED = Symbol("cocktail.schema.TRANSLATED");
    const MEMBER_MAP = Symbol("cocktail.schema.MEMBER_MAP");
    const BASE = Symbol("cocktail.schema.BASE");
    const DERIVED_SCHEMAS = Symbol("cocktail.schema.DERIVED_SCHEMAS");
    const TYPE = Symbol("cocktail.schema.TYPE");
    const SOURCE_MEMBER = Symbol("cocktail.schema.SOURCE_MEMBER");
    const ITEMS = Symbol("cocktail.schema.ITEMS");
    const DATA_SOURCE = Symbol("cocktail.schema.DATA_SOURCE");
    const PRIMARY_MEMBER = Symbol("cocktail.schema.PRIMARY_MEMBER");
    const RELATED_END = Symbol("cocktail.schema.RELATED_END");
    const CLASS_FAMILY = Symbol("cocktail.schema.CLASS_FAMILY");

    pkg.MEMBERS = Symbol("cocktail.schema.MEMBERS");
    pkg.PARAMETERS = Symbol("cocktail.schema.PARAMETERS");
    pkg.MEMBER_PARAMETERS = Symbol("cocktail.schema.MEMBER_PARAMETERS");

    pkg.membershipTypes = {
        member: Symbol("cocktail.schema.membershipTypes.member"),
        collectionItems: Symbol("cocktail.schema.membershipTypes.collectionItems")
    }

    const claimMember = (owner, member, membershipType) => {
        const currentOwner = member[OWNER];
        if (currentOwner) {
            throw new pkg.MemberRelocationError(member, currentOwner, owner);
        }
        member[OWNER] = owner;
        member[MEMBERSHIP_TYPE] = membershipType;
    }

    const schemasByName = {};

    pkg.getSchemaByName = function getSchemaByName(name) {
        return schemasByName[name];
    }

    pkg.getMemberByName = function getMemberByName(name) {
        const pos = name.lastIndexOf(".");
        if (pos != -1) {
            const schema = this.getSchemaByName(name.substr(0, pos));
            if (schema) {
                return schema.getMember(name.substr(pos + 1));
            }
        }
        return null;
    }

    pkg.resolveSchema = function (model) {
        return typeof(model) == "string" ? this.getSchemaByName(model) : model;
    }

    pkg.resolveMember = function (member) {
        return typeof(member) == "string" ? this.getMemberByName(member) : member;
    }

    pkg.objectFromJSONValue = function (value, defaultType = null) {
        if (value) {
            const schema = value._class ? pkg.getSchemaByName(value._class) : defaultType;
            if (schema) {
                return schema.fromJSONValue(value);
            }
        }
        return value;
    }

    pkg.objectsFromJSONValue = function (value) {
        return Array.from(value, (obj) => this.objectFromJSONValue(obj));
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

        [cocktail.ui.CONSOLE_HEADER]() {

            const items = [];
            const fullName = this.fullName;
            const pos = fullName.lastIndexOf(".");
            let name;

            if (pos != -1) {
                items.push(fullName.substr(0, pos + 1));
                name = fullName.substr(pos + 1);
            }
            else {
                name = fullName;
            }

            items.push(["span", {style: "font-weight: bold"}, name]);

            return [
                "div",
                [
                    "span",
                    {style: "color: #604b33; font-weight: bold"},
                    this.constructor.name
                ],
                " ",
                [
                    "span",
                    {style: "color: #c77400"},
                    ...items
                ]
            ];
        }

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ["owner", this[OWNER]],
                ["name", this[NAME]],
                ["membershipType", this[MEMBERSHIP_TYPE]],
                ["translated", this[TRANSLATED]],
                ["type", this[TYPE]],
                ["sourceMember", this[SOURCE_MEMBER]],
                ["required", this.required]
            ];
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

        get fullName() {
            if (this[OWNER]) {
                if (this[MEMBERSHIP_TYPE] == pkg.membershipTypes.member) {
                    return `${this[OWNER].fullName}.${this[NAME]}`;
                }
                else if (this[MEMBERSHIP_TYPE] == pkg.membershipTypes.collectionItems) {
                    return `${this[OWNER].fullName}.items`;
                }
            }
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

        getObjectValue(object, language = null, index = null) {
            let value = object[this.name];
            if (index !== null && index !== undefined) {
                value = value[index];
            }
            if (language && this.translated) {
                value = value[language];
            }
            return value;
        }

        fromJSONValue(value) {
            return value;
        }

        toJSONValue(value) {
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

        translateValue(value, params = null) {
            if (value === undefined || value === null || value === "") {
                return this.translate(".none");
            }
            else if (this.enumeration && this.translatableEnumeration) {
                return this.translate(".values." + value);
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

        sameValue(value1, value2) {
            return value1 == value2;
        }
    }

    cocktail.schema.Member.prototype.descriptive = false;
    cocktail.schema.Member.prototype.translated = false;
    cocktail.schema.Member.prototype.defaultValue = null;
    cocktail.schema.Member.prototype.translatableEnumeration = true;

    cocktail.schema.Schema = class Schema extends cocktail.schema.Member {

        constructor(parameters = null) {
            super(parameters);
            this[DERIVED_SCHEMAS] = [];
        }

        [cocktail.ui.CONSOLE_CHILDREN](config) {

            const membersDict = {};
            const ownMembersDict = {};

            for (let member of this.members()) {
                membersDict[member.name] = member;
                if (member.owner === this) {
                    ownMembersDict[member.name] = member;
                }
            }

            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["base", this[BASE]],
                    ["members", membersDict],
                    ["ownMembers", ownMembersDict]
                ]
            ];
        }

        static declare(parameters) {
            let schema = new this(parameters);
            cocktail.setVariable(schema.name, schema);
            schemasByName[schema.name] = schema;
            if (schema.base) {
                schema.base[DERIVED_SCHEMAS].push(schema);
            }
            return schema;
        }

        get localName() {
            let name = this.name;
            if (name) {
                let dot = name.lastIndexOf(".");
                if (dot != -1) {
                    name = name.substr(dot + 1);
                }
            }
            return name;
        }

        getId(record) {
            if (this.primaryMember && record) {
                return record[this.primaryMember.name];
            }
            return undefined;
        }

        getInstance(id, options = null) {
            let dataSource = this.dataSource;
            return dataSource ? dataSource.loadObject(id, options) : undefined;
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
                if (value instanceof Array) {
                    for (let member of value) {
                        this.addMember(member);
                    }
                }
                else {
                    for (let name in value) {
                        let member = value[name];
                        member[NAME] = name;
                        this.addMember(member);
                    }
                }
            }
            else {
                super.applyParameter(key, value);
            }
        }

        get base() {
            return this[BASE];
        }

        *ascendInheritance(includeSelf = true) {
            let schema = includeSelf ? this : this[BASE];
            while (schema) {
                yield schema;
                schema = schema[BASE];
            }
        }

        get derivedSchemas() {
            return this[DERIVED_SCHEMAS];
        }

        *schemaTree(includeSelf = true) {
            if (includeSelf) {
                yield this;
            }
            for (let child of this[DERIVED_SCHEMAS]) {
                yield* child.schemaTree();
            }
        }

        isSchema(schema) {
            let ancestor = this;
            while (ancestor) {
                if (ancestor === schema) {
                    return true;
                }
                ancestor = ancestor[BASE];
            }
            return false;
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

        *orderedMembers(recursive = true) {
            if (!this.membersOrder) {
                yield* this.members(recursive);
            }
            else {
                let memberMap = {};
                for (let member of this.members(recursive)) {
                    memberMap[member.name] = member;
                }
                for (let key of this.membersOrder) {
                    let member = memberMap[key];
                    if (member) {
                        yield member;
                    }
                }
            }
        }

        getMember(name) {
            let member = null;
            for (let schema = this; !member && schema; schema = schema[BASE]) {
                member = schema[MEMBER_MAP].get(name);
            }
            return member;
        }

        get primaryMember() {
            return this[PRIMARY_MEMBER] || (this[BASE] && this[BASE].primaryMember);
        }

        requireMember(name) {
            let member = this.getMember(name);
            if (!member) {
                throw new cocktail.schema.MemberNotFoundError(this, name);
            }
            return member;
        }

        addMember(member) {

            claimMember(this, member, pkg.membershipTypes.member);

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
                this[PRIMARY_MEMBER] = member;
            }

            if (member.descriptive) {
                this.descriptiveMember = member;
            }

            return member;
        }

        translate(suffix = "") {
            return (
                super.translate(suffix)
                || (this[BASE] && this[BASE].translate(suffix))
                || ""
            );
        }

        translateValue(value, params = null) {
            if (value && this.descriptiveMember) {
                let descriptiveValue = value[this.descriptiveMember.name];
                if (descriptiveValue && this.descriptiveMember.translated) {
                    descriptiveValue = descriptiveValue[cocktail.getLanguage()];
                }
                return this.descriptiveMember.translateValue(descriptiveValue, params);
            }
            else {
                return super.translateValue(value, params);
            }
        }

        copyAttribute(copy, key, value, parameters) {
            if (key == "membersOrder") {
                copy.membersOrder = value ? Array.from(value) : value;
            }
            else if (key == MEMBER_MAP) {

                let members = parameters && parameters[pkg.MEMBERS] || this.members();
                let generalParameters = parameters ? parameters[pkg.PARAMETERS] : null;
                let memberParameters = parameters ? parameters[pkg.MEMBER_PARAMETERS] : null;

                for (let sourceMember of members) {

                    if (typeof(sourceMember) == "string") {
                        sourceMember = this.requireMember(sourceMember)
                    }

                    let targetMember;
                    let copyParams = Object.assign(
                        {},
                        generalParameters,
                        memberParameters && memberParameters[sourceMember.name]
                    );
                    targetMember = sourceMember.copy(copyParams);
                    copy.addMember(targetMember);
                }
            }
            else if (key != BASE && key != "descriptiveMember") {
                super.copyAttribute(copy, key, value, parameters);
            }
        }

        get translated() {
            for (let member of this.members()) {
                if (member.translated) {
                    return true;
                }
            }
            return false;
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

        fromJSONValue(value) {

            const record = {};

            for (let propName of Reflect.ownKeys(value)) {
                let member = this.getMember(propName);
                let propValue = value[propName];
                if (member) {
                    if (member.translated) {
                        let propProcValue = {};
                        for (let language in propValue) {
                            propProcValue[language] = member.fromJSONValue(propValue[language]);
                        }
                        propValue = propProcValue;
                    }
                    else {
                        propValue = member.fromJSONValue(propValue);
                    }
                }
                record[propName] = propValue;
            }

            record._class = this;
            return record;
        }

        toJSONValue(value, parameters = null) {
            let record = Object.assign({}, value);
            record._class = this.originalMember.fullName;
            for (let member of this.members()) {
                if (!parameters || !parameters.includeMember || parameters.includeMember(member)) {
                    let memberValue = value[member.name];
                    const memberParameters = parameters && parameters.getMemberParameters ? parameters.getMemberParameters(member) : null;
                    if (member.translated) {
                        let exportedValue = {};
                        for (let language in memberValue) {
                            exportedValue[language] = member.toJSONValue(memberValue[language], memberParameters);
                        }
                        memberValue = exportedValue;
                    }
                    else {
                        memberValue = member.toJSONValue(memberValue, memberParameters);
                    }
                    record[member.name] = memberValue;
                }
                else {
                    delete record[member.name];
                }
            }
            return record;
        }

        *diff(obj1, obj2, params = null) {

            for (let member of this.members()) {

                if (params && params.includeMember) {
                    if (!params.includeMember(member)) {
                        continue;
                    }
                }

                const value1 = obj1[member.name];
                const value2 = obj2[member.name];

                if (member.translated) {
                    const languages = new Set();

                    if (value1) {
                        for (let lang in value1) {
                            languages.add(lang);
                        }
                    }

                    if (value2) {
                        for (let lang in value2) {
                            languages.add(lang);
                        }
                    }

                    for (let lang of languages) {
                        const translation1 = value1[lang];
                        const translation2 = value2[lang];
                        if (!member.sameValue(translation1, translation2)) {
                            yield {member, language: lang, value1: translation1, value2: translation2};
                        }
                    }
                }
                else if (!member.sameValue(value1, value2)) {
                    yield {member, language: null, value1, value2};
                }
            }
        }
    }

    {
        const DESCRIPTIVE_MEMBER = Symbol.for("cocktail.schema.Schema.DESCRIPTIVE_MEMBER");

        Object.defineProperty(
            cocktail.schema.Schema.prototype,
            "descriptiveMember",
            {
                get() {
                    return this[DESCRIPTIVE_MEMBER] || (this[BASE] && this[BASE].descriptiveMember);
                },
                set(value) {
                    this[DESCRIPTIVE_MEMBER] = value;
                }
            }
        );
    }

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

        translateValue(value, params = null) {
            if (value !== null && value !== undefined) {
                return cocktail.ui.translations[
                    "cocktail.schema.Boolean.instance." + (value ? "true" : "false")
                ];
            }
            else {
                return super.translateValue(value, params);
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

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["min", this.min],
                    ["max", this.max]
                ]
            ];
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

        get relatedType() {
            return this.type;
        }

        get relatedEnd() {
            if (this.relatedKey && this.relatedType) {
                return this.relatedType.getMember(this.relatedKey);
            }
            return null;
        }

        get dataSource() {
            return this[DATA_SOURCE] || this.type && this.type.dataSource;
        }

        set dataSource(value) {
            this[DATA_SOURCE] = value;
        }

        translateValue(value, params = null) {

            const type = params && params.type || this.type;

            if (value && type) {
                return type.translateValue(value, params);
            }

            return super.translateValue(value, params);
        }

        parseValue(value) {
            let type = this.type;
            if (type) {
                let primaryMember = type.primaryMember;
                if (primaryMember) {
                    return new Promise((resolve, reject) => {
                        Promise.resolve(primaryMember.parseValue(value))
                            .then((id) => {
                                if (id === undefined) {
                                    resolve(undefined);
                                }
                                else {
                                    type.getInstance(id)
                                        .then(resolve)
                                        .catch(reject);
                                }
                            })
                            .catch(reject)
                    });
                }
            }
            return undefined;
        }

        serializeValue(value) {
            if (!value) {
                return "";
            }
            else {
                if (!this.type) {
                    throw new cocktail.schema.SerializationError(this, value, "no type defined for this member");
                }

                if (typeof(value) != "object") {
                    return String(value);
                }

                let id = this.type.getId(value);
                if (id === undefined) {
                    throw new cocktail.schema.SerializationError(this, value, `${this.type.name} can't produce an ID for ${value}`);
                }

                return String(id);
            }
        }

        fromJSONValue(value) {
            return pkg.objectFromJSONValue(value, this.relatedType);
        }

        toJSONValue(value, parameters = null) {
            if (value) {
                if (typeof(value) == "object") {
                    if (
                        this.integral
                        || (this.membershipType == pkg.membershipTypes.collectionItems && this.owner && this.owner.integral)
                        || (parameters && parameters.expandReferences)
                    ) {
                        const type = value._class;
                        value = type.toJSONValue(value, parameters);
                    }
                    else {
                        value = value[this.type.primaryMember.name];
                    }
                }
            }
            return value;
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

        sameValue(value1, value2) {
            return this.type.getId(value1) == this.type.getId(value2);
        }
    }

    cocktail.schema.Collection = class Collection extends cocktail.schema.Member {

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["items", this[ITEMS]],
                    ["relatedType", this.relatedType],
                    ["min", this.min],
                    ["max", this.max]
                ]
            ];
        }

        get relatedType() {
            return this.items && this.items.relatedType;
        }

        get relatedEnd() {
            if (this.relatedKey && this.relatedType) {
                return this.relatedType.getMember(this.relatedKey);
            }
            return null;
        }

        get items() {
            return this[ITEMS];
        }

        set items(value) {
            if (typeof(value) == "string") {
                value = new cocktail.schema.Reference({type: value});
            }
            claimMember(this, value, pkg.membershipTypes.collectionItems);
            this[ITEMS] = value;
        }

        copyAttribute(copy, key, value, parameters) {
            if (key == ITEMS && value) {
                value = value.copy();
                claimMember(copy, value, pkg.membershipTypes.collectionItems);
            }
            super.copyAttribute(copy, key, value, parameters);
        }

        translateValue(value, params = null) {
            if (this.items && value) {
                let items = [];
                for (let item of value) {
                    items.push(this.items.translateValue(item, params));
                }
                return items.join(", ");
            }
            else {
                return super.translateValue(value, params);
            }
        }

        parseValue(value) {
            let values = [];
            let promised = false;
            for (let item of this.splitValue(value)) {
                let parsedItem = this.items.parseValue(item);
                values.push(parsedItem);
                promised = promised || parsedItem instanceof Promise;
            }
            return promised ? Promise.all(values) : values;
        }

        serializeValue(value) {
            if (!value) {
                return "";
            }
            return this.joinValue(
                Array.from(value, item => this.items.serializeValue(item))
            );
        }

        fromJSONValue(value) {
            if (value && this[ITEMS]) {
                return value.map((item) => this[ITEMS].fromJSONValue(item));
            }
            return value;
        }

        toJSONValue(value, parameters = null) {
            if (value === undefined || value === null) {
                return null;
            }
            let items = this.items;
            if (items) {
                return Array.from(value, (item) => items.toJSONValue(item, parameters));
            }
            else {
                return Array.from(value);
            }
        }

        splitValue(value) {
            if (value.trim() == "") {
                return [];
            }
            return value.split(this.stringSeparator);
        }

        joinValue(value) {
            if (!(value instanceof Array)) {
                value = Array.from(value);
            }
            return value.join(this.stringGlue);
        }

        get dataSource() {
            return this[DATA_SOURCE] || this.items && this.items.dataSource;
        }

        set dataSource(value) {
            this[DATA_SOURCE] = value;
        }

        sameValue(value1, value2) {

            if (!(value1 instanceof Array)) {
                value1 = Array.from(value1);
            }

            if (!(value2 instanceof Array)) {
                value2 = Array.from(value2);
            }

            if (value1.length != value2.length) {
                return false;
            }

            for (let i = 0; i < value1.length; i++) {
                if (!this.items.sameValue(value1[i], value2[i])) {
                    return false;
                }
            }

            return true;
        }
    }

    cocktail.schema.Collection.prototype.defaultValue = () => [];
    cocktail.schema.Collection.prototype.stringSeparator = /\s+/;
    cocktail.schema.Collection.prototype.stringGlue = " ";

    cocktail.schema.Mapping = class Mapping extends cocktail.schema.Member {

        fromJSONValue(value) {
            if (value && this.keys && this.values) {
                var items = new Map();
                for (let [k, v] of value) {
                    items.set(
                        this.keys.fromJSONValue(k),
                        this.values.fromJSONValue(v)
                    );
                }
                return items;
            }
            return value;
        }

        toJSONValue(value) {
            if (value && this.keys && this.values) {
                var obj = {};
                for (let [k, v] of value) {
                    obj[this.keys.toJSONValue(k)] = this.values.toJSONValue(v);
                }
                return obj;
            }
            return value;
        }

        translateValue(value, params = null) {

            var items = [];

            if (value) {
                for (let [k, v] of value.entries()) {
                    if (this.keys) {
                        k = this.keys.translateValue(k);
                    }
                    if (this.values) {
                        v = this.values.translateValue(v);
                    }
                    items.push(`${k}: ${v}`);
                }
            }

            return items.join(", ");
        }
    }

    cocktail.schema.Mapping.prototype.keys = null;
    cocktail.schema.Mapping.prototype.values = null;

    cocktail.schema.Tuple = class Tuple extends cocktail.schema.Member {

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["items", this.items]
                ]
            ];
        }

        fromJSONValue(value) {
            if (value && this.items) {
                const tuple = [];
                for (var i = 0; i < value.length && i < this.items.length; i++) {
                    tuple.push(this.items[i].fromJSONValue(value[i]));
                }
                return tuple;
            }
            return value;
        }

        toJSONValue(value) {
            if (value) {
                const tuple = [];
                for (var i = 0; i < value.length && i < this.items.length; i++) {
                    tuple.push(this.items[i].toJSONValue(value[i]));
                }
                return tuple;
            }
            return value;
        }

        sameValue(value1, value2) {

            if (!(value1 instanceof Array)) {
                value1 = Array.from(value1);
            }

            if (!(value2 instanceof Array)) {
                value2 = Array.from(value2);
            }

            if (value1.length != value2.length) {
                return false;
            }

            for (let i = 0; i < value1.length; i++) {
                if (!this.items.sameValue(value1[i], value2[i])) {
                    return false;
                }
            }

            return true;
        }
    }

    cocktail.schema.Tuple.prototype.items = [];

    const JSDate = Date;

    cocktail.schema.Date = class Date extends cocktail.schema.Member {

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["min", this.min],
                    ["max", this.max]
                ]
            ];
        }

        parseValue(value) {
            if (value) {
                const date = new JSDate(value);
                if (!isNaN(date)) {
                    return date;
                }
            }
            return value;
        }

        serializeValue(value) {
            if (value) {
                let month = (value.getMonth() + 1).toString();
                if (month.length == 1) {
                    month = "0" + month;
                }
                return (
                    value.getFullYear()
                    + "-"
                    + month
                    + "-"
                    + value.getDate()
                );
            }
            return value;
        }

        fromJSONValue(value) {
            return this.parseValue(value);
        }

        toJSONValue(value) {
            return this.serializeValue(value);
        }

        translateValue(value, params = null) {
            if (!value) {
                return "";
            }
            return value.toLocaleDateString(
                cocktail.getLanguage(),
                {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit"
                }
            );
        }

        sameValue(value1, value2) {
            if (value1 && value2) {
                value1 = new Date(value1);
                value1.setHours(0, 0, 0, 0);
                value2 = new Date(value2);
                value2.setHours(0, 0, 0, 0);
                return value1.getTime() == value2.getTime();
            }
            return super.sameValue(value1, value2);
        }
    }

    cocktail.schema.DateTime = class DateTime extends cocktail.schema.Member {

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["min", this.min],
                    ["max", this.max]
                ]
            ];
        }

        parseValue(value) {
            if (value) {
                const date = new JSDate(value);
                if (!isNaN(date)) {
                    return date;
                }
            }
            return value;
        }

        serializeValue(value) {
            return value ? value.toISOString() : value;
        }

        fromJSONValue(value) {
            return this.parseValue(value);
        }

        toJSONValue(value) {
            return this.serializeValue(value);
        }

        translateValue(value, params = null) {
            if (!value) {
                return "";
            }
            return value.toLocaleDateString(
                cocktail.getLanguage(),
                {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit"
                }
            );
        }

        sameValue(value1, value2) {
            if (value1 && value2) {
                return value1.getTime() == value2.getTime();
            }
            return super.sameValue(value1, value2);
        }
    }

    cocktail.schema.Time = class Time extends cocktail.schema.Member {

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["min", this.min],
                    ["max", this.max]
                ]
            ];
        }
    }

    cocktail.schema.HTML = class HTML extends cocktail.schema.String {
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

        translateValue(value, params = null) {
            if (value) {
                return cocktail.ui.translations["cocktail.locales." + value];
            }
            else {
                return super.translateValue(value, params);
            }
        }
    }

    cocktail.schema.String.prototype.defaultValue = "";

    cocktail.schema.MemberReference = class MemberReference extends cocktail.schema.Member {

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["sourceSchema", this.sourceSchema]
                ]
            ];
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

        fromJSONValue(value) {
            return this.parseValue(value);
        }

        toJSONValue(value) {
            if (value) {
                return value.fullName;
            }
            return value;
        }

        serializeValue(value) {
            if (value) {
                value = value.name;
            }
            return value;
        }

        toJSONValue(value) {
            return this.serializeValue(value);
        }

        translateValue(value, params = null) {
            if (value) {
                return value.translate();
            }
            return super.translateValue(value, params);
        }
    }

    cocktail.schema.SchemaReference = class SchemaReference extends cocktail.schema.Member {

        [cocktail.ui.CONSOLE_CHILDREN](config) {
            return [
                ...super[cocktail.ui.CONSOLE_CHILDREN](config),
                ...[
                    ["classFamily", this.classFamily],
                    ["includeRootSchema", this.includeRootSchema]
                ]
            ];
        }

        getPossibleValues(obj = null) {
            let values = super.getPossibleValues(obj);
            if (!values && this.classFamily) {
                values = new Set(this.classFamily.schemaTree(this.includeRootSchema));
            }
            return values;
        }

        get classFamily() {
            let classFamily = this[CLASS_FAMILY];
            if (typeof(classFamily) == "string") {
                classFamily = (this[CLASS_FAMILY] = pkg.getSchemaByName(classFamily));
            }
            return classFamily;
        }

        set classFamily(value) {
            this[CLASS_FAMILY] = value;
        }

        parseValue(value) {

            if (!value) {
                return null;
            }

            return pkg.getSchemaByName(value);
        }

        serializeValue(value) {
            if (value) {
                value = value.fullName;
            }
            return value;
        }

        fromJSONValue(value) {
            return this.parseValue(value);
        }

        toJSONValue(value) {
            return this.serializeValue(value);
        }

        translateValue(value, params = null) {
            if (value) {
                return value.translate();
            }
            return super.translateValue(value, params);
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
        return [];
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

    cocktail.schema.CodeBlock = class CodeBlock extends cocktail.schema.String {
    }

    cocktail.schema.addLocale = function (object, schema, locale) {
        for (let member of schema.members()) {
            if (member.translated) {
                let value = object[member.name];
                if (value === undefined || value === null) {
                    value = {};
                }
                if (typeof(value) == "object" && !(locale in value)) {
                    value[locale] = member.getDefaultValue(object, locale);
                }
            }
            else if (member instanceof cocktail.schema.Collection) {
                if (member.items && member.items instanceof cocktail.schema.Reference && member.items.type) {
                    let value = object[member.name];
                    if (value) {
                        for (let item of value) {
                            cocktail.schema.addLocale(item, member.items.type, locale);
                        }
                    }
                }
            }
            else if (member instanceof cocktail.schema.Reference && member.type) {
                let value = object[member.name];
                if (value && typeof(value) == "object") {
                    cocktail.schema.addLocale(value, member.type, locale);
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

    cocktail.schema.SerializationError = class ReferenceSerializationError extends cocktail.schema.Error {

        constructor(member, value, reason = "") {
            super();
            this.member = member;
            this.value = value;
            this.reason = reason;
        }

        toString() {
            let desc = `Can't serialize value ${this.value} for member ${this.member}`;
            if (this.reason) {
                desc += ` (${this.reason})`;
            }
            return desc;
        }
    }
}

