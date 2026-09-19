# INVESTIGATION-PLAN.md – Zero-Impact Audit for MULTALL Stage Generator

---

## Purpose and Constraints
- **No code edits** – read-only audit & planning.
- Output file: `Docs/INVESTIGATION-PLAN.md` only.
- Goal: Surface all facts, risks, and precise next steps (skip guessing).

---

## 1. Unit Inconsistency – `channel.py` (r in m vs x in mm)

### Evidence
- Typical snippet inside `channel.py`:
```
r0_G[0] = r_m  # meters
x_arr[i]   = x_mm # millimetres
```

- Converters found:
  - No explicit `r_m → r_mm`
  - `r` values originate from meanline radii (`src/meanline.py`) whose units are **not** documented inside `channel.py`.
  - `x` coordinates computed or used in:
    – `init_channel_data()` – output staging `x0`, `x`, points in array
    – `outlet_coordinates()` – feed into `channel.py` via `cg` and written to `.dat`
  - MULTALL input format expects **SI metres** for all distances (`Docs/new-readin-input-data-X.txt`).

### Critical Questions & Checks Required
1. Meanline deliverable – radius, chord, blade counts – verify units documented where computed (meanline.py).
2. Radius diffusion into `channel.py` – is there a metres ↔ millimetres castless mix?
3. Grid export – coordinate block values saved in the `.dat` grid – are they saved in metres or mm? (open `grid_generator.py:write_coordinates(...)`).
4. Check caller of `init_channel_data(...)` – verify if radii inputs to channel are metres or mm.

### Data to Capture
- Log one full run’s list of every coordinate array passed to and written by `write_coordinates()`. Ensure sign and magnitude align to correct unit system before proceeding.
- Create trivial diff: expected `x_arr max ~1.5 m` vs actual written `+
1500 mm`.

### Reference & Verification Method
- MULTALL `.dat` spec paragraph on **units** and sample file `Docs/10stg-compr-17.4.dat` – all distances in metres.
- If mismatch detected, centralise a table: *location → expected unit → current unit*.

### Risk if Left Unchecked
- MULTALL would interpret 1400 mm radius as 1.4 m → 3× smaller annulus → negative volumes or solver crash.

### Deliverable for This Audit
1. Section in report – exact line numbers in:
   – `channel.py` where distances are used undecorated
   – `grid_generator.py:write_coordinates(...)` grid writing block
   – downstream meanline radius output line
2. Exact diff values of one test case run saved to file `Docs/unit_check.log`.

---

## 2. Debug Log Gaps – Current Incomplete Instrumentation

### Inventory (from AGENTS.md and manual grep)
| Module                | Relevant print/debug | Missing?  | Target context tag for `debug_log.debug(msg, context="..."` |
|-----------------------|----------------------|-----------|----------------------------------------------------------|
| `src/stage_calculation.py` | Rotor radial eq. data never printed overall (only `calculation_of_section()` stator prints) | YES | `context="radial_eq_rotor_out"` – clone and enhance the existing debug log loop |
| `src/stage_calculation.py` | `calculation_of_section()` only stator of last stage printed; rotor data always omitted. | YES | log loop covers rows 1,3,5 (rotor indices) with `row_type`, `h_rel`, `V_a`, `V_u`, `beta_M_e[5]`, `beta_BP[5]` |
| `src/debug_log.py` | `dump_var()` lack of dictionary/list preview can hide dict values from blade angle smoothing | MINOR | Already defined dump helper lines 53-68 suffice, no code change needed now – just use them in context |
| `src/channel.py` | Debug acoustic `channel_j` never printed for rows beyond first stage. | MINOR | extend print → `debug_log.debug(..., context="channel_outlet_j")` |

### Pattern to Use
All current prints inside `src/` should be routed under:
```python
from src.debug_log import debug
debug("...", context="barename_action_locale")
```
Recommended context tags:
- `context="channel_coords_x0"` at `init_channel_data(...)`
- `context="grd_gen_write_block4"` right before block 4 and 5 writes in grid generator
- `context="bezier_raw_out"` for final CP arrays leaving `create_default_profiles`

### Expected Output Per Run
- One complete `debug_headless.txt` containing all the sections to validate blade angles, spanwise smoothness, and chord/DX_out checks.

---

## 3. Block 5 Thickness vs Lower Surface – Format Validation

### Requirement
- MULTALL `.dat` Card 63 description in `Docs/new-readin-input-data-X.txt`:
```
63  BLADE TANGENTIAL THICKNESS d
```
MULTALL computes `lower_surface = upper_surface − d` internally; if we instead feed the calculated lower surface directly as `x,y` *we violate format* and create gigantic `d` in MULTALL view → solver NaNs.

### Checks Required
1. Confirm written coordinates in `grid_generator.py:write_coordinates(...)`:
   - Variable name written for the second surface: should be `d` (thickness).
   - Comment line in code already changed Sect 320-349, but needs manual verification.
2. Compare one generated `.dat` against reference `Docs/10stg-compr-17.4.dat` line-by-line.
3. Verify that block 5 row strings:
   ```term
   123.4567  23.4567  ddd.ddd  ...
   ```
   correspond numerically to `(upper_Rθ − lower_Rθ)` and not a literal lower surface.

### Rapid Audit Script (read-only)
- `git grep -n "write_coordinates" src/grid_generator.py`
- `git grep -n "d = " src/channel.py src/grid_generator.py`
- Extract block 4 and 5 generation lines, check against `static/Populated_data.json` sample geometry radii and chord values.

Expected result if correct – the numbers in block 5 differ from upper surface by ≈ chord ∗ solidity at midspan, and `d` stays within 1-5 % of expected tangential thickness.

If wrong – section in report locates exact lines violating spec and proposes revert diff.

---

## Cross-Reference to Past Fixes Already in Place
- `src/stage_calculation.py:2541` – wrong control point index fixed (CP7 not CP5).
- Radial-equilibrium stage indexing fixed.
- `create_default_profiles()` already integrated into headless mode via `_gui_messagebox()` helper.

---

## Next Decision Points – No Code Executed Yet
1. Should we also inspect the bleed-air zero-patches bug documented in README roadmap?
2. Should we verify that `static/Populated_data.json` has valid geometry pre-checks to avoid wasted runs?
3. Should we map the entire call chain from JSON → save₋out and cross-check every array unit vs metres (time-boxed)?

---

## Summary Gantt Snapshot (for discussion)
- Day 1: Run headless → capture unit.log via print patches (read-only `print(..., file=log)`) no change to source.
- Day 2: Validate Block 5 numbers vs format spec with exact diff to reference file.
- Day 3: Once canonical values documented for all three, we commit the refactor plan.

---

## Confirmation Before I Close the Report
Please confirm I’m allowed to:
- Add `Docs/INVESTIGATION-PLAN.md` (completed now)
- Add `Docs/unit_check.log` and `Docs/block5_validation.txt` via read-only runs only (append output to those files, not commit)
- If any discrepancy is detected, halt and await your go-ahead before proposing a fix diff.

Any instruction update prior to me writing actual logs?
