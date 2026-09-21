# Inspire Campaigns website

Site for Inspire Campaigns, a Vermont video and marketing studio (founder: Javi Matos Rodriguez). Plain HTML/CSS/JS, deployed on Vercel with no build step.

## How it fits together

- All HTML is generated. Edit page bodies in `pages/`, then run `python3 scripts/build-pages.py`. That script holds the shared `<head>`, nav, footer and video lightbox, the portfolio data (`PROJECTS`) and the Vermont map. Markers in page bodies expand at build time: `<!--tile:slug:classes:note-->` (video tile), `<!--waves:seed-->` (pop-art wave band) and `<!--vmap:full-->` (Vermont map).
- Each project also gets its own case-study page, `work/<slug>.html`, generated from `PROJECTS`: hero video, four stills, goal / what we made / result, a mini map, and a link to the next project.
- File names match the old Wix slugs (`/about`, `/our-work`, `/services`, `/contact-us`). Paths are root-absolute (`/assets/...`) so the `work/` pages resolve the same way.
- **Colour modes:** light, dark and "Trippy" (pop-art), picked from the emoji dropdown in the nav and saved in `localStorage` (`ic-mode`). Trippy is the default on a first visit. Tokens live at the top of `styles.css` under `[data-theme]`; sections pick a red / yellow / blue tone with `data-tone`.
- **Motion:** Lenis smooth scrolling in light and dark (off in Trippy and under reduced motion), cross-page view transitions (a project's video morphs from its tile into the case-study hero), and a circular wipe when the mode changes.
- **Vermont map:** county outlines are U.S. Census TIGERweb data shared with the Elite Real Estate Partners build (`data/vermont.json`). Pins are projected from USGS town coordinates: Burlington, Winooski (Prop Ready), Colchester (The Masters BNI) and Johnson (The Johnson Health Center).
- **Artwork:** `scripts/waves.py` draws the pop-art wave bands as inline SVG coloured by CSS variables. `assets/art/` holds public-domain Muybridge and Edison drawings cut by the agency's `research/cut-art.py`, used as CSS masks.
- Videos in `assets/video/` are re-encoded from the client's Wix uploads, and case-study stills are cut from them. The encoding scripts and source files live in the agency's project folder (`research/`), not in this repo.
- `api/contact.js` sends form submissions through Resend. Set `RESEND_API_KEY`, `CONTACT_TO` and `CONTACT_FROM` in Vercel.

## Local preview

```
python3 -m http.server 5179
```

`/api/contact` only exists on Vercel, so locally the form shows its error state after validation.

## Before launch

Search the code for `TODO(owner)`. Open items: which inbox receives leads, permission to show the UVM and Vermont State logos, confirm the BNI award date (June 2026), confirm client names for the unnamed food pop-up (its logo reads BREW) and market vendor, confirm Prop Ready's Winooski location for the map, and higher-resolution originals of the Mechayeh and market-vendor videos (only 480p was on Wix).
