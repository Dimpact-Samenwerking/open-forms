import logging
from typing import TYPE_CHECKING, Iterator, List, Optional

from django.http import HttpRequest

from openforms.plugins.registry import BaseRegistry

if TYPE_CHECKING:  # pragma: no cover
    from openforms.forms.models import Form

    from .base import BasePlugin, LoginInfo  # noqa: F401

logger = logging.getLogger(__name__)


def _iter_plugin_ids(form: Optional["Form"], registry: "Registry") -> Iterator[str]:
    if form is not None:
        yield from form.authentication_backends
    else:
        for plugin in registry.iter_enabled_plugins():
            yield plugin.identifier


class Registry(BaseRegistry["BasePlugin"]):
    """
    A registry for the authentication module plugins.
    """

    module = "authentication"

    def get_options(
        self, request: HttpRequest, form: Optional["Form"] = None
    ) -> List["LoginInfo"]:
        options = list()
        for plugin_id in _iter_plugin_ids(form, self):
            if plugin_id not in self._registry:
                logger.warning(
                    "Plugin %s not found in registry, ignoring it.",
                    plugin_id,
                    extra={"plugin_id": plugin_id, "form": form.pk if form else None},
                )
                continue
            plugin = self._registry[plugin_id]
            info = plugin.get_login_info(request, form)
            options.append(info)
        return options


# Sentinel to provide the default registry. You can easily instantiate another
# :class:`Registry` object to use as dependency injection in tests.
register = Registry()
