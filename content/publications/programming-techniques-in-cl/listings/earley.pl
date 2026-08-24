% ============================================================
% earley.pl
%
% A chart parser which uses Earley's algorithm.
%
% Caution
% -------
% There are two problems with this program:
% - rules whose right-hand side is empty (epsilon rules) do
%   not work
% - the test for edge subsumption is not implemented
%
% These are left as exercises.
%
% Example Query:
% ?- parse(s, [the,cat,sings]).
%
% The program was taken from [Covington, 1994], but it
% has been modified to some extent.
% ============================================================

% Representation of edges
% -----------------------
% All edges (both inactive and active) are asserted as Prolog
% facts edge/5. They have the following form:
%
% edge(StartVertex, EndVertex, Category, Found, ToFind)
% StartVertex: the vertex number where the edge starts
% EndVertex:   the vertex number where the edge ends
% Category:    the category of the edge
% Found:       a list of categories which have already been
%              found (i.e. the part "before the dot"),
%              in reversed order (for efficiency reasons)
% ToFind:      a list of categories which have yet to be found
%              in order to make the edge complete (i.e. the
%              part "after the dot")
%
% Examples (= edges inserted for "the cat sings")
% -----------------------------------------------
% edge(1, 1, s,   [], [np, vp]).       % <1,1> S --> . NP VP
% edge(1, 1, np,  [], [np, conj, np]). % <1,1> NP --> . NP Conj NP
% edge(1, 1, np,  [], [det, n]).       % <1,1> NP --> . Det N
% edge(1, 2, det, [the], []).          % <1,2> Det --> the .
% edge(1, 2, np,  [det], [n]).         % <1,2> NP --> Det . N
% edge(2, 3, n,   [cat], []).          % <2,3> N --> cat .
% edge(1, 3, np,  [n, det], []).       % <1,3> NP --> Det N .
% edge(1, 3, np,  [np], [conj, np]).   % <1,3> NP --> NP . Conj NP
% edge(1, 3, s,   [np], [vp]).         % <1,3> S --> NP . VP
% edge(3, 3, vp,  [], [v]).            % <3,3> VP --> . V
% edge(3, 3, vp,  [], [v, np]).        % <3,3> VP --> . V NP
% edge(3, 4, v,   [sings], []).        % <3,4> V --> sings .
% edge(3, 4, vp,  [v], [np]).          % <3,4> VP --> V . NP
% edge(3, 4, vp,  [v], []).            % <3,4> VP --> V .
% edge(1, 4, s,   [vp, np], []).       % <1,4> S --> NP VP .


% Tell Prolog that edge/5 will be modified dynamically, i.e.
% with assert and retract.
:- dynamic(edge/5).

test :-
	parse(s, [the, cat, sees, a, dog]).

parse(StartSymbol, Sentence) :-
	clear_chart,
	write('Initialization'), nl,
	foreach(
	  rule(StartSymbol, RHS),
	  add_to_chart(edge(
		/* StartVertex */ 1,
		/* EndVertex */   1,
		/* Category */    StartSymbol,
		/* Found */       [],
		/* ToFind */      RHS))),
	process(Sentence, /* first vertex */ 1, LastVertex),
	!,
	% Test whether there exists any edge which spans the
	% entire chart, is of category StartSymbol and inactive.
	edge(
		/* StartVertex */ 1,
		/* EndVertex */   LastVertex,
		/* Category */    StartSymbol,
		/* Found */       _,
		/* ToFind */      []).


process([], LastVertex, LastVertex).
process([Word|Words], Vertex, LastVertex) :-
	nl, write('Predictor for '), write(Vertex), write(':'), nl,
	predictor(Vertex),

	nl, write('Scanner for '), write(Vertex), write(':'), nl,
	scanner(Word, Vertex, NextVertex),

	nl, write('Completer for '), write(NextVertex), write(':'), nl,
	completer(NextVertex),

	process(Words, NextVertex, LastVertex).


% ------------------------------------------------------------
% predictor(+Vertex)
% ------------------------------------------------------------
% For every active edge which is ending at Vertex and is look-
% ing for a symbol FirstToFind, predict new active edges of
% category FirstToFind.
%
% Example
% =======
% Assume that <1,3> s --> np . vp is in the chart, and that
% predictor(3) is called. This leads to a call of
% predict(vp, 3) -- which will in turn lead to an insertion
% of <3,3> vp --> . v and <3,3> vp --> . v np

predictor(Vertex) :-
	foreach(
	  edge(/*StartVertex*/ _, /* EndVertex */ Vertex,
	       /* Category */  _, /* Found */     _,
	       /* ToFind*/     [FirstToFind | _]),
	  predict(FirstToFind, Vertex)).


% ------------------------------------------------------------
% predict(+Nonterminal, +Vertex)
% ------------------------------------------------------------
% A helper predicate for predictor(+Vertex).
%
% Example
% =======
% Assume: rule(s,[np,vp]). rule(np,[det,n]).
% Upon calling predict(s, 1), the following edges will be added:
% <1,1> s  --> . np vp
% <1,1> np --> . det n

predict(Nonterminal, Vertex) :-
	rule(Nonterminal, [First|Rest]),
	add_to_chart(edge(
		/* StartVertex */ Vertex,
		/* EndVertex */   Vertex,
		/* Category */    Nonterminal,
		/* Found */       [],
		/* ToFind */      [First|Rest])),
	predict(First, Vertex),
	fail.

predict(_,_).


% ------------------------------------------------------------
% scanner(+Word, +Vertex, -NextVertex)
% ------------------------------------------------------------
% Looks up a word in the lexicon. For every reading of Word,
% a corresponding inactive preterminal edge is inserted
% into the chart.

scanner(Word, Vertex, NextVertex) :-
	NextVertex is Vertex + 1,
	foreach(
	  word(Category, Word),
	  add_to_chart(edge(
		/* StartVertex */ Vertex,
		/* EndVertex */   NextVertex,
		/* Category */    Category,
		/* Found */       [Word],
		/* ToFind */      []))).


% ------------------------------------------------------------
% completer(+Vertex)
% ------------------------------------------------------------
% For every inactive edge ending at Vertex, complete all
% possible higher constituents.

completer(Vertex) :-
	foreach(
	  edge(
		/* StartVertex */ InactiveStart,
		/* EndVertex */   Vertex,
		/* Category */    InactiveCategory,
		/* Found */       _,
		/* ToFind */      []),
	  complete(InactiveStart, Vertex, InactiveCategory)).


% ------------------------------------------------------------
% complete(+InactiveStart, +InactiveEnd, +InactiveCategory)
% ------------------------------------------------------------
% Applies the Fundamental Rule of Chart Parsing.

complete(InactiveStart, InactiveEnd, InactiveCategory) :-
	edge(
		/* StartVertex */ ActiveStart,
		/* EndVertex */   InactiveStart,
		/* Category */    ActiveCategory,
		/* Found */       ActiveFound,
		/* ToFind */      [InactiveCategory|RestToFind]),
	add_to_chart(edge(
		/* StartVertex */ ActiveStart,
		/* EndVertex */   InactiveEnd,
		/* Category */    ActiveCategory,
		/* Found */       [InactiveCategory|ActiveFound],
		/* ToFind */      RestToFind)),

	% If the result of the completion is an inactive edge,
	% call the completer recursively.
	(/* if this condition holds */ RestToFind == []
	 -> complete(ActiveStart, InactiveEnd, ActiveCategory)),

	fail.

complete(_, _, _).


% ------------------------------------------------------------
% add_to_chart
% ------------------------------------------------------------
% Edges are only added to the chart if a "similar" edge is not
% already part of the chart. Note that the definition of
% "similar" is not trivial; many textbooks discuss this
% in depth.
% The implementation of add_to_chart below leads to problems
% with some grammars; a better implementation will be provided
% with the solutions to the exercises.

add_to_chart(Edge) :-
	\+ call(Edge),
	assert_edge(Edge).


% ------------------------------------------------------------
% clear_chart
% ------------------------------------------------------------
% Removes all edges from the chart.

clear_chart :-
	retractall(edge(_,_,_,_,_)).


% ------------------------------------------------------------
% assert_edge(+Edge)
% ------------------------------------------------------------
% Adds an edge into the chart with assert. For debugging, the
% added edge is written to the screen as well.

assert_edge(Edge) :-
	asserta(Edge),
	write_edge(Edge).


% ------------------------------------------------------------
% write_edge(+Edge)
% ------------------------------------------------------------
% Writes an edge to the screen.

write_edge(edge(Vfrom, Vto, Category, Found, ToFind)) :-
	write('<'), write(Vfrom), write(','),
	write(Vto), write('>  '),
	write(Category), write(' --> '), write_list(Found),
	write(' . '), write_list(ToFind),
	nl.

write_list([]).
write_list([First|Rest]) :-
	write(First),
	write(' '),
	write_list(Rest).


% ------------------------------------------------------------
% foreach(+X, +Y)
% ------------------------------------------------------------
% Applies a failure-driven loop to find all possible solutions
% for X. For each one, Y is called once.

foreach(X, Y) :-
	call(X),
	once(Y),
	fail.

foreach(_, _) :-
	true.


% ------------------------------------------------------------
% once(+Goal)
% ------------------------------------------------------------
% Calls Goal once; will fail upon backtracking.

once(Goal) :-
	call(Goal),
	!.


% ------------------------------------------------------------
% Phrase Structure Rules
% ------------------------------------------------------------
% Note that these rules do not contain pre-terminal rules,
% for instance "N --> cat". Therefore, the part below is
% not the entire context-free phrase structure grammar.

rule(s,  [np, vp]).             % S --> NP VP
rule(np, [np, conj, np]).		% NP --> NP Conj NP
rule(np, [det, n]).             % NP --> Det N
rule(vp, [v]).                  % VP --> V
rule(vp, [v, np]).              % VP --> V NP


% ------------------------------------------------------------
% Lexicon
% ------------------------------------------------------------
% Of course, the lexicon could be a more complicated program,
% for instance it could provide some sort of morphological
% processing.

word(det,     the).
word(det,     a).
word(n,       dog).
word(n,       cat).
word(v,       sings).
word(v,       chases).
word(v,       sees).
word(conj,    and).
word(conj,    or).
