%%%% CONSTANTS

#const rmax = 4.
#const m = 60.
#const p2 = 10.
#const p3 = 3.
#const p4 = 1.


%%%% CONSTRAINTS

% C1: each team plays a home game against each other team at most once.
% C2: home team availability is respected.
% C3: away team unavailability is respected.
0 { schedule(HomeTeam, AwayTeam, Time) : home(HomeTeam, Time), not forbidden(AwayTeam, Time) } 1 :-
   team(HomeTeam), team(AwayTeam), HomeTeam != AwayTeam.

% C4: each team plays at most one game per time slot.
:- schedule(Team, _, Time), schedule(_, Team, Time). 
:- schedule(Team,Opp1,Time), schedule(Team,Opp2,Time), Opp1 != Opp2.
:- schedule(Opp1,Team,Time), schedule(Opp2,Team,Time), Opp1 != Opp2.

% C5: each team plays at most 2 games in a period of rmax time slots.
play(Team, Time) :- schedule(Team, _, Time).
play(Team, Time) :- schedule(_, Team, Time).
:- play(Team, Time1), play(Team, Time2), play(Team, Time3), 
   Time1 < Time2, Time2 < Time3,
   Time3 - Time1 < rmax.

% C6: there are at least m time slots between two games with the same pair of teams.
:- schedule(Team, Opp, Time1), schedule(Opp, Team, Time2), Time1 != Time2, |Time2 - Time1| <= m.


%%%% HEURISTICS

% prefer to schedule games with away teams on days that are not their home days
% #heuristic schedule(_, AwayTeam, Time) : not home(AwayTeam, Time). [2@1, factor]

% calc the number of time slots teams can play with one another
possible_matches(HomeTeam, AwayTeam, N) :- team(HomeTeam), team(AwayTeam), HomeTeam!=AwayTeam, N = #count { Time : home(HomeTeam, Time), not forbidden(AwayTeam, Time), time(Time) }.

% prefer to schedule games that have less possible matches 
#heuristic schedule(HomeTeam, AwayTeam, _) : possible_matches(HomeTeam, AwayTeam, N), N<20. [20-N@10, init]



%%%% OPTIMIZE

% a close game is a game with a difference of rmax or less of another.
close_game(Team, Time1, Time2, Diff) :-
   play(Team, Time1), play(Team, Time2), Time1 < Time2, Diff = Time2 - Time1, Diff < rmax.

% maximize scheduled games:
#maximize { 1@10, HomeTeam, AwayTeam : schedule(HomeTeam, AwayTeam, Time) }.

% minimize close games:
#minimize { p2@1, Team, Time : close_game(Team, Time, _, 1) }.
#minimize { p3@1, Team, Time : close_game(Team, Time, _, 2) }.
#minimize { p4@1, Team, Time : close_game(Team, Time, _, 3) }.

% #show schedule/3.
% #show close_game/4.