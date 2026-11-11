"""One module per section of the film, in story order. Each exports shots(env) -> {shot id: spec}.

A spec is {'render': fn(ctx, t, f, u), 'palette'?: str | (a, b, k) | fn(t, u), 'camera'?: fn(t, f, u) -> dict}.
Cut times, lines, colour states and transitions are NOT given here: they come from STORYBOARD.md.
"""
