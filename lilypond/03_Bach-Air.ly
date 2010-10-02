% JS Bach's Air on the G String (doesn't have liasons or other things.... have to develop support for it)

<<
\new Staff \relative c'' {
        \key d \major
        fis1
        
        fis8 b16 g e d cis d cis4 a
        
        a'2 a16 fis c b e dis a' g
        
        g2 g16 e b a d cis g' fis
        
        fis4. gis16 a d,8 d32 e fis16 fis e e d
        
        cis b b32 cis d16 d8 cis16 b a2
}

\new Staff \relative c'' {
        \key d \major
        d1
}

\new Staff \relative c'' {
        \clef alto
        \key d \major
        a2 b
}

\new Staff \relative c {
        \clef bass
        \key d \major
        d8 d' cis cis, b b' a a, 
        
        g g' gis gis, a a' g g,
        
        fis fis' e e, dis dis' b b'
        
        e,, e' d d, cis cis' a a'
        
        d, d' cis cis, b b' gis e
        
        a d, e e, a16 b cis d e g fis e
}
>>