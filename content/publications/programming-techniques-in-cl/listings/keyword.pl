% ============================================================
% keyword.pl
%
% A keyword-based natural-language interface to a database
% with employees in a company.
%
% Usage:
%  1. ?- [keyword].              % consult this file
%  2. ?- process_queries.        % start
%  3. who works as a programmer? % enter your queries
%     fire all underpaid men     % etc.
%  4. quit                       % stop by entering "quit"
%
% Taken from [Covington, 1994], but with large modifications.
% ============================================================

% Ensure that the tokenizer is loaded.
:- ensure_loaded('tokenizer.pl').

% ------------------------------------------------------------
% process_queries
% ------------------------------------------------------------
% Asks the user to enter a query and processes the entered
% query.

process_queries :-
	repeat,
		write('Query: '),
		read_atomics(Words),
		process_query(Words),
	Words == [quit],
	!.

% ------------------------------------------------------------
% process_query(+Query)
% ------------------------------------------------------------
% Processes a single query. Call process_query_chattering in
% order to generate output which can be useful for debugging.
%
% Query: A list of tokens, e.g. [tell,me,who,is,the,boss,'.']

process_query(Query) :-
	filter(Query, Filtered),
	translate(Filtered, X, TestsOnX, Actions),
	findall(X, TestsOnX, MatchingEmployees),
	execute_query(Actions, MatchingEmployees).

process_query_chattering(Query) :-
	filter(Query, Filtered),
	write('Filtered: '), write(Filtered), nl,
	translate(Filtered, X, TestsOnX, Actions),
	write('Tests on '), write(X), write(': '), write(TestsOnX), nl,
	write('Actions: '), write(Actions), nl,
	findall(X, TestsOnX, MatchingEmployees),
	write('Matching Employees: '), write(MatchingEmployees),
	execute_query(Actions, MatchingEmployees).


% ------------------------------------------------------------
% execute_query(+Actions, +Employees)
% ------------------------------------------------------------
% If one or more action keywords were found, execute these
% actions by calling execute_actions/2. Otherwise, display
% the matching employees.
%
% Actions:   A list of actions, e.g. [display_records]
% Employees: A list with the IDs of matching employees,
%            for instance [1001, 1004, 1009]

execute_query([], Employees) :-
	display_records(Employees), !.

execute_query(Actions, Employees) :-
	execute_actions(Actions, Employees).


% ------------------------------------------------------------
% execute_actions(+Actions, +Employees)
% ------------------------------------------------------------
% For each element of the Actions list, a term is constructed
% which has that element as its functor and the entire Employee
% list as its single argument.  Then, call is used to invoke
% that predicate.
%
% Example: execute_actions([display_records, remove_records],
%                          [1001,1004,1009])
% call -----> display_records([1001,1004,1009])
% call -----> remove_records([1001,1004,1009])

execute_actions([], _).
execute_actions([Action|Actions], Employees) :-
	Command =.. [Action, Employees],
	call(Command),
	execute_actions(Actions, Employees).



% ------------------------------------------------------------
% translate(+KeywordSemantics, ?Variable, -Tests, -Actions)
% ------------------------------------------------------------
% Translates a list of keyword semantics into a number of
% tests over Variable and into a number of actions to be
% performed on the employees which pass the tests.
%
% KeywordSemantics: List of keyword semantics
% Tests:            Single Prolog term which can be passed
%                   to findall in order to determine the
%                   matching employees.
% Actions:          Actions to be performed on the set of
%                   matching employees.

translate([], X, employed(X), []).

translate([action(Action) | Items], X, Tests, [Action|Actions]) :-
	translate(Items, X, Tests, Actions).

translate([test(X^Test) | Items], X, (Test,Tests), Actions) :-
	translate(Items, X, Tests, Actions).

translate([argument(X^Y^T1),
		comparison(Y^Z^T3),
		argument(X^Z^T2) | Items],
		X, (T1, T2, T3,Tests), Actions) :-
	translate(Items, X, Tests, Actions).


% ------------------------------------------------------------
% filter(+Token, -KeywordSemanticsList)
% ------------------------------------------------------------
% Takes a list of tokens and extracts those known as keyword
% (or as a synonym of a keyword).  The result is a list of
% the "semantics" of the recognized keywords.

% Termination
filter([], []).

% Known keyword
filter([Word|Words], [Translation|Translations]) :-
	keyword(Word, Translation),
	!,
	filter(Words, Translations).

% Synonym
filter([Word|Words], [Translation|Translations]) :-
	synonym(Word, Synonym),
	keyword(Synonym, Translation),
	!,
	filter(Words, Translations).

% Unknown word
filter([_|Words], Translations) :-
	filter(Words, Translations).


% ------------------------------------------------------------
% keyword(+Keyword, -Semantics)
% ------------------------------------------------------------
% Associates keywords with their semantics.

keyword(show, action(display_records)).
keyword(delete, action(remove_records)).
keyword(man, test(X^sex(X, m))).
keyword(woman, test(X^sex(X, f))).
keyword(president, test(X^title(X, 'President'))).
keyword(programmer, test(X^title(X, 'Programmer'))).
keyword(salesrep, test(X^title(X,'Sales Representative'))).
keyword(employee, test(X^title(X, _))).
keyword(underpaid, test(X^underpaid(X))).
keyword(friendly, test(X^friendly(X))).
keyword(unfriendly, test(X^unfriendly(X))).
keyword(over, comparison(Y^Z^(Y>Z))).
keyword(under, comparison(Y^Z^(Y<Z))).
keyword(salary, argument(X^Y^salary(X, Y))).
keyword(age, argument(X^Y^age(X, Y))).
keyword(N, argument(_^Y^(Y=N))) :- number(N).


% ------------------------------------------------------------
% synonym(+Synonym, -Keyword)
% ------------------------------------------------------------
% Associates synonyms with synonymous keywords.

synonym(boss, president).
synonym(programmers, programmer).
synonym(men, man).
synonym(male,man).
synonym(guy, man).
synonym(women, woman).
synonym(employees, employee).
synonym(female,woman).
synonym(display, show).
synonym(present, show).
synonym(give, show).
synonym(tell, show).
synonym(remove, delete).
synonym(fire, delete).



% ------------------------------------------------------------
% display_records(+EmployeeIDList)
% ------------------------------------------------------------
% Displays employees to the user.
%
% EmployeeIDList: A list of employee IDs, e.g. [1001,1004]

display_records([]).
display_records([ID|IDs]) :-
	write(ID), write(': '),
	full_name(ID, Name), write(Name),
	write(', '), title(ID, Title), write(Title),
	write(', salary '), salary(ID, Salary), write(Salary),
	write('.'), nl,
	display_records(IDs).


% ------------------------------------------------------------
% remove_records(+EmployeeIDList)
% ------------------------------------------------------------
% Removes employees from the database.
%
% EmployeeIDList: A list of employee IDs, e.g. [1001,1004]

remove_records([]).
remove_records([ID|IDs]) :-
	retract(employee(ID, _, _, _, _, _, _)),
	remove_records(IDs).


% ------------------------------------------------------------
% Database Predicates
% ------------------------------------------------------------
% Represents the database as Prolog clauses.  A real system
% would access an external database management system, e.g.
% by passing SQL queries to a DB server.

:- dynamic(employee/7).

employee(1001, 'Doe, John',    47, m, friendly,   'President', 100000).
employee(1002, 'Smith, Mary',  28, f, friendly,   'Programmer', 60000).
employee(1003, 'Zimmer, Fred', 35, m, unfriendly, 'Sales Representative',
                                                                55000).
employee(1004, 'Smith, Mark',  48, m, friendly,   'Programmer', 15000).
employee(1005, 'Russel, Ann',  31, f, unfriendly, 'Programmer', 17000).


full_name(ID, Name) :- employee(ID, Name, _, _, _, _, _).
age(ID, Age) :- employee(ID, _, Age, _, _, _, _).
sex(ID, Sex) :- employee(ID, _, _, Sex, _, _, _).
friendly(ID) :- employee(ID, _, _, _, friendly, _, _).
unfriendly(ID) :- employee(ID, _, _, _, unfriendly, _, _).
title(ID, Title) :- employee(ID, _, _,_,_, Title, _).
salary(ID, Salary) :- employee(ID, _, _,_,_, _, Salary).
underpaid(ID) :- salary(ID, Salary), Salary < 40000.
employed(ID) :- employee(ID, _,_,_,_,_,_).
