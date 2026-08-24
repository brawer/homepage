---
title: "Programming Techniques in Computational Linguistics"
original_title: "Programmiertechniken der Computerlinguistik"
original_language: "de"
date: 1997-10-01
publishDate: 2026-08-23
tags: ["NLP", "Prolog"]
kind: "lecture"
venue: "Universität Zürich, Institut für Informatik, Computerlinguistik"
abstract: >
  A lecture series on programming techniques in computational
  linguistics, taught from winter semester 1997/98 through summer
  semester 1999. The winter part introduces Prolog and basic parsing
  techniques; the summer part goes deeper into chart parsing, efficient
  Prolog techniques, and formal language hierarchies. It comes with six
  downloadable Prolog programs as starting points for exercises.
image: "teaser.webp"
---
University of Zurich, [Department of Informatics](http://www.ifi.uzh.ch/),
Computational Linguistics — winter semester 1997/98 through summer
semester 1999.

I designed this course from scratch. Prolog wouldn’t necessarily have
been my first choice for it — I’m a systems programmer at heart — but
the department insisted I teach exactly this language. It looks fairly
odd from today’s vantage point, but back in the 1990s, Prolog, together
with Lisp, was *the* language of choice in artificial intelligence.

## Winter Semester

1. [Introduction](slides/ws-01-einfuehrung.pdf)
2. [Structures](slides/ws-02-strukturen.pdf)
3. [Control Flow](slides/ws-03-ablauf.pdf)
4. [Recursion](slides/ws-04-rekursion.pdf)
5. [Tracing](slides/ws-05-tracing.pdf)
6. [Lists](slides/ws-06-listen.pdf)
7. [Arithmetic](slides/ws-07-arithmetik.pdf)
8. [Term Predicates](slides/ws-08-term-praedikate.pdf)
9. [Occurs Check](slides/ws-09-occurs-check.pdf)
10. [Introduction to Parsing](slides/ws-10-parsing-einfuehrung.pdf)
11. [Review](slides/ws-11-repetition.pdf)
12. [Input/Output](slides/ws-12-ein-ausgabe.pdf)
13. [Parsing Review](slides/ws-13-parsing-repetition.pdf)
14. [Definite Clause Grammars](slides/ws-14-definit-klausel-grammatiken.pdf)
15. [Shift-Reduce Parsing](slides/ws-15-shift-reduce-parsing.pdf)
16. [Control Constructs](slides/ws-16-kontrolle.pdf)
17. [Sample Solutions for All Exercises](slides/ws-17-musterloesungen.pdf)

## Summer Semester

1. [Introduction](slides/ss-01-einfuehrung.pdf)
2. [Tokenizer](slides/ss-02-tokenizer.pdf)
3. [Parsing Review](slides/ss-03-parsing-repetition.pdf)
4. [Morphology](slides/ss-04-morphologie.pdf)
5. [Selection Restrictions](slides/ss-05-selektions-beschraenkungen.pdf)
6. [Chart Parsing](slides/ss-06-chart-parsing.pdf)
7. [Bottom-Up Chart Parsing](slides/ss-07-bottom-up-chart-parsing.pdf)
8. [Earley Parsing](slides/ss-08-earley-parsing.pdf)
9. [Edge Subsumption](slides/ss-09-kanten-subsumtion.pdf)
10. [Efficient Prolog Techniques](slides/ss-10-effiziente-prolog-techniken.pdf)
11. [Faster Parsing](slides/ss-11-schneller-parsen.pdf)
12. [Finite Automata](slides/ss-12-endliche-automaten.pdf)
13. [Language Hierarchy; Non-Context-Freeness of Zurich German](slides/ss-13-sprachenhierarchie-zuerichdeutsch.pdf)
14. [Feature Structures](slides/ss-14-merkmalstrukturen.pdf)
15. [Keyword Recognition](slides/ss-15-stichwort-erkennung.pdf)

## Prolog Programs to Download

[Tokenizer](listings/tokenizer.pl)
: A simple Prolog tokenizer.

[Definite Clause Grammar](listings/dcg.pl)
: A very simple definite clause grammar, meant as a starting point for an exercise.

[Shift-Reduce Parser](listings/shiftred.pl)
: A simple shift-reduce parser in Prolog.

[Bottom-Up Chart Parser](listings/botupchart.pl)
: A simple bottom-up chart parser in Prolog.

[Earley Parser](listings/earley.pl)
: A simple chart parser in Prolog using the Earley algorithm. Note: two bugs are left as exercises to fix!

[Keyword Recognition](listings/keyword.pl)
: A Prolog program that recognizes certain keywords in natural-language (English) input and issues corresponding “database” queries. Requires the [Tokenizer](listings/tokenizer.pl).