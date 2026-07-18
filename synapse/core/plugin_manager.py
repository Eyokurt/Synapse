import importlib
import logging
from typing import Any

from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self, tool_registry: ToolRegistry, event_bus: EventBus) -> None:
        self.tool_registry = tool_registry
        self.event_bus = event_bus
        self.loaded_plugins = set()

    def load_plugin(self, module_name: str) -> None:
        if module_name in self.loaded_plugins:
            return

        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            logger.error(f"Failed to import plugin {module_name}: {e}")
            raise ValueError(f"Plugin module {module_name} not found") from e

        if not hasattr(module, 'setup') or not callable(module.setup):
            error_msg = f"Plugin {module_name} missing setup(tool_registry, event_bus) function"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        try:
            module.setup(self.tool_registry, self.event_bus)
            self.loaded_plugins.add(module_name)
        except Exception as e:
            logger.error(f"Error during setup of plugin {module_name}: {e}")
            raise ValueError(f"Error initializing plugin {module_name}") from e
