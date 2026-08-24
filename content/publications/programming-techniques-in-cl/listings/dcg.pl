% ------------------------------------------------------------
%  det(Kasus, Numerus, Genus) - Artikel
% ------------------------------------------------------------

det(nom, sg, m) --> [der].  % der Hund ist wichtig
det(gen, sg, m) --> [des].  % Max leidet wegen des Hundes
det(dat, sg, m) --> [dem].  % mit dem Hund ist das Leben schön
det(akk, sg, m) --> [den].  % Daniel dämonisierte den Hund

det(nom, pl, m) --> [die].  % die Hunde sind wichtig
det(gen, pl, m) --> [der].  % Max leidet wegen der Hunde
det(dat, pl, m) --> [den].  % mit den Hunden ist das Leben schön
det(akk, pl, m) --> [die].  % Daniel dämonisierte die Hunde

det(nom, sg, f) --> [die].  % die Tasse ist wichtig
det(gen, sg, f) --> [der].  % Max leidet wegen der Tasse
det(dat, sg, f) --> [der].  % mit der Tasse ist das Leben schön
det(akk, sg, f) --> [die].  % Daniel dämonisierte die Tasse

det(nom, pl, f) --> [die].  % die Tassen sind wichtig
det(gen, pl, f) --> [der].  % Max leidet wegen der Tassen
det(dat, pl, f) --> [den].  % mit den Tassen ist das Leben schön
det(akk, pl, f) --> [die].  % Daniel dämonisierte die Tassen

det(nom, sg, n) --> [das].  % das Haus ist wichtig
det(gen, sg, n) --> [des].  % Max leidet wegen des Hauses
det(dat, sg, n) --> [dem].  % mit dem Haus ist das Leben schön
det(akk, sg, n) --> [das].  % Daniel dämonisierte das Haus

det(nom, pl, n) --> [die].  % die Häuser sind wichtig
det(gen, pl, n) --> [der].  % Max leidet wegen der Häuser
det(dat, pl, n) --> [den].  % mit den Häusern ist das Leben schön
det(akk, pl, n) --> [die].  % Daniel dämonisierte die Häuser


% ------------------------------------------------------------
%  n(Kasus, Numerus, Genus) - Nomina
% ------------------------------------------------------------

n(nom, sg, m) --> [hund].   % der Hund geht
n(gen, sg, m) --> [hundes]. % Max leidet wegen des Hundes
n(dat, sg, m) --> [hund].   % mit dem Hund ist das Leben schön
n(dat, sg, m) --> [hunde].  % mit dem Hunde ist das Leben schön
n(akk, sg, m) --> [hund].   % Daniel dämonisierte den Hund
n(nom, pl, m) --> [hunde].  % die Hunde gehen
n(gen, pl, m) --> [hunde].  % Max leidet wegen der Hunde
n(dat, pl, m) --> [hunden]. % mit den Hunden ist das Leben schön
n(akk, pl, m) --> [hunde].  % Daniel dämonisierte die Hunde

n(nom, sg, f) --> [katze].  % der Hund geht
n(gen, sg, f) --> [katze].  % Max leidet wegen des Hundes
n(dat, sg, f) --> [katze].  % mit dem Hunde ist das Leben schön
n(akk, sg, f) --> [katze].  % Daniel dämonisierte den Hund
n(nom, pl, f) --> [katzen]. % die Katzen gehen
n(gen, pl, f) --> [katzen]. % Max leidet wegen der Katzen
n(dat, pl, f) --> [katzen]. % mit den Katzen ist das Leben schön
n(akk, pl, f) --> [katzen]. % Daniel dämonisierte die Katzen


% ------------------------------------------------------------
%  pron(Kasus, Person, Numerus) - Pronomina
% ------------------------------------------------------------
% Auch Wörter wie "mein" würden üblicherweise als Pronomina
% bezeichnet. Es sind auch nicht alle Kasus verzeichnet.

pron(nom, 1, sg) --> [ich].
pron(gen, 1, sg) --> [meiner].
pron(dat, 1, sg) --> [mir].
pron(akk, 1, sg) --> [mich].
pron(nom, 2, sg) --> [du].
pron(nom, 3, sg) --> [er].
pron(nom, 3, sg) --> [sie].
pron(nom, 3, sg) --> [es].
pron(nom, 1, pl) --> [wir].
pron(nom, 2, pl) --> [ihr].
pron(nom, 3, pl) --> [sie].


% ------------------------------------------------------------
%  v(Person, Numerus, Transitivität) - Verben
% ------------------------------------------------------------

v(1, sg, trans) --> [sehe].    % ich sehe den Hund
v(2, sg, trans) --> [siehst].  % du siehst den Hund
v(3, sg, trans) --> [sieht].   % Anna sieht den Hund
v(1, pl, trans) --> [sehen].   % wir sehen den Hund
v(2, pl, trans) --> [seht].    % ihr seht den Hund
v(3, pl, trans) --> [sehen].   % sie sehen den Hund

v(1, sg, intrans) --> [gehe].  % ich gehe
v(2, sg, intrans) --> [gehst]. % du gehst
v(3, sg, intrans) --> [geht].  % Anna geht
v(1, pl, intrans) --> [gehen]. % wir gehen
v(2, pl, intrans) --> [gehen]. % ihr geht
v(3, pl, intrans) --> [gehen]. % sie gehen



% ------------------------------------------------------------
%  s - Sätze
% ------------------------------------------------------------

s -->
  np(nom, Person, Numerus, _), % das Genus interessiert nicht
  vp(Person, Numerus).

% ------------------------------------------------------------
%  np(Kasus, Person, Numerus, Genus) - Nominalphrasen
% ------------------------------------------------------------

np(Kasus, 3, Numerus, Genus) -->
  det(Kasus, Numerus, Genus),  % der
  n(Kasus, Numerus, Genus).    % Katzen

np(Kasus, Person, Numerus, _) -->
  pron(Kasus, Person, Numerus).

% ------------------------------------------------------------
%  vp(Person, Numerus) - Verbalphrasen
% ------------------------------------------------------------

vp(Person, Numerus) -->
  v(Person, Numerus, intrans).

vp(Person, Numerus) -->      % [sie] sahen die Katze: Keine
  v(Person, Numerus, trans), % Kongruenz zwischen Verb und
  np(akk, _, _, _).          % Akkusativobjekt!
