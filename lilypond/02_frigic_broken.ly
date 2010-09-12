% Example lilypond file with a simple frigic cycle

\new Staff \relative c' {
    \key c \major
    \time 4/4
    < c e g c >2
    < ais e' g c >
    < a c f c' >
    < g d' f ces' >
    < c fes g bis >1
}