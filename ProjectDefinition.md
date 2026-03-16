# Guns, Grit & Gravity
### *A Text Adventure in Deep Space, Where the Stars Don't Care and Neither Does the Sheriff*

> "Space is big. You just won't believe how vastly, hugely, mind-bogglingly big it is.
> The frontier, however, is a state of mind — and states of mind tend to smell of
> recycled air, cheap whiskey, and someone else's regrets."
>
> — *The Outer Sprawl Traveler's Almanac, Vol. 3, Chapter 1, Footnote 7*

---

## 1. Concept

**Guns, Grit & Gravity** is a parser-driven text adventure in the tradition of Zork and the Infocom classics, set in the lawless fringes of deep space where the aesthetic is firmly Old West and the philosophy is firmly "someone's going to get shot, and it will probably be your fault."

The game is written in **Python 3.10+** with no mandatory external dependencies, playable in any terminal, and structured to be extended without requiring a PhD in spaghetti code.

The tone is Terry Pratchett: warm but sardonic, fond of the universe's inhabitants despite their persistent inability to make sensible decisions, with footnotes* used as a literary device rather than an admission of defeat.

\* Like this one. Footnotes in this game appear at the bottom of room descriptions and serve as the narrator's running commentary on your life choices.

---

## 2. Setting: The Outer Sprawl

The **Outer Sprawl** is what happens when humanity reaches the stars and immediately tries to claim them, tax them, and open a saloon on them. It is the frontier — not in any romantic sense, but in the sense that the nearest law enforcement is six light-years away and takes fourteen months to file a complaint with.

The Sprawl is home to:

- **Asteroid mining boomtowns** built on rock, ambition, and remarkably poor planning
- **Derelict freighters** converted into trading posts, gambling dens, or extremely awkward family homes
- **Corporate claim offices** staffed by people who chose bureaucracy over personality
- **Independent space stations** that maintain order through a careful combination of posted notices and the implicit threat of airlock-related accidents

The Milky Way here is not the grand cosmic cathedral of science fiction. It's more like a very large county fair that's been going on for too long and nobody can find where they parked.

---

## 3. Story

You are **a drifter**. This is not a romantic description. It means you own a battered ship, a questionable reputation, and precisely the number of enemies that accumulates when you have been drifting for a while.

You have just docked at **Dustpocket Station** — a mid-sized frontier station orbiting a thoroughly unremarkable asteroid designated LV-7-Gamma, which the locals have nicknamed "Clementine" because miners are sentimental like that.

The station is in an uproar. The **Quantum Codicil** — a legendary data crystal containing the deed to the most mineral-rich unclaimed asteroid in the Sprawl — has gone missing. Three factions want it. The sheriff wants everyone to calm down. Nobody is calm.

The factions:

- **The Consolidated Mining Concern** — a corporation so large it has its own gravity
- **The Free Claim Brotherhood** — independent miners united by the belief that solidarity is important, right after individual profit
- **The Station Syndicate** — the people who actually run Dustpocket, who will back whoever wins, as they always have

Your goal: find the Quantum Codicil, survive the factions, and ideally leave with more money than you arrived with. The universe makes no promises about the "ideally" part.

---

## 4. Tone & Style Guide

### The Narrator

The narrator speaks in **second person, present tense**, which is the Zork tradition and also what happens when someone who's read too much literary fiction gets hold of a game engine.

The narrator:
- Describes the world with affectionate disdain
- Has opinions, shares them when relevant, restrains itself when not
- Uses footnotes for asides that don't fit in the main description*
- Never lies to the player, but occasionally withholds information on grounds of narrative interest

\* The footnote system is a first-class feature, not an afterthought.

### Sample Room Description

```
DUSTPOCKET STATION — DOCKING BAY 7

The docking bay smells of engine coolant and ambition, neither of which has
aged well. Your ship — the Bellerophon, though you've been meaning to rename
it to something that doesn't tempt fate quite so aggressively — sits in berth
seven, looking like it always does: technically spaceworthy, philosophically
ambivalent.

The main concourse lies to the north. A maintenance hatch is set into the
floor, sealed and labelled DO NOT OPEN. Someone has added "SERIOUSLY" in red
marker. A battered locker stands against the east wall.

Exits: North.

* Berth seven is considered unlucky by everyone except the people who assign
  berths, who consider it conveniently cheap to maintain.
```

### Sample NPC Dialogue

```
> TALK TO SHERIFF

Sheriff Vasquez looks up from an impressive pile of paperwork with the
expression of someone who has been hoping you'd leave and is deeply
unsurprised that you haven't.

"You got a problem, drifter? Because I got seventeen problems already and
I'm running out of desk space to put them."

[1] Ask about the Quantum Codicil
[2] Ask about the factions
[3] Ask if she needs help
[4] Leave her to her paperwork
```

### Sample Death Message

```
You have died.

Specifically, you have died by attempting to negotiate with a plasma cutter
while it was running. The universe would like you to know that it tried to
include warning labels, but someone kept stealing them.

Your score: 14 of 250 points.
Your rank: "Enthusiastic"

> RESTART, RESTORE, or QUIT?
```

### Voice Checklist

- [ ] Does the description have a specific, slightly absurd detail that makes the space feel real?
- [ ] Does the narrator sound like it has seen things but remains professionally functional?
- [ ] Are any footnotes present? (Not mandatory, but encouraged for significant locations)
- [ ] Do NPCs have opinions beyond their plot function?
- [ ] Is the humor earned rather than announced?

---

## 5. World Map

### Starting Area: Dustpocket Station

```
                    [Mining Claim Office]
                           |
[Cargo Hold] -- [Main Concourse] -- [Rusty Spur Saloon]
                           |
              [Sheriff's Office]  [Medical Bay]
                           |
              [Docking Bay 7] (START)
                           |
                    [The Bellerophon]
```

### Mid-Game: The Outer Reaches

Accessed after solving the station's opening puzzle arc:

- **Asteroid LV-7-Gamma (Clementine)** — the mining site, accessible via shuttle
- **The Salvager's Rest** — a derelict freighter converted into a trading post
- **Claim Junction** — a pressurized tent city on Clementine's surface

### Endgame: The Syndicate Levels

Hidden below Dustpocket Station, revealed through investigation.

---

## 6. Items of Note

| Item | Description | Use |
|------|-------------|-----|
| **Plasma Revolver** | "Shoots first. Asks questions never." | Combat/puzzle tool |
| **Rustbucket Spurs** | Magnetic boot attachments shaped like spurs, because someone had a sense of humor | Traversal in low-gravity |
| **Quantum Codicil** | A data crystal the size of your thumb, worth more than your ship | MacGuffin; end goal |
| **Deed to Berth Seven** | Technically yours. Technically worth nothing. | Humor item; useful late game |
| **Protein Jerky (half-eaten)** | "Made from 100% protein. Source unspecified." | Restore minor health; very minor |
| **Sheriff's Badge (replica)** | "Collector's item." | Intimidation in certain conversations |
| **The Salvager's Manual** | Handwritten, coffee-stained, annotated in four languages | Hints and lore |

---

## 7. NPCs

### Sheriff Marta Vasquez
**Role:** Reluctant authority figure
**Personality:** Pragmatic, overworked, fundamentally decent in a universe that makes decency difficult
**Wants:** For everyone to calm down. Just. For once.
**Arc:** Can become an ally if the player helps with a side case involving missing station rations

### Clem Duster (Bartender, The Rusty Spur)
**Role:** Information broker disguised as a bartender
**Personality:** Cheerful nihilist; believes everything is fine because nothing matters
**Wants:** For people to pay their tabs
**Arc:** Knows more about the Codicil's history than anyone; reveals it only over multiple visits

### Deputy TACK-7
**Role:** Android deputy; the sheriff's only backup
**Personality:** Earnestly literal; interprets idioms with devastating accuracy
**Wants:** To serve and protect; also to understand why humans say "break a leg"
**Arc:** Comic relief that becomes unexpectedly moving in the late game

### Augusto Claim (Mining Boss, Free Claim Brotherhood)
**Role:** Faction leader; passionate, loud, genuinely believes in the cause
**Personality:** Revolutionary fire tempered by the fact that he's also a businessman
**Wants:** The Codicil for the Brotherhood — "for all of us," he says, meaning it
**Arc:** Morally complex; can be trusted or manipulated

### Director Fen Holloway (Consolidated Mining Concern)
**Role:** Corporate representative
**Personality:** Serene, expensive, accustomed to getting what she wants by making it seem reasonable
**Wants:** The Codicil, obviously; also for this to be concluded quietly
**Arc:** Not the villain, exactly. More the person who makes villains unnecessary.

---

## 8. Technical Architecture

### Module Structure

```
guns-grit-gravity/
├── main.py              # Entry point, initializes and runs the game loop
├── engine.py            # Core game engine; processes turns, manages state
├── parser.py            # Text input parser; verb/noun extraction, synonym resolution
├── world.py             # Room graph, location registry, exit management
├── player.py            # Player state: inventory, stats, flags, score
├── items.py             # Item class, item registry, interaction handlers
├── npcs.py              # NPC class, dialogue trees, behavior state machines
├── narrator.py          # Output formatting, footnote rendering, text wrapping
├── save.py              # Save/load via JSON serialization
├── puzzles.py           # Puzzle state tracking, solution verification
└── data/
    ├── rooms.json        # Room definitions (description, exits, items, NPCs)
    ├── items.json        # Item definitions (name, description, properties)
    ├── npcs.json         # NPC definitions (dialogue trees, initial state)
    └── strings.json      # Flavor text, death messages, help text, narrator quips
```

### Parser

The parser handles **verb + noun** commands with synonym resolution:

```python
# Recognized verbs (examples)
VERBS = {
    "go": ["go", "move", "walk", "travel", "head"],
    "take": ["take", "get", "grab", "pick", "collect"],
    "examine": ["examine", "look", "inspect", "check", "read", "x"],
    "talk": ["talk", "speak", "ask", "chat", "converse"],
    "use": ["use", "apply", "activate", "operate"],
    "drop": ["drop", "put", "place", "leave"],
    "inventory": ["inventory", "inv", "i", "items", "pockets"],
}

# Direction shortcuts
DIRECTIONS = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "u": "up", "d": "down", "in": "inside", "out": "outside",
}
```

### Room Data Model

```json
{
  "docking_bay_7": {
    "name": "Docking Bay 7",
    "description": "The docking bay smells of engine coolant and ambition...",
    "footnote": "Berth seven is considered unlucky by everyone except...",
    "exits": {
      "north": "main_concourse"
    },
    "items": ["battered_locker"],
    "npcs": [],
    "visited": false,
    "flags": {}
  }
}
```

### Player State

```python
@dataclass
class PlayerState:
    current_room: str
    inventory: list[str]          # item IDs
    max_carry_weight: int         # in arbitrary "units"
    score: int
    turns: int
    flags: dict[str, bool]        # puzzle/story flags
    npc_states: dict[str, dict]   # per-NPC relationship/dialogue state
```

### Footnote System

Footnotes are displayed after room descriptions, separated by a blank line and prefixed with `*`. They appear on first visit and can be toggled with `FOOTNOTES ON/OFF`.

```
> LOOK

DUSTPOCKET STATION — DOCKING BAY 7

[Room description here]

Exits: North.

* Berth seven is considered unlucky by everyone except the people who assign
  berths, who consider it conveniently cheap to maintain.
```

### Save System

Game state is serialized to `~/.guns_grit_gravity/saves/<slot>.json` using stdlib `json`. The format is human-readable to permit debugging and mild cheating, which the narrator will acknowledge if the player loads a save with implausibly good stats.

---

## 9. Command Reference

| Command | Aliases | Effect |
|---------|---------|--------|
| `LOOK` | `L` | Redescribe current room |
| `GO [direction]` | `N`, `S`, `E`, `W`, `U`, `D` | Move in direction |
| `EXAMINE [item/NPC]` | `X`, `INSPECT`, `READ` | Detailed description |
| `TAKE [item]` | `GET`, `GRAB`, `PICK UP` | Add item to inventory |
| `DROP [item]` | `PUT DOWN`, `LEAVE` | Remove item from inventory |
| `INVENTORY` | `I`, `INV` | List carried items |
| `TALK TO [NPC]` | `SPEAK TO`, `ASK` | Initiate dialogue |
| `USE [item]` | `APPLY`, `ACTIVATE` | Use item in context |
| `USE [item] ON [target]` | — | Use item on specific target |
| `OPEN [item]` | `UNLOCK` | Open container or door |
| `CLOSE [item]` | — | Close container or door |
| `SAVE [slot]` | — | Save game to named slot |
| `LOAD [slot]` | `RESTORE` | Load saved game |
| `SCORE` | — | Display current score |
| `HELP` | `?` | Show command list |
| `QUIT` | `Q`, `EXIT` | End game |
| `FOOTNOTES ON/OFF` | — | Toggle footnote display |

---

## 10. Development Phases

### Phase 1 — Core Engine (Foundation)
- [ ] `main.py`: game loop, startup/shutdown
- [ ] `parser.py`: verb/noun parsing, synonym resolution, direction shortcuts
- [ ] `world.py`: room graph with 3 rooms (Docking Bay 7, Main Concourse, Rusty Spur)
- [ ] `player.py`: basic state (location, inventory, score)
- [ ] `narrator.py`: output formatting, text wrapping at 80 chars, footnote display
- [ ] `engine.py`: turn processing, command dispatch
- Goal: A playable (if empty) world you can walk around in

### Phase 2 — World Build-Out
- [ ] Full station map (10 rooms)
- [ ] `items.py`: item class, interaction system
- [ ] Populate rooms with items and basic puzzles
- [ ] `data/` JSON files for rooms and items
- [ ] First puzzle chain: getting past the locked maintenance hatch
- Goal: A world worth exploring

### Phase 3 — Characters & Story
- [ ] `npcs.py`: NPC class, dialogue tree system
- [ ] All 5 main NPCs implemented
- [ ] `puzzles.py`: puzzle state tracking
- [ ] Full story arc: find Codicil, navigate factions, ending(s)
- [ ] Asteroid exterior locations (Phase 2 extension)
- Goal: A game with a story

### Phase 4 — Polish & Systems
- [ ] `save.py`: save/load system
- [ ] Score system fully implemented
- [ ] Death messages for all meaningful deaths
- [ ] Footnote system complete
- [ ] `HINTS` command (limited per game)
- [ ] `colorama` integration (optional, graceful fallback)
- [ ] Full test suite with `pytest`
- Goal: A game worth shipping

---

## 11. Python Requirements

| Requirement | Detail |
|-------------|--------|
| Python version | 3.10+ (uses `match` statement for parser, `dataclasses`) |
| Core dependencies | None (stdlib only: `json`, `os`, `sys`, `pathlib`, `dataclasses`, `textwrap`) |
| Optional dependencies | `colorama` (terminal color, Windows compatibility) |
| Test framework | `pytest` |
| Code style | PEP 8; type hints throughout; `mypy`-compatible |

### Installation

```bash
# No dependencies required to play
python main.py

# For development
pip install pytest colorama mypy
pytest tests/
```

---

## 12. Design Principles

1. **The parser should fail gracefully.** "I don't understand that" is a last resort. Try to interpret intent.

2. **Every room should have at least one detail that rewards curiosity.** EXAMINE everything. The narrator has opinions.

3. **NPCs are people, not quest dispensers.** They have bad days. They remember things you said. They are occasionally wrong.

4. **Footnotes are not jokes.** They are the narrator's honest asides. They can be funny, melancholy, or simply true.

5. **Death should be meaningful, not punishing.** The player should understand why they died and feel that it was, in retrospect, avoidable.

6. **The universe is indifferent. The narrator is not.** The game should feel like it was written by someone who is rooting for you, even when the plot isn't.

---

*"It is a well-known fact that the frontier attracts two types of people: those who are fleeing something, and those who are looking for something. The third type — those who simply took a wrong turn and ended up here — are more common than either group likes to admit."*

*— The Outer Sprawl Traveler's Almanac, Vol. 3, Chapter 7, Footnote 2*
