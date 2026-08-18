# Camp Perkins reel — music mix

Track: **"Morning Light on the Water"** (Suno, generated 18 Aug 2026 from
`plan/suno-prompt-camp-perkins.md`). 3:09, 48 kHz stereo.

Mixed **locally with ffmpeg, not in Descript**. If the reel is ever re-cut in
Descript the music is lost and must be re-applied with the command below.

## The problem it also fixed

Descript's export came out at **-32.1 LUFS** — far too quiet for web, and 18 dB
*below* the music. Simply laying the track underneath would have buried the
voices. The mix normalises speech to -16 LUFS first, then sits the bed under it.

## Levels achieved

| | mean | max |
|---|---|---|
| Speech, normalised | -21.1 dB | -1.5 dB |
| Music bed at mix level | -31.9 dB | -15.8 dB |
| Finished reel | -17.6 LUFS integrated, LRA 8.0 | |

Music sits about **11 dB under** the speech, and sidechain compression pulls it
further back under each spoken line, lifting again in the gaps.

## The command

```
ffmpeg -i reel.mp4 -i "Morning Light on the Water.mp3" -filter_complex "\
[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,asplit=2[sp1][sp2];\
[1:a]volume=-16dB,afade=t=in:st=0:d=4,afade=t=out:st=175:d=6[mus];\
[mus][sp2]sidechaincompress=threshold=0.025:ratio=12:attack=15:release=450:makeup=1[duck];\
[sp1][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]" \
 -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 160k -movflags +faststart -y reel-music.mp4
```

Fade in over 4s; fade out from 175s over 6s so it lands with the last words.

## Still to consider

The six individual highlight cuts are also around **-32 LUFS** and would benefit
from the same `loudnorm=I=-16` pass, with or without music.
