Sheet music (piano only) .mp3 by defualt defualt.

Synthesizer support.

3 equations running at once , 3 variables each (X, Y , Z)

Timing equations (For example start time 00:00 and end time 02:00 (mins:secs)) 

Variable pattern equations.

Optional Lyrics: Teto

User gets prompted for variable starting values
and then an equation on how the program should increase it

For example , user may enter
F(X, Y , Z) = 5x^2 + yx + z

then do

x = 0
x = x + 1 (causes x to increase linearly)

and then also a option to cap the value, for example when x reaches 10 it resets to starting value

UI: NiceGUI but first impliment to program with a bunch of input() statements.

User gets prompted wether the equation is for a piano or snyth beat for each equation.

It must support operators like + - * / but also functions like sin() , cos() and tan() (other trig functions).
It must also support Random().

Var count input

Note length?

Inter variable support in equations (But only if the equation that defines that variable is already given)


See design.md for more info.