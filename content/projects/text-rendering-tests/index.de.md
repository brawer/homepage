---
title: "Testen der Text-Darstellung"
image: "text-rendering-tests.webp"
date: 2016-08-31
publishDate: 2026-08-25
date_range: "Seit 2016"
status: "active"
role: "creator"
tags: ["Typografie", "Google", "Unicode", "Python", "C++", "Quelloffen"]
summary: "Unicodes Testsuite für Text-Rendering-Engines"
github_url: "https://github.com/unicode-org/text-rendering-tests"
---
Ich habe dieses Projekt 2016 begonnen, während ich bei Google an
Text-Rendering arbeitete – gemeinsam mit [Behdad Esfahbod](https://behdad.org/)
brachte ich damals [Variable Schriften](https://en.wikipedia.org/wiki/Variable_font)
wieder zum Leben. Dazu war aber nötig, dass sich die
Closed-Source-Engines von Adobe, Apple und Microsoft _exakt_ so
verhalten wie der freie Software-Stack, den wir in Chrome und Android
auslieferten; ansonsten wäre die Idee gleich wieder an der
Fragmentierung der Plattformen gescheitert, genau wie schon beim
«[Schriftenkrieg](https://www.pastemagazine.com/design/adobe/the-font-wars)».
Also habe ich mich
bei anderen Firmen und bei Schriftenherstellern umgehört und diese
Testsuite zusammengestellt. Nicht gerade meine technisch
anspruchsvollste Arbeit, aber sie hat dazu beigetragen, dass die
Implementierungen in
der ganzen Branche konsistenter wurden. Inzwischen liegt das Projekt
beim Unicode-Konsortium, wo ich formal noch immer der Maintainer bin
 – auch wenn ich mittlerweile kaum noch etwas daran mache.
