/**
 * puzzles.js — Puzzle state tracking (port of puzzles.py).
 */

const SCORE_EVENTS = {
  maintenance_hatch_open: 10,
  found_syndicate:        15,
  syndicate_door_open:    20,
  clem_told_you:          10,
  working_with_sheriff:   10,
  codicil_recovered:      50,
  game_complete:          25,
};

export class PuzzleState {
  constructor() { this._flags = {}; }

  sync(playerFlags) { this._flags = playerFlags; }

  flag(name) { return !!this._flags[name]; }

  maintenanceHatchOpen()  { return this.flag('maintenance_hatch_open'); }
  playerHasSpurs()        { return this.flag('wearing_spurs'); }
  foundSyndicate()        { return this.flag('found_syndicate'); }
  syndicateDoorOpen()     { return this.flag('syndicate_door_open'); }
  isWorkingWithSheriff()  { return this.flag('working_with_sheriff'); }
  knowsAboutThirdParty()  { return this.flag('clem_told_you') || this.flag('holloway_revealed_third_party'); }
  codicilRecovered()      { return this.flag('codicil_recovered'); }
  gameComplete()          { return this.flag('game_complete'); }

  checkScoreEvents(oldFlags, newFlags) {
    let points = 0;
    for (const [flag, pts] of Object.entries(SCORE_EVENTS)) {
      if (newFlags[flag] && !oldFlags[flag]) points += pts;
    }
    return points;
  }
}
