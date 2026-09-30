# Browser fallback: count FCC words on a lyrics page

Use this only for tracks the APIs couldn't screen. Run each snippet with the browser `javascript_exec` tool after you've navigated to the page.

Every snippet returns counts and locations only. None of them returns lyric text.

## Genius song page

The URL pattern is `https://genius.com/<Artist>-<title>-lyrics`:

- Separate words with hyphens.
- Capitalize only the first letter.
- Drop punctuation.
- Write "&" as "and."

A "Burrr!" page title means the page doesn't exist (404). Try dropping "The," or check the song on the artist's Genius page.

```js
// Runs fresh on every page. Returns: title | word count | {"word@section": n}
(() => {
  // Each key is a word to flag; each value is the regex that matches it.
  // \b = word boundary, so "cock" doesn't match "peacock". \w* catches -ing, -ed endings.
  const W = {
    fuck: /\bf+u+c+k\w*|\bmotherf\w*/gi,   // FCC, all forms
    shit: /\bshit(?!ake)\w*|\bbullshit\w*/gi, // FCC
    piss: /\bpiss\w*/gi,                   // FCC
    cunt: /\bcunt\w*/gi,                   // FCC
    cocksucker: /\bcocksuck\w*/gi,         // FCC
    cock: /\bcock(?!tail|roach|pit)s?\b/gi, // FCC
    tits: /\btits?\b|\btitties\b/gi,       // FCC
    bitch: /\bbitch\w*/gi,                 // caution
    asshole: /\bassholes?\b/gi,            // caution
    goddamn: /\bgod\s?damn\w*/gi           // caution
  };
  // Genius puts lyrics in divs marked data-lyrics-container="true"
  const cs = [...document.querySelectorAll('[data-lyrics-container="true"]')];
  if (!cs.length) return document.title.slice(0, 50) + ' | NO LYRICS';
  const lines = cs.map(c => c.innerText).join('\n').split('\n');
  let sec = 'unlabeled', agg = {}, nw = 0;
  for (const L of lines) {
    const m = L.match(/^\[([^\]]+)\]/);          // section header like [Verse 1]
    if (m) { sec = m[1].split(':')[0]; continue; }
    nw += (L.match(/\w+/g) || []).length;       // word count: a check that lyrics loaded
    for (const [k, re] of Object.entries(W)) {
      const n = (L.match(re) || []).length;
      if (n) agg[k + '@' + sec] = (agg[k + '@' + sec] || 0) + n;
    }
  }
  return document.title.slice(0, 50) + ' | ' + nw + 'w | ' + JSON.stringify(agg);
})()
```

## Any other lyrics page (AZLyrics, Bandcamp, label sites)

Pass the CSS selector for the lyrics block. Common selectors:

| Site | Selector |
|---|---|
| AZLyrics | `.col-xs-12.col-lg-8.text-center > div:not([class])` |
| Bandcamp | `.lyricsText` |

```js
// Change SEL to the lyrics element. Returns line-number hits, never text.
(() => {
  const SEL = '.lyricsText';
  const el = document.querySelector(SEL);
  if (!el) return 'NO LYRICS at ' + SEL;
  const W = /\bf+u+c+k\w*|\bmotherf\w*|\bshit(?!ake)\w*|\bpiss\w*|\bcunt\w*|\bcocksuck\w*|\bcock(?!tail|roach|pit)s?\b|\btits?\b|\bbitch\w*|\bassholes?\b|\bgod\s?damn\w*/gi;
  const lines = el.innerText.split('\n').filter(l => l.trim());
  // [line number, lowercased matched words] for each line with a hit
  const hits = lines.map((l, i) => [i + 1, (l.match(W) || []).map(w => w.toLowerCase()).join(',')]).filter(x => x[1]);
  return JSON.stringify(hits) + ' of ' + lines.length + ' lines';
})()
```

## Limits

- Each `javascript_exec` call must finish in about 35 seconds. Batch navigate-then-count pairs with `browser_batch`, about five tracks per batch.
- Tool output gets cut off at about 1,000 characters. The snippets return short strings, so that's rarely a problem.
- Close the tabs you opened when you're done.
