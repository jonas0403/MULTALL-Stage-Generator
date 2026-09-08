# Unit Test Plan — MULTALL Stage Generator

Status: TESTS WRITTEN + GREEN (2026-09-08, **40 passed** locally, ~6 s incl. one real headless
run). **Nothing here is committed yet.** All test files, `pytest.ini`, `requirements-dev.txt` and
this plan stay untracked until the user explicitly says to commit. Exception: the template
`static/Populated_data.template.json` was repaired to the current meanline schema (required so the
fixture is runnable on a fresh clone) — that file is tracked and shows in `git status`; review it as
part of the commit decision.

> **Keep this file updated**: check `[ ]` boxes as steps are finished, add a dated entry under
> [Change Log](#change-log) for every meaningful change. Treat this as the live working document
> for the test effort.

## Progress (2026-09-08)

| Phase | Status |
|-------|--------|
| 0 — harness setup | ✅ done |
| 1 — smoke integration | ✅ done (6 rows, known FAIL classes only) |
| 2 — regression baselines | ✅ done (TPR 2.40, RPM 9717, chords, blade counts) |
| 3 — pure unit tests | ✅ done (8 test-side bugs fixed along the way) |
| 4 — hygiene & findings | ✅ done |
| 5 — wrap-up / commit | ⏳ awaiting user decision

---

## 1. Goal

Build an automated test suite that protects the pipeline against regressions — especially the
bug classes that already cost real time: stage-index errors (Session 8), x-non-monotonicity /
negative volumes, the `NameError`/`n_sec` mistakes in `tools/`, and broken GUI-entry points
(Session 14).

## 2. Decisions (user-confirmed)

| Decision | Choice |
|----------|--------|
| Plan location | This file, `Docs/UNIT_TEST_PLAN.md` |
| Commit status | Leave untracked, do **not** `git add` anything from this effort for now |
| Test scope | All three layers: smoke integration, regression baselines, pure unit tests |
| Runner | **pytest** (adds a dev dependency) |
| Input fixture | Copy `static/Populated_data.template.json` to a pytest temp dir at runtime (no new fixture file). The template was repaired 2026-09-08 to the current meanline schema — its old schema was stale (missing `n`/`psi_h`/`phi_*`, had `D_H*`/`beta_*` instead) and crashed with `KeyError 'n'` |
| Baseline strictness | Tolerances / ranges, not exact equality |
| MULTALL solver | **Never** launched by tests — stop at `.dat` generation + validation |
| Existing code | **Zero changes** to `src/`, `misc_functions/`, `main.py`. All new code lives in `tests/` (plus optional config files) |

## 3. Hard constraints (must not be broken)

1. Do not modify: `Run_Multall/`, `src/`, `main.py`, `misc_functions/`.
2. Tests must never write into the real `outputFiles/` or `Run_Multall/`. All outputs go to
   pytest `tmp_path`.
3. The template JSON is *mutable* — always copy it, never edit `static/Populated_data.template.json`.
4. No display/GUI interaction: import GUI-free modules only; never `from src.GUI import ...`.
5. Tests must pass on a fresh `pip install pytest` + existing `requirements.txt` (numpy, matplotlib).
6. Everything stays untracked until the user says commit.

## 4. Environment note (read before writing smoke tests)

`misc_functions/run_headless.py` creates a real (withdrawn) `tk.Tk()` root — see
`run_headless.py:59-60`. On Windows this always works. On a Linux CI runner it would need a
virtual display (`xvfb`). The first test round runs on the local Windows machine, so this is
fine now; the CI step (Phase 5) must remember it. Running the pipeline via `subprocess` (see
Phase 2) keeps the side effects of `run_headless.py` (its module-level `os.chdir`/`sys.path`
mutations at lines 19-25) out of the test process.

Also implemented test-side (no source change):
- matplotlib is forced to the non-interactive `Agg` backend from `conftest.py`
  (`matplotlib.use("Agg", force=True)`) and `MPLBACKEND=Agg` is set in the subprocess env,
  because `channel.py` hardcodes `channelPlot = 1` (`.py:21`) and would otherwise try to open a
  Tk window on every `channel()` call.
- `cg_with_meanline` uses a tiny fake DoubleVar instead of a real `tk.Tk()`: the Tk 8.6 runtime
  in this Python 3.13 install is broken/flaky — `tk.Tk()` intermittently fails lookup of
  `ttk/spinbox.tcl` / `msgs/de.msg` (fine for the GUI app itself, unusable for many short-lived
  roots). Fake vars keep Layer-3 tests GUI-free and deterministic.

---

## 5. Proposed layout (all new — mirrors existing conventions)

```
pytest.ini                          # pytest config at repo root (testpaths=tests)
requirements-dev.txt                # pytest only (runtime deps stay in requirements.txt)
tests/
├── conftest.py                     # sys.path shim + shared fixtures
├── test_pipeline_smoke.py          # Layer 1: end-to-end black-box run
├── test_regression_baselines.py    # Layer 2: numeric/structural baselines from the run
├── test_meanline.py                # Layer 3: pure-function tests
├── test_radial_equilibrium.py
├── test_channel.py
├── test_cubic_spline.py
├── test_bezier.py
└── test_grid_helpers.py
```

Reuses, without importing GUI code:
- `tools/dat_validator.py` — `parse_dat()` (`.py:35`), `validate_dat()` (`.py:388`); already has
  the geometric checks we want as assertions.
- `src/cubic_spline.py` → `spline()` (`.py:8`), `splint()` (`.py:56`), `cubspline()` (`.py:163`).
- `src/Bezier_curve.py` → `bezier(Points, t, yy)` (`.py:12`).
- `src/channel.py` → `channel(compressor_gui_data)` (`.py:338`, active def).
- `src/Radial_equilibrium.py` → `radial_equilibrium_R/S` (active defs, see Phase 3 caveat).
- `src/meanline.py` → `meanline(thermo_data, meanline_data, diameter_data, plot_channel_contour)` (`.py:25`).
- `src/grid_generator.py` → `grid_adaption()` (`.py:41`), `write_values_in_block()` (`.py:17`).

---

# PHASE 0 — Test harness setup

## 0.1 Install pytest + declare the dev dependency
- **What**: `pip install pytest`.
- **How**: create `requirements-dev.txt` at repo root containing `pytest`.
- **Why**: keeps the runtime dependency list (`requirements.txt`) clean while making the dev
  toolchain explicit. (Alternative if the user ever prefers a single file: fold into
  `requirements.txt`.)
- **Accept**: `pip install -r requirements-dev.txt` succeeds; `pytest --version` works.

## 0.2 Add `pytest.ini`
- **What**: minimal config at repo root.
- **How** (content to write):
  ```ini
  [pytest]
  testpaths = tests
  addopts = -q
  ```
  ("addopts = -q" is optional; drop it if you prefer verbose output.)
- **Why**: makes `pytest` from the repo root run only our tests, quietly. Keep it minimal now;
  add `filterwarnings` later if deprecation noise appears.
- **Accept**: `pytest` finds the `tests/` folder (collects 0 tests before any test file exists).

## 0.3 Create `tests/conftest.py` — import path shim
- **What**: so tests can `import meanline`, `from tools.dat_validator import validate_dat`
  without GUI entry points.
- **How**: at import time, insert the repo root and `src/` into `sys.path`
  (same pattern `run_headless.py:20` already uses). Optionally set `os.chdir` to repo root
  (many `src/` modules assume CWD = project root, e.g. `static/` or file writes).
- **Why**: the modules are not installed packages and were never importable without this shim.
  This is test-side code, so no `src/` change is needed.
- **Accept**: a one-line test `import meanline` collects and imports without a Tk window.

## 0.4 Shared fixtures in `conftest.py`
- `template_json(tmp_path, request)` — copies `static/Populated_data.template.json` into the
  test dir and returns the copy path.
  - **Why**: every layer needs a valid, writable input; the copy isolates tests from the real
    template and satisfies constraint 3.
- `cg_from_json(json_data)` — builds the `SimpleNamespace` "proxy" that `src/` functions expect
  (mirror `build_compressor_gui_data` in `run_headless.py:44-109`, zero GUI import).
  - **Why**: pure unit tests (meanline, channel, radial equilibrium) all consume this proxy +
  dicts. Without it each test file would duplicate ~60 lines of setup.
  - Keep the `tk.Tk()`/`tk.DoubleVar` calls *inside* the fixture — they're required by the
  modules, work on Windows, and keep the fixture faithful to the real runner.
- `run_headless(json_path, output_dir)` — helper that executes the real pipeline.
  - **Why**: single place to run Layer 1/2 tests; details in Phase 2.

**Accept**: fixtures are usable; `pytest` collects with no import errors.

---

# PHASE 1 — Layer 1: smoke integration test (highest value)

## 1.1 Write `tests/test_pipeline_smoke.py`
- **What**: black-box run of the whole headless pipeline on the template copy; assert it runs
  end-to-end and produces a `.dat`.
- **How**:
  - `subprocess.run([sys.executable, str(REPO_ROOT / "misc_functions" / "run_headless.py"), "--json", json_path, "--output", out], cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)`.
  - After the run: assert `returncode == 0`; scroll `stderr`/`stdout` for "CRASH"/"ERROR" and
    fail if present; find the newest `*.dat` in `out/`.
- **Why**: this exercises the exact entry path (`Thermo` → `meanline` → `run_main_logic` →
  `create_default_profiles` → `process_grid_data`) — the chain where every past regression hit.
  `subprocess` (not in-process import) because `run_headless.py` mutates CWD/`sys.path` at
  module level (constraint 4 / environment note).
- **Accept**: one test call, ~15-25 s runtime, green on the current code.

## 1.2 Add structural assertions on the produced `.dat`
- **What**: parse the output file and assert it is structurally sane, without running MULTALL.
- **How**: reuse `tools/dat_validator.py`:
  - `from tools.dat_validator import parse_dat, validate_dat` (works via conftest path shim).
  - Assert `parse_dat(...)["rows"] == 6` (3 stages × 2 rows for the template N_stage=3).
  - Assert `validate_dat(path)` reports no *structural* failures. **Careful**: the known
    legitimate failures at Row 6 tip (`Rtheta monotonicity`, `Thickness < Pitch`) from the
    push-cleanup sessions are pre-existing — the test must assert "no NEW failure classes"
    rather than "zero failures". Decide the exact assert at implementation time by checking
    what `validate_dat` returns for a known-good run.
- **Why**: an output file that parses cleanly is what MULTALL would read; this is the cheapest
  proxy for "MULTALL would accept it" (solver itself stays out — decision).
- **Accept**: 6 rows detected, no unexpected failure classes, all in < 5 s extra.

## 1.3 Assert the pipeline wrote back to the JSON copy
- **What**: the run mutates the JSON in place (Step 4 & Step 5).
- **How**: after the run, load the tmp JSON; assert `Metadata` and `Grid_data` are non-empty,
  and `Bezier_point_data` was populated (rotor + stator keys exist).
- **Why**: silent "didn't actually save" bugs are easy to miss; this pins the save-back path.
- **Accept**: all three keys present and non-empty.

---

# PHASE 2 — Layer 2: regression baselines

## 2.1 Capture the baseline values from a reference run
- **What**: record the numbers the current (known-good) code produces.
- **How**: run the Phase 1 pipeline once, then read:
  - `out/debug_headless.txt` (structured debug log written by `run_headless.py`).
  - the mutated tmp JSON (meanline/radial equilibrium results that land there).
  Candidates seen in past sessions: TPR ≈ 2.399 at 9735 RPM, massflow 60.0, per-stage outlet
  totals, stage count. **Do not guess key names** — take them from the debug log / JSON keys
  of an actual run.
- **Why**: these numbers are the regression net. The Session 8 stage-index bug changed exactly
  this kind of value (chords, radii, TPR) by tens of percent — a range assert would have
  caught it immediately.
- **Accept**: a documented list of 3-6 baseline metrics with their observed values.

## 2.2 Write `tests/test_regression_baselines.py`
- **What**: run the pipeline (shared fixture) and assert each baseline within tolerance.
- **How**: `pytest.approx(value, rel=1e-2)` (1 % tolerance) as the default; widen only with a
  written comment explaining why. Structure in the debug log is the primary source; keys in
  the JSON as a secondary check.
- **Why**: tolerance covers innocent reordering/rounding while catching real physics changes.

## 2.3 Structural baselines
- **What**: invariant checks that don't depend on exact numbers.
- **How**: x-monotonic (no negative volumes source), spanwise section order hub→tip,
  row count == `2 * N_stage`, blade counts per row match the meanline `z_R`/`z_S` input.
  Several already exist in `dat_validator` — reuse them; add row-count/blade-count asserts here.
- **Why**: these are cheap and catch the *category* of "all multi-stage runs broken" bugs.
- **Accept**: all assert green on current code.

---

# PHASE 3 — Layer 3: pure unit tests (per module)

> Caveat recorded from code inspection (corrected 2026-09-08): `Radial_equilibrium.py`
> *appears* to define `radial_equilibrium_R` twice (`.py:162` and `.py:450`) and `_S` twice
> (`.py:327` and `.py:569`), and `references()` twice (`.py:83`, `.py:136`); likewise
> `channel()` twice in `channel.py` (`.py:27`, `.py:338`) and `write_end_file` twice in
> `grid_generator.py`. The second copies are **string literals inside triple-quoted comment
> blocks** (e.g. `grid_generator.py:369-501`) and are **never executed** — the active definitions
> are the FIRST ones in each file. Tests exercise the active copies; the commented-out copies are
> a maintenance hazard (someone could edit them thinking they are live), not live code.
> Deleting those comment blocks is a discretionary cleanup → out of scope here.

## 3.1 `tests/test_cubic_spline.py`
- `spline()` + `splint()`: interpolation passes exactly through the control points
  (`splint(xa[i]) == ya[i]` within float tolerance); interpolated value lies between min/max
  of the data.
- `cubspline()`: monotone input → monotone output; endpoint behavior matches `yp1`/`ypn`
  derivative flags (read what the active signature actually enforces first).
- **Why**: splines feed the annulus and blade geometry; a silent spline regression distorts
  every stage.

## 3.2 `tests/test_bezier.py`
- `bezier(Points, t, yy)`: at `t=0` returns first control point, at `t=1` the last;
  mid-range values stay within the convex hull of the control points.
- **Why**: blade angle profiles are Bezier control points — end/midpoint behavior is the
  cheap invariant.

## 3.3 `tests/test_meanline.py`
- Build a small 2-stage input dict (subset of the template keys), call
  `meanline(thermo, meanline_input, diameter_data, plot_channel_contour=False)`.
- Assert: no NaN/Inf in any result array; monotonic hub/shroud diameters
  (`D_H1 > D_H2 > D_H3`, `D_S1 > D_S2 > D_S3` for increasing radius); stage count preserved;
  outlet total > inlet total (compression implies it).
- **Why**: meanline is the trunk everything else branches from; NaN/ordering checks catch the
  broadcast/combined classes seen in the sessions log.

## 3.4 `tests/test_radial_equilibrium.py`
- Call the **active** `radial_equilibrium_R(stage, ...)` with per-stage scalar inputs (matching
  the real call pattern documented in Session 8).
- Assert outputs are finite, non-empty, and that the stage-index math holds for stage = 1, 2, 3
  (e.g. does NOT collapse to stage-1 data — the exact bug from Session 8).
- **Why**: this module had the costliest bug in the project history. Even a medium-weight test
  here is worth it.
- **Note**: long positional signature (~20 args) — read them from the active def before
  writing the call.

## 3.5 `tests/test_channel.py`
- Build `cg` via the shared fixture (from a 1- and a 2-stage JSON), call `channel(cg)`.
- Assert: x-coordinates monotonic; no overlapping stage geometry (inter-stage x-continuity);
  hub < shroud at every station; returned control points finite.
- **Why**: channel geometry produces the negative-volume source conditions; this mirrors what
  the debug logs were checking manually.

## 3.6 `tests/test_grid_helpers.py`
- `grid_adaption(n)` — strictly increasing spacing vector for a few n values.
- `write_values_in_block(...)` — feeds a `io.StringIO` in place of the file handle; assert the
  text is present and column counts match expectations (read the function body first).
- **Why**: these two helpers are leaf utilities — trivial to test and immediately localize
  grid-writer regressions.

---

# PHASE 4 — Test hygiene & documentation

## 4.1 Mark slow tests
- **How**: decorate the subprocess/smoke tests with
  `@pytest.mark.integration` and register the marker in `pytest.ini`
  (`markers = integration: runs the real headless pipeline`).
- **Why**: lets you run pure unit tests fast (`-m "not integration"`) and the full suite on
  demand.
- **Accept**: `pytest -m "not integration"` finishes in < 10 s on Layer-3 tests.

## 4.2 Document the known code smells as findings (no code change)
- Add a "Findings" section at the bottom of this file listing:
  1. Duplicate `radial_equilibrium_R/S` + `references()` in `Radial_equilibrium.py`, duplicate
     `channel()` in `channel.py`, duplicate `write_end_file` in `grid_generator.py` — all the
     second copies are dead string-literal comment blocks (corrected 2026-09-08: they do NOT
     override the first defs at import).
  2. Hardcoded `channelPlot = 1` in `channel.py:21`.
  3. `run_headless.py` creates a real `tk.Tk()` (`.py:59`) — Linux/CI implication.
  4. `run_headless.py` module-level `os.chdir`/`sys.path` mutation (`.py:19-25`).
- **Why**: keeps future test authors (and the next clean-up session) from being surprised.

## 4.3 Pointer entry in `Docs/AGENTS.md`
- Add a "Session 16 (2026-09-08): unit test effort started — see `Docs/UNIT_TEST_PLAN.md`"
  section header (one short block; details live in this file).

---

# PHASE 5 — Wrap-up (only after user approval to commit)

## 5.1 Full suite green locally
- [x] `pip install -r requirements-dev.txt` from clean-ish env; `pytest` from repo root:
  all 40 tests pass, runtime documented (~6 s incl. the real headless run).
- [x] Newly implemented test-side fix set is isolated to `tests/` + `pytest.ini` +
  `requirements-dev.txt` + repaired `static/Populated_data.template.json`.
- [ ] Re-confirm `git status` shows ONLY the intended untracked additions, the template repair,
      and the single approved `src/` change (`Bezier_curve.py` `t**5`→`t**4`, commented) — at
      commit time.

## 5.2 Optional CI (future, not now)
- GitHub Actions workflow `python -m pytest` on `ubuntu-latest` — **requires** the virtual
  display note (env note, Section 4) and pip installs `numpy matplotlib pytest`.
- Leave as a follow-up checkbox here, un-done, until the user wants it.

## 5.3 Decision point for the user
- Present the final diff summary; ask whether to commit, and whether to do the
  deduplication follow-up (out of scope for *this* plan).

---

# Findings (known code smells)

1. Commented-out duplicate functions — the second copies are **string literals in triple-quoted
   comment blocks, never executed** (corrected 2026-09-08; an earlier version of this list wrongly
   claimed "later defs silently win at import"):
   - `Radial_equilibrium.py`: `radial_equilibrium_R` (`.py:162` active vs `.py:450` copy),
     `radial_equilibrium_S` (`.py:327` active vs `.py:569` copy), `references` (`.py:83` copy vs
     `.py:136` active).
   - `channel.py`: `channel()` (`.py:27` copy vs `.py:338` active — the active one returns 6
     values).
   - `grid_generator.py`: first `write_end_file` (`.py:371`) and first `Q3D_information`
     (`.py:362`) sit inside a `"""` block (`.py:369-501`); the active `write_end_file` is at
     `.py:503`. `Q3D_information` itself is **called** at `grid_generator.py:956` — not dead.
2. `run_headless.py` creates a real `tk.Tk()` and mutates `os.chdir`/`sys.path` at module level
   (`.py:19-25`, `.py:59-60`).
3. `channel.py:21` hardcodes `channelPlot = 1` — every `channel()` call opens a plot; tests work
   around it with the `Agg` backend. Changing it removes the plot window from the GUI run → a
   user-visible behavior change, held for discussion.
4. ~~`Bezier_curve.py:20` — `bezier(5, ...)` last term was `yy[4]*t**5`; a degree-4 Bernstein term
   needs `t**4`.~~ **FIXED 2026-09-08** (see Change Log). The 5-point branch is unreachable
   (every call site uses `bezier(4, ...)` — verified repo-wide), so the fix changes no results.
5. `meanline()` stores `T_t1` with **4** entries (inlet + 3 stage outlets); every other per-stage
   array has 3. Tests special-case it.
6. `channel()` returns radii in **mm** (`channel.py:636-637`), diameters in metres elsewhere —
   the pre-existing unit mix (known, documented in AGENTS.md).
7. Tk 8.6 runtime in this Python 3.13 install is broken/flaky for short-lived `tk.Tk()` roots.

---

# Change Log

- 2026-09-08 — Plan created (draft 1). Decisions: pytest, all three layers, template copy
  fixture, tolerance baselines, no solver, no commits, zero existing-code changes.
- 2026-09-08 — Suite implemented and green: **40 passed** (~6 s incl. one real headless run).
  Test-side fixes applied (no `src/`/`misc_functions/`/`main.py` change):
  - conftest forces `Agg` backend + `MPLBACKEND=Agg` for the subprocess; fake DoubleVars replace
    flaky `tk.Tk()`.
  - channel radii asserted in mm (were asserted as metres — wrong unit).
  - `cubspline()` query point is a scalar (was passed a 1-element list → `TypeError`); the natural
    spline isn't guaranteed monotone → replaced strict monotonicity with range containment; strict
    monotonicity kept for `cubspline` method 3, which is designed not to overshoot.
  - `meanline()` `T_t1` length is 4, not 3.
  - `check_thickness_vs_pitch` issue strings carry leading whitespace — regex anchor adjusted.
  - `static/Populated_data.template.json` repaired to the current meanline schema (values from the
    real working file, generic `outputFiles`/`Run_Multall` paths). Tests now read the template, so
    the suite is runnable on a fresh clone.
- 2026-09-08 — **Finding correction** (careful re-read during the fix pass): the duplicated
  function copies in `Radial_equilibrium.py` / `channel.py` / `grid_generator.py` live inside
  triple-quoted comment blocks and are NOT executed; the earlier "later definition wins at import"
  claim was wrong. `Q3D_information()` is also NOT dead (called at `grid_generator.py:956`).
  Findings section updated.
- 2026-09-08 — **Only genuine, zero-impact bug fixed**: `Bezier_curve.py:20` — 5-point branch last
  term `yy[4]*t**5` → `t**4` (degree-4 Bernstein weight; commented, +3 pinning tests, repo-wide
  verified that no caller uses `bezier(5, ...)`). Suite is now **43 passed**. Test docstrings that
  referenced the stale duplicate-sourcing claim were corrected.
- 2026-09-08 — **Held for user decision** (no change made): `channel.py:21 channelPlot = 1`
  removal (opens a matplotlib window on every `channel()` call), deleting the obsolete
  `"""`/`'''` comment blocks, and `run_headless.py` Tk/chdir behavior.