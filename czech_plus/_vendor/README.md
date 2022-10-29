# Why vendoring? Why not `poetry`?


We use `poerty` for dev dependencies, but unfortunately Anki doesn't support
dependencies in addons, and we must use vendoring in production.

If you can propose a better way, please open an issue!

For now, you can install vendor dependencies with `vendoring sync`.
