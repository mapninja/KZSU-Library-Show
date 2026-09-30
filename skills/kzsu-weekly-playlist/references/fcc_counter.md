# FCC word counter for Genius lyric pages

Run this with the browser's `javascript_exec` tool after navigating to a Genius song page. It returns only the page title, a word count and the offending words by section. It never returns lyric text.

```js
// Wrap in an arrow function so it runs fresh on every page (navigation clears window variables)
(() => {
  // Each key is a word to flag; each value is a regex that matches it.
  // \b means "word boundary" so "cock" doesn't match "peacock". \w* catches endings like -ing, -ed.
  const W = {
    fuck: /\bf+u+c+k\w*/gi,          // FCC: all forms
    shit: /\bshit\w*/gi,             // FCC
    piss: /\bpiss\w*/gi,             // FCC
    cunt: /\bcunt\w*/gi,             // FCC
    cocksucker: /\bcocksucker\w*/gi, // FCC
    cock: /\bcock(s)?\b/gi,          // FCC
    tits: /\btits?\b/gi,             // FCC
    bitch: /\bbitch\w*/gi,           // caution
    asshole: /\bassholes?\b/gi,      // caution
    goddamn: /\bgod\s?damn\w*/gi     // caution
  };
  // Genius puts lyrics in one or more divs marked data-lyrics-container="true"
  const cs = [...document.querySelectorAll('[data-lyrics-container="true"]')];
  if (!cs.length) return document.title.slice(0, 50) + ' | NOLYR';  // no lyrics posted
  // innerText keeps line breaks, so we can split into lines
  const lines = cs.map(c => c.innerText).join('\n').split('\n');
  let sec = 'unlabeled', agg = {}, nw = 0;
  for (const L of lines) {
    // Section headers look like [Verse 1] or [Chorus: Artist]; remember the current one
    const m = L.match(/^\[([^\]]+)\]/);
    if (m) { sec = m[1].split(':')[0]; continue; }
    nw += (L.match(/\w+/g) || []).length;  // running word count, a sanity check that lyrics loaded
    for (const [k, re] of Object.entries(W)) {
      const n = (L.match(re) || []).length;
      if (n) agg[k + '@' + sec] = (agg[k + '@' + sec] || 0) + n;  // e.g. "fuck@Chorus": 2
    }
  }
  return document.title.slice(0, 50) + ' | ' + nw + 'w | ' + JSON.stringify(agg);
})()
```

## Line position when a page has no section labels

```js
// Returns [line number, matched word] pairs plus the total line count. No lyric text.
(() => {
  const cs = [...document.querySelectorAll('[data-lyrics-container="true"]')];
  const lines = cs.map(c => c.innerText).join('\n').split('\n').filter(l => l.trim());
  const hits = lines.map((l, i) => [i + 1, (l.match(/\bf+u+c+k\w*|\bshit\w*/gi) || []).join(',')]).filter(x => x[1]);
  return JSON.stringify(hits) + ' of ' + lines.length + ' lines';
})()
```

## Tips

- A "Burrr!" page title means the URL guess was wrong (404). Try dropping "The," spelling out "&" as "and," or removing punctuation.
- Genius returns HTML instead of JSON to scripted `fetch()` calls on `/api/search`, so navigate page by page instead.
- Each javascript_exec call must finish in about 35-45 seconds. Keep loops short.
