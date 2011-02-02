#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from zodbupdate.update import Updater
from cocktail.modeling import (
    getter,
    ListWrapper,
    SetWrapper
)
from cocktail.typemapping import TypeMapping
from cocktail.events import EventHub, Event
from cocktail.pkgutils import resolve, import_object
from cocktail.persistence import datastore


class Migration(object):
    
    def __init__(self, migration_id):
        self.__migration_id = migration_id
        self.__step_id = 0
        self.__steps = ListWrapper()

    def __repr__(self):
        return "Migration(%r)" % self.__migration_id

    @getter
    def id(self):
        return self.__migration_id

    @getter
    def steps(self):
        return self.__steps

    def step(self):
        self.__step_id += 1
        step = MigrationStep(self.__step_id)
        self.__steps._items.append(step)
        return step

    @getter
    def version_key(self):
        return "%s.schema_version" % self.id

    def _get_current_version(self):
        return datastore.root.get(self.version_key, 0)

    def _set_current_version(self, value):
        datastore.root[self.version_key] = value

    current_version = property(
        _get_current_version, _set_current_version
    )

    def execute(self, target_version = None, verbose = True):
        if target_version is None:
            if self.__steps:
                target_version = self.__steps[-1].id
            else:
                target_version = 0

        for step in self.__steps[self.current_version:target_version]:
            if verbose:
                print "Updating schema %s to version %s" % (
                    self.version_key,
                    step.id
                )
            step.executing(verbose = verbose)
            self.current_version = step.id

        datastore.commit()


class MigrationStep(object):

    __metaclass__ = EventHub

    executing = Event()

    def __init__(self, id):
        self.__id = id
        self.__renamed_classes = {}
        self.__class_processors = TypeMapping()        
        self.executing.append(self.renaming_handler)
        self.executing.append(self.instance_processing_handler)

    @getter
    def id(self):
        return self.__id

    @classmethod
    def renaming_handler(cls, e):
        step = e.source

        if step.__renamed_classes:
            
            def format_class_name(class_name):
                pos = class_name.rfind(".")
                return "%s %s" % (class_name[:pos], class_name[pos + 1:])

            updater = Updater(
                datastore.storage,
                renames = dict(
                    (format_class_name(old_name),
                     format_class_name(new_name))
                    for old_name, new_name 
                    in step.__renamed_classes.iteritems()
                )
            )
            updater()
            
            root = datastore.root

            # Rename indexes
            for key in list(root.iterkeys()):
                for old_name, new_name in step.__renamed_classes.iteritems():
                    if key == old_name + "-keys":
                        root[new_name + "-keys"] = root[key]
                        del root[key]
                    elif key.startswith(old_name + "."):
                        root[new_name + key[len(old_name):]] = root[key]
                        del root[key]
    
    @classmethod
    def instance_processing_handler(cls, e):        
        step = e.source
        for cls, processors in step.__class_processors.iteritems():
            for instance in cls.select():
                for processor in processors:
                    processor(instance)

    def rename_class(self, old_name, new_name):
        self.__renamed_classes[old_name] = new_name

    def process_instances(self, cls, func):
        cls = resolve(cls)
        class_processors = self.__class_processors.get(cls)
        if class_processors is None:
            class_processors = [func]
            self.__class_processors[cls] = class_processors
        else:
            class_processors.append(func)

    def processor(self, cls):
        def decorator(func):
            self.process_instances(cls, func)
            return func
        return decorator

    def _resolve_member(self, member):
        
        if isinstance(member, basestring):
            last_dot = member.rfind(".")
            
            if last_dot == -1:
                raise ValueError("%s is not a valid member reference" % member)

            class_name = member[:last_dot]
            member_name = member[last_dot + 1:]
            cls = import_object(class_name)
            member = cls.get_member(member_name)

            if member is None:
                raise ValueError(
                    "Can't find member %s in class %s"
                    % (member_name, class_name)
                )

        return member

    def remove_member(self, member, translated = False):
        
        member = self._resolve_member(member)

        if translated:
            @self.processor(member.schema)
            def process(instance):
                key = "_" + member.name
                for trans in instance.translations.itervalues():
                    try:
                        delattr(trans, key)
                    except AttributeError:
                        pass                        
        else:
            @self.processor(member.schema)
            def process(instance):
                key = "_" + member.name
                try:
                    delattr(instance, key)
                except AttributeError:
                    pass

    def translate_member(self, member, languages):

        member = self._resolve_member(member)

        @self.processor(member.schema)
        def process(instance):
            key = "_" + member.name
            try:
                value = getattr(key)
            except AttributeError:
                pass
            else:
                delattr(instance, key)
                for language in languages:
                    instance.set(member, value, language)

    def untranslate_member(self, member, prefered_languages):
        
        member = self._resolve_member(member)
        undefined = object()

        @self.processor(member.schema)
        def process(instance):
            key = "_" + member.name
            for language in prefered_languages:
                trans = instance.translations.get(language)
                if trans is not None:
                    value = getattr(trans, key, undefined)
                    if value is not undefined:
                        instance.set(member, value)
                        break
            for trans in instance.translations.itervalues():
                delattr(trans, key)

cocktail_migration = Migration("cocktail.persistence")
datastore.migrations.append(cocktail_migration)

