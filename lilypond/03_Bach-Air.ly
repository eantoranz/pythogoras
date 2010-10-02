% JS Bach's Air on the G String (doesn't have liasons or other things.... have to develop support for it)

<<
\new Staff \relative c'' {
        \key d \major
        fis1
        
        fis8 b16 g e d cis d cis4 a
        
        a'2 a16 fis c b e dis a' g
        
        g2 g16 e b a d cis g' fis
        
        fis4. gis16 a d,8 d32 e fis16 fis e e d

        % first end
        cis b b32 cis d16 d8 cis16 b a2
        
        % repeat
        fis'1
        
        fis8 b16 g e d cis d cis4 a
        
        a'2 a16 fis c b e dis a' g
        
        g2 g16 e b a d cis g' fis
        
        fis4. gis16 a d,8 d32 e fis16 fis e e d
        
        %second end
        cis b b32 cis d16 d8 cis16 b a2
}

\new Staff \relative c'' {
        \key d \major
        d1
        
        d4 b a2
        
        a8 c16 b c8 a'16 c, b8 r r4
        
        b8 e16 d e fis g e a,8 r r4
        
        a2 a8 gis16 a b8 gis
        
        % first end
        a a4 gis8 e2
        
        % Repeat
        d'1
        
        d4 b a2
        
        a8 c16 b c8 a'16 c, b8 r r4
        
        b8 e16 d e fis g e a,8 r r4
        
        a2 a8 gis16 a b8 gis
        
        % second end
        a8 a4 gis8 e2
        
}

\new Staff \relative c'' {
        \clef alto
        \key d \major
        a2 b
        
        b,4 e e2
        
        e8 dis4 e8 fis r r4
        
        e8 b4 e8 e r r4
        
        d4. e8 fis d b e
        
        % first end
        e fis b, e cis2
        
        % repeat
        a'2 b
        
        b,4 e e2
        
        e8 dis4 e8 fis r r4
        
        e8 b4 e8 e r r4
        
        d4. e8 fis d b e
        
        % second end
        e fis b, e cis2
        
}

\new Staff \relative c {
        \clef bass
        \key d \major
        d8 d' cis cis, b b' a a, 
        
        g g' gis gis, a a' g g,
        
        fis fis' e e, dis dis' b b'
        
        e,, e' d d, cis cis' a a'
        
        d, d' cis cis, b b' gis e
        
        % first end
        a d, e e, a16 b cis d e g fis e
        
        % repeat
        d8 d' cis cis, b b' a a, 
        
        g g' gis gis, a a' g g,
        
        fis fis' e e, dis dis' b b'
        
        e,, e' d d, cis cis' a a'
        
        d, d' cis cis, b b' gis e
        
        % second end
        a d, e e, a2
        
}
>>