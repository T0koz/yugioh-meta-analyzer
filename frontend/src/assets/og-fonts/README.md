# Polices des images de partage

Fichiers WOFF (sous-ensemble latin) des trois polices du design system, lus par `src/lib/og.tsx`
pour dessiner les images Open Graph. `next/font` ne fournit que du WOFF2, que le moteur de rendu
des images (Satori) ne lit pas : d'où ces copies. Origine : paquets npm `@fontsource/inter-tight`,
`@fontsource/jetbrains-mono`, `@fontsource/instrument-serif` (relevé du 2026-11-16).

Licence : SIL Open Font License 1.1 (https://openfontlicense.org), qui autorise la redistribution.
- Inter Tight : Copyright 2022 The Inter Project Authors (https://github.com/rsms/inter-tight)
- JetBrains Mono : Copyright 2020 The JetBrains Mono Project Authors (https://github.com/JetBrains/JetBrainsMono)
- Instrument Serif : Copyright 2022 The Instrument Serif Project Authors (https://github.com/Instrument/instrument-serif)
