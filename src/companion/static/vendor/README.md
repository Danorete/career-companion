# Vendored motion libraries

Both files are ES module bundles, tree-shaken to the few functions the app uses, so nothing loads from a CDN.

| File | Package | Version | Exports | Licence |
|---|---|---|---|---|
| `anime.js` | animejs | 4.5.0 | `animate`, `stagger` | MIT, `LICENSE-animejs.md` |
| `motion.js` | motion (mini build) | 14.12.0 | `animate` | MIT, `LICENSE-motion.md` |

To rebuild, in a scratch folder (not in this repo):

```
npm i animejs@4.5.0 motion@14.12.0 esbuild
echo "export { animate, stagger } from 'animejs';" > a.js
echo "export { animate } from 'motion/mini';" > m.js
npx esbuild a.js --bundle --minify --format=esm --outfile=anime.js
npx esbuild m.js --bundle --minify --format=esm --outfile=motion.js
```

They are loaded by `fx()` in `app.js`, which skips them when the person prefers reduced motion.
