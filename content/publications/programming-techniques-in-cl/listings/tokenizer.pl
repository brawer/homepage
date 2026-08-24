/************************************************************
 * read_atomics(-Atomics)
 *
 *  Reads a line of text, breaking it into a list of atomic
 *  terms.
 *
 *  Example: "This is an example." [this,is,an,example,'.'].
 *
 *  Source: [Covington, 1994], Appendix B
 ************************************************************/

read_atomics(Atomics) :-
	read_char(FirstChar, FirstType),
	complete_line(FirstChar, FirstType, Atomics).



% read_char(-Char, -Type)
%  Reads a character and runs it through char_type/1.

read_char(Char, Type) :-
	get0(EnteredChar),
	char_type(EnteredChar, Type, Char).



% complete_line(+FirstChar, +FirstType, -Charlists)
%  Given FirstChar (the first character) and FirstType (its type),
%  reads and tokenizes the rest of the line into atoms and numbers.

complete_line(_, end, []) :- !.                   % stop at end

complete_line(_, blank, Atomics) :-               % skip blanks
	!,
	read_atomics(Atomics).

complete_line(FirstChar, special, [A|Atomics]) :- % special char
	!,
	name(A, [FirstChar]),
	read_atomics(Atomics).

complete_line(FirstChar, alpha, [A|Atomics]) :-   % begin word
	complete_word(FirstChar, alpha, Word, NextChar, NextType),
	name(A, Word),
	complete_line(NextChar, NextType, Atomics).


% complete_word(+FirstChar, +FirstType,
%               -List, -FollowChar, -FollowType)
%  Given FirstChar (the first character) and FirstType (its type),
%  reads the rest of a word, putting its characters into List.

complete_word(FirstChar, alpha, [FirstChar|List], FollowChar, FollowType) :-
	!,
	read_char(NextChar, NextType),
	complete_word(NextChar, NextType, List, FollowChar, FollowType).

complete_word(FirstChar, FirstType, [], FirstChar, FirstType).
	% where FirstType is not alpha; otherwise, the first clause
	% for complete_word would have been taken.


% char_type(+Code, ?Type, -NewCode)
%  Given an ASCII code, classifies the character as
%  'end' (of line/file), 'blank', 'alpha'(numeric), or 'special'.
%  and changes it to a potentially different character (NewCode).

char_type(10,end,10) :- !.       % UNIX end of line mark
char_type(13,end,13) :- !.       % Macintosh/DOS end of line mark
char_type(-1,end,-1) :- !.       % get0 end of file code

char_type(Code,blank,32) :-      % blanks, other control codes
	Code =< 32,
	!.

char_type(Code,alpha,Code) :-    % digits
	48 =< Code, Code =< 57,
	!.

char_type(Code,alpha,Code) :-    % lower-case letters
	97 =< Code, Code =< 122,
	!.

char_type(Code,alpha,NewCode) :- % upper-case letters
	65 =< Code, Code =< 90,
	!,
	NewCode is Code + 32.       % translate to lower case

char_type(Code,special,Code).
