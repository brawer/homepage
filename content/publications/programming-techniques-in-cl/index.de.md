---
title: "Programmiertechniken der Computerlinguistik"
date: 1997-10-01
publishDate: 2026-08-23
tags: ["NLP", "Prolog"]
kind: "lecture"
venue: "Universität Zürich, Institut für Informatik, Computerlinguistik"
abstract: >
  Eine Vorlesungsreihe zu Programmiertechniken der Computerlinguistik,
  gehalten vom Wintersemester 1997/98 bis und mit Sommersemester 1999.
  Der Winterteil führt in Prolog und grundlegende Parsing-Techniken ein,
  der Sommerteil vertieft Chart-Parsing, effiziente Prolog-Techniken und
  formale Sprachhierarchien. Dazu gibt es sechs herunterladbare
  Prolog-Programme als Ausgangspunkt für Übungsaufgaben.
image: "teaser.webp"
---
Universität Zürich, [Institut für Informatik](http://www.ifi.uzh.ch/),
Computerlinguistik – Wintersemester 1997/98 bis und mit Sommersemester 1999

Diese Vorlesung habe ich von Grund auf selbst konzipiert. Prolog wäre
nicht unbedingt meine erste Wahl für diesen Kurs gewesen – ich selbst
programmiere lieber systemnah –, doch das Institut bestand darauf,
dass ich genau diese Sprache unterrichte. Aus heutiger Sicht mag das
einigermassen kurios wirken, aber in den 1990er Jahren war Prolog,
zusammen mit Lisp, *die* Sprache der Wahl in der Künstlichen Intelligenz.

## Wintersemester

1. [Einführung](slides/ws-01-einfuehrung.pdf)
2. [Strukturen](slides/ws-02-strukturen.pdf)
3. [Ablauf](slides/ws-03-ablauf.pdf)
4. [Rekursion](slides/ws-04-rekursion.pdf)
5. [Tracing](slides/ws-05-tracing.pdf)
6. [Listen](slides/ws-06-listen.pdf)
7. [Arithmetik](slides/ws-07-arithmetik.pdf)
8. [Term-Prädikate](slides/ws-08-term-praedikate.pdf)
9. [Occurs Check](slides/ws-09-occurs-check.pdf)
10. [Parsing-Einführung](slides/ws-10-parsing-einfuehrung.pdf)
11. [Repetition](slides/ws-11-repetition.pdf)
12. [Ein-/Ausgabe](slides/ws-12-ein-ausgabe.pdf)
13. [Parsing-Repetition](slides/ws-13-parsing-repetition.pdf)
14. [Definit-Klausel-Grammatiken](slides/ws-14-definit-klausel-grammatiken.pdf)
15. [Shift-Reduce-Parsing](slides/ws-15-shift-reduce-parsing.pdf)
16. [Kontrolle](slides/ws-16-kontrolle.pdf)
17. [Musterlösungen zu allen Aufgaben](slides/ws-17-musterloesungen.pdf)

## Sommersemester

1. [Einführung](slides/ss-01-einfuehrung.pdf)
2. [Tokenizer](slides/ss-02-tokenizer.pdf)
3. [Parsing-Repetition](slides/ss-03-parsing-repetition.pdf)
4. [Morphologie](slides/ss-04-morphologie.pdf)
5. [Selektions-Beschränkungen](slides/ss-05-selektions-beschraenkungen.pdf)
6. [Chart-Parsing](slides/ss-06-chart-parsing.pdf)
7. [Bottom-Up-Chart-Parsing](slides/ss-07-bottom-up-chart-parsing.pdf)
8. [Earley-Parsing](slides/ss-08-earley-parsing.pdf)
9. [Kanten-Subsumtion](slides/ss-09-kanten-subsumtion.pdf)
10. [Effiziente Prolog-Techniken](slides/ss-10-effiziente-prolog-techniken.pdf)
11. [Schneller Parsen](slides/ss-11-schneller-parsen.pdf)
12. [Endliche Automaten](slides/ss-12-endliche-automaten.pdf)
13. [Sprachenhierarchie; Nicht-Kontextfreiheit des Zürichdeutschen](slides/ss-13-sprachenhierarchie-zuerichdeutsch.pdf)
14. [Merkmalstrukturen](slides/ss-14-merkmalstrukturen.pdf)
15. [Stichwort-Erkennung](slides/ss-15-stichwort-erkennung.pdf)

## Prolog-Programme zum Herunterladen

[Tokenizer](listings/tokenizer.pl)
: Ein einfacher Prolog-Tokenizer.

[Definit-Klausel-Grammatik](listings/dcg.pl)
: Eine sehr einfache Definit-Klausel-Grammatik, die als Ausgangspunkt für eine Übungsaufgabe dient.

[Shift-Reduce-Parser](listings/shiftred.pl)
: Ein einfacher Shift-Reduce-Parser in Prolog.

[Bottom-Up-Chart-Parser](listings/botupchart.pl)
: Ein einfacher Bottom-Up-Chart-Parser in Prolog.

[Earley-Parser](listings/earley.pl)
: Ein einfacher Chart-Parser in Prolog, der den Earley-Algorithmus benutzt. Achtung: zwei Fehler sind als Übungsaufgaben zu korrigieren!

[Stichwort-Erkennung](listings/keyword.pl)
: Ein Prolog-Programm, das in einer natürlichsprachlichen (englischen) Eingabe bestimmte Stichwörter erkennt und daraufhin entsprechende «Datenbank»-Anfragen stellt. Benötigt den [Tokenizer](listings/tokenizer.pl).
