#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from zodbupdate.update import Updater
from cocktail.modeling import (
    ListWrapper,
    DictWrapper,
    OrderedSet,
    OrderedDict
)
from cocktail.events import Event, when
from cocktail.typemapping import TypeMapping
from cocktail.pkgutils import resolve, import_object, get_full_name
from cocktail.styled import styled
from cocktail.persistence import PersistentSet, datastore
from cocktail.persistence.utils import is_broken

DATASTORE_KEY = "cocktail.persistence.migration_steps"

migration_steps = DictWrapper(OrderedDict())

def migrate(verbose = False, commit = False):
    """Executes all migration steps that haven't been executed yet, in the
    correct order.

    :param verbose: When set to True, migration steps will print out
        informative messages of their progress.
    :type verbose: bool
    """
    for step in migration_steps.values():
        step.execute(verbose = verbose, commit = commit)

def mark_all_migrations_as_executed():
    """Flags all migration steps as already executed."""
    for step in migration_steps.values():
        step.mark_as_executed()

def migration_step(func=None, before=None, after=None):
    """A decorator to quickly define function based migrations."""

    if func:
        if before and after:
            raise ValueError(
                "Can't specify both 'before' and 'after' parameters when "
                "registering a migration step"
            )

        step = MigrationStep(get_full_name(func))
        step.executing.append(func)

        if before:
            before.require(step)
        elif after:
            step.require(after)

        return step

    def decorator(func):
        return migration_step(func, before=before, after=after)

    return decorator


class MigrationStep:

    executing = Event()

    step_styles = {"foreground": "bright_green"}
    step_id_styles = {"style": "bold"}

    def __init__(self, id):

        if not id:
            raise ValueError("MigrationStep instances require a non-empty id")

        if id in migration_steps:
            raise KeyError(
                "The migration step id %r is already claimed by another step"
                % id
            )

        migration_steps._items[id] = self

        self.__id = id
        self.__renamed_classes = {}
        self.__class_processors = OrderedDict()
        self.__dependencies = ListWrapper(OrderedSet())
        self.executing.append(self._renaming_handler)
        self.executing.append(self._instance_processing_handler)

    def __repr__(self):
        return "MigrationStep(%r)" % self.__id

    @property
    def id(self):
        """A unique identifier for the migration step."""
        return self.__id

    def execute(self, verbose = False, commit = False):
        """Executes the migration step on the current datastore.

        :param verbose: When set to True, the migration step will print out
            informative messages of its progress.
        :type verbose: bool

        :return: Returns True if the step is actually executed, False if it had
            already been executed and has been skipped.
        :rtype: bool
        """

        # Make sure the step is not executed twice
        if not self.mark_as_executed():
            return False

        # Execute dependencies first
        for dependency in self.dependencies():
            dependency.execute(verbose = verbose)

        # Launch migration logic
        if verbose:
            print("%s%s" % (
                styled("Executing migration step ", **self.step_styles),
                styled(self.__id, **self.step_id_styles)
            ))

        self.executing(verbose = verbose)

        if commit:
            datastore.commit()

        return True

    def mark_as_executed(self):
        """Flags the step as executed.

        :return: True if the step had already been flagged as executed, False
            otherwise.
        :rtype: bool
        """
        applied_steps = datastore.root.get(DATASTORE_KEY)

        if applied_steps is None:
            applied_steps = PersistentSet()
            datastore.root[DATASTORE_KEY] = applied_steps
        elif self.__id in applied_steps:
            return False

        applied_steps.add(self.__id)
        return True

    def mark_as_pending(self):
        """Flags the step as not executed.

        This is mostly useful during the implementation of a migration step; if
        the step is executed and committed, but later on it is found to have a
        flaw or bug, this allows to indicate that the step should be run on the
        next migration execution.

        :return: True if the step had been executed and has had its state
            reset to pending; False otherwise.
        :rtype: bool
        """
        applied_steps = datastore.root.get(DATASTORE_KEY)

        if applied_steps and self.__id in applied_steps:
            applied_steps.remove(self.__id)
            return True

        return False

    def dependencies(self, recursive = False):
        """Iterates over the dependencies of the migration step.

        :param recursive: Set to True to calculate dependencies recursively;
            False limits the return value to a shallow search.

        :return: An iterable sequence of those `MigrationStep` instances that
            must be executed before this step can be safely executed.
        """
        for dependency in self.__dependencies:

            if recursive:
                for recursive_dependency in dependency.dependencies(True):
                    yield recursive_dependency

            yield dependency

    def require(self, dependency):
        """Adds a dependency on another migration step.

        :param dependency: The migration step to add as a dependency. If given
            as a string.

        :type dependency: `MigrationStep` or str
        """
        if isinstance(dependency, str):
            dependency = migration_steps[dependency]

        self.__dependencies._items.append(dependency)

    @classmethod
    def _renaming_handler(cls, e):
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
                    in step.__renamed_classes.items()
                )
            )
            updater()

            root = datastore.root

            # Rename indexes
            for key in list(root.keys()):
                for old_name, new_name in step.__renamed_classes.items():
                    if key == old_name + "-keys":
                        root[new_name + "-keys"] = root[key]
                        del root[key]
                    elif key.startswith(old_name + "."):
                        root[new_name + key[len(old_name):]] = root[key]
                        del root[key]

    @classmethod
    def _instance_processing_handler(cls, e):
        step = e.source
        root = datastore.root
        for cls, processors in step.__class_processors.items():
            for instance in resolve(cls).select():
                for processor in processors:
                    processor(instance)

    def rename_class(self, old_name, new_name):
        self.__renamed_classes[old_name] = new_name

    def process_instances(self, cls, func):
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

        if isinstance(member, str):
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

    def rename_member(self, cls, old_name, new_name, translated = False):

        old_key = "_" + old_name
        new_key = "_" + new_name

        def rename(obj):
            try:
                old_value = getattr(obj, old_key)
            except AttributeError:
                pass
            else:
                setattr(obj, new_key, old_value)
                delattr(obj, old_key)

        if translated:
            @self.processor(cls)
            def process(instance):
                for trans in instance.translations.values():
                    rename(trans)
        else:
            self.process_instances(cls, rename)

    def remove_member(self, member, translated = False):

        member = self._resolve_member(member)

        if translated:
            @self.processor(member.schema)
            def process(instance):
                key = "_" + member.name
                for trans in instance.translations.values():
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
            for trans in instance.translations.values():
                delattr(trans, key)

