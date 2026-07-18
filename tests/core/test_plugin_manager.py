import pytest
import sys
from types import ModuleType
from unittest.mock import MagicMock

from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.core.plugin_manager import PluginManager

@pytest.fixture
def tool_registry():
    return ToolRegistry()

@pytest.fixture
def event_bus():
    return EventBus()

@pytest.fixture
def plugin_manager(tool_registry, event_bus):
    return PluginManager(tool_registry, event_bus)

def test_load_valid_plugin(plugin_manager, tool_registry, event_bus, monkeypatch):
    # Create a dummy module
    module_name = "dummy_plugin"
    dummy_module = ModuleType(module_name)
    
    mock_setup = MagicMock()
    dummy_module.setup = mock_setup
    
    # Inject it into sys.modules
    monkeypatch.setitem(sys.modules, module_name, dummy_module)
    
    plugin_manager.load_plugin(module_name)
    
    mock_setup.assert_called_once_with(tool_registry, event_bus)
    assert module_name in plugin_manager.loaded_plugins

def test_load_plugin_not_found(plugin_manager):
    with pytest.raises(ValueError, match="not found"):
        plugin_manager.load_plugin("non_existent_plugin_xyz")

def test_load_plugin_missing_setup(plugin_manager, monkeypatch):
    module_name = "dummy_plugin_no_setup"
    dummy_module = ModuleType(module_name)
    
    monkeypatch.setitem(sys.modules, module_name, dummy_module)
    
    with pytest.raises(ValueError, match="missing setup"):
        plugin_manager.load_plugin(module_name)

def test_load_plugin_setup_error(plugin_manager, tool_registry, event_bus, monkeypatch):
    module_name = "dummy_plugin_error"
    dummy_module = ModuleType(module_name)
    
    def failing_setup(registry, bus):
        raise RuntimeError("Setup failed")
        
    dummy_module.setup = failing_setup
    monkeypatch.setitem(sys.modules, module_name, dummy_module)
    
    with pytest.raises(ValueError, match="Error initializing"):
        plugin_manager.load_plugin(module_name)
