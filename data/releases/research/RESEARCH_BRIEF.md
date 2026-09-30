# Research brief: upcoming releases for DJ Stace (KZSU "The Library")

Today is Tuesday, Sept. 29, 2026. Stace plays indie, garage/psych, post-punk, '90s indie, stoner rock, wry songwriters, goth/darkwave, Americana, soul/funk. The show leans heavily to new releases; she airs advance singles in heavy rotation.

## Goal
Find UPCOMING releases (albums, EPs, notable reissues/live albums) with a release date from **2026-09-29 through 2027-06-30**, plus **new singles released 2026-09-01 or later** (standalone or ahead of an album). Also include albums released **2026-09-18 to 2026-09-28** marked status "just_out" (so she doesn't miss them).

## Tools
- Use **WebSearch** (load it with ToolSearch "select:WebSearch" first). Run many searches: e.g. `"<label>" new album 2026 announce`, `"<label>" October 2026 release`, `<artist> new album 2027`, `site:stereogum.com <label>`, `site:brooklynvegan.com <artist> new album`. Good sources: label news pages, Stereogum, BrooklynVegan, Pitchfork news, Paste, Under the Radar, Consequence, The Line of Best Fit, Exclaim, NME, Uncut, Aquarium Drunkard, Bandcamp Daily, Loud and Quiet, The Quietus, Gorilla vs Bear, Post-Trash, Glide.
- Web fetch is disabled by org policy. Do not attempt it or any workaround (no curl/python HTTP).
- Do not use any browser tools.
- Verify each date/label from at least one search result that states it. If only a year/month is known, use "2027-02" or "2026-TBA". Don't invent anything. Omit items you can't substantiate.
- Ignore releases dated before 2026-09-18.

## Output
Write a JSON array with the Write tool to the file path given in your task. One object per release:

```json
{
  "artist": "Bodega",
  "title": "All Inside Aquarium",
  "type": "album",            // album | EP | single | reissue | live | compilation
  "label": "Chrysalis",
  "release_date": "2026-10-09", // YYYY-MM-DD, YYYY-MM, or YYYY-TBA
  "status": "announced",      // announced | just_out | single_out | rumored
  "latest_single": "Literary World",
  "single_date": "2026-09-16",   // or ""
  "preview_url": "https://www.youtube.com/watch?v=...",  // YouTube, Bandcamp or label page, only if a result gave it; else ""
  "source_url": "https://...",   // page that confirms date/label
  "source_name": "Stereogum",
  "pull_quote": "Short (under 25 words) quote from press or the band, verbatim from a result snippet, or \"\"",
  "notes": "producer, tour, format, anything useful for radio (e.g. 'lead single has profanity')",
  "found_via": "label:Chain Smoking Records"   // or artist:<name> or aggregator:<site>
}
```

Also append at the end a final object `{"_checked": ["list of every label/artist you searched", ...], "_nothing_found": ["labels/artists with no upcoming release found"]}` so coverage can be audited.

Your final message: a 3-5 line summary (count of releases, any problems). Don't paste the JSON in the message.
