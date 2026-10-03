%% Modlitwa gdy dziatki spać idą (Już się zmierzka) — Wacław z Szamotuł
%% Voice data at the pitch and note values of the Andrysowic print
%% (known from the Przyborowska facsimile, 1880). Absolute pitch, c' = middle C.
%% One breve per line; a note may run across the line (no editorial ties).
%% \fi = editorial accidental (printed above the note). The print has none.


cantusNotes = {
  a'\breve |                    % 1
  a'1 g'1 |                     % 2
  f'2 a'2 c''2. b'4 |           % 3
  a'4 g'4 a'1 \fi gis'2 |       % 4
  a'1 a'2 c''1                  % 5  (c'' runs into 6)
  b'4 a'4 g'1 |                 % 6
  f'2 a'1 g'4 f'4 |             % 7
  g'1 f'2 a'2.                  % 8  (a' runs into 9)
  b'4 c''2 d''1 |               % 9
  c''\breve |                   % 10
  r1 a'1 |                      % 11
  f'1 d'1 |                     % 12
  g'1 c'2 c''1                  % 13
  b'2 a'1 |                     % 14
  a'1 d'2 d''2.                 % 15
  c''4 b'2 a'1 |                % 16
  g'4 f'4 e'4 d'4 c'2 c''2 |    % 17
  b'4 a'4 g'4 f'4 e'2. f'4 |    % 18
  g'2 a'1 \fi gis'2 |           % 19
  a'\breve |                    % 20
  e'\breve |                    % 21
  e'1 f'1 |                     % 22
  e'1 c'1 |                     % 23
  d'1 d'1 |                     % 24
  c'2 c''2. b'4 a'4 g'4 |       % 25
  f'2 d'2 f'1.                  % 26
  e'4 d'4 e'1 |                 % 27
  c'2 e'2 d'2 f'2 |             % 28
  e'2 d'1 \fi cis'2 |           % 29
  \finalis 2 d'\longa \bar "|."  % 30
}

altusNotes = {
  a4 b4 c'4 d'4 e'2 f'2.        % 1
  e'4 d'1 \fi cis'2 |           % 2
  d'2 c'2 f'1 |                 % 3
  e'\breve |                    % 4
  c'1 e'1 |                     % 5
  e'\breve |                    % 6
  f'1 e'\breve                  % 7
  c'4 b4 a4 g4 |                % 8
  f2 e2 d1 |                    % 9
  e1 e'1 |                      % 10
  c'1 a\breve                   % 11
  b1 |                          % 12
  g1 g'1 |                      % 13
  a'2 g'4 f'4 e'1 |             % 14
  f'1 r2 f2 |                   % 15
  g1 a2. b4 |                   % 16
  c'2 b2 a2 a'2 |               % 17
  g'4 f'4 e'4 d'4 c'2. b8 a8 |  % 18
  b2 a2 e'1 |                   % 19
  c'\breve |                    % 20
  c'\breve |                    % 21
  c'1 a2 d'2 |                  % 22
  b2 c'2. b4 a4 g4 |            % 23
  a1 b1 |                       % 24
  a\breve |                     % 25
  d'1 d'2 a1                    % 26
  b2 c'2 e'2.                   % 27
  d'4 c'4 b4 a1 |               % 28
  b1 a1 |                       % 29
  \finalis 2 a\longa \bar "|."   % 30
}

tenorNotes = {
  a\breve |                     % 1
  f1 g1 |                       % 2
  a1 a1 |                       % 3
  c'1 b1 |                      % 4
  a\breve |                     % 5
  c'\breve |                    % 6
  d'1 c'1 |                     % 7
  b1 a1 |                       % 8
  a1 \fi gis1 |                 % 9
  a\breve |                     % 10
  a\breve |                     % 11
  d'1 b1 |                      % 12
  c'1 e'1 |                     % 13
  d'1 c'1 |                     % 14
  d'\breve |                    % 15
  d'\breve |                    % 16
  g1 a1 |                       % 17
  b1 c'1 |                      % 18
  d'1 b1 |                      % 19
  a\breve |                     % 20
  a\breve |                     % 21
  g1 f1 |                       % 22
  g1 e1 |                       % 23
  f1 g1 |                       % 24
  e\breve |                     % 25
  d\breve |                     % 26
  f1 g1 |                       % 27
  a1 f1 |                       % 28
  g1 e1 |                       % 29
  \finalis 2 d\longa \bar "|."   % 30
}

bassusNotes = {
  a,2. b,4 c2 d2.               % 1
  e4 f2 e1 |                    % 2
  d2 f2. g4 a1                  % 3
  a,2 e1 |                      % 4
  a,1 a,2 a1                    % 5
  g4 f4 e1 |                    % 6
  d1 a,4 b,4 c4 d4 |            % 7
  e2 e2 f2. e4 |                % 8
  d2 c2 b,1 |                   % 9
  a,\breve |                    % 10
  a1 f1 |                       % 11
  d1 g1 |                       % 12
  c2 c2. d4 e2 |                % 13
  f2 g2 a1 |                    % 14
  d1 d1 |                       % 15
  g,2 g1 f2 |                   % 16
  e1 f1 |                       % 17
  g1 a1 |                       % 18
  g2 f2 e1 |                    % 19
  a,\breve |                    % 20
  a,\breve |                    % 21
  c1 d1 |                       % 22
  e1 a,1 |                      % 23
  d1 g,1 |                      % 24
  a,\breve |                    % 25
  r2 a2. g4 f4 e4 |             % 26
  d2 d2 c1 |                    % 27
  a,1 d1 |                      % 28
  g,1 a,1 |                     % 29
  \finalis 2 d\longa \bar "|."   % 30
}

%% ------------------------------------------------------------ underlay
%% Stanza 1, transcribed (see "Text"). "_" = a further note of a melisma.

cantusWords = \lyricmode {
  Już się zmierz -- ka, nad -- cho -- _ _ _ _ dzi noc, po -- proś -- _ _ my Bo -- _ _ _ ga o __ _ _ _ po -- moc, a -- by on na -- _ _ szem stra -- żem był, od __ _ _ złych __ _ _ _ _ czar -- _ _ _ _ _ tów __ _ nas o -- bro -- nił, któ -- rzy na -- wię -- cej w_ciem -- no -- ści u -- _ _ _ _ ży -- wa -- _ _ _ ją __ _ swej __ _ chy -- tro -- _ ści.
}

altusWords = \lyricmode {
  Już __ _ _ _ _ _ się zmierz -- _ ka, nad -- cho -- dzi noc, po -- proś -- my Bo -- _ _ _ _ ga o po -- moc, a -- by on na -- _ szem stra -- _ _ żem był, od złych __ _ _ _ _ czar -- _ _ _ _ _ tów __ _ _ nas o -- bro -- nił, któ -- rzy na -- _ wię -- _ cej __ _ _ w_ciem -- no -- ści u -- ży -- wa -- _ _ _ ją __ _ _ swej chy -- tro -- ści.
}

tenorWords = \lyricmode {
  Już się zmierz -- ka, nad -- cho -- dzi noc, po -- proś -- my Bo -- ga o po -- moc, a -- by on na -- szem stra -- żem był, od złych czar -- tów nas o -- bro -- nił, któ -- rzy na -- wię -- cej w_ciem -- no -- ści u -- ży -- wa -- ją swej chy -- tro -- ści.
}

bassusWords = \lyricmode {
  Już __ _ _ _ _ się zmierz -- ka, nad -- _ _ cho -- dzi noc, po -- proś -- _ _ my Bo -- _ _ _ _ _ ga o __ _ po -- _ _ moc, a -- by on na -- _ szem __ _ _ _ _ stra -- _ żem był, od __ _ złych czar -- tów nas o -- _ bro -- nił, któ -- rzy na -- wię -- cej w_ciem -- no -- ści u -- _ _ _ _ ży -- wa -- ją swej chy -- tro -- ści.
}

