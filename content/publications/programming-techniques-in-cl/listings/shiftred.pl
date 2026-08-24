% ============================================================
% shiftred.pl
%
% A Bottop-Up Shift-Reduce Parser
%
% Example Query:
% ?- parse([the,dog,sees,the,cat], [s]).
%
% Taken from [Covington, 1994].
% ============================================================


% ------------------------------------------------------------
% parse(+S, ?Result)
% ------------------------------------------------------------
% parses input string S, where Result is list of categories
% to which it reduces.

parse(S, Result) :-
	shift_reduce(S, [], Result).


% ------------------------------------------------------------
% shift_reduce(+String, +Stack, ?Result)
% ------------------------------------------------------------
% parses input string S, where Stack is list of categories
% parsed so far.

shift_reduce([], Stack, Stack).

shift_reduce(String, Stack, Result) :-
	shift(Stack, String, NewStack, NewString),
	reduce(NewStack, ReducedStack),
	shift_reduce(NewString, ReducedStack, Result).


% ------------------------------------------------------------
% shift(+Stack, +String, -NewStack, -NewString)
% ------------------------------------------------------------
% shifts first element from S onto Stack.

shift(Stack, [Word|S], [Word|Stack], S).


% ------------------------------------------------------------
% reduce(+Stack, -ReducedStack)
% ------------------------------------------------------------
% repeatedly reduces beginning of Stack
% to form fewer, larger constitutents.

reduce(Stack, ReducedStack) :-
	brule(Stack, Stack2),
	reduce(Stack2, ReducedStack).

reduce(Stack, Stack).


% ------------------------------------------------------------
% Phrase Structure Rules
% ------------------------------------------------------------
brule([vp, np | X], [s | X]).              % S --> NP VP
brule([n, det | X], [np | X]).             % NP --> Det N
brule([np, v  | X], [vp | X]).             % VP --> V NP
brule([v      | X], [vp | X]).             % VP --> V

brule([Word   | X], [Cat | X]) :-
	word(Cat, Word).


% ------------------------------------------------------------
% Lexicon
% ------------------------------------------------------------
word(det, the).
word(n, dog).
word(n, cat).
word(v, chase).
word(v, chases).
word(v, see).
word(v, sees).
