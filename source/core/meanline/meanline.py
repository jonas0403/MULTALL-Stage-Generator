# ------------------------------------------------------------------
# File:    source/core/meanline/meanline.py
# Author:  Jonas Scholz
# Purpose: Compatibility redirect to the split solver (coordinator.py).
# ------------------------------------------------------------------

# The former 819-line implementation was decomposed (Session 23) into
# initialization / stage_iteration / tpr_convergence / results, driven by
# coordinator. Untouched backup: old/meanline_before_split.py.
# This redirect keeps every existing `... import meanline` working unchanged.

from source.core.meanline.coordinator import meanline

__all__ = ["meanline"]
