bl_info = {
    "name": "ColorPalette Theme Editor",
    "author": "@altangarts",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "Edit > Preferences > Add-ons > ColorPalette Theme Editor",
    "description": "Derives the entire Blender interface theme from a small set of colors and customizes the viewport.",
    "category": "Interface",
}

import bpy
import colorsys
import os

# =============================================================================
# INTERNAL DERIVATION SETTINGS
# =============================================================================

STRUCTURAL_VALUE_DELTAS = {
    # General Body and Panels
    "background":                           {"delta":  0.00, "alpha": 1.00},
    "panel_body":                           {"delta":  0.03, "alpha": 1.00},
    "sub_back":                             {"delta":  0.03, "alpha": 1.00},
    "sub_header":                           {"delta": -0.01, "alpha": 1.00},
    "panel_header":                         {"delta": -0.04, "alpha": 1.00},
    "panel_outline":                        {"delta": -0.04, "alpha": 1.00},

    # Headers
    "editor_header":                        {"delta":  0.13, "alpha": 1.00},
    "side_header":                          {"delta": -0.07, "alpha": 1.00},
    "viewport_header":                      {"delta":  0.00, "alpha": 0.40},

    # Core UI Regions
    "region_back":                          {"delta": -0.03, "alpha": 1.00},
    "navigation_back":                      {"delta": -0.03, "alpha": 1.00},
    "tab_back":                             {"delta": -0.03, "alpha": 1.00},
    "tab_inactive":                         {"delta":  0.05, "alpha": 1.00},
    "tab_active":                           {"delta":  0.15, "alpha": 1.00},

    # Direct Path Regions
    "regions.asset_shelf.back":             {"delta": -0.02, "alpha": 1.00},
    "regions.asset_shelf.header_back":      {"delta": -0.05, "alpha": 1.00},
    "regions.channels.back":                {"delta": -0.03, "alpha": 1.00},
    "regions.scrubbing.back":               {"delta": -0.02, "alpha": 1.00},
    "regions.sidebars.back":                {"delta": -0.015, "alpha": 0.00},
    "regions.sidebars.tab_back":            {"delta": -0.015, "alpha": 0.00},
    "text_editor.line_numbers_background":  {"delta": -0.15, "alpha": 1.00},

    # Shared Grid Definitions Across Editors
    "graph_editor.grid":                    {"delta":  0.40, "alpha": 0.30},
    "nla_editor.grid":                      {"delta":  0.40, "alpha": 0.30},
    "dopesheet_editor.grid":                {"delta":  0.40, "alpha": 0.30},
    "image_editor.grid":                    {"delta":  0.40, "alpha": 0.30},
    "sequence_editor.grid":                 {"delta":  0.40, "alpha": 0.30},
    "node_editor.grid":                     {"delta":  0.40, "alpha": 0.30},
    "node_editor.grid_levels":              {"delta":  0.40, "alpha": 0.30},
    "clip_editor.grid":                     {"delta":  0.40, "alpha": 0.30},

    # Editor Border Line
    "user_interface.editor_border":         {"delta":  0.13, "alpha": 1.00},
    "user_interface.editor_outline": 	    {"delta":  0.13, "alpha": 1.00},

}

WCOL_VALUE_DELTAS = {
    "wcol_regular":     {"inner_delta": -0.10, "outline_delta": -0.00, "inner_alpha": 1.00},
    "wcol_tool":        {"inner_delta":  0.03, "outline_delta": -0.00, "inner_alpha": 1.00},
    "wcol_text":        {"inner_delta":  0.08, "outline_delta": -0.00, "inner_alpha": 1.00},
    "wcol_radio":       {"inner_delta":  0.03, "outline_delta": -0.03, "inner_alpha": 1.00},
    "wcol_toggle":      {"inner_delta": -0.10, "outline_delta": -0.00, "inner_alpha": 1.00},
    "wcol_num":         {"inner_delta":  0.08, "outline_delta": -0.00, "inner_alpha": 1.00},
    "wcol_numslider":   {"inner_delta":  0.08, "outline_delta": -0.00, "inner_alpha": 1.00},
    "wcol_box":         {"inner_delta": -0.05, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_state":       {"inner_delta": -0.10, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_tab":         {"inner_delta": -0.015, "outline_delta": -0.015, "inner_alpha": 1.00},
    "wcol_toolbar_item":{"inner_delta": -0.00, "outline_delta":  0.02, "inner_alpha": 0.40},
    "wcol_scroll":      {"inner_delta": -0.05, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_progress":    {"inner_delta": -0.10, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_list_item":   {"inner_delta": -0.05, "outline_delta": -0.05, "inner_alpha": 1.00},

    # Contrast for option-type widgets
    "wcol_option":      {"inner_delta": -0.18, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_menu":        {"inner_delta":  0.03, "outline_delta": -0.00, "inner_alpha": 1.00},
    "wcol_pulldown":    {"inner_delta": -0.08, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_menu_back":   {"inner_delta": -0.04, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_menu_item":   {"inner_delta": -0.03, "outline_delta": -0.02, "inner_alpha": 1.00},
    "wcol_tooltip":     {"inner_delta": -0.00, "outline_delta": -0.05, "inner_alpha": 1.00},
    "wcol_pie_menu":    {"inner_delta": -0.12, "outline_delta": -0.05, "inner_alpha": 1.00},
}

SHADED_WIDGETS = (
    "wcol_tool", "wcol_radio", "wcol_menu"
)

TEXT_LIGHT = (0.92, 0.92, 0.92, 1.0)
TEXT_DARK = (0.05, 0.05, 0.05, 1.0)
TEXT_WHITE_SELECTED = (1.00, 1.00, 1.00, 1.0)
LUMINANCE_THRESHOLD = 0.5

# Apply Theme button status indicator - plain RGB, edit freely.
STATUS_COLOR_PENDING = (0.80, 0.15, 0.15)   # red: not applied / settings changed since last apply
STATUS_COLOR_APPLIED = (0.15, 0.70, 0.20)   # green: applied and up to date


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def value_shift(rgba, delta, alpha=None):
    r, g, b = rgba[0], rgba[1], rgba[2]
    a = alpha if alpha is not None else (rgba[3] if len(rgba) > 3 else 1.0)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    v = clamp(v + delta)
    nr, ng, nb = colorsys.hsv_to_rgb(h, s, v)
    return (nr, ng, nb, a)


def contrast_pair(rgba):
    r, g, b = rgba[0], rgba[1], rgba[2]
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if luminance > LUMINANCE_THRESHOLD:
        return TEXT_DARK, TEXT_WHITE_SELECTED
    return TEXT_LIGHT, TEXT_WHITE_SELECTED


def derive_palette(base_rgba, interaction_rgba, slider_item_rgba, item_rgba, number_text_rgba,
                    text_field_text_rgba, playhead_rgba, active_editor_outline_rgba, alt_row_alpha):
    r, g, b = base_rgba[0], base_rgba[1], base_rgba[2]
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    if luminance > LUMINANCE_THRESHOLD:
        accent_rgba = (0.0, 0.0, 0.0, 1.0)
        alt_rgb = (0.0, 0.0, 0.0)
    else:
        accent_rgba = (1.0, 1.0, 1.0, 1.0)
        alt_rgb = (1.0, 1.0, 1.0)

    palette = {
        "accent": tuple(accent_rgba),
        "interaction": tuple(interaction_rgba),
        "slider_item": tuple(slider_item_rgba),
        "item": tuple(item_rgba),
        "number_text": tuple(number_text_rgba),
        "text_field_text": tuple(text_field_text_rgba),
        "playhead": tuple(playhead_rgba),
        "user_interface.editor_outline_active": tuple(active_editor_outline_rgba),
        "alt_row": (alt_rgb[0], alt_rgb[1], alt_rgb[2], alt_row_alpha),
        "wcol": {},
    }

    for name, cfg in STRUCTURAL_VALUE_DELTAS.items():
        palette[name] = value_shift(base_rgba, cfg["delta"], alpha=cfg["alpha"])

    palette["text"], palette["text_selected"] = contrast_pair(palette["background"])
    palette["title"], palette["title_hi"] = contrast_pair(palette["panel_header"])

    palette["header_text"], palette["header_text_hi"] = contrast_pair(palette["editor_header"])
    palette["side_header_text"], palette["side_header_text_hi"] = contrast_pair(palette["side_header"])
    palette["viewport_header_text"], palette["viewport_header_text_hi"] = contrast_pair(palette["viewport_header"])

    palette["tab_active_text"], _ = contrast_pair(palette["tab_active"])
    palette["tab_inactive_text"], _ = contrast_pair(palette["tab_inactive"])

    for wname, cfg in WCOL_VALUE_DELTAS.items():
        palette["wcol"][wname] = {
            "inner": value_shift(base_rgba, cfg["inner_delta"], alpha=cfg.get("inner_alpha", 1.0)),
            "outline": value_shift(base_rgba, cfg["outline_delta"]),
            "outline_sel": value_shift(interaction_rgba, cfg["outline_delta"]),
        }

    return palette


# =============================================================================
# USER INTERFACE (ADDON PREFERENCES)
# =============================================================================

def _mark_theme_dirty(self, context):
    self.status_color = STATUS_COLOR_PENDING


def _on_base_color_update(self, context):
    _mark_theme_dirty(self, context)
    if self.border_color_linked:
        self.active_editor_outline_color = value_shift(tuple(self.base_color), 0.13)
    if self.lower_gradient_linked:
        self.viewport_bg_color = value_shift(tuple(self.base_color), -0.01)
    if self.upper_gradient_linked:
        self.viewport_bg_grad = value_shift(tuple(self.base_color), 0.06)
    if self.grid_color_linked:
        self.viewport_grid_color = value_shift(tuple(self.base_color), 0.10)
    if self.grid_major_color_linked:
        self.viewport_grid_major_color = value_shift(tuple(self.base_color), 0.15)


def _on_border_color_update(self, context):
    _mark_theme_dirty(self, context)


def _on_lower_gradient_update(self, context):
    _mark_theme_dirty(self, context)


def _on_upper_gradient_update(self, context):
    _mark_theme_dirty(self, context)


def _on_grid_color_update(self, context):
    _mark_theme_dirty(self, context)


def _on_grid_major_color_update(self, context):
    _mark_theme_dirty(self, context)


def _prop_row(layout, data, prop_name, factor=0.4):
    split = layout.split(factor=factor, align=True)
    split.label(text=data.bl_rna.properties[prop_name].name)
    split.prop(data, prop_name, text="")


def _linked_prop_row(layout, data, prop_name, link_prop_name, factor=0.4):
    """Same as _prop_row but with a chain-icon toggle button next to the
    color field, mirroring the Active Editor Outline link pattern."""
    split = layout.split(factor=factor, align=True)
    split.label(text=data.bl_rna.properties[prop_name].name)
    sub = split.row(align=True)
    sub.prop(data, prop_name, text="")
    linked = getattr(data, link_prop_name)
    sub.prop(data, link_prop_name, text="", icon='LINKED' if linked else 'UNLINKED', toggle=True)


class FCTM_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    base_color: bpy.props.FloatVectorProperty(
        name="Background Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.14, 0.14, 0.16, 1.0), update=_on_base_color_update)

    border_color_linked: bpy.props.BoolProperty(
        name="Link Border Color to Background",
        description="When enabled, the Active Editor Outline color always "
                    "follows the Background Color (+0.15 value shift). Any "
                    "manual edit to the Active Editor Outline color only "
                    "lasts until the Background Color is changed again - it "
                    "gets overwritten at that point. Turn this off (chain "
                    "icon) to fully disconnect the border color instead",
        default=True)

    interaction_color: bpy.props.FloatVectorProperty(
        name="Selected / Interaction Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.41, 0.09, 0.79, 1.0), update=_mark_theme_dirty)

    active_editor_outline_color: bpy.props.FloatVectorProperty(
        name="Active Editor Outline", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.24, 0.24, 0.28, 1.0), update=_on_border_color_update,
        description="Outline color of the currently focused/active editor area "
                    "(User Interface > Editor & Widgets > Active Editor Outline). "
                    "While linked, this is overwritten with a +0.15 value shift "
                    "of the Background Color every time it changes.")

    slider_item_color: bpy.props.FloatVectorProperty(
        name="Value Slider Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.70, 0.35, 0.00, 1.0), update=_mark_theme_dirty)

    item_color: bpy.props.FloatVectorProperty(
        name="Text / Number Field Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.10, 0.10, 0.10, 1.0), update=_mark_theme_dirty,
        description="Color of the 'item' element for wcol_text and wcol_num "
                    "(the text cursor in text fields and the arrows/indicator "
                    "in number fields) - a single shared color for both.")

    number_text_color: bpy.props.FloatVectorProperty(
        name="Number Field Text Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.92, 0.88, 0.00, 1.0), update=_mark_theme_dirty,
        description="Color of the actual number text displayed inside "
                    "wcol_num fields (separate from the generic auto-contrast "
                    "text color and from the item/cursor color above).")

    text_field_text_color: bpy.props.FloatVectorProperty(
        name="Text Field Text Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.00, 0.70, 0.70, 1.0), update=_mark_theme_dirty,
        description="Color of the actual text typed inside wcol_text fields "
                    "(line edits) - separate from the generic auto-contrast "
                    "text color and from the item/cursor color above.")

    playhead_color: bpy.props.FloatVectorProperty(
        name="Playhead (Timeline)", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.85, 0.00, 0.11, 1.0), update=_mark_theme_dirty)

    alt_row_alpha: bpy.props.FloatProperty(
        name="Alternate Row Alpha",
        description="Visibility amount of alternate rows in lists and panels",
        min=0.0, max=1.0, default=0.05, update=_mark_theme_dirty)

    viewport_bg_type: bpy.props.EnumProperty(
        name="Background Type",
        description="Determines the draw style of the 3D Viewport background",
        items=[
            ('SINGLE_COLOR', "Single Color", "Uses a flat, single background color"),
            ('LINEAR', "Linear Gradient", "Uses a smooth two-color vertical gradient"),
            ('RADIAL', "Vignette", "Uses a circular gradient shading from the center")
        ],
        default='LINEAR', update=_mark_theme_dirty
    )

    lower_gradient_linked: bpy.props.BoolProperty(
        name="Link Lower Gradient to Background",
        description="When enabled, the Lower Gradient Color always follows "
                    "the Background Color (-0.05 value shift). Any manual "
                    "edit to the Lower Gradient Color only lasts until the "
                    "Background Color is changed again - it gets overwritten "
                    "at that point. Turn this off (chain icon) to fully "
                    "disconnect the gradient color instead",
        default=True)

    viewport_bg_color: bpy.props.FloatVectorProperty(
        name="Lower Gradient Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.12, 0.12, 0.14, 1.0), update=_on_lower_gradient_update,
        description="Bottom color of the viewport gradient. Also used as the "
                    "flat background color when Background Type is set to "
                    "Single Color. While linked, this is overwritten with a "
                    "-0.05 value shift of the Background Color every time it "
                    "changes.")

    upper_gradient_linked: bpy.props.BoolProperty(
        name="Link Upper Gradient to Background",
        description="When enabled, the Upper Gradient Color always follows "
                    "the Background Color (-0.15 value shift). Any manual "
                    "edit to the Upper Gradient Color only lasts until the "
                    "Background Color is changed again - it gets overwritten "
                    "at that point. Turn this off (chain icon) to fully "
                    "disconnect the gradient color instead",
        default=True)

    viewport_bg_grad: bpy.props.FloatVectorProperty(
        name="Upper Gradient Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.20, 0.20, 0.22, 1.0), update=_on_upper_gradient_update,
        description="Top color of the viewport gradient (Linear or Radial). "
                    "While linked, this is overwritten with a -0.15 value "
                    "shift of the Background Color every time it changes.")

    grid_color_linked: bpy.props.BoolProperty(
        name="Link Grid Color to Background",
        description="When enabled, the Grid Color always follows the "
                    "Background Color (-0.05 value shift). Any manual edit "
                    "to the Grid Color only lasts until the Background Color "
                    "is changed again - it gets overwritten at that point. "
                    "Turn this off (chain icon) to fully disconnect the grid "
                    "color instead",
        default=True)

    viewport_grid_color: bpy.props.FloatVectorProperty(
        name="Grid Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.15, 0.15, 0.15, 1.0), update=_on_grid_color_update,
        description="While linked, this is overwritten with a -0.05 value "
                    "shift of the Background Color every time it changes.")

    grid_major_color_linked: bpy.props.BoolProperty(
        name="Link Major Grid Color to Background",
        description="When enabled, the Major Grid Color always follows the "
                    "Background Color (-0.15 value shift). Any manual edit "
                    "to the Major Grid Color only lasts until the Background "
                    "Color is changed again - it gets overwritten at that "
                    "point. Turn this off (chain icon) to fully disconnect "
                    "the grid color instead",
        default=True)

    viewport_grid_major_color: bpy.props.FloatVectorProperty(
        name="Major Grid Color", subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=(0.20, 0.20, 0.20, 1.0), update=_on_grid_major_color_update,
        description="Color of the major grid lines in the 3D Viewport "
                    "(theme.view_3d.grid_major) - separate from the regular "
                    "grid color above. While linked, this is overwritten "
                    "with a -0.15 value shift of the Background Color every "
                    "time it changes.")

    status_color: bpy.props.FloatVectorProperty(
        name="Status", subtype='COLOR_GAMMA', size=3, min=0.0, max=1.0,
        default=STATUS_COLOR_PENDING,
        description="Plain RGB indicator next to the Apply Theme button: "
                    "red = not applied / out of date, green = applied.")

    has_saved_initial_preset: bpy.props.BoolProperty(
        name="Initial 'ColorPaletteTheme' Preset Saved", default=False,
        description="Internal flag - not shown in the UI. Tracks whether the "
                    "'ColorPaletteTheme' XML preset has already been written "
                    "once, so it is only created on the very first Apply "
                    "and never re-created/overwritten on later Applies.")

    def draw(self, context):
        layout = self.layout

        box_ui = layout.box()
        box_ui.label(text="General Interface Parameters", icon='PREFERENCES')

        col_ui = box_ui.column(align=False)
        _prop_row(col_ui, self, "base_color")
        _prop_row(col_ui, self, "interaction_color")

        border_split = col_ui.split(factor=0.4, align=True)
        border_split.label(text=self.bl_rna.properties["active_editor_outline_color"].name)
        border_sub = border_split.row(align=True)
        border_sub.prop(self, "active_editor_outline_color", text="")
        border_sub.prop(
            self, "border_color_linked", text="",
            icon='LINKED' if self.border_color_linked else 'UNLINKED', toggle=True
        )

        col_ui.separator()  # Visual spacing

        # Keep the slider/item/playhead colors neatly stacked vertically
        _prop_row(col_ui, self, "slider_item_color")
        _prop_row(col_ui, self, "item_color")
        _prop_row(col_ui, self, "number_text_color")
        _prop_row(col_ui, self, "text_field_text_color")
        _prop_row(col_ui, self, "playhead_color")

        col_ui.separator()  # Visual spacing

        _prop_row(col_ui, self, "alt_row_alpha")

        box_vp = layout.box()
        box_vp.label(text="3D Viewport Visual Settings", icon='VIEW3D')
        col_vp = box_vp.column(align=True)

        type_split = col_vp.split(factor=0.4, align=True)
        type_split.label(text="Background Type")
        type_split.prop(self, "viewport_bg_type", text="")

        _linked_prop_row(col_vp, self, "viewport_bg_color", "lower_gradient_linked")

        if self.viewport_bg_type != 'SINGLE_COLOR':
            _linked_prop_row(col_vp, self, "viewport_bg_grad", "upper_gradient_linked")

        _linked_prop_row(col_vp, self, "viewport_grid_color", "grid_color_linked")
        _linked_prop_row(col_vp, self, "viewport_grid_major_color", "grid_major_color_linked")

        layout.separator()

        reset_row = layout.row()
        reset_row.alignment = 'CENTER'
        reset_row.scale_y = 1.1
        reset_row.operator("fctm.reset_defaults", icon='LOOP_BACK')

        layout.separator()

        is_pending = tuple(self.status_color) == STATUS_COLOR_PENDING

        row = layout.row()
        row.alignment = 'CENTER'
        sub = row.row(align=True)
        sub.scale_y = 1.6
        sub.alert = is_pending

        indicator_left = sub.row(align=True)
        indicator_left.scale_x = 0.3
        indicator_left.prop(self, "status_color", text="")

        op_row = sub.row(align=True)
        op_row.ui_units_x = 8
        op_row.operator("fctm.apply_theme", icon='FILE_REFRESH')

        indicator_right = sub.row(align=True)
        indicator_right.scale_x = 0.3
        indicator_right.prop(self, "status_color", text="")


MAIN_AREAS = ["topbar", "statusbar"]
VIEWPORT_AREAS = ["view_3d"]
SIDE_AREAS = [
    "outliner", "properties", "file_browser",
    "console", "info", "preferences", "image_editor",
    "node_editor", "sequence_editor",
    "clip_editor", "text_editor", "graph_editor", "dopesheet_editor",
    "nla_editor", "spreadsheet",
]


def set_color(struct, attrname, color, alpha=None):
    if not hasattr(struct, attrname):
        return
    try:
        current = getattr(struct, attrname)
        n = len(current)
    except Exception:
        return
    try:
        if n == 4:
            a = alpha if alpha is not None else (color[3] if len(color) > 3 else 1.0)
            setattr(struct, attrname, (color[0], color[1], color[2], a))
        elif n == 3:
            setattr(struct, attrname, (color[0], color[1], color[2]))
    except Exception:
        pass


def set_color_by_path(root, path, color, alpha=None):
    if root is None:
        return
    parts = path.split('.')
    obj = root
    for part in parts[:-1]:
        if not hasattr(obj, part):
            return
        obj = getattr(obj, part)
    set_color(obj, parts[-1], color, alpha)


def _rna_identity(obj):

    as_pointer = getattr(obj, "as_pointer", None)
    if callable(as_pointer):
        try:
            return as_pointer()
        except Exception:
            pass
    return id(obj)


def apply_color_deep(obj, target_names, color, visited=None):

    if visited is None:
        visited = set()

    if obj is None:
        return

    obj_id = _rna_identity(obj)
    if obj_id in visited:
        return
    visited.add(obj_id)

    if hasattr(obj, "rna_type"):
        for prop in obj.rna_type.properties:
            prop_id = prop.identifier
            if prop_id in ("rna_type", "bl_rna"):
                continue
            if prop_id in target_names:
                set_color(obj, prop_id, color)
            elif prop.type == 'POINTER':
                try:
                    sub_obj = getattr(obj, prop_id, None)
                    if sub_obj is not None and sub_obj != obj:
                        apply_color_deep(sub_obj, target_names, color, visited)
                except Exception:
                    pass
            elif prop.type == 'COLLECTION':
                try:
                    coll = getattr(obj, prop_id, None)
                    if coll is not None:
                        for item in coll:
                            apply_color_deep(item, target_names, color, visited)
                except Exception:
                    pass


def remove_text_shadows(context):
    ui_styles = context.preferences.ui_styles
    if not ui_styles:
        return
    style = ui_styles[0]
    for attr in ("panel_title", "widget", "widget_label", "tooltip", "regular"):
        font_style = getattr(style, attr, None)
        if font_style is None:
            continue
        for prop, value in (
            ("shadow", 0),
            ("shadow_offset_x", 0),
            ("shadow_offset_y", 0),
            ("shadow_alpha", 0.0),
            ("shadow_value", 0.0),
        ):
            if hasattr(font_style, prop):
                setattr(font_style, prop, value)


def apply_widget_colors(wcol, wcol_colors, palette, is_shaded=False):
    set_color(wcol, "inner", wcol_colors["inner"])
    set_color(wcol, "inner_sel", palette["interaction"])
    set_color(wcol, "outline", wcol_colors["outline"])
    set_color(wcol, "outline_sel", wcol_colors["outline_sel"])
    set_color(wcol, "item", palette["accent"])
    set_color(wcol, "item_sel", palette["interaction"])
    set_color(wcol, "text", palette["text"])
    set_color(wcol, "text_sel", TEXT_WHITE_SELECTED)

    if is_shaded:
        for attr in ("show_shaded", "use_shaded", "shaded", "shading"):
            if hasattr(wcol, attr):
                setattr(wcol, attr, True)
        if hasattr(wcol, "shadetop"):
            wcol.shadetop = 20
        if hasattr(wcol, "shadedown"):
            wcol.shadedown = -20
    else:
        for attr in ("show_shaded", "use_shaded", "shaded", "shading"):
            if hasattr(wcol, attr):
                setattr(wcol, attr, False)
        if hasattr(wcol, "shadetop"):
            wcol.shadetop = 0
        if hasattr(wcol, "shadedown"):
            wcol.shadedown = 0


def apply_region_colors(region, back_color, nav_back_color, text_color, text_hi_color):
    if region is None:
        return
    set_color(region, "back", back_color)
    set_color(region, "text", text_color)
    set_color(region, "text_hi", text_hi_color)
    set_color(region, "title", text_hi_color)

    for attr in ("tab_back", "tab_inactive", "navigation_back", "nav_back"):
        if hasattr(region, attr):
            set_color(region, attr, nav_back_color)


RESETTABLE_PROPS = (
    "base_color", "interaction_color", "active_editor_outline_color",
    "border_color_linked", "lower_gradient_linked", "upper_gradient_linked",
    "grid_color_linked", "grid_major_color_linked",
    "slider_item_color", "item_color", "number_text_color", "text_field_text_color",
    "playhead_color", "alt_row_alpha", "viewport_bg_type", "viewport_bg_color",
    "viewport_bg_grad", "viewport_grid_color", "viewport_grid_major_color",
)


class FCTM_OT_reset_defaults(bpy.types.Operator):
    bl_idname = "fctm.reset_defaults"
    bl_label = "Default"
    bl_description = ("Resets all color and viewport settings above back to "
                       "their initial install values. Does not touch the "
                       "currently applied Blender theme until you press "
                       "Apply Theme again.")

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        for prop_name in RESETTABLE_PROPS:
            prefs.property_unset(prop_name)

        prefs.status_color = STATUS_COLOR_PENDING
        self.report({'INFO'}, "Settings reset to defaults - press Apply Theme to use them")
        return {'FINISHED'}


class FCTM_OT_apply_theme(bpy.types.Operator):
    bl_idname = "fctm.apply_theme"
    bl_label = "Apply Theme"
    bl_description = "Regenerates the entire Blender theme from the colors you selected"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        theme = context.preferences.themes[0]
        palette = derive_palette(
            tuple(prefs.base_color),
            tuple(prefs.interaction_color),
            tuple(prefs.slider_item_color),
            tuple(prefs.item_color),
            tuple(prefs.number_text_color),
            tuple(prefs.text_field_text_color),
            tuple(prefs.playhead_color),
            tuple(prefs.active_editor_outline_color),
            prefs.alt_row_alpha
        )

        remove_text_shadows(context)

        # 1. UI Widget and General Panel Colors
        ui = getattr(theme, "user_interface", None)
        if ui is not None:
            for wname, wcol_colors in palette["wcol"].items():
                wcol = getattr(ui, wname, None)
                if wcol is not None:
                    is_shaded = wname in SHADED_WIDGETS
                    apply_widget_colors(wcol, wcol_colors, palette, is_shaded=is_shaded)

            for wname in ("wcol_numslider", "wcol_progress"):
                wcol = getattr(ui, wname, None)
                if wcol is not None:
                    set_color(wcol, "item", palette["slider_item"])
                    set_color(wcol, "item_sel", palette["slider_item"])
                    set_color(wcol, "text", palette["number_text"])
                    set_color(wcol, "text_sel", palette["number_text"])

            wcol_num = getattr(ui, "wcol_num", None)
            if wcol_num is not None:
                set_color(wcol_num, "item", palette["item"])
                set_color(wcol_num, "item_sel", palette["item"])
                set_color(wcol_num, "text", palette["number_text"])
                set_color(wcol_num, "text_sel", palette["number_text"])

            set_color(ui, "panel_outline", palette["panel_outline"])
            set_color(ui, "panel_active", palette["interaction"])

            wcol_subpanel = getattr(ui, "wcol_subpanel", None)
            if wcol_subpanel is not None:
                set_color(wcol_subpanel, "inner", palette["sub_header"])
                set_color(wcol_subpanel, "outline", value_shift(palette["sub_header"], -0.10))
                set_color(wcol_subpanel, "item", palette["accent"])
                set_color(wcol_subpanel, "text", palette["title"])
                set_color(wcol_subpanel, "text_sel", TEXT_WHITE_SELECTED)

            set_color(ui, "panel_back", palette["panel_body"])
            for attr in ("sub_back", "subpanel_back", "panel_sub_back", "panel_subpanel_back"):
                if hasattr(ui, attr):
                    set_color(ui, attr, palette["sub_back"])
            set_color(ui, "panel_header", palette["panel_header"])
            set_color(ui, "panel_title", palette["title"])
            set_color(ui, "panel_text", palette["text"])

            wcol_text = getattr(ui, "wcol_text", None)
            if wcol_text is not None:
                set_color(wcol_text, "text", palette["text_field_text"])
                set_color(wcol_text, "text_sel", palette["text_field_text"])
                set_color(wcol_text, "item", palette["item"])
                set_color(wcol_text, "item_sel", palette["item"])

            for attr in ("region_back", "navigation_back", "tab_back", "tab_inactive", "tab_active"):
                if hasattr(ui, attr):
                    set_color(ui, attr, palette[attr])

            for attr in ("region_background", "sidebar_back", "toolbar_back", "tools_back", "ui_back"):
                if hasattr(ui, attr):
                    set_color(ui, attr, palette["region_back"])
            for attr in ("navigation_background", "nav_back", "tabs_back"):
                if hasattr(ui, attr):
                    set_color(ui, attr, palette["navigation_back"])

        # 2. Shared Processing for All Areas (Main, Side, Viewport)
        all_areas = (
            (MAIN_AREAS, palette["editor_header"], palette["header_text"], palette["header_text_hi"]),
            (SIDE_AREAS, palette["side_header"], palette["side_header_text"], palette["side_header_text_hi"]),
            (VIEWPORT_AREAS, palette["viewport_header"], palette["viewport_header_text"], palette["viewport_header_text_hi"])
        )

        for area_list, header_col, header_text, header_text_hi in all_areas:
            for area_name in area_list:
                area = getattr(theme, area_name, None)
                if area is None:
                    continue
                space = getattr(area, "space", None)
                if space is None:
                    continue

                set_color(space, "back", palette["background"])
                set_color(space, "text", palette["text"])
                set_color(space, "text_hi", palette["text_selected"])
                set_color(space, "title", palette["title"])

                set_color(space, "header", header_col)
                set_color(space, "header_text", header_text)
                set_color(space, "header_text_hi", header_text_hi)

                set_color(space, "tab_back", palette["tab_back"])
                set_color(space, "tab_inactive", palette["tab_inactive"])
                set_color(space, "tab_inactive_text", palette["tab_inactive_text"])
                set_color(space, "tab_active", palette["tab_active"])
                set_color(space, "tab_active_text", palette["tab_active_text"])

                for region_name in ("tools", "ui", "navigation", "regions"):
                    reg = getattr(area, region_name, None)
                    if reg is not None:
                        apply_region_colors(
                            reg,
                            palette["region_back"],
                            palette["navigation_back"],
                            palette["text"],
                            palette["text_selected"]
                        )

        # 3. Direct Path Updates
        set_color_by_path(theme, "common.anim.playhead", palette["playhead"])
        set_color_by_path(theme, "user_interface.editor_outline_active",
                           palette["user_interface.editor_outline_active"])

        set_color_by_path(theme, "regions.asset_shelf.back", palette["regions.asset_shelf.back"])
        set_color_by_path(theme, "regions.asset_shelf.header_back", palette["regions.asset_shelf.header_back"])
        set_color_by_path(theme, "regions.channels.back", palette["regions.channels.back"])
        set_color_by_path(theme, "regions.scrubbing.back", palette["regions.scrubbing.back"])
        set_color_by_path(theme, "regions.sidebars.back", palette["regions.sidebars.back"])
        set_color_by_path(theme, "regions.sidebars.tab_back", palette["regions.sidebars.tab_back"])
        set_color_by_path(theme, "text_editor.line_numbers_background", palette["text_editor.line_numbers_background"])

        # Dynamic Editor Grids
        set_color_by_path(theme, "graph_editor.grid", palette["graph_editor.grid"])
        set_color_by_path(theme, "nla_editor.grid", palette["nla_editor.grid"])
        set_color_by_path(theme, "dopesheet_editor.grid", palette["dopesheet_editor.grid"])
        set_color_by_path(theme, "image_editor.grid", palette["image_editor.grid"])
        set_color_by_path(theme, "sequence_editor.grid", palette["sequence_editor.grid"])
        set_color_by_path(theme, "node_editor.grid", palette["node_editor.grid"])
        set_color_by_path(theme, "node_editor.grid_levels", palette["node_editor.grid_levels"])
        set_color_by_path(theme, "clip_editor.grid", palette["clip_editor.grid"])

        # Dynamic Editor Border Line
        set_color_by_path(theme, "user_interface.editor_border", palette["user_interface.editor_border"])
        set_color_by_path(theme, "user_interface.editor_outline", palette["user_interface.editor_outline"])

        # --- SAFE DEEP ASSIGNMENT (VISITED-SET BACKED) ---
        apply_color_deep(
            theme,
            ("row_alternate", "list_alternate", "alternate_row", "table_row_alternate", "space_list_alternate"),
            palette["alt_row"]
        )

        # 4. Applying User-Selected Viewport Settings
        v3d = getattr(theme, "view_3d", None)
        if v3d is not None:
            v3d_space = getattr(v3d, "space", None)
            if v3d_space is not None:
                set_color(v3d_space, "back", prefs.viewport_bg_color)

                gradients = getattr(v3d_space, "gradients", None)
                if gradients is not None:
                    if hasattr(gradients, "background_type"):
                        gradients.background_type = prefs.viewport_bg_type

                    set_color(gradients, "high_gradient", prefs.viewport_bg_grad)
                    set_color(gradients, "gradient", prefs.viewport_bg_color)

            set_color(v3d, "grid", prefs.viewport_grid_color)
            set_color(v3d, "grid_major", prefs.viewport_grid_major_color)

        prefs.status_color = STATUS_COLOR_APPLIED

        if not prefs.has_saved_initial_preset:
            try:
                bpy.ops.wm.interface_theme_preset_add(name="ColorPaletteTheme")
                prefs.has_saved_initial_preset = True

                try:
                    preset_dir = bpy.utils.user_resource(
                        'SCRIPTS', path=os.path.join("presets", "interface_theme")
                    )
                    preset_filepath = os.path.join(preset_dir, "ColorPaletteTheme.xml")
                    if os.path.exists(preset_filepath):
                        bpy.ops.script.execute_preset(
                            filepath=preset_filepath,
                            menu_idname="USERPREF_MT_interface_theme_presets"
                        )
                except Exception:
                    pass

                self.report(
                    {'INFO'},
                    "Theme applied and saved as the active 'ColorPaletteTheme' preset"
                )
            except Exception as exc:
                self.report(
                    {'WARNING'},
                    f"Theme applied, but could not save 'ColorPaletteTheme' preset: {exc}"
                )
        else:
            self.report({'INFO'}, "Theme applied")

        return {'FINISHED'}


classes = (FCTM_Preferences, FCTM_OT_reset_defaults, FCTM_OT_apply_theme)

MIN_BLENDER_VERSION = (5, 0, 0)


def register():
    if bpy.app.version < MIN_BLENDER_VERSION:
        raise Exception("Requires Blender 5.0 or newer.")
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()