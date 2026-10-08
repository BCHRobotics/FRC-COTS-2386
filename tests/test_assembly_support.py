"""Regression checks with Fusion API doubles; run with unittest outside Fusion."""
import importlib
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]


class APIObject:
    @staticmethod
    def cast(value):
        return value


class APIModule(types.ModuleType):
    def __getattr__(self, name):
        return APIObject


def package(name, path):
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module
    return module


# Import the actual add-in modules without Autodesk's runtime or filesystem/network access.
app = MagicMock()
core = APIModule('adsk.core')
core.Application = types.SimpleNamespace(get=lambda: app)
core.Matrix3D = types.SimpleNamespace(create=lambda: object())
fusion = APIModule('adsk.fusion')
fusion.DesignIntentTypes = types.SimpleNamespace(
    AssemblyDesignIntentType=1, HybridDesignIntentType=2, PartDesignIntentType=3)
adsk = package('adsk', ROOT)
adsk.core, adsk.fusion = core, fusion
sys.modules['adsk.core'], sys.modules['adsk.fusion'] = core, fusion
package('addon', ROOT)
commands = package('addon.commands', ROOT / 'commands')
commands.start, commands.stop = MagicMock(), MagicMock()
for command in ['insertPart', 'insertSpacer', 'makeSpacer']:
    package('addon.commands.' + command, ROOT / 'commands' / command)
package('addon.lib', ROOT / 'lib')
futil = types.ModuleType('addon.lib.fusionAddInUtils')
futil.log, futil.add_handler, futil.handle_error = MagicMock(), MagicMock(), MagicMock()
sys.modules[futil.__name__] = futil
database = types.ModuleType('addon.database_thread')
database.myCustomEvent = 'test-database-event'
database.get_sorted_database_list = MagicMock()
database.get_data_file = MagicMock()
sys.modules[database.__name__] = database
config = importlib.import_module('addon.config')
design_utils = importlib.import_module('addon.lib.design_utils')
parts = importlib.import_module('addon.commands.insertPart.entry')
spacers = importlib.import_module('addon.commands.insertSpacer.entry')
make_spacer = importlib.import_module('addon.commands.makeSpacer.entry')
spec = importlib.util.spec_from_file_location('addon.main', ROOT / 'FRC-COTS.py')
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)


class AssemblySupportTests(unittest.TestCase):
    def setUp(self):
        app.reset_mock()
        app.activeProduct = MagicMock(designIntent=1, activeOccurrence=None)
        parts.g_dataFile = types.SimpleNamespace(name='Test part')
        parts.g_active_occ = None
        main.g_dbThread = None
        main.handlers = []
        main.g_palette = None
        futil.handle_error.reset_mock()

    def dialog(self):
        inputs = MagicMock()
        fields = {}
        for method in ['addBoolValueInput', 'addTextBoxCommandInput', 'addSelectionInput']:
            getattr(inputs, method).side_effect = lambda name, *args: fields.setdefault(name, MagicMock())
        command = MagicMock(commandInputs=inputs)
        parts.command_created(types.SimpleNamespace(command=command))
        return fields

    def test_assembly_dialog_requires_link_even_if_config_default_disabled(self):
        with patch.object(config, 'DEFAULT_TO_LINKED_PARTS', False):
            fields = self.dialog()
        self.assertTrue(fields['link_part'].value)
        self.assertFalse(fields['link_part'].isEnabled)
        self.assertIn('assembly_info', fields)

    def test_hybrid_defaults_linked_but_allows_opt_out(self):
        app.activeProduct.designIntent = 2
        fields = self.dialog()
        self.assertTrue(fields['link_part'].value)
        self.assertTrue(fields['link_part'].isEnabled)
        self.assertNotIn('assembly_info', fields)

    def preview(self, intent, linked, occurrence=None):
        app.activeProduct.designIntent = intent
        inserted = occurrence if occurrence is not None else MagicMock()
        app.activeProduct.rootComponent.occurrences.addByInsert.return_value = inserted
        selections = MagicMock(selectionCount=1)
        fields = {'link_part': types.SimpleNamespace(value=linked),
                  'force_flip': types.SimpleNamespace(value=False), 'target_entity': selections}
        inputs = MagicMock()
        inputs.itemById.side_effect = fields.get
        args = types.SimpleNamespace(command=types.SimpleNamespace(commandInputs=inputs), isValidResult=False)
        with patch.object(parts, 'joint_part') as joint:
            parts.command_preview(args)
        return args, joint

    def test_assembly_preview_never_inserts_an_unlinked_copy(self):
        args, joint = self.preview(1, False)
        self.assertTrue(app.activeProduct.rootComponent.occurrences.addByInsert.call_args.args[2])
        joint.assert_called_once()
        self.assertTrue(args.isValidResult)

    def test_hybrid_can_still_insert_an_explicit_unlinked_copy(self):
        args, _ = self.preview(2, False)
        self.assertFalse(app.activeProduct.rootComponent.occurrences.addByInsert.call_args.args[2])
        self.assertTrue(args.isValidResult)

    def test_linked_failure_does_not_fall_back_to_a_copy_or_create_joint(self):
        app.activeProduct.rootComponent.occurrences.addByInsert.return_value = None
        fields = {'link_part': types.SimpleNamespace(value=True),
                  'force_flip': types.SimpleNamespace(value=False),
                  'target_entity': MagicMock(selectionCount=1)}
        inputs = MagicMock()
        inputs.itemById.side_effect = fields.get
        args = types.SimpleNamespace(command=types.SimpleNamespace(commandInputs=inputs), isValidResult=False)
        with patch.object(parts, 'joint_part') as joint:
            parts.command_preview(args)
        joint.assert_not_called()
        self.assertFalse(args.isValidResult)
        self.assertEqual(app.activeProduct.rootComponent.occurrences.addByInsert.call_count, 1)
        self.assertIn('linked part', app.userInterface.messageBox.call_args.args[0])

    def test_library_routes_assembly_spacers_to_linked_part_command(self):
        database.get_sorted_database_list.return_value = [('/', 'Spacer', 'id', '')]
        database.get_data_file.return_value = parts.g_dataFile
        app.userInterface.commandDefinitions.itemById.reset_mock()
        with patch.object(main, 'get_palette', return_value=MagicMock()), \
                patch.object(make_spacer, 'is_dataFile_spacer', return_value=True) as inspect_source:
            main.FRCHTMLHandler().notify(types.SimpleNamespace(action='insertPart', data='{"index": 0}'))
        inspect_source.assert_not_called()
        app.userInterface.commandDefinitions.itemById.assert_called_once_with(config.INSERT_PART_CMD_ID)
        self.assertEqual(parts.g_dataFile.name, 'Test part')
        app.userInterface.commandDefinitions.itemById.return_value.execute.assert_called_once()
        app.userInterface.messageBox.assert_not_called()

    def test_library_keeps_dynamic_spacer_command_for_hybrid(self):
        app.activeProduct.designIntent = 2
        database.get_sorted_database_list.return_value = [('/', 'Spacer', 'id', '')]
        app.userInterface.commandDefinitions.itemById.reset_mock()
        with patch.object(main, 'get_palette', return_value=MagicMock()), \
                patch.object(make_spacer, 'is_dataFile_spacer', return_value=True):
            main.FRCHTMLHandler().notify(types.SimpleNamespace(action='insertPart', data='{"index": 0}'))
        app.userInterface.commandDefinitions.itemById.assert_called_once_with(config.INSERT_SPACER_CMD_ID)

    def test_part_design_is_rejected_before_reading_library_file(self):
        app.activeProduct.designIntent = 3
        database.get_data_file.reset_mock()
        with patch.object(main, 'get_palette', return_value=MagicMock()):
            main.FRCHTMLHandler().notify(types.SimpleNamespace(action='insertPart', data='{"index": 0}'))
        database.get_data_file.assert_not_called()
        self.assertIn('Assembly or Hybrid', app.userInterface.messageBox.call_args.args[0])

    def test_spacer_preview_in_assembly_does_not_attempt_geometry_edits(self):
        args = types.SimpleNamespace(isValidResult=False)
        spacers.command_preview(args)
        self.assertFalse(args.isValidResult)
        app.activeProduct.rootComponent.occurrences.addByInsert.assert_not_called()
        app.activeProduct.timeline.item.assert_not_called()

    def test_both_toolbar_layouts_register_and_clean_up(self):
        panels = {'InsertPanel': MagicMock(), 'InsertAssemblePanel': MagicMock()}
        app.userInterface.workspaces.itemById.return_value.toolbarPanels.itemById.side_effect = panels.get
        for panel in panels.values():
            panel.controls.itemById.return_value = None
        app.isStartupComplete = False
        with patch.object(main, '_ensure_file_paths_exist', return_value=True):
            main.run(None)
        for panel in panels.values():
            panel.controls.addCommand.assert_called_once()
            panel.controls.itemById.return_value = MagicMock()
        main.stop(None)
        for panel in panels.values():
            panel.controls.itemById.return_value.deleteMe.assert_called_once()
        app.userInterface.messageBox.assert_not_called()

    def test_older_fusion_with_only_hybrid_panel_and_no_intent_api(self):
        panel = MagicMock()
        app.userInterface.workspaces.itemById.return_value.toolbarPanels.itemById.side_effect = (
            lambda name: panel if name == 'InsertPanel' else None)
        self.assertEqual(list(main._library_panels()), [panel])
        with patch.object(fusion, 'DesignIntentTypes', None):
            self.assertFalse(design_utils.is_assembly_design(app.activeProduct))
            self.assertFalse(design_utils.is_part_design(app.activeProduct))
            self.assertTrue(design_utils.uses_dynamic_spacer_command(app.activeProduct, True))


if __name__ == '__main__':
    unittest.main()
