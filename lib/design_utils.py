"""Design-intent checks compatible with Fusion versions before January 2026."""

import adsk.fusion


def _has_intent(design, name):
    intent_types = getattr(adsk.fusion, 'DesignIntentTypes', None)
    intent = getattr(intent_types, name, None)
    return intent is not None and getattr(design, 'designIntent', None) == intent


def is_assembly_design(design):
    return _has_intent(design, 'AssemblyDesignIntentType')


def is_part_design(design):
    return _has_intent(design, 'PartDesignIntentType')


def uses_dynamic_spacer_command(design, is_spacer):
    # Assembly designs only support external components, not local geometry edits.
    return is_spacer and not is_assembly_design(design)
