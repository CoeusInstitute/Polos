# Polos brand assets

This folder holds the images referenced by the project `README.md`.

## Required file

| File | Used by | Notes |
|---|---|---|
| `polos-logo.png` | root `README.md` header (dark theme + fallback) | The Polos wordmark/logo. Recommended width ~840px (displayed at 420px). Transparent background. This is the variant shown on GitHub **dark** mode and as the universal fallback. |
| `polos-logo-light.png` | root `README.md` header (light theme) | A **dark or full-color** variant of the same logo for GitHub **light** mode. If your primary logo is white, this file prevents it from disappearing on the near-white light-mode background. |

The `README.md` header uses a `<picture>` element that swaps the logo by color scheme, so:

1. Save your primary (white/light) logo as `docs/assets/polos-logo.png`.
2. Save a dark or full-color version as `docs/assets/polos-logo-light.png`.

If you only have one version, you can point both filenames at the same file, but a white-on-transparent
logo will be hard to see in GitHub light mode, so a contrasting light-mode variant is strongly
recommended. No README edits are needed once the files are in place.
