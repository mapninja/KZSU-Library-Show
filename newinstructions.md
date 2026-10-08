ok, I've been trying to work across two machines for this project, but that seems to be causing problems, and UIT has blocked the syncing across instances for us. I want to completely rescaffold this KZSU project, to run on this machine, only. Most of the skills were created on this machine and moved,so it should be possible to examine the project and rebuild it so that we get a set of bulletprooof skills and workflows. Here's what I need:

I need you to create my baseline musical taste profile, and repopulate the dashboard.

Your sources are my KZSU past playlists and reviews, and all of my youtube music paylists, as well as my YTM activity from google takeout

For my weekly listening, I want you to help maintain my Stace's Weekly Playlist which you should add suggested new releases, tracks relevant from "day in music" facts, and riffing on recent release albums I have been playing by suggesting alternative tracks, etc...

Your sources should be stereogum, pitchfork, indieisnotagenre, and other similar review sites, as well as the new release pages/feeds for the labels I have played. You should also use any emails from Mark Mollineaux or the Music Dept that list available for review records. 

For my Thursday Night 6-8pm Pacific "The Library Show" on KZSU 90.1FM Stanford, CA, I want you to maintain these artifacts:

My YTM playlists:
DJ Stace library show Air Order - Is the draft AIr Order Playlist, that I listen to to get a feel for the flow of the show draft.  THis playlist is built in conjunction with the weekly script, built from recent releases already in rotation, new releases, and tracks relevant to "Today in Music" and other timely topics.  This playlist should provide roughly 1:15 hrs of music for each hour of show, so that I have an extra 30 minutes of music to cull each week. I will occasionally add tracks to this playlist,during the week, as well. 

DJ Stace library show working - Is the draft working playlist for the show. It should be maintained in reverse order, so that I can turn of autoplay and always play the last track first, so that playback stops by itself in the YTM interface. This is how I crossfade. It should always be in synced with changes to the  AIr Order Playlist. 

The Library Show with DJ Stace (month,day,year Show) - This playlist should be built each week, from the official KZSU playlist,  after The Library Show airs, so that there is a playable archiveal version of each of my shows. This captures on the fly changes, such as requests, that I make during the on the air. 

Stace's Weekly Playlist - This is my review list, where you should put suggestions, new release tracks, upcoming Day in Music tracks, tracks promoting upcoming bay area shows, etc... it is a rolling playlist, that you should ADD to bu mostly NOT delete from. I will remove tracks when they feel stale. You should use this playlist as a source for building the Air Order and Working drafts. Note when I delete Day in Music tracks from this playlist and find new ones to replace, if warranted by the relevance of music based upon my tastes. 

FCC Edit needed - All playlist suggestions should be vetted agains the available lyrics sites for FCC lyrics, and if the tracks are strong enough they should be added to this playlist for me to consider making Radio Edit versions of. All FCC suggestions should be clearly noted in the show script, notes, etc...

DJ Stace - Next Show - Is my old baseline playlist where I've been dumping tacks for the show, and I continue to use. You should monitor it for changes that suggest new interests for show playlist inclusion. 

To Review - This existing playlist is stale and should be repopulated with the albums I have requested Boilerplate Review md files for. 

Specialty shows - For seasonal and topical shows (Halloween, Valentine's, Xmas, etc...), build suggestion playlists, drawn from my profile, with 2.5 hrs of content for me to review. For instance, Halloween is coming up, so I will need thematic music (Ministry - Everyday is Halloween, FCC clean Misfits, etc...) for a show. THe playlists should ALSO take into account Day in Music, New releases, etc... when overlap makes it possible. 

KZSU Current Adds - This playlist should be refreshed each week from the KZSU Current Adds list from Zookeeper. These are the albums that have been recently reviewed and put in charting rotation for KZSU. This playlist should be filtered from the current adds to fit my musical profile.

College radio Charts Top 50 - Maintain a playlist of the current college radio top 50 from the indie/rock/alt charts.

KZSU Library SHow Draft and final scripts

Library SHow Working Playlist Notes Sheet - This shoud be a GOogle Sheet with the data that will build the final AIr Order and WOrking playlists. It should be sources from the Weekly playlists, with the notes and data for all of the adds you put in that for me to review each week. It should be ordered as the weekly playlist, and it should include all relevant track info (artist, name, album, orig release date, label, notes, playtime, fcc status[link to lyics site]) as well as the thematic/topical/date notes for the tracks. try to suggest micbreak talking points, etc... The SHeet should include two checkbox columns one called 'cull' and one called'replace' whic indicate that I want you to drop the track altogether, or find an alternative track for the same purpose. 

Library Show Working Show Script - THis is a Google Document built from the Library SHow Working Playlist Notes Sheet and formatted to be as readable as possible on a laptop screen. It should contain all of the notes/metadata from the sheet, inline for each track. Add a bay area shows air break. 

Library SHow  FInal SHow Script - Mirrors that Working hshow script, but represents that changes, deletions, replacements, I've indicated for the week, in the working playlist sheet, as well as changes I've made to AIr order, weekly of next show.  It should be built on Wednesday Night so that I can review and ask for changes Thursday before the show. 

weekly playlist csv for upload to KZSU. THis is the reverse order csv, with mic breaks, and zookeeper tags, forrmatted for upload to the KZSU zookeeper site for the live playlist during the show. the playlist should be names library_show_playlist_DATE.csv and formatted as noted on the upload page:

CSV Format
File must be UTF-8 encoded, with one track per line. Each line may contain 4, 5, or 6 columns:

artist  track  album  label  or
artist  track  album  tag   label  or
artist  track  album  tag   label  timestamp
where each column is enclosed by the specified field enclosure characters "", and separated by a delimiter character , . An empty row inserts a mic break.

Any file data not in this format will be ignored.

Stace's KZSU FIltered Review Shelf - A google sheet of all of the suggest new releases, KZSU review shelf albums from MusicDept/Mark Mollineaux, and albums/tracks that I have added to To Review. THis list should include a checkmark column I can use to indicate I want Review Boilerplate and adds to the To Review playlist. 



ALl Artifacts should be published to the Google Drive /KZSU/ folder. FEel free to create an obvious system for archiving old artifaccts, each week, and use the top level folder for all current artifacts. 

ALl code for the project should be placed in the /Users/maples/Github/KZSU-Library-Show repo

/Users/maples/Github/KZSU-Album-Reviews should be used form y reviews (boilerplate stuvbe, finals, etc...)


7. Decisions needed
Is Sat/Fri 11 a.m. right for the draft, or do you want it Sunday?
Let's do an early draft on Thursday Nights, after THe lbrary show

Reversed CSV: confirm Zookeeper expects last track first.
Yes, that will load the tracks in the correct order to use in the live playlist app

Playlist API: OK to use ytmusicapi with your headers, browser as fallback?
Yes, prefer API for efficiency, with browser for resilience

Can I rotate the KZSU API key, or do you do it?
It doesn't need to be refreshed

Connect KZSU-Album-Reviews as a workspace folder?
yes

Bay Area venues to prioritize?
here are the typical ticket giveaway venues for KZSU: Mountain Winery
Yoshis
Independent
Fox
Chapel
Chapel
Yoshis
The Lab
The Lab
The Lab
Chapel
Chapel
Fox RWC
Chapel
Yoshis 
Yoshis 
Freight
Chapel
Fox
Guild
Chapel
Chapel
Chapel
Freight
Fox
Chapel
Fillmore
Fox RWC
Chapel

But you should base the Bay Area concerts list on my musical tastes. Use http://www.foopee.com/punk/the-list/ as a primary source

OK to pause or delete the old Mac tasks listed above?
Yes, they should be puased, then listed for me to delete, once the new workflows are tested and solid

Push method: you push each week, or add a GitHub token in .env?
I will give you a token in .env
