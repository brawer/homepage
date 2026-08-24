% ============================================================
% botUpChartParse.pl
%
% A simple bottom-up chart parser
%
% Example Query:
% ?- parse(s, [the,cat,sings]).
%
% The program was taken from [Gazdar/Mellish, 1989], but it
% has been modified to a large extent.
% ============================================================

% Representation of edges
% -----------------------
% All edges (both inactive and active) are asserted as Prolog
% facts edge/6. They have the following form:
%
% edge(ID, StartVertex, EndVertex, Category, Found, ToFind)
% ID:          a unique identification number for the edge
% StartVertex: the vertex number where the edge starts
% EndVertex:   the vertex number where the edge ends
% Category:    the category of the edge
% Found:       a list of those inactive edges that lead to the
%              part "before the dot" -- in reversed order.
%              either an edge ID or a term lex/1
% ToFind:      a list of categories which have yet to be found
%              in order to make the edge complete (i.e. the
%              part "after the dot")
%
% Examples
% --------
% edge(101, 1, 2, det, [lex(the)], []).  % <1,2> det --> the .
% edge(102, 1, 1, np,  [], [det, n]).    % <1,1> np  --> . det n
% edge(103, 1, 2, np,  [101], [n]).      % <1,2> np --> det . n
% edge(104, 2, 3, n,   [lex(cat)], []).  % <2,3> n  --> cat .
% edge(105, 1, 3, np,  [104, 101], []).  % <1,3> np --> det n .
% edge(106, 1, 1, s,   [], [np, vp]).    % <1,1> s --> . np vp

% Tell Prolog that edge/6 will be modified dynamically, i.e.
% with assert and retract.
:- dynamic(edge/6).


test :-
	parse(s, [the,cat,sings]).       % for debugging


% ------------------------------------------------------------
% parse(+Symbol, +String)
% ------------------------------------------------------------
% Tries to parse String as Symbol, according to a phrase-
% structure grammar given at the end of the listing.
% Initializes the chart and performs bottom-up parsing
% (with start_chart/3). Then, all edges are retrieved
% - that span the entire chart
% - and that are inactive (i.e. don't need any more things in
%   order to be complete)
% - and whose category is Symbol.
% ==> write the ID for these edges on the screen.

parse(Symbol, String) :-
	V0 is 1,
	start_chart(V0, Vn, String),
	foreach(edge(ID, V0, Vn, Symbol, /* Found */ _, /* ToFind */ []),
		(write('Found parse: Edge #'), write(ID), nl)),
	retractall(edge(_,_,_,_,_,_)).


% ------------------------------------------------------------
% start_chart(+StartVertex, -EndVertex, +SentenceList)
% ------------------------------------------------------------
% Initializes the chart (starting at StartVertex) with edges
% for the terminal symbols in SentenceList. Performs a
% bottom-up chart parsing (see add_edge below). Returns the
% last vertex in EndVertex.

start_chart(V, V, []).                     % termination

start_chart(Vfirst, Vlast, [Word | Words]) :-
	Vfirst_plus_1 is Vfirst + 1,
	foreach(word(Cat, Word),
		add_edge(Vfirst, Vfirst_plus_1, Cat,
			/* Found */ [lex(Word)],
			/* ToFind */ [])),
	start_chart(Vfirst_plus_1, Vlast, Words).


% ------------------------------------------------------------
% add_edge -- case 1: attempt to add an existing edge
% ------------------------------------------------------------
% Edges are only added to the chart if no such edge is in
% the chart yet.

add_edge(Vfrom, Vto, Cat, Found, ToFind) :-
	% The next line succeeds only if the to-be-added edge is
	% already in the edge. Otherwise, backtracking occurs
	% and another clause of add_edge/5 is called.
	edge(ID, Vfrom, Vto, Cat, Found, ToFind),
	!,
	write('Ignoring: '),
	write_edge(edge(ID, Vfrom, Vto, Cat, Found, ToFind)).


% ------------------------------------------------------------
% add_edge -- case 2: add an inactive edge
% ------------------------------------------------------------
% When an inactive edge I of category Cat is to be added:
% 1. add I to the chart
% 2. for each grammar rule
%    - where the leftmost symbol in the right-hand side = Cat
%      (i.e. the rule is of the form LHS --> Cat Cs)
%    ==> add an active edge that needs I to the chart
% 3. for each active edge A
%    - that immediately precedes I
%      (i.e. end vertex of A = start vertex of I)
%    - and that can combine with I
%      (i.e. A needs an edge of I's category)
%    ==> add the combination of A with I to the chart

add_edge(V1, V2, Cat, Found, []) :-
	new_id(ID),
	assert_edge(edge(ID, V1, V2, Cat, Found, [])),
	foreach(rule(LHS, [Cat | Cs]),
		add_edge(V1, V1, LHS,
			/* Found */  [],
			/* ToFind */ [Cat | Cs])),
	foreach(edge(_, V0, V1, LeftCat, LeftFound, [Cat | LeftToFind]),
		 add_edge(V0, V2, LeftCat,
			/* Found */  [ID | LeftFound],
			/* ToFind */ LeftToFind)).


% ------------------------------------------------------------
% add_edge -- case 3: add an active edge
% ------------------------------------------------------------
% When an active edge A is to be added:
% 1. add A to the chart
% 2. for each inactive edge I
%    - that immediately follows A
%      (i.e. end vertex of A = start vertex of I)
%    - and that can combine with A
%      (i.e. A needs an edge of I's category)
%    ==> add the combination of A with I to the chart

% Example
% -------
%   <2,3> VP --> V . NP PP   <V0,V1> Cat --> Found . [M1|MRest]
% + <3,5> NP --> Det N .     <V1,V2> M1  --> _ .
% ------------------------   ----------------------------------
% = <2,5> VP --> V NP . PP   <V0,V2> Cat --> Found+M1 . MRest

add_edge(V0, V1, Cat, Found, [M1|MRest]) :-
	new_id(ID),
	assert_edge(edge(ID, V0, V1, Cat, Found, [M1|MRest])),
	foreach(edge(InactiveEdgeID, V1, V2, M1, _, []),
		add_edge(V0, V2, Cat,
			/* Found */  [InactiveEdgeID | Found],
			/* ToFind */ MRest)).


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

write_edge(edge(ID, V1, V2, Category, Found, ToFind)) :-
	write(ID), write(':'),
	write('<'), write(V1), write(','),
	write(V2), write('>  '),
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
% new_id(-ID)
% ------------------------------------------------------------
% Returns a new, unique identification number. Upon each call,
% a different number will be returned.

:- dynamic(last_id/1).
last_id(100).
new_id(Result) :-
	last_id(LastID),
	Result is LastID + 1,
	retract(last_id(LastID)),
	asserta(last_id(Result)).


% ------------------------------------------------------------
% Phrase Structure Rules
% ------------------------------------------------------------

rule(s,  [np, vp]).             % S --> NP VP
rule(np, [det, n]).             % NP --> Det N
rule(vp, [v]).                  % VP --> V
rule(vp, [v, np]).              % VP --> V NP


% ------------------------------------------------------------
% Lexicon
% ------------------------------------------------------------

word(det, the).
word(det, a).
word(n, dog).
word(n, cat).
word(v, chases).
word(v, sees).
word(v, sings).
