#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import gc
from threading import Lock
from cgi import escape
from collections import Counter, OrderedDict
from cocktail.modeling import ListWrapper, SetWrapper, DictWrapper
from cocktail.controllers import Controller

_counts = []
_lock = Lock()


class MemoryMonitorController(Controller):

    def __call__(
        self,
        action = None,
        filter = None,
        max_depth = None,
        ref_index = "0",
        order = "diff",
        **kwargs
    ):
        # Add a new object count
        with _lock:
            if action == "reset":
                del _counts[:]

            if action in ("reset", "update") or not _counts:
                gc.collect()
                new_count = Counter(type(o) for o in gc.get_objects())
                _counts.append(new_count)
            else:
                new_count = _counts[-1]

            counts = list(_counts)

        # Render all counts in a table.
        # Not using a template file is deliverate, to minimize dependencies
        # which could meddle with the object count.
        yield """
            <html>
                <head>
                    <title>Memory monitor</title>
                    <style type="text/css">
                        * {
                            font-family: sans-serif;
                        }
                        .field {
                            margin-bottom: 0.5em;
                        }
                        .field label {
                            display: inline-block;
                            width: 10em;
                            padding-right: 1em;
                            font-size: 0.9em;
                        }
                        input {
                            width: 20em;
                        }
                        button {
                            margin-left: 0.5em;
                        }
                        select {
                            margin-left: 12.2em;
                        }
                        table {
                            font-size: 0.8em;
                            border-collapse: collapse;
                            margin-bottom: 2em;
                        }
                        tr:nth-child(even) td {
                            background-color: #f5f5f5;
                        }
                        th, td {
                            padding: 0.2em 0.8em;
                        }
                        th {
                            text-align: left;
                            border-bottom: 1px solid #ddd;
                        }
                        td.type {
                            text-align: left;
                            font-weight: normal;
                        }
                        a.type {
                            text-decoration: none;
                            color: #1a66d1;
                        }
                        a.type:hover {
                            text-decoration: underline;
                        }
                        td.count {
                            text-align: right;
                        }
                        td.stable,
                        td.incr,
                        td.decr {
                            padding-right: 0;
                            padding-left: 1.2em;
                            text-align: right;
                            font-size: 0.9em;
                            border-left: 1px solid #eee;
                        }
                        td.incr {
                            color: #ae0000;
                        }
                        td.decr {
                            color: #127a00;
                        }
                        td.stable {
                            color: #999;
                        }
                        td.path ul {
                            list-style-type: none;
                            padding: 0;
                            white-space: nowrap;
                            margin: 0;
                        }
                        td.path ul li {
                            display: inline-block;
                            vertical-align: baseline;
                        }
                        td.path ul li + li {
                            margin-left: 0.5em;
                        }
                        td.path ul li + li:before {
                            content: '>';
                            display: inline-block;
                            vertical-align: baseline;
                            margin-right: 0.5em;
                            color: #999;
                        }
                    </style>
                    <script type="text/javascript">
                        window.addEventListener("DOMContentLoaded", function () {

                            var form = document.querySelector("form");

                            var search = form.querySelector("input[type='search']");
                            search.addEventListener("search", function (e) {
                                form.submit();
                            });

                            function autoreload(controlId) {
                                var control = document.getElementById(controlId);
                                if (control) {
                                    control.addEventListener("change", function () {
                                        form.submit();
                                    });
                                }
                            }

                            autoreload("order_selector");
                            autoreload("max_depth_input");
                            autoreload("ref_index_input");
                        });
                    </script>
                </head>
                <body>
                    <form>
                        <div class="field">
                            <label for="search_input">Filter:</label>
                            <input id="search_input" type="search" name="filter" value="%s" autofocus/>
                        </div>
        """ % (filter or "")

        if filter:
            yield """
                        <div class="field">
                            <label for="max_depth_input">Referrers max depth:</label>
                            <input id="max_depth_input" type="number" name="max_depth" value="%s"/>
                        </div>
                        <div class="field">
                            <label for="ref_index_input">Referrers index:</label>
                            <input id="ref_index_input" type="text" name="ref_index" value="%s"/>
                        </div>
            """ % (
                max_depth or "",
                ref_index or ""
            )

        yield """
                        <select id="order_selector" name="order">
                            %s
                        </select>
                        <button name="action" value="update">
                            Update
                        </button>
        """ % (
            "".join(
                (
                    "<option%s value='%s'>Order by %s</option>"
                    % (
                        (" selected" if order == criteria else ""),
                        criteria,
                        criteria
                    )
                )
                for criteria in ("diff", "count", "name")
            )
        )

        yield """
                        <button formmethod="POST" name="action" value="reset">
                            Reset
                        </button>
                    </form>
                    <table id="counts">
                        <thead>
                            <tr>
                                <th class='type'>Type</th>
        """

        for i in range(len(counts)):
            yield "<th class='count' colspan='%d'>#%d</th>\n" % (
                2 if i else 1,
                i + 1
            )

        yield """
                            </tr>
                        </thead>
                    <tbody>
        """

        classes = [cls for cls, count in new_count.most_common()]

        if filter:
            classes = [
                cls for cls in classes
                if any(
                    b.__name__ == filter
                    for b in cls.__mro__
                )
            ]

        if order == "diff" and len(counts) >= 2:
            classes.sort(
                key = lambda cls:
                    (
                        -(new_count.get(cls, 0) - counts[-2].get(cls, 0))
                        or float("inf"),
                        -new_count.get(cls, 0),
                        cls.__name__.lower()
                    )
            )
        elif order == "name":
            classes.sort(key = lambda cls: cls.__name__.lower())
        elif order == "count" or order == "diff" and len(counts) < 2:
            classes.sort(
                key = lambda cls:
                    (-new_count.get(cls), cls.__name__.lower())
            )

        def class_link(class_name):
            return "<a class='type' href='?filter=%s&order=%s'>%s</a>" % (
                class_name,
                order,
                class_name
            )

        for cls in classes:

            class_name = cls.__name__
            yield "<tr>\n"
            yield "<td class='type'>%s</td>\n" % class_link(class_name)

            prev_count = None

            for count in counts:
                cls_count = count.get(cls, 0)

                if prev_count is not None:
                    prev_cls_count = prev_count.get(cls, 0)

                    diff = cls_count - prev_cls_count

                    if diff > 0:
                        diff_class = "incr"
                        diff_value = "+%d" % diff
                    elif diff < 0:
                        diff_class = "decr"
                        diff_value = str(diff)
                    else:
                        diff_class = "stable"
                        diff_value = "-"

                    yield "<td class='%s'>%s</td>" % (diff_class, diff_value)

                yield "<td class='count'>%d</td>" % cls_count

                prev_count = count

            yield "</tr>\n"

        yield "</table>\n"

        if filter and max_depth:
            yield """
                <table id="refs">
                    <thead>
                        <tr>
                            <th class="path">Referrers</th>
                            <th class="count">Count</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            if ref_index:
                try:
                    ref_index = list(map(
                        int,
                        [part.strip() for part in ref_index.split("-")]
                    ))
                except (TypeError, ValueError):
                    pass

            ref_count = self._collect_ref_paths(
                filter,
                max_depth = int(max_depth),
                ref_index = ref_index
            )

            for path, count in ref_count.most_common():
                yield """
                    <tr>
                        <td class='path'><ul>%s</ul></td>
                        <td class='count'>%d</td>
                    </tr>
                """ % (
                    "".join(
                        ("<li>%s</li>" % item)
                        for item in path
                    ),
                    count
                )

            yield """
                    </tbody>
                </table>
            """

        yield """
            </body>
        </html>
        """

    def _collect_ref_paths(
        self,
        class_name,
        ref_index = None,
        max_depth = 10
    ):
        counter = Counter()
        visited = set()

        def _descend(obj, depth = 1, path = ()):

            for referrer in gc.get_referrers(obj):

                referrer_id = id(referrer)
                if referrer_id in visited:
                    continue
                visited.add(referrer_id)

                referrer_desc = escape(self._repr_referrer(referrer))
                referrer_path = path + (referrer_desc,)
                counter[referrer_path] += 1
                if depth < max_depth:
                    _descend(referrer, depth + 1, referrer_path)

        objects = [
            o
            for o in gc.get_objects()
            if any(
                cls.__name__ == class_name
                for cls in type(o).__mro__
            )
        ]

        if ref_index:
            if len(ref_index) == 1:
                try:
                    objects = [objects[ref_index[0]]]
                except IndexError:
                    objects = []
            else:
                objects = objects[ref_index[0]:ref_index[1]]

        for o in objects:
            _descend(o)

        return counter

    opaque_referrer_classes = (
        tuple,
        list,
        dict,
        set,
        frozenset,
        OrderedDict,
        Counter,
        ListWrapper,
        SetWrapper,
        DictWrapper
    )

    def _repr_referrer(self, referrer):
        if (
            isinstance(referrer, self.opaque_referrer_classes)
            or type(referrer).__repr__ is object.__repr__
        ):
            return type(referrer).__name__
        else:
            return repr(referrer)

