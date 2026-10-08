#!/usr/bin/env python3
"""Build Zookeeper JSON:API payloads for DJ Stace's finished reviews.

What this does (and does NOT do)
--------------------------------
- It writes two files for Stace to approve BEFORE anything is uploaded:
    1. albums_for_approval.json  -> one album POST body per album (do this FIRST)
    2. reviews_for_upload.json   -> one review POST body per album (do this SECOND)
- It never talks to Zookeeper. No POST, PATCH or DELETE is sent from here.
- Reviews need the album "tag" (Zookeeper's album ID). Zookeeper only gives us that
  tag after the album is keyed, so the review files hold the placeholder
  "TAG_PENDING_<key>". Run again with --tags tags.json to fill in real tags.

Usage
-----
    python3 scripts/zk_review_payloads.py                  # writes both files
    python3 scripts/zk_review_payloads.py --tags tags.json # fills in album tags
        tags.json looks like: {"twisted-teens-blame-the-clown": "1155800", ...}
"""
import argparse
import json
import re
from pathlib import Path

# Where the approval files get written (relative to the repo root).
OUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "zookeeper_upload" / "2026-10-06"

# Review attributes shared by every review.
AIRNAME = "DJ Stace"          # the airname string used on her past reviews
REVIEW_DATE = "2026-10-04"    # matches the "Review Date: 10/4/2026" line in each body

# Labels already in the Zookeeper label table (checked Oct. 6, 2026): name -> label ID.
# Labels not listed here are sent by name, and Zookeeper creates them.
KNOWN_LABEL_IDS = {
    "Matador Records": "1952",
    "Easy Eye Sound": "21304",
    "Handmade Records": "17538",
    "Drag City": "989",
    "Sub Pop Records": "3124",
    # Palace's own imprint "Palace Presents" is not in the table; its distributor Awal is.
    "Awal": "21943",
}

# ---------------------------------------------------------------------------
# The ten reviews Stace finished (edited in the Review Templates folder).
# "lib_artist" is the library form of the artist name (people go "Last, First").
# "body" is her review text, copied from her Google Doc with markdown escapes removed.
# ---------------------------------------------------------------------------
ALBUMS = [
    {
        "key": "twisted-teens-blame-the-clown",
        "lib_artist": "Twisted Teens",
        "album": "Blame the Clown",
        "label": "Chain Smoking Records",
        "doc_id": "1HQ3lAxkV-HR7WHCKAJVQumT1Pgjep66JuLs3liz0ZPM",
        "body": """Album / Artist: Blame the Clown / Twisted Teens

Label: Chain Smoking Records

Release Date: February 13, 2026
Review Date: 10/4/2026
Reviewer: DJ Stace

General Comments / Reviews:

Raw Power-era Stooges sitting in with a pedal steel player at a New Orleans dive. Scrappy, loud and a blast. If the Grateful Dead had been a garage punk band - DJ Stace

“punk unbounded” - Paste

Release Notes:

New Orleans garage-punk band; pedal steel runs through the songs.
Bandcamp lists a first release on Chain Smoking in September 2025; wide release Feb. 13, 2026.
12 tracks, about 31 minutes.
released February 13, 2026

FCCs: 2,7,8, 11(maybe)

RIYL: The Stooges, Black Lips, Ty Segall, Shannon and the Clams

Play: All but FCCs (All FCCs worth editing), Favs Rated with up to *****

Tracklist:
1. **** Is It Real? 03:02 - Fast, driving guitar rocker. A banger right out of the gate.
2. Wild Connection 02:49 - Medium Fast paced love song that would have been right at home on the True Romance soundtrack. Worth editing. FCC shit x1.
3. **** I Operate 01:54 - Upbeat jangly, quirky, infectious, talking lyrics.
4. **** Little Seed 02:50 - Cool lowfi radio-style intro. Medium fast crooner.
5. *** 100 Bill Is Gone! 02:58 - Upbeat gravelly screamer about losing $100 in a purchase gone wrong in the French Quarter (probably, I’m not speaking from experience, or anything).
6. ***** Peekaboo Hand 03:23 - Upbeat, toe tapper with brilliant lyrics and phrasing. Brilliant steel guitar. This is peak TT. Possibly my favorite new song. Smells like Grateful Dead if they’d been a garage punk band. You can’t play this one enough.
7. Not Real 02:54 - Mid-uptempo power chord based talker. Definitive answer to the opening track. FCC “wake the fuck up” after the alarm noise at the outro x1.
8. **** Who Could It Be? 02:41 - Upbeat rocker about the devil come a’knockin’? Worth an edit, if someone were so inclined.FCC pissing x1?
9. **** Circus Clown 02:06 - Machine gun rapid fire screaming rocker with killer Theremin-style steel guitar. Play it!
10. **** Hurricane 02:00 - Medium tempo noisy (in a good way), trashcan percussion, recorded inside a giant tin foil roasting pan. Actually, perfect for a song about a hurricane!
11. ***** White Hot Coal 02:54 - Medium paced acoustic guitar blues crooning rocker! Outro with Fiddle, possibly Hurdy Gurdy!?, which would totally be on brand for these guys. Greatness. Possible FCC sounds like “shit”, lyrics sites say its “ship” but better safe than sorry.
12. Corpse Pose 01:02 - Instrumental noise weirdness with backward masking overlays, etc.. Short closer, about a minute. Cool for soundbed, maybe.""",
    },
    {
        "key": "twisted-teens-florida-water-blues",
        "lib_artist": "Twisted Teens",
        "album": "Florida Water Blues",
        "label": "Going Underground",
        "doc_id": "1nut8CJNkWuG-RGJkVTGpSfeEg3vyVqpqXkntycU2KIQ",
        "body": """Album / Artist: Florida Water Blues / Twisted Teens

Label: Chain SMoking / Going Underground

Release Date: July 10, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Same band six months later, slowed down and sunburned. Backroads swamp rock with unbelievably consistent songwriting and “finely” crafted recordings about backroads, marshes and coastal motels in place of city nerves. Mind the FCCs, and look for lofi, abrupt endings. - DJ Stace

Release Notes:

New Orleans band's second album of 2026, six months after Blame the Clown.

Next album: The Holy Cross Tigers is due Nov. 6, 2026 on Sub Pop (single When We First Met out now).

FCCs: 1,5,7,9,10,12

RIYL: Black Lips, Kurt Vile, The Gun Club, Ty Segall

Play: All but FCCs, Favs Rated with up to *****

Tracklist:

1. Why Did You Miss It? 03:36 - Fast Paced, starts with a frantic guitar intro, then the drum track leads into a fuzzed out lofi awesomeness. FCC fucked up x1.
2. ***** Hand Me A Cigarette 03:26 - FIngerpicked Delta Blues jam intro, leads into a driving lofi junk blues stomper full of understated, dusty swagger. Play it!
3. **** Swamp 02:55 - Noisy backwards masking intro leads into an upbeat swamp rock anthem to ,... LIVING IN THE SWAMP!
4. *** Guided Thunder 03:13 - Fast, emphatic. Spoken-word breakdown that builds and cuts off on a drum hit to stomp all the way to the raucous toy piano ending.
5. **** Florida Water Blues 03:45 - Pace: ____. Title track. Worth editing. FCC shit x1.
6. ***** Top Of The World Hwy No.2 2:12 - Fast paced power chord jammer!
7. Concealed Weepin' 02:27 - Fast paced buzzing rhythm section, with a plucky little guitar solo over the top. Frenetic and chaotic at points. Cool post-punk buzzer. FCC little fucker x1.
8. ***** Riding 03:54 - Drum machine starts off with a great little breakdown. Heavy steel guitar, driving pace. Great tune. Transitions to this amazing distorted over-autotuned harmonic vocals at 3:00 that turns out to be the best part of the song, maybe.
9. Business 02:23 - Jumpy female blues field recording vocals devolve into a janky plucker with talking vocals. FCC fuck x2.
10. Javelina 02:50 - Slow twangy country rocker chock full of FCCs and great lap[ steel guitar. FCC fuck x1, shit x1.
11. **** Weather The Season 03:45 - Crazy Horse style metallic guitar intros an early 60’s style crooner.
12. Dancer 03:00 - Fast paced with crying steel guitar riffage. Ode to the Exotic Dancers of the FC. FCC fuck x1.
13. **** Sun Go Down 05:10 - Straight guitar and lap steel strummer. Great closer, 12-string acoustic, the one real slow song.""",
    },
    {
        "key": "this-is-lorelei-the-singer-in-my-band",
        "lib_artist": "This Is Lorelei",
        "album": "The Singer in My Band",
        "label": "Matador Records",
        "doc_id": "1o1auc4gQyPiRJOufY69jrMcPr4VuU-rN1In2l7K8S5U",
        "body": """Album / Artist: The Singer in My Band / This Is Lorelei

Label: Matador Records

Release Date: September 11, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Nate Amos gets in the car and comes back with a twangy alt-country road record. Tight, warm and catchy as hell. Look for cover versions of most of these, a la Box for Buddy, cause who could resist? - DJ Stace

Release Notes:

Third album from Nate Amos as This Is Lorelei, and his first for Matador.

Self-produced and recorded at his home studio in Brooklyn.

Amos calls it his road album; he wrote the songs daydreaming in the car with no instruments.

Lead single Billy Came Back (June 23, 2026). NACC #12 the week of Oct. 1.

released September 11, 2026

FCCs: None found

RIYL: MJ Lenderman, Wednesday, Alex G, Big Thief

Play: All, Favs Rated with up to *****

Tracklist:

1. *** I Will Eat My Heart in the Morning Light 03:18 - Upbeat guitar anthem. Great lyrics and vocals.
2. ***** Oh No Now My 03:09 - Strong mid tempo thumper with great guitar hook throughout. Least alt-country track of the album. Stacked harmonies over low-tuned guitars. Play it!!
3. **** Billy Came Back 03:10 - Upbeat, jangly strummer about Billy, a karaoke legend.
4. *** Watching Heaven Fall 03:13 - Upbeat country popper.
5. *** Sailing (Your Baby's Down) 03:33 - Medium tempo upbeat country harmony yacht rocker.
6. *** The Singer in My Band 02:26 - Upbeat country rocker with banjos.
7. Nitro 01:27 - Fast paced low tuned acoustic guitar instrumental.
8. ***** Hey Sarah Is It Gonna Rain Forever 03:28 - Continuing the riff from the previous instrumental, becomes a cool baritone guitar stomper anthem to Sarah. Great vocal styling. Playing this one heavily on The Library Show.
9. **** The Kid With the Crown 04:15 - Starts with a light acoustic guitar jam, abruptly hits with an alt-country rocker punch in the face, and stays upbeat and bright throughout.
10. **** And I Haven't Seen My Love in Quite a While 03:29 - Fast-paced country two-step bouncer. Segue with Old 97’s.
11. **** Don't You Cry in Lonesomeness 03:19 - Strumming electric guitar and vocals alone. Brief. Goes quiet at 3:05, and hangs dead air for about 15 seconds.""",
    },
    {
        "key": "little-barrie-gravity-freeze",
        "lib_artist": "Little Barrie",
        "album": "Gravity Freeze",
        "label": "Easy Eye Sound",
        "doc_id": "1myGAWbTOJJC1gYyRlqEcJ0OBcvDi0BWozjcojkvilE4",
        "body": """Album / Artist: Gravity Freeze / Little Barrie

Label: Easy Eye Sound

Release Date: May 22, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Greasy, low-slung Easy Eye Sound garage soul from a 70’s that never was. They turned the heat down a notch, but Cadogan's guitar still bites. Low-slung grooves and bursts of guitar. - DJ Stace

Release Notes:

Sixth album from the London trio led by guitarist Barrie Cadogan; new drummer Coote joins.

Recorded at Rat Salad Studios in Hornsey, North London, with Rupert Lyddon engineering and co-producing.

released May 22, 2026

FCCs: None found

RIYL: The Black Keys, Allah-Las, Oh Sees, The Mystery Lights, El Michels Affair, Skinshape

Play: All, Favs Rated with up to *****

Tracklist:

1. ***** More Bad Miles Of Road 03:49 - Upper-mid pace, slinky and naughty wah-wah pedal heavy funk burlesque rock. Lead single; announced the album in February 2026. Heavy play on Library Show as a single.
2. *** It Isn't Soul 02:49 - Slow slinky with fuzzy guitar backing and bright guitar along the top. Great mix of dirt and polish. At home in a Tarantino film in a few years.
3. December 05:08 - Upbeat high-hat pace, echoing vocals. This one threw its go-go boots in the corner and is dancing barefoot.
4. ***** Luggin' Hurt 07:08 - “Do do do, de bap bap badada do,...” Shuffling R&B rhythm and licorice taffy guitar stretching all over 7 minutes of ass-shaking funky wah-riff perfect. Play this song and people will ask “who is this?” If you’re going to spend 7 minutes of your show on a single, it better be good. This one is worth the minutes.
5. Talk It Up Like It's Wanted 03:02 - Mid-tempo, unremarkable guitar solo shuffler.
6. ** Anything You Are 03:20 - Slow and slinky. Rhythm flits around under the strumming R&B guitar and smoky jazz club vocals. Picks up the pace at 1:30 a little.
7. *** Coralisa 04:49 - Great backbeat based rhythm, with buzzing guitar work over the top. Lightly reminiscent of Jon Spencer Blues Explosion.
8. Wire 03:37 - Another uptempo backbeat based slightly buzzy krauty?
9. ** Gravity Freeze 03:07 - Another R&B Funk hip swayer.""",
    },
    {
        "key": "palace-ox",
        "lib_artist": "Palace",
        "album": "Ox",
        "label": "Awal",   # CONFIRM: review says "Palace Presents/Awal"
        "doc_id": "1a9Wq3fnul1ITzeQk3JWf2vKiMFgUG8yo5JKke4KcNgc",
        "body": """Album / Artist: Ox / Palace

Label: Palace Presents/Awal

Release Date: September 18, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Dreamy, floaty Palace, all of them new dads and singing about it. Big basslines, guitars that drift instead of hit. Great road trip music. - DJ Stace

Release Notes:

Fifth album from the London band; first release on their own label, Palace Presents (distributed by AWAL).

Written as the band members became fathers; songs about watching a child hear music for the first time.

Reviewers hear a floatier, dreamier record than 2024's Ultrasound.

Ten tracks, about 44 minutes.

released September 18, 2026

FCCs: 3,8,10

RIYL: My Morning Jacket, Bombay Bicycle Club, Foals, Wild Beasts, Daughter, Jeff Buckley

Play: All but FCCs, Favs Rated with up to *****

Tracklist:

1. **** Dream On 04:23 - Mid-tempo rising rock anthem. Like Coldplay, but listenable. Lead single; announced the album. About becoming a parent. Cavernous bassline under vast dissonant desert guitars.
2. **** Kid 04:22 - Upbeat jangly toe tapper with great vocal styling. Second single; fatherhood through absence.
3. **** Ohio 03:42 - Loping, bouncy and infectious. Great falsetto peaks in vocals. Like this one, worth an edit, if PISS bothers us. FCC “piss wine” x1.
4. ***** Denny's 04:50 - Brilliant, beautiful mid-temp Yacht Rock anthem about home being where your heart is. Great lyrics and vocal styling. Play it.
5. **** Lucky Boy 03:20 - More upbeat jangle pop rock, on the edge of yachtiness. This one segues well with My Morning Jacket.
6. **** I've Been Laughing 03:52 - Uptempo jangle strummer with a great refrain.
7. Kicking Up Shadows 03:56 - Shuffling uptempo sparklier guitar pop.
8. Brown Bread 06:26 - Iron&Wine type rhythm, guitar and lyrics, upbeat Americana flavored guitar pop. Good tune, but the whole refrain is FCC. FCC fuck x3, shit x3.
9. ***** Made My Bed 04:01 - Vast, big sky soaring guitar. Beautiful lyrics. Dreamy love song. Just about perfect. Play it.
10. Ox 05:21 - Up-paced shuffling snare rhythm, vocals get alittle Hamilton Leithauser on this one. Nice closer, but with an FCC. FCC “fucking grateful” x2.""",
    },
    {
        "key": "dread-spectre-council-thetans",
        "lib_artist": "Dread Spectre Council",
        "album": "Thetans",
        "label": "Handmade Records",
        "doc_id": "1QI92WK7LL15J7xBmXRKunRo8Z7cXa5A3EFvMMGp_dlo",
        "body": """Album / Artist: Thetans / Dread Spectre Council

Label: Handmade Records

Release Date: March 29, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Summer sleeper that too many missed. Fuzzy, crashing DIY indie rock from one guy in Norway. Solid songwriting and spectacular musical craftsmanship. If you miss the Built To Spill and Swervedriver lane, pull up a chair. This deserves to be an indie hit, let’s encourage more from this guy. 10/10 - DJ Stace

Release Notes:

Solo project of Kenneth Amundsen from Nittedal, Norway; billed as indie rock from Oslo.

https://www.dreadspectrecouncil.com/

Released March 2026 by Handmade Records / Indigo (Oslo)

10 tracks, about 34 minutes.

released March 29, 2026

FCCs: None found

RIYL: Ty Segall, Built To Spill, Swervedriver, Dungen, Yo La Tengo

Play: All, Favs Rated with up to *****

Tracklist:

1. ***** Hex's Up 03:50 - Kickass heir to Swervedriver starts the album strong. Play this one.
2. ***** Hooves & Cloves 03:24 - Killer Melvinsesque monotone vocal chunky riffage intro. Explodes to wailing fuzz guitar greatness that will make Ty Segall wonder if someone stole his DNA. Segue with Ty Segall or Melvins.
3. ***** Where Would the Light Go 03:11 - Upbeat pop anthem. Great melody and vocals. Best I can characterize this one is “Jangle-fuzz” and it’s pretty great. Hard to believe this is a one man show.
4. **** Sungate 03:52 - Great lilting guitar intro, solid lyrics, crescendos into a crashing outro. Another great track. Found audio recording in the background.
5. **** Spiderette 04:21 - Solid upbeat indiepoprock anthem. Bandcamp focus track. Would be right at home segued with Replacements or softer Iggy.
6. **** Evil Incarnate 02:37 - Medium paced rocker. Another Ty Segallesque fuzz rock anthem. More found audio recordings overlaid for atmospherics. Love it.
7. *** Wildling 02:59 - Quiet Travis pick tune that would be at home in Billy Bragg’s catalog. Outlier?
8. **** Treasure Trove 03:10 - Another killer medium tempo rocker with less fuzz than other tracks, with great effect. Great refrain. Play it.
9. ***** Raven 04:54 - Midtempo Built to Spill style guitar rocker. Excellent lyricism. Segue with BtS, obviously.
10. ***** Summon the Sparks 03:38 - Love the off kilter pace of this one. Reminds of Pedro the Lion. Another great song, lyrically and musically. Killer anthemic power chord ending to the left-field sleeper album of the year.""",
    },
    {
        "key": "sluice-companion",
        "lib_artist": "Sluice",
        "album": "Companion",
        "label": "Mtn Laurel Recording Co.",
        "doc_id": "15UOGddOzcdXMiRaMbeYkPk4KdrC8Cza47o5XogoKEHk",
        "body": """Album / Artist: Companion / Sluice

Label: Mtn Laurel Recording Co.

Release Date: March 27, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Hushed, wordy Durham folk rock with two nine-minute stunners and a song about Zillow. Bill Callahan fans, form a line. - DJ Stace

“exists in a cloud of dreamy contemplation” - Pitchfork

Release Notes:

Third album from the Durham, N.C., folk-rock band led by Justin Morris (guitar, piano, synth, kalimba, field recordings, vocals).

10 tracks, about 44 minutes

released March 27, 2026

FCCs: 3,4,6,10

RIYL: Fust, Bill Callahan, Friendship, Hovvdy, Sin Ropas, Red Red Meat, Califone

Play: All but FCCs, Favs Rated with up to *****

Tracklist:

1. ***** Beadie 04:01 - Slow, plodding spacious, epic and glorious opener. Plodding anthem moves to a crashing crescendo at 3 minutes until the end. Great vocals. Lyrics refer to the romantically involved partners from TV’s “The Wire.”
2. **** Ratchet Strap 03:30 -. Quiet, low fi, no country strummer, reminiscence of Uncle Tupelo’s harmonic best, ends up a rocker by the end. Fiddles and two part harmonies always get me. Segue with Avett Brothers.
3. WTF 03:33 - Quiet intro gives way to “orchestra tuning vocal” layering, then quietly transitions to a fuzzy guitar plodder that reminds in places of Jason Molina. Great epic guitar interludes. FCC fuck x2.
4. *** Gator 08:46 - Very long stream-of-consciousness track; Lovely guitar accompaniment. Morris joked about making it a single. Kind of track you don’t hear starts at first, but grabs you and holds you so you end up listening to it again. FCC “smelled like shit” x1, piss x1.
5. The Ephemeral Stream 01:46 - Quiet, atmospheric recording, pastoral. Some sort of chopping breaks the silence. Bracing.
6. Torpor 02:49 - Medium tempo, story song about being the victim of a home robbery. Starts with soft guitar and transitions to a country rocker. FCC “get on the fuckin’ ground” x1.
7. Unknowing 09:01 - Slow, fuzzed but soft intro. VERY heavily distorted autotuned lyrics. Centerpiece; built on a prayer by a Trappist monk (source: Paste Magazine). Seque with “Tripped on Your Cape” by Sin Ropas. Final 90 seconds is near total silence, so you can crossfade at 7:30.
8. ***** Overhead 03:57 - Another quiet strumming guitar and vocal start, without being redundant. Reminds of Bill Callahan, here.
9. ***** Zillow 03:13 - Great no country pop toe tapper with lyrics culled/inspired from Zillow descriptions and comments about local housing prices.
10. Vegas 03:18 - Upbeat country rocker, gives Old 97’s vibes. FCC shit x3.""",
    },
    {
        "key": "tricky-different-when-its-silent",
        "lib_artist": "Tricky",
        "album": "Different When It's Silent",
        "label": "False Idols",
        "doc_id": "1PlCAGtgt796YoaYdZX7ySGyVDpfh3onRy8JZBctMP4M",
        "body": """Album / Artist: Different When It's Silent / Tricky

Label: False Idols

Release Date: July 17, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Tricky's best in years. Dark, guitar-heavy trip-hop, with Mitch Sanders' ghostly falsetto doing a lot of the heavy lifting. - DJ Stace

Release Notes:

Bristol producer Adrian Thaws' 15th studio album and first full-length under his own name in six years, on his own False Idols label.

Bristol singer Mitch Sanders, 22, sings top lines on 12 of 14 tracks in a high falsetto; guests also include Marta Złakowska, Radana and Run Red Rambo.

Reviewers note distorted guitars, hypnotic basslines and electronic textures, with Tricky's low growl underneath.

released July 17, 2026

FCCs: 6,10

RIYL: Massive Attack, Portishead, Martina Topley-Bird

Play: All but FCCs, Favs Rated with up to *****

Tracklist:

1. **** I Still See Me There 03:39 - Slow, plodding, whispering, sinister and Trypnotic. Falsetto vocals float over Tricky’s growling whispers. Tricky is back.
2. ** I'm Yours 02:36 - Medium paced bass and snare dominant rhythm line. Feat. Mitch Sanders falsetto; Interludes of Walls of sound applied to EDM.
3. *** Be Still In The Pain 03:22 - Upbeat by Tricky standard. Feat. Mitch Sanders and Run Red Rambo great falsetto duet juxtaposition. Abrupt ending.
4. *** I Tried 02:16 - Soft guitar intro, gives way to buzzing plodding marching rhythm and metallic guitar accompaniment with bass and vocal interludes.
5. So Cold 02:39 - Medium to uptempo ticking and buzzing tapper. “Bright,” for Tricky.
6. Paris Maybe 02:53 - Pretty straightforward guitar, bass and drums rock ballad? Would be at home in the 90’s segued to Divinyl. Not bad, but seems sonically isolated from the rest of the album. FCC fuck x1, shit x1.
7. *** Cannon Fodder 02:48 - Organ & heartbeat intro. Breathy falsetto is right up front. Transitions to some very fuzzy, desert rock guitar solo, then back to breathy whispers and organ to the end.
8. ***** Because I Don't Know 04:34 - Sinister, falsetto, trancy, repetitive, infectious groove. This is the hit on the record. Wall of sound drops with soaring falsetto crescendos are great. Can’t play it enough.
9. ** Marinade 03:20 - String intro, gives way to “Velvet Undergroundish” bass riff and spoken lyrics. Kinda cool. Would segue well with Kae Tempest. Abrupt ending.
10. Radana 03:10 - Middle Eastern flavor to the underlying music. Lyrics go hard. Would segue well with DAM. Feat. RMR & Radana. FCC fuck x3, piss x1, bitch x2.
11. *** Piano 02:43 - Piano and vocals with light atmospherics transition to strings and operatic chorale accompaniment. Lovely. Another abrupt ending.
12. **** Frontier Town 01:40 - Killer stomp, cap and cal.,Clearly inspired by field songs. If Alan Lomax recorded EDM, this would be on his radar. Segue with Delta blues or field recordings from Parnman Farm. short.
13. **** Hengrove Blues 02:57 - Soft acoustic strummer about a Bristol neighborhood. Lovely falsetto vocals with Tricky’s low growl underneath.
14. *** Out of Place 02:38 - Quiet operatic opening vocals give way to a fast-paced staccato growling rocker with Tricky and Marta Złakowska’s vocals full forward. . Lead single (April 2026, announced the album).""",
    },
    {
        "key": "ty-segall-chrome",
        "lib_artist": "Segall, Ty",
        "album": "Chrome",
        "label": "Drag City",
        "doc_id": "1JMnEW-DGAMR6OVfNyQAopLlfi75FOTfMnkBZSOEHiVA",
        "body": """Chrome / Ty Segall

Label: Drag City

Release Date: August 28, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Ty goes heavy. Mostly cut live with the band, fuzz pinned in the red, with a couple of crooner turns. Big, dumb, glorious riffage,and smart lyrics, man. - DJ Stace

Release Notes:

Ty Segall's 18th solo studio album, billed as one of his heaviest.

Recorded mostly live with Ben Boye, Evan Burrows, Mikal Cronin and Emmett Kelly, plus Bitchin Bajas' Cooper Crain.

Same-day companion Love Fuzzz EP (Twins cover plus My Pet Guru).

Louder Than War Album of the Week.

Nine tracks, about 33 minutes.

released August 28, 2026

FCCs: None found

RIYL: Thee Oh Sees, King Gizzard & The Lizard Wizard, Black Sabbath, Fuzz

Play: All, Favs Rated with up to *****

Tracklist:

1. *** Hospital 04:43 - Opener; quiet/loud blippy dirge transfers into a chaotic twin-guitar solo with all the slanted guitar god greatness you expect of Segall.
2. Running to Nowhere 02:30 - Super sludgy, with notes of Fu Manchu ruffage. Screamy lyrics give way to Segall's harmonics, gives way to screamy lyrics again.
3. ***** Black Paint 02:00 - Jangle-fuzz bouncing rock anthem with Segall’s wailing lead solos. Lead single and in a sane world, a hit. (June 2026);
4. *** Glass 04:27 - Medium upbeat. Proggy and metallic; Bass in heavy modulated fuzz; guitar duel mid-song. Segue with King GIzzard.
5. ***** Play Cowboys 04:59 - Climbing raw opening riffage is infectious. Psych ballad with keyboards; Ty croons. Probably my favorite on the album.
6. Everything You've Been 02:06 - Fast paced, breathy, least standout on the album. Still better than 99% of what was released, last year.
7. Let Go 03:33 - Starts with some 1/4” audio jack feedback lead that turns into a fast paced guitar puncher with siren guitar solo highlights.
8. *** Separation 02:52 - Fast paced, snared out punk rocker. Fun.
9. *** Chrome 05:08 - Ty steals and reforms Ted Nugent’s blues metal riffage for a machine gun repetitive rocker that will make you drive too fast if you aren’t careful. Title track closer, the longest at 5:08.""",
    },
    {
        "key": "lex-walton-ultimate-love-forever",
        "lib_artist": "Walton, Lex",
        "album": "Ultimate Love Forever",
        "label": "Sub Pop Records",
        "doc_id": "1ApggA6DvzNnf6sdS-JpH3Dy_XY-sjk7QQs7HLkB2Y4M",
        "body": """Album / Artist: Ultimate Love Forever / Lex Walton

Label: Sub Pop Records

Release Date: August 26, 2026

Review Date: 10/4/2026

Reviewer: DJ Stace

General Comments / Reviews:

Twenty minutes of scuzzy, anxious warbling power pop that bites the music-industry hand that feeds it. Sharp, funny and over before you know it (way too soon, IMHO). I'm loving this album right now. - DJ Stace

“wiggly, anxious power pop” - Paste

Release Notes:

Seven-song Sub Pop debut, about 20 minutes; first released on Youth Against Satan before Sub Pop signed her in August 2026.

Written by Walton; produced by Walton and Dan Boeckner (Wolf Parade, Handsome Furs); recorded, mixed and mastered by Ben Greenberg (Uniform, The Men).

CD/LP out Nov. 20, 2026 in North America.

released August 26, 2026

FCCs: 2,3 Track 4's title contains a slur.

RIYL: Wolf Parade, The Men, Speedy Ortiz, Parquet Courts

Play: All but FCCs, Favs Rated with up to *****

Tracklist:

1. ***** For Thee I Sing 02:01 - Smashing, crashing glorious intro. Walton’s warbling sarcasm and spit is the anthem we all need right now. Play it.
2. Hipster Runoff 02:17 - FIrst Single. Killer flailing angular rocker. Probably worth an edit! Single. About the blog-era buzz band life cycle. Abrupt ending. FCC shit x1.
3. ***** Yr Op-Ed Won't Get You Into Heaven Anymore 02:52 - Stoogeseque growler with soaring vocal interludes and a killer Stooges style solo freakkout. FCC go fuck yourself x1.
4. *** USA = FAG NATION 03:23 - Upbeat Kraut-rockish talker. “I am not your market”. Title contains a slur. Consider on airbreaks.
5. *** I Wish I Was An M80 03:15 - Medium pop rocker with a killer rhythm, and interludes. FCC “After she sucked us both off…”
6. ***** Adrian Borland Will Have His Revenge On London 03:08 - Staccato strumming bright guitar and Walton’s fantastic warble is perfect here. Lots of “Meatloaf” feels on this on. Devolves into a crashing distortion fest with strings to a crashing outro. This one will be in heavy rotation on my playlist for years. About The Sound's Adrian Borland.
7. ***** Ultimate Love 4Ever 03:06 - Title track. Bouncing rocking perfection. Make this one a hit. This is the anchor hit song for soundtrack for the remake of “Pretty in Pink” (if anyone were ever dumb enough to do that). Fun, infectious, I guarantee you will dance like Molly Ringwald, when noone is looking.""",
    },
]

# ---------------------------------------------------------------------------
# Bandcamp preview links for the Zookeeper track "url" field (checked Oct. 6, 2026).
# Each entry: album key -> (Bandcamp site, {track number: track page path}).
# Only tracks Bandcamp lets people stream are listed, so the others keep url "".
# These are stable track pages that play the audio. Bandcamp's raw .mp3 stream links
# are signed and expire, so they are not stored here.
# ---------------------------------------------------------------------------
BANDCAMP = {
    # Corpse Pose (track 12) is not on the Bandcamp release, so it has no link.
    "twisted-teens-blame-the-clown": ("https://twistedteens.bandcamp.com", {
        1: "is-it-real", 2: "wild-connection", 3: "i-operate", 4: "little-seed",
        5: "100-bill-is-gone", 6: "peekaboo-hand", 7: "not-real", 8: "who-could-it-be",
        9: "circus-clown", 10: "hurricane", 11: "white-hot-coal"}),
    "twisted-teens-florida-water-blues": ("https://twistedteens.bandcamp.com", {
        1: "why-did-you-miss-it", 2: "hand-me-a-cigarette", 3: "swamp",
        4: "florida-water-blues-2", 5: "guided-thunder", 6: "top-of-the-world-hwy-no-2",
        7: "concealed-weeping", 8: "riding", 9: "business", 10: "javelina",
        11: "weather-the-season", 12: "dancer", 13: "sun-go-down"}),
    # Only three tracks stream on this page.
    "this-is-lorelei-the-singer-in-my-band": ("https://thisislorelei.bandcamp.com", {
        2: "oh-no-now-my", 3: "billy-came-back", 9: "the-kid-with-the-crown"}),
    "little-barrie-gravity-freeze": ("https://littlebarrie.bandcamp.com", {
        1: "more-bad-miles-of-road", 2: "it-isnt-soul", 3: "december", 4: "luggin-hurt",
        5: "talk-it-up-like-its-wanted", 6: "anything-you-are", 7: "coralisa",
        8: "wire", 9: "gravity-freeze"}),
    "palace-ox": ("https://palace.bandcamp.com", {
        1: "dream-on", 2: "kid", 3: "ohio", 4: "dennys", 5: "lucky-boy",
        6: "ive-been-laughing", 7: "kicking-up-shadows", 8: "brown-bread",
        9: "made-my-bed", 10: "ox"}),
    "dread-spectre-council-thetans": ("https://handmaderecs.bandcamp.com", {
        1: "hexs-up-2", 2: "hooves-cloves-2", 3: "where-would-the-light-go-2",
        4: "sungate-2", 5: "spiderette-2", 6: "evil-incarnate-2", 7: "wildling-2",
        8: "treasure-trove-2", 9: "raven", 10: "summon-the-sparks"}),
    "sluice-companion": ("https://sluice.bandcamp.com", {
        1: "beadie", 2: "ratchet-strap", 3: "wtf", 4: "gator", 5: "the-ephemeral-stream",
        6: "torpor", 7: "unknowing", 8: "overhead", 9: "zillow", 10: "vegas"}),
    "tricky-different-when-its-silent": ("https://tricky.bandcamp.com", {
        1: "i-still-see-me-there-feat-mitch-sanders", 2: "im-yours-feat-mitch-sanders",
        3: "be-still-in-the-pain-feat-mitch-sanders-run-red-rambo",
        4: "i-tried-feat-mitch-sanders", 5: "so-cold-feat-mitch-sanders",
        6: "paris-maybe-feat-mitch-sanders", 7: "cannon-fodder-feat-mitch-sanders",
        8: "because-i-don-t-know-feat-mitch-sanders", 9: "marinade-feat-mitch-sanders",
        10: "radana-feat-mitch-sanders-radana", 11: "piano-feat-mitch-sanders",
        12: "frontier-town-2", 13: "hengrove-blues-feat-mitch-sanders",
        14: "out-of-place-feat-marta"}),
    # Only two tracks stream on this page.
    "ty-segall-chrome": ("https://tysegall.bandcamp.com", {
        2: "running-to-nowhere", 3: "black-paint"}),
    "lex-walton-ultimate-love-forever": ("https://youthagainstsatan.bandcamp.com", {
        1: "for-thee-i-sing", 2: "hipster-runoff",
        3: "yr-op-ed-won-t-get-you-into-heaven-anymore", 4: "usa-fag-nation",
        5: "i-wish-i-was-an-m80-2", 6: "adrian-borland-will-have-his-revenge-on-london",
        7: "ultimate-love-4ever"}),
}


def add_bandcamp_urls(key, tracks):
    """Fill each track's url from the BANDCAMP table when a link is known."""
    site, pages = BANDCAMP.get(key, ("", {}))
    for t in tracks:
        slug = pages.get(t["seq"])
        if slug:
            t["url"] = "{}/track/{}".format(site, slug)
    return tracks


# Matches one track line: "7. ***** Title 03:12 - notes". Stars and notes are optional.
TRACK_RE = re.compile(r"^(\d+)\.\s+(?:\*+\s+)?(.+?)\s+(\d{1,2}:\d{2})(?:\s*-.*|\s*\.?\s*)$")


def parse_tracks(body):
    """Pull (seq, title, hh:mm:ss) out of the 'Tracklist:' section of a review body."""
    tracks = []
    in_list = False
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("Tracklist:"):
            in_list = True
            continue
        if not in_list:
            continue
        m = TRACK_RE.match(line)
        if not m:
            continue
        seq, title, mmss = m.groups()
        minutes, seconds = mmss.split(":")
        # Zookeeper wants hh:mm:ss, so pad "3:02" out to "00:03:02".
        duration = "00:{:02d}:{:02d}".format(int(minutes), int(seconds))
        tracks.append({"seq": int(seq), "track": title.strip(), "duration": duration, "url": ""})
    return tracks


def album_payload(a):
    """Build the POST /api/v1/album body for one album."""
    attributes = {
        "artist": a["lib_artist"],
        "album": a["album"],
        "category": "General",   # all prior reviewed albums use General
        "medium": "CD",          # CONFIRM: her new releases are digital
        "size": "Full",
        "location": "Pending Appr",   # keyed albums with reviews wait here for approval
        "bin": None,
        "coll": False,
        "tracks": add_bandcamp_urls(a["key"], parse_tracks(a["body"])),
    }
    label_id = KNOWN_LABEL_IDS.get(a["label"])
    # Zookeeper's Albums.md shows the POST body with "data" as an ARRAY of one album,
    # so we wrap the album in a list.
    if label_id:
        # Label already exists: link it by ID.
        doc = {"data": [{"type": "album", "attributes": attributes,
                         "relationships": {"label": {"data": {"type": "label", "id": label_id}}}}]}
    else:
        # Label is new: send its name in an "included" object; Zookeeper creates it.
        local_id = "local-" + a["key"]
        doc = {"data": [{"type": "album", "attributes": attributes,
                         "relationships": {"label": {"data": {"type": "label", "id": local_id}}}}],
               "included": [{"type": "label", "id": local_id, "attributes": {"name": a["label"]}}]}
    return doc


def review_payload(a, tags):
    """Build the POST /api/v1/review body for one album."""
    tag = tags.get(a["key"], "TAG_PENDING_" + a["key"])
    # Zookeeper stores line breaks as \r\n, as in her older reviews.
    text = a["body"].replace("\r\n", "\n").replace("\n", "\r\n")
    return {"data": {"type": "review",
                     "attributes": {"airname": AIRNAME, "published": True,
                                    "date": REVIEW_DATE, "review": text},
                     "relationships": {"album": {"data": {"type": "album", "id": tag}}}}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags", help="JSON file mapping album key -> Zookeeper tag")
    args = parser.parse_args()
    tags = json.loads(Path(args.tags).read_text()) if args.tags else {}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    albums = [{"key": a["key"], "post_to": "/api/v1/album", "source_doc": a["doc_id"],
               "payload": album_payload(a)} for a in ALBUMS]
    reviews = [{"key": a["key"], "post_to": "/api/v1/review", "payload": review_payload(a, tags)}
               for a in ALBUMS]
    (OUT_DIR / "albums_for_approval.json").write_text(json.dumps(albums, indent=2, ensure_ascii=False))
    (OUT_DIR / "reviews_for_upload.json").write_text(json.dumps(reviews, indent=2, ensure_ascii=False))
    for a in albums:
        n = len(a["payload"]["data"][0]["attributes"]["tracks"])
        print(a["key"], "tracks:", n)


if __name__ == "__main__":
    main()
