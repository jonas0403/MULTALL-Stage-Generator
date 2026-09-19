# ------------------------------------------------------------------
# File:    source/gui/tabs/__init__.py
# Author:  Jonas Scholz
# Purpose: Per-tab construction functions (0D/1D/3D/Grid/Other).
# ------------------------------------------------------------------

"""Per-tab GUI builders. Each module exposes a ``build_<tab>_tab(gui, parent)``
function; ``gui`` is the CompressorGui instance, ``parent`` the ttk.Frame."""