import collections
from sqlalchemy import event
from sqlalchemy import exc as sqla_exc
import re


class DuplicateKeyError(Exception):
    """Duplicate entry at unique column error."""

    def __init__(self, columns=None, inner_exception=None, value=None):
        self.columns = columns or []
        self.value = value
        self.inner_exception = inner_exception

    def __str__(self):
        return "Duplicate key for columns %s" % (
            self.columns,
        )


_registry = collections.defaultdict(lambda: collections.defaultdict(list))


def filters(ame, exception_type, regex):
    """Mark a function as receiving a filtered exception."""

    def _receive(fn):
        _registry[ame][exception_type].extend(
            (fn, re.compile(reg))
            for reg in ((regex,) if not isinstance(regex, tuple) else regex)
        )

        return fn
    return _receive


@filters(
    "postgresql",
    sqla_exc.IntegrityError,
    (
            r'^.*duplicate\s+key.*'
            # r'^.*duplicate\s+key.*"(?P<columns>[^"]+)"\s*\n.*'
            # r"Key\s+\((?P<key>.*)\)=\((?P<value>.*)\)\s+already\s+exists.*$",
            # r"^.*duplicate\s+key.*\"(?P<columns>[^\"]+)\"\s*\n.*$",
    ),
)
def _default_dupe_key_error(
        integrity_error, match, engine_name, is_disconnect
):
    columns = match.group("columns")
    uniqbase = "uniq_"
    if not columns.startswith(uniqbase):
        if engine_name == "postgresql":
            columns = [columns[columns.index("_") + 1: columns.rindex("_")]]
        else:
            columns = [columns]
    else:
        columns = columns[len(uniqbase):].split("0")[1:]

    value = match.groupdict().get("value")

    raise DuplicateKeyError(columns, integrity_error, value)


def handler(context):
    """Iterate through available filters and invoke those which match.
    The first one which raises wins.
    """

    def _dialect_registries(engine):
        if engine.dialect.name in _registry:
            yield _registry[engine.dialect.name]
        if "*" in _registry:
            yield _registry["*"]

    for per_dialect in _dialect_registries(context.engine):
        for exc in (context.sqlalchemy_exception, context.original_exception):
            for super_ in exc.__class__.__mro__:
                if super_ in per_dialect:
                    regexp_reg = per_dialect[super_]
                    for fn, regexp in regexp_reg:
                        match = regexp.match(exc.args[0])
                        if match:
                            fn(
                                exc,
                                match,
                                context.engine.dialect.name,
                                context.is_disconnect,
                            )


# https://stackoverflow.com/questions/55133384/make-sqlalchemy-errors-more-user-friendly-and-detailed