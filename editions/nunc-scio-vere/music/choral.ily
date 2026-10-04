%% Nunc scio vere — Wacław z Szamotuł
%% Voice data. Absolute pitch (c' = middle C). One bar per line, numbered.
%% Base text: Perz (P), Feicht ed. 1966, at tablature pitch (P transposes up a minor third).
%% Editorial interventions are marked %ED and listed in the report.

\version "2.24.0"

global = {
  \key c \major
  \time 4/4
}

soprano = {
  r1 |                                  % 1
  f'2 d'2 |                             % 2
  g'2 f'4 d'4~ |                        % 3
  d'8 e'8 f'4 g'4 e'4 |                 % 4
  e'4 d'4 e'2~ |                        % 5
  e'4 e'4 f'8 d'8 e'4 |                              % 6
  r1 |                                  % 7
  r2 g'2~ |                             % 8
  g'4 a'4 a'8 g'8 a'8 b'8 |             % 9
  c''4 d''4~ d''8 c''8 c''4~ |          % 10
  c''4 b'4 c''2~ |                      % 11
  c''2 r2 |                             % 12
  c''2\cfStart c''2 |                           % 13
  c''2 a'2 |                            % 14
  a'2 c''2 |                            % 15
  b'4 c''4~ c''8 b'8 a'4~ |             % 16
  a'8 \ficta gis'16 fis'16 gis'4 a'2 |   % 17
  a'2 g'2 |                             % 18
  f'2 g'2 |                             % 19
  a'2 a'2~ |                            % 20
  a'2 c''4. b'8 |                       % 21
  a'4 g'4~ g'8 f'8 f'4~ |               % 22
  f'8 e'16 d'16 e'4 f'2 |               % 23
  f'2 f'2 |                             % 24
  e'2 f'2 |                             % 25
  g'2 g'2 |                             % 26
  a'8 b'8 c''2 b'8 a'8 |                % 27
  g'4 a'4~ a'8 g'8 g'4~ |               % 28
  g'4 \ficta fis'4 g'2 |                % 29
  g'2 a'2 |                             % 30
  a'2 f'2 |                             % 31
  f'2 a'2 |                             % 32
  g'2 a'2 |                             % 33
  f'4 g'4~ g'8 f'8 f'4~ |               % 34
  f'4 e'4 f'2~ |                        % 35
  f'1~ |                                % 36
  f'2 r2 |                              % 37
  r1 |                                  % 38
  f'2 f'2 |                             % 39
  d'2 g'2 |                             % 40
  g'2 a'2 |                             % 41
  d'2 g'2 |                             % 42
  g'2 g'2 |                             % 43
  c''2 b'4\optFlat c''4~ |                      % 44
  c''4 bes'8 a'8 g'4 a'4~ |             % 45
  a'4 g'8 f'8 e'4 g'4~ |                % 46
  g'8 f'8 e'8 d'8 c'4 f'4~ |            % 47
  f'4 e'4 f'2 |                         % 48
  e'2 f'4 g'4~ |                        % 49
  g'4 f'4~ f'8 e'8 d'4~ |               % 50
  d'4 \ficta cis'4 d'4 f'4~ |           % 51
  f'8 e'8 d'8 c'8 d'4. e'8 |            % 52
  f'4 g'4 a'2 |                         % 53
  g'4 f'4~ f'8 e'8 e'4~ |               % 54
  e'4 d'4 e'2~ |                        % 55
  e'2 e'2\fermata\cfEnd |                      % 56
  g'2 a'2 |                             % 57
  c''2. b'4~ |                          % 58
  b'4 a'8 g'8 a'8 b'8 c''4~ |           % 59
  c''4 b'8 a'8 b'4 b'4 |                % 60
  c''4 a'4 g'2~ |                       % 61
  g'4 g'4 e'4 f'4 |                     % 62
  g'2 r4 c'4~ |                         % 63
  c'4 c''4 c''4. b'8 |                  % 64
  a'4 g'4 f'4 e'4~ |                    % 65
  e'8 f'8 g'4 a'4 g'4~ |                % 66
  g'8 f'8 e'8 d'8 e'4 f'4~ |            % 67
  f'4 e'4 f'4 f'4 |                     % 68
  e'4 g'4 g'4 g'4 |                     % 69
  e'4 e'4 a'2 |                         % 70
  e'4 a'4 g'4 c''4~ |                   % 71
  c''4 b'8 a'8 g'4 a'4 |                % 72
  g'4 c''4 c''4 b'4 |                   % 73
  c''1 |                                % 74
  r1 |                                  % 75
  c''2 g'2 |                            % 76
  a'4 c''2 b'4 |                        % 77
  c''2. b'8 a'8 |                       % 78
  g'4 a'4 g'2 |                         % 79
  a'4 e''4~ e''8 d''8 c''8 b'8 |        % 80
  c''4 a'4 b'4 g'4 |                           % 81
  f'4 a'4 b'2 |                             % 82
  c''2 c''4 a'4 |                           % 83
  b'2 r4 c''4~ |                        % 84
  c''4 b'8 a'8 b'8 a'8 g'8 f'8 |        % 85
  e'4 a'2 \ficta gis'4 |                % 86
  a'1~ |                                % 87
  \fin a'1                             % 88
}

alto = {
  c'2 a2 |                              % 1
  d'4. c'8 b8 a8 b4~ |                  % 2
  b4 c'4 a2~ |                          % 3
  a4 d'4 e'8 d'8 c'8 b8 |               % 4
  a4. b8 c'4 b4~ |                      % 5
  b4 c'4 c'4. b8 |                      % 6
  c'8 b8 c'8 d'8 e'4 f'4 |              % 7
  f'4 f'4 d'2 |                         % 8
  e'4 f'4 r2 |                          % 9
  e'4 g'4 e'4 fis'4 |                   % 10
  g'2 e'4 a'4~ |                        % 11
  a'4 g'4 a'4 f'4~ |                    % 12
  f'8 e'16 d'16 e'4 f'2 |               % 13
  a'4. g'8 f'8 e'8 f'4 |                % 14
  e'4 f'4 a'4. g'16 f'16 |              % 15
  g'4 g'2 f'4 |                         % 16
  e'2 c'2 |                             % 17
  r4 c'4 d'4 e'4 |                      % 18
  c'4 f'4~ f'8 e'16 d'16 e'4 |          % 19
  f'2 f'2~ |                            % 20
  f'4 f'4 f'2 |                         % 21
  r4 e'4 d'4 b4 |                       % 22
  c'2 c'2 |                             % 23
  r4 d'2 d'4 |                          % 24
  g2 d'2 |                              % 25
  b4 c'2 r4 |                           % 26
  c'4. d'8 e'4. f'8 |                   % 27
  d'4 f'2 e'4 |                         % 28
  d'2 b2 |                              % 29
  e'2 c'4. b8 |                         % 30
  a4 d'2 c'8 b8 |                       % 31
  c'4 d'4 r4 f'4 |                      % 32
  e'8 d'8 e'4 f'2 |                     % 33
  c'2. b4 |                             % 34
  c'2 r4 c'4 |                          % 35
  c'2 a2 |                              % 36
  d'2 d'4 e'4~ |                        % 37
  e'8 d'8 c'8 b8 a2~ |                  % 38
  a2 a2 |                               % 39
  b2 d'2~ |                             % 40
  d'4 e'4 f'2 |                         % 41
  a2 e'4 d'4~ |                         % 42
  d'4 e'4 e'2 |                         % 43
  e'2 f'2 |                             % 44
  c'4. d'8 e'8 d'8 c'8 b8 |             % 45
  c'2. b8 a8 |                          % 46
  b4 c'2 d'4 |                          % 47
  r4 c'2 b4 |                           % 48
  c'2 c'4 c'4~ |                        % 49
  c'8 b8 a8 g8 a2~ |                    % 50
  a2 f2 |                               % 51
  r2 a4 b4 |                            % 52
  a4 e'4 f'8 e'8 d'8 c'8 |              % 53
  d'2 c'2 |                             % 54
  a4. b8 c'2 |                          % 55
  \ed e'2 b2\fermata |                          % 56
  r1 |                                  % 57
  c'2 d'2 |                             % 58
  f'2. e'4~ |                           % 59
  e'4 d'8 c'8 d'4 g'4~ |                % 60
  g'8 f'8 f'2 e'8 d'8 |                 % 61
  e'4 d'4 c'4 c'4 |                     % 62
  b2 c'4 a4 |                           % 63
  g2 e'2~ |                             % 64
  e'2 c'2 |                             % 65
  c'4 c'4 e'2 |                         % 66
  e'8 d'8 c'8 b8 c'2 |                  % 67
  c'4 c'4~ c'8 b16 a16 b4 |             % 68
  c'2 c'2 |                             % 69
  r4 c'4 c'4 c'4 |                      % 70
  a2 e'8 d'8 e'8 f'8 |                  % 71
  g'4 f'4 e'4 c'4 |                     % 72
  g'4 f'4 g'2 |                         % 73
  e'8 d'8 e'8 f'8 g'4 a'4~ |            % 74
  a'4 g'4 f'2 |                         % 75
  e'2 e'2 |                             % 76
  e'2 e'2 |                             % 77
  e'1 |                                 % 78
  r4 f'2 e'4 |                          % 79
  f'4 g'4 c'2 |                         % 80
  c'2 d'2 |                             % 81
  d'4 c'4 b2 |                          % 82
  e'2 e'4 f'4 |                         % 83
  d'2 e'2 |                             % 84
  e'2 d'4 e'4 |                         % 85
  c'4 d'4 e'2 |                         % 86
  \ficta cis'2 d'2 |                    % 87
  \fin cis'1                                 % 88
}

tenor = {
  r1 |                                  % 1
  r1 |                                  % 2
  r2 f2\cfStart |                               % 3
  d2 g2 |                               % 4
  f2 e2 |                               % 5
  g2 a2 |                               % 6
  a8 g8 a8 b8 c'4 d'4~ |                % 7
  d'4 c'2 b4 |                          % 8
  c'2 c'4 c'4~ |                            % 9
  c'4 b4 c'2 |                          % 10
  d'2 c'2\cfEnd |                       % 11
  r2 c'2 |                              % 12
  c'2 c'2 |                             % 13
  a8 g8 a8 b8 c'2 |                     % 14
  c'4 d'4 e'4 c'4 |                     % 15
  d'4 e'2 d'8 c'8 |                     % 16
  b2 a2~ |                              % 17
  a2 r2 |                               % 18
  a2 g2 |                               % 19
  f8 g8 a8 b8 c'4 d'4~ |                % 20
  d'4 c'8 b8 a2 |                       % 21
  c'4. b8 a4 g8 f8 |                    % 22
  g2 f2 |                               % 23
  r4 a2 b4 |                            % 24
  c'2 a2 |                              % 25
  g4 c'2 b4 |                           % 26
  a2 c'2 |                              % 27
  b4 c'4~ c'8 b8 a8 g8 |                % 28
  a2 g2 |                               % 29
  c'2 a4. b8 |                          % 30
  c'4 f4 f2 |                           % 31
  f2 f8 g8 a8 b8 |                      % 32
  c'2 c'4 a4~ |                         % 33
  a4 g8 f8 e4 f4 |                      % 34
  g2 f2~ |                              % 35
  f2 r2 |                               % 36
  r1 |                                  % 37
  r2 f2 |                               % 38
  f2 d2 |                               % 39
  g2 g4. a8 |                           % 40
  b4 c'4~ c'8 b8 a8 g8 |                % 41
  f2 c'4 b4~ |                          % 42
  b8 a8 g8 f8 g4 c'4 |                  % 43
  a4 c'4~ c'8 bes8 a4~ |                % 44
  a4 g8 f8 e4 f4~ |                     % 45
  f4 e8 d8 e4. f8 |                     % 46
  g4 a2 g8 f8 |                         % 47
  g2 f2 |                               % 48
  g2 a4 g8 f8 |                         % 49
  e4 f2 f4 |                            % 50
  e2 d2~ |                              % 51
  d2 f4 g4 |                            % 52
  a4 g4 f2 |                            % 53
  g4 a2 g4 |                            % 54
  f2 e2~ |                              % 55
  e2 e2\fermata |                               % 56
  R1 |                                  % 57
  R1 |                                  % 58
  R1 |                                  % 59
  g1 |                                  % 60
  a2 c'2~ |                             % 61
  c'4 b4 a4 a4 |                        % 62
  g4 g2 f4~ |                           % 63
  f4 e8 f8 g4 c'4 |                     % 64
  c'4. b8 a4 g4 |                       % 65
  g4. f8 e4. f8 |                       % 66
  g4 a2 g8 f8 |                         % 67
  g2 f2 |                               % 68
  g2 r4 g4 |                            % 69
  g4 g4 a2 |                            % 70
  c'2 c'2 |                             % 71
  e'4 d'8 c'8 b4 a4 |                   % 72
  b4 c'4 d'2 |                          % 73
  c'2. a4~ |                            % 74
  a8 b8 c'2 b4 |                        % 75
  c'2 r2 |                              % 76
  c'2 g2 |                              % 77
  a2 c'2 |                              % 78
  c'2 c'2 |                             % 79
  c'2 g4 g4 |                           % 80
  g4 fis4 g2 |                          % 81
  a2 g2 |                               % 82
  a2 a4 a4~ |                           % 83
  a4 \ficta gis4 a2 |                   % 84
  r4 b2 b4 |                            % 85
  c'4 a4 b2 |                           % 86
  a1~ |                                 % 87
  \fin a1                                    % 88
}

bassus = {
  r2 f2 |                               % 1
  d2 g4. f8 |                           % 2
  e4 c4 d4 f4~ |                        % 3
  f8 e8 d4 c2 |                         % 4
  d2 a,4 e4~ |                          % 5
  e8 d8 c8 b,8 a,2 |                    % 6
  r4 a4~ a8 g8 f8 e8 |                  % 7
  d4 f4 g2 |                            % 8
  c4 f2 e8 d8 |                         % 9
  c4 g4 a2 |                            % 10
  g2 c4 f4~ |                           % 11
  f4 e4 f2 |                            % 12
  c2 f,2 |                              % 13
  f2 f4. g8 |                           % 14
  a4 d4 a2 |                            % 15
  g4 c2 d4 |                            % 16
  e2 a,4 a4~ |                          % 17
  a8 g8 f2 e4 |                         % 18
  f2 c2 |                               % 19
  f2 f4 d4~ |                           % 20
  d8 e8 f8 g8 a4 f4~ |                  % 21
  f4 c4 d2 |                            % 22
  c2 r4 f4~ |                           % 23
  f8 e8 d8 c8 d2 |                      % 24
  c2 d2 |                               % 25
  e4 c4~ c8 d8 e4 |                     % 26
  f8 g8 a2 g8 f8 |                      % 27
  g4 f2 g4 |                            % 28
  d2 e2 |                               % 29
  c2 f2~ |                              % 30
  f4 d4~ d8 e8 f4~ |                    % 31
  f8 e8 d8 c8 d8 e8 f4 |                % 32
  c2 f,4 f4~ |                          % 33
  f4 e8 d8 c4 d4 |                      % 34
  c2 f,2 |                              % 35
  r4 f4 f2 |                            % 36
  d2 g2 |                               % 37
  g4 a4~ a8 g8 f8 e8 |                  % 38
  d2 r2 |                               % 39
  r2 r4 g4~ |                           % 40
  g4 c4 f4. e8 |                        % 41
  d8 c8 d4 c4 g4~ |                     % 42
  g8 f8 e8 d8 c4 c4~ |                  % 43
  c8 \ficta bes,8 a,8 g,8 f,2~ |        % 44
  f,2 r4 f,4~ |                         % 45
  f,8 g,8 a,8 b,8 c8 d8 e4~ |           % 46
  e8 d8 c8 b,8 a,4 d4 |                 % 47
  c2 d2 |                               % 48
  c2 f4 e8 d8 |                         % 49
  c4 d4 d2 |                            % 50
  a,2 r4 a4~ |                          % 51
  a8 g8 f8 e8 d4 g,4 |                  % 52
  d4 e4 d2 |                            % 53
  g,4 d4 a,4 c4 |                       % 54
  d2 a,4 c4~ |                          % 55
  c8 b,8 a,4 e,2\fermata |                      % 56
  R1*3 | r1 | r1 | r1 |                 % 57-62
  g,2\cfStart a,2 |                             % 63
  c2 c2 |                               % 64
  c2 c2 |                               % 65
  c2 c2 |                               % 66
  c2 c2 |                               % 67
  c2 d2 |                               % 68
  c2 c2 |                               % 69
  c2 a,2~ |                             % 70
  a,2 c2\cfEnd |                        % 71
  c4 d4 e4 f4 |                         % 72
  g4 a4 g2 |                            % 73
  c4. d8 e4 f4 |                        % 74
  f4 e4 d2 |                            % 75
  c1 |                                  % 76
  r4 c4~ c8 d8 e4 |                     % 77
  c4 a,4~ a,8 b,8 c8 d8 |               % 78
  e4 f4 c2 |                            % 79
  f4 c4~ c8 b,8 a,8 g,8 |               % 80
  a,2 g,4 g,4 |                         % 81
  d4 a,4 e2 |                           % 82
  a,4. b,8 c4 d4 |                      % 83
  b,2 a,2 |                             % 84
  a4 g8 f8 g4 e4 |                      % 85
  a4 f4 e2 |                            % 86
  a,2 d2 |                              % 87
  \fin a,1                                   % 88
}
