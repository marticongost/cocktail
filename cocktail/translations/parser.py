#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from collections import defaultdict
from cocktail.stringutils import normalize_indentation
from cocktail.modeling import arguments


class TranslationsFileParser(object):

    default_case = object()
    encoding = "utf-8"
    tab_width = 4
    value_regexp = re.compile(
        r"^\s*(?P<locale>(\w+|\*)):\s*(?P<value>.*)"
    )
    whitespace_norm_expr = re.compile(r"\s\s+")
    python_string_expr = re.compile(r"""
        (
            "{3}.*?"{3}     # Triple double quotes
          | '{3}.*?'{3}     # Triple single quotes
          | "(\\"|[^"])*"   # Double quotes
          | '(\\'|[^'])*'   # Single quotes
        )
        """, re.VERBOSE
    )

    LITERAL = "l"
    EXPRESSION = "$"
    TRANSLATION_EXPRESSION = "t"

    def __init__(self,
        file,
        file_path = None,
        encoding = None,
        tab_width = None
    ):
        self.__file = file
        self.__file_path = file_path

        if encoding is not None:
            self.encoding = encoding

        if tab_width is not None:
            self.tab_width = tab_width

        self.__node = None
        self.__init_code = None
        self.__multiline_locale = None
        self.__multiline_value = None
        self.__current_line = None
        self.__current_line_number = None

        from .translation import (
            translations,
            get_language
        )

        from .helpers import (
            join,
            either,
            plural2,
            ca_apostrophe,
            ca_possessive,
            ca_possessive_with_article
        )

        self.context = {
            "translations": translations,
            "get_language": get_language,
            "join": join,
            "either": either,
            "plural2": plural2,
            "ca_apostrophe": ca_apostrophe,
            "ca_possessive": ca_possessive,
            "ca_possessive_with_article": ca_possessive_with_article,
            "arguments": arguments,
            "_expr_value": _expr_value
        }

    @property
    def file(self):
        return self.__file

    @property
    def file_path(self):
        return self.__file_path

    @property
    def current_path(self):
        if self.__node:
            return self.__node.path
        else:
            return ""

    @property
    def current_line_number(self):
        return self.__current_line_number

    @property
    def current_line(self):
        return self.__current_line

    def __finish_node(self):

        assert self.__node
        self.__multiline_locale = None

        for definition in self.__node.iter_definitions():
            yield definition

        self.__node = self.__node.parent

    def __iter__(self):

        for n, line in enumerate(self.__file):
            line = line.decode(self.encoding).rstrip()
            self.__current_line = line
            self.__current_line_number = n + 1

            lsline = line.lstrip()
            sline = lsline.rstrip()
            line_indent = (
                line[:len(line) - len(lsline)]
                .replace("\t", " " * self.tab_width)
            )

            # @init directive
            if sline == "@init":
                if self.__node:
                    self._syntax_error(
                        "@init directives can only be attached to the file's root"
                    )
                else:
                    self.__init_code = []

            # @end directive
            elif sline == "@end":
                if self.__init_code is None:
                    self._syntax_error(
                        "@end directive without an @init directive"
                    )
                else:
                    code = normalize_indentation(u"\n".join(self.__init_code))
                    self.__init_code = None
                    self._exec_code(code)

            # @init content
            elif self.__init_code is not None:
                self.__init_code.append(line)

            # @switch directive
            elif sline.startswith("@switch "):

                if not self.__node:
                    self._syntax_error(
                        "@switch directives must be attached to translation "
                        "keys"
                    )

                self.__node.switch_condition = sline[len("@switch "):].strip()
                if not self.__node.switch_condition:
                    self._syntax_error(
                        "@switch directive without an expression"
                    )

            # @case directive
            elif sline.startswith("@case "):

                if (
                    not self.__node
                    or not self.__node.parent
                    or not self.__node.parent.switch_condition
                ):
                    self._syntax_error(
                        "@case directives must be attached to translation "
                        "keys with a @switch directive"
                    )

                self.__node.switch_value = sline[len("@case "):].strip()
                if not self.__node.switch_value:
                    self._syntax_error(
                        "@case directive without an expression"
                    )

                self.__node.parent.switch_cases.append((
                    self.__node.path,
                    self.__node.switch_value
                ))

                if not self.__node.func_args:
                    self.__node.func_args = self.__node.parent.func_args

            # @default directive
            elif sline == "@default":

                if (
                    not self.__node
                    or not self.__node.parent
                    or not self.__node.parent.switch_condition
                ):
                    self._syntax_error(
                        "@default directives must be attached to translation "
                        "keys with a @switch directive"
                    )

                self.__node.switch_value = self.default_case

                self.__node.parent.switch_cases.append((
                    self.__node.path,
                    self.__node.switch_value
                ))

                if not self.__node.func_args:
                    self.__node.func_args = self.__node.parent.func_args

            # @reuse directive
            elif sline.startswith("@reuse "):

                if not self.__node:
                    self._syntax_error(
                        "@reuse directives must be attached to translation "
                        "keys"
                    )

                self.__node.reused_key = sline[len("@reuse "):].strip()
                if not self.__node.reused_key:
                    self._syntax_error(
                        "@reuse directive without a key to reuse"
                    )

                if not self.__node.func_args:
                    self.__node.func_args = "*args, **kwargs"

            # Keys
            elif len(lsline) > 2 and lsline[0] == "[" and lsline[-1] == "]":

                while self.__node and line_indent <= self.__node.indent:
                    for definition in self.__finish_node():
                        yield definition

                key = lsline[1:-1]
                pos = key.find("(")
                if pos == -1:
                    func_args = ""
                else:
                    if key[-1] != ")":
                        self._syntax_error(
                            "Missing closing parenthesis on parameter list"
                        )
                    else:
                        func_args = key[pos + 1:-1]
                        key = key[:pos]

                self.__node = TranslationsFileNode(
                    self,
                    key = key,
                    indent = line_indent,
                    func_args = func_args,
                    parent = self.__node
                )

            # Values
            else:
                match = self.value_regexp.match(line)
                if match and (
                    not self.__multiline_locale
                    or line_indent <= self.__node.indent
                ):
                    locale = match.group("locale")
                    locale_value = match.group("value")
                    if locale_value:
                        self.__node.definitions[locale].append(locale_value)
                    else:
                        self.__multiline_locale = locale
                elif self.__multiline_locale is not None:
                    self.__node \
                        .definitions[self.__multiline_locale] \
                        .append(line + "\n")
                elif lsline:
                    self._syntax_error(
                        "Content can't be parsed. Expected a translation "
                        "key/value or a directive."
                    )

        if self.__init_code is not None:
            self._syntax_error(
                "@init directive without an @end directive"
            )

        while self.__node:
            for definition in self.__finish_node():
                yield definition

    def _iter_expressions(self, code):

        i = 0
        start = 0
        depth = 0
        strlen = len(code)
        prevc = None
        expr_type = None

        def escaped(n = 0):
            index = i + n - 1
            if index >= 0:
                c1 = code[index]
                c2 = None if index is 0 else code[index - 1]
                return c1 == "\\" and c2 != "\\"
            else:
                return False

        while i < strlen:

            c = code[i]

            if not depth and c == "\\" and not escaped():
                if i != start and i - 1 > start:
                    yield code[start:i - 1], self.LITERAL
                i += 1
                start = i

            elif c == "{" and not escaped(-1):

                if not depth and prevc in "$t":
                    if i != start and i - 1 > start:
                        yield code[start:i - 1], self.LITERAL

                    depth += 1
                    start = i + 1
                    expr_type = prevc

                elif depth:
                    depth += 1

                i += 1

            elif c == "}":
                depth -= 1

                if not depth:
                    if i > start:
                        yield code[start:i], expr_type
                    expr_type = None
                    start = i + 1

                i += 1

            else:
                match = self.python_string_expr.match(code, i)
                if match:
                    i = match.end()
                else:
                    i += 1

            prevc = c

        if i != start:
            yield code[start:], self.LITERAL

    def _get_expression(self, value):

        clean_value = value.strip()
        clean_value = self.whitespace_norm_expr.sub(" ", clean_value)
        parts = list(self._iter_expressions(clean_value))

        if not parts:
            self._syntax_error("Empty expression")

        is_constant = len(parts) == 1 and parts[0][1] == self.LITERAL

        if is_constant:
            value = parts[0][0]
        else:
            func_name = self.__node.func_name
            func_args = self.__node.func_args
            code = "def %s(%s):\n    return " % (func_name, func_args)
            glue = ""
            for part_value, part_type in parts:
                code += glue
                if part_type == self.LITERAL:
                    code += 'u"%s"' % part_value.replace('"', '\\"')
                elif part_type == self.EXPRESSION:
                    code += "_expr_value(" + part_value + ")"
                elif part_type == self.TRANSLATION_EXPRESSION:
                    code += u"translations(%s)" % part_value
                glue = " + "

            context = self._exec_code(code, copy_context = True)
            value = context[func_name]

        return value

    def _exec_code(self, code, copy_context = False):
        code_obj = compile(
            code,
            "<%s>" % self.__file_path or "?",
            "exec"
        )
        if copy_context:
            context = self.context.copy()
            context["key"] = self.__node.path
        else:
            context = self.context
        exec code_obj in context
        return context

    def _syntax_error(self, reason = None):
        raise TranslationsFileSyntaxError(
            self.__file_path,
            self.__current_line,
            self.__current_line_number,
            reason
        )


class TranslationsFileNode(object):

    def __init__(self, parser, key, indent, func_args = None, parent = None):
        self.parser = parser
        self.key = key
        self.indent = indent
        self.parent = parent
        self.path = key if parent is None else parent.path + "." + key
        self.func_args = func_args
        self.switch_condition = None
        self.switch_value = None
        self.switch_cases = []
        self.reused_key = None
        self.definitions = defaultdict(list)

    @property
    def func_name(self):
        return self.path.replace(".", "__")

    def iter_definitions(self):

        if self.switch_condition:
            indent = u" " * 4
            code_lines = ["def %s(%s):" % (self.func_name, self.func_args)]
            code_lines.append(u"%s__args, __kwargs = arguments()" % indent)
            code_lines.append(u"%s__value = %s" % (indent, self.switch_condition))

            if len(self.switch_cases) < 2:
                self.parser._syntax_error(
                    "@switch directives must contain 2+ cases"
                )

            op = "if"
            for case_key, case_value in self.switch_cases:
                if case_value is self.parser.default_case:
                    code_lines.append(u"%selse:\n" % indent)
                else:
                    code_lines.append(u"%s%s __value == %s:\n" % (
                        indent,
                        op,
                        case_value
                    ))
                code_lines.append(
                    u"%sreturn translations('%s', *__args, **__kwargs)" % (
                        indent * 2,
                        case_key
                    )
                )
                op = "elif"

            code = "\n".join(code_lines)
            context = self.parser._exec_code(code, copy_context = True)
            yield (
                self.path,
                None,
                context[self.func_name]
            )
        elif self.reused_key:
            code = (
                "def %s(*args, **kwargs):\n"
                "    return translations(%s, *args, **kwargs)"
                % (
                    self.func_name,
                    self.reused_key
                )
            )
            context = self.parser._exec_code(code, copy_context = True)
            yield (
                self.path,
                None,
                context[self.func_name]
            )
        else:
            for locale, values in self.definitions.iteritems():
                yield (
                    self.path,
                    None if locale == "*" else locale,
                    self.parser._get_expression(u"\n".join(values))
                )


class TranslationsFileSyntaxError(Exception):

    def __init__(self, file_path, line, line_number, reason = None):
        Exception.__init__(
            self,
            "Syntax error in translations file %s at line %d: %s)"
            % (
                file_path or "<?>",
                line_number,
                line.strip().encode("utf-8")
            )
            + (". " + reason if reason else "")
        )
        self.file_path = file_path
        self.line = line
        self.line_number = line_number
        self.reason = reason


def _expr_value(value):
    return u"" if value is None else unicode(value)

