"""Textual TUI for pet creation and customization."""

from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
)

from claude_pet.ascii_art import get_species_template, render_eyes, _render_ascii, xp_bar
from claude_pet.models import (
    SPECIES_LIST,
    PetData,
    get_all_unlocked,
    load_pet,
    save_pet,
)


class AsciiPreview(Static):
    """Widget that displays the ASCII art preview."""

    def update_preview(self, species: str, eyes: str = "default", mood: str = "", pattern: str = "solid", color: str = "") -> None:
        lines = _render_ascii(species, eyes, mood, pattern)
        art = "\n".join(lines)
        if color:
            art += f"\n\n[{color}]"
        self.update(art)


class SpeciesScreen(Screen):
    """Screen for selecting a species. First-time only."""

    BINDINGS = [Binding("escape", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self.selected_species = SPECIES_LIST[0]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Label("Choose Your Species (this is permanent!)", id="title")
        with Horizontal(id="species-layout"):
            yield ListView(
                *[ListItem(Label(s.capitalize()), name=s) for s in SPECIES_LIST],
                id="species-list",
            )
            yield AsciiPreview(id="preview")
        with Horizontal(id="button-bar"):
            yield Button("Continue", variant="primary", id="continue-btn")
        yield Footer()

    def on_mount(self) -> None:
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(SPECIES_LIST[0])

    @on(ListView.Highlighted)
    def species_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.name:
            self.selected_species = event.item.name
            preview = self.query_one("#preview", AsciiPreview)
            preview.update_preview(self.selected_species)

    @on(ListView.Selected)
    def species_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.name:
            self.selected_species = event.item.name
            preview = self.query_one("#preview", AsciiPreview)
            preview.update_preview(self.selected_species)

    @on(Button.Pressed, "#continue-btn")
    def continue_pressed(self) -> None:
        self.app.selected_species = self.selected_species
        self.app.push_screen(CustomizeScreen())

    def action_quit(self) -> None:
        self.app.exit()


class CustomizeScreen(Screen):
    """Screen for customizing pet appearance. Level-gated options."""

    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Label("Customize Appearance", id="title")
        with Horizontal(id="customize-layout"):
            with VerticalScroll(id="options-panel"):
                yield Label("Color:")
                yield Select([], id="color-select", prompt="Color")
                yield Label("Eyes:")
                yield Select([], id="eyes-select", prompt="Eyes")
                yield Label("Pattern:")
                yield Select([], id="pattern-select", prompt="Pattern")
                yield Label("Hat:")
                yield Select([], id="hat-select", prompt="Hat")
                yield Label("Scarf:")
                yield Select([], id="scarf-select", prompt="Scarf")
                yield Label("Collar:")
                yield Select([], id="collar-select", prompt="Collar")
                yield Label("Glasses:")
                yield Select([], id="glasses-select", prompt="Glasses")
                yield Label("Cape:")
                yield Select([], id="cape-select", prompt="Cape")
            yield AsciiPreview(id="preview")
        with Horizontal(id="button-bar"):
            yield Button("Next", variant="primary", id="next-btn")
        yield Footer()

    def on_mount(self) -> None:
        pet = getattr(self.app, "_editing_pet", None)
        level = pet.level if pet else 1
        unlocked = get_all_unlocked(level)

        self._set_options("color-select", unlocked.get("colors", []), pet.color if pet else None)
        self._set_options("eyes-select", unlocked.get("eyes", []), pet.eyes if pet else None)
        self._set_options("pattern-select", unlocked.get("patterns", []), pet.pattern if pet else None)

        acc = unlocked.get("accessories", {})
        for slot in ("hat", "scarf", "collar", "glasses", "cape"):
            items = acc.get(slot, [])
            current = pet.accessories.get(slot) if pet else None
            self._set_options(f"{slot}-select", ["none"] + items, current or "none")

        species = getattr(self.app, "selected_species", "cat")
        eyes_select = self.query_one("#eyes-select", Select)
        eyes = str(eyes_select.value) if eyes_select.value != Select.BLANK else "default"
        pattern_select = self.query_one("#pattern-select", Select)
        pattern = str(pattern_select.value) if pattern_select.value != Select.BLANK else "solid"
        color_select = self.query_one("#color-select", Select)
        color = str(color_select.value).capitalize() if color_select.value != Select.BLANK else ""
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(species, eyes=eyes, pattern=pattern, color=color)

    def _set_options(self, select_id: str, options: list[str], current: str | None) -> None:
        select = self.query_one(f"#{select_id}", Select)
        option_tuples = [(opt.capitalize(), opt) for opt in options]
        select.set_options(option_tuples)
        select.allow_blank = False
        if current and current in options:
            select.value = current
        elif options:
            select.value = options[0]

    @on(Select.Changed)
    def option_changed(self, event: Select.Changed) -> None:
        species = getattr(self.app, "selected_species", "cat")
        eyes_select = self.query_one("#eyes-select", Select)
        eyes = str(eyes_select.value) if eyes_select.value != Select.BLANK else "default"
        pattern_select = self.query_one("#pattern-select", Select)
        pattern = str(pattern_select.value) if pattern_select.value != Select.BLANK else "solid"
        color_select = self.query_one("#color-select", Select)
        color = str(color_select.value).capitalize() if color_select.value != Select.BLANK else ""
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(species, eyes=eyes, pattern=pattern, color=color)

    @on(Button.Pressed, "#next-btn")
    def next_pressed(self) -> None:
        self.app.pet_color = self._get_value("color-select", "white")
        self.app.pet_eyes = self._get_value("eyes-select", "default")
        self.app.pet_pattern = self._get_value("pattern-select", "solid")
        self.app.pet_accessories = {}
        for slot in ("hat", "scarf", "collar", "glasses", "cape"):
            val = self._get_value(f"{slot}-select", "none")
            if val != "none":
                self.app.pet_accessories[slot] = val
        self.app.push_screen(NameScreen())

    def _get_value(self, select_id: str, default: str) -> str:
        select = self.query_one(f"#{select_id}", Select)
        if select.value == Select.BLANK:
            return default
        return str(select.value)

    def action_go_back(self) -> None:
        self.app.pop_screen()


class NameScreen(Screen):
    """Screen for naming the pet."""

    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Label("Name Your Pet!", id="title")
        with Horizontal(id="name-layout"):
            yield AsciiPreview(id="preview")
            with Vertical(id="name-panel"):
                yield Input(
                    placeholder="Enter a name...",
                    id="name-input",
                )
                yield Button("Save & Exit", variant="primary", id="save-btn")
        yield Footer()

    def on_mount(self) -> None:
        species = getattr(self.app, "selected_species", "cat")
        eyes = getattr(self.app, "pet_eyes", "default")
        pattern = getattr(self.app, "pet_pattern", "solid")
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(species, eyes=eyes, pattern=pattern)

        pet = getattr(self.app, "_editing_pet", None)
        if pet:
            name_input = self.query_one("#name-input", Input)
            name_input.value = pet.name

    @on(Button.Pressed, "#save-btn")
    def save_pressed(self) -> None:
        name_input = self.query_one("#name-input", Input)
        name = name_input.value.strip()

        if not name:
            name_input.focus()
            return

        pet = getattr(self.app, "_editing_pet", None)
        if pet is None:
            pet = PetData(
                species=getattr(self.app, "selected_species", "cat"),
                name=name,
            )
        else:
            pet.name = name

        pet.color = getattr(self.app, "pet_color", "white")
        pet.eyes = getattr(self.app, "pet_eyes", "default")
        pet.pattern = getattr(self.app, "pet_pattern", "solid")
        pet.accessories = getattr(self.app, "pet_accessories", {})

        save_pet(pet)
        self.app.exit(message=f"Saved {pet.name} the {pet.species.capitalize()}!")

    def action_go_back(self) -> None:
        self.app.pop_screen()


class PetDesignerApp(App):
    """Main Textual application for pet design."""

    TITLE = "claude-pet designer"
    CSS = """
    #title {
        text-align: center;
        text-style: bold;
        margin: 1 0;
        width: 100%;
    }
    #species-layout, #customize-layout, #name-layout {
        height: 1fr;
        margin: 1 2;
    }
    #species-list {
        width: 30;
        height: 100%;
    }
    #preview {
        width: 1fr;
        height: auto;
        max-height: 12;
        content-align: center middle;
        padding: 1 4;
    }
    #options-panel {
        width: 40;
        height: 100%;
        padding: 1 2;
    }
    #options-panel Label {
        margin-top: 1;
        color: $text-muted;
    }
    #options-panel Select {
        margin-bottom: 0;
    }
    #button-bar {
        height: 3;
        align: center middle;
        margin: 1 0;
    }
    #name-layout {
        height: auto;
    }
    #name-panel {
        width: 1fr;
        height: auto;
        padding: 2 4;
    }
    #name-input {
        margin: 1 0;
    }
    #save-btn {
        margin: 1 0;
    }
    """

    def __init__(self, editing_pet: PetData | None = None) -> None:
        super().__init__()
        self._editing_pet = editing_pet
        self.selected_species = editing_pet.species if editing_pet else ""

    def on_mount(self) -> None:
        if self._editing_pet:
            self.push_screen(CustomizeScreen())
        else:
            self.push_screen(SpeciesScreen())


def run_designer() -> None:
    """Entry point for the pet designer TUI."""
    pet = load_pet()
    app = PetDesignerApp(editing_pet=pet)
    result = app.run()
    if result:
        print(result)
