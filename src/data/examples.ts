export type ExampleScript = {
  id: string
  title: string
  description: string
  script: string
}

export const DEFAULT_SCRIPT = `Stop met scrollen. [pause]
Dit is de fout die bijna iedereen maakt als ze hun eerste YouTube-video opnemen.

Je script is te lang. [pause]
Je hook is te traag.
En je CTA komt pas ná de outro.

Hier is de regel: [pause]
<emphasis>De eerste zin moet een belofte zijn, geen begroeting.</emphasis>

Niet: "Hey guys, welkom terug."
Wel: "In 40 seconden kun jij dit ook."

Probeer het in je volgende video. [pause]
En volg voor deel twee: hoe je de middenmoot spannend houdt.`

export const EXAMPLES: ExampleScript[] = [
  {
    id: 'shorts-hook',
    title: 'Shorts-hook',
    description: '45 seconden, kijkers stoppen in seconde 1.',
    script: `Stop. [pause]
Als jij dit nog doet in 2026, verspil je views.

De meeste Shorts beginnen te traag. [pause]
Geen belofte. Geen spanning. Alleen een begroeting.

Doe dit: [pause]
<emphasis>Open met een probleem dat ze herkennen in één zin.</emphasis>

Dan één snelle tip.
Dan één bewijs.
Dan een CTA in de laatste twee seconden.

Klaar. [pause]
Volg voor de template die 3× beter presteert.`,
  },
  {
    id: 'tutorial',
    title: 'Tutorial',
    description: 'How-to met duidelijke stappen.',
    script: `In vijf minuten leer je precies hoe je dit zelf doet. [pause]

Stap één: open je editor en plak dit script.
Stap twee: markeer de pauzes waar je adem wilt nemen.
Stap drie: kies een kalme stem — zoals Lux — en speel de opening af.

De truc zit niet in fancy tools. [pause]
<emphasis>De truc zit in een script dat iemand hardop kan volgen.</emphasis>

Als je vastloopt: pauzeer de video, doe de stap, en ga pas verder.
Aan het eind download je je voice-over en sleep je 'm in je timeline.

Klaar. Probeer het nu op je volgende clip.`,
  },
  {
    id: 'top-5',
    title: 'Top 5',
    description: 'Countdown die blijft hangen.',
    script: `Dit zijn de vijf fouten die je bereik kapotmaken. [pause]
We beginnen bij vijf — en nummer één doet pijn.

Vijf: te lange intro's.
Vier: geen CTA voor de outro.
Drie: een stem die niet bij je niche past.
Twee: hooks zonder belofte.

En nummer één: [pause]
<emphasis>Publiceren zonder eerst hardop te lezen.</emphasis>

Als je script raar klinkt in je eigen oren, klinkt het erger op YouTube.
Bewaar deze lijst. Gebruik 'm voor elke video.`,
  },
  {
    id: 'review',
    title: 'Review',
    description: 'Eerlijk oordeel, duidelijke verdict.',
    script: `Ik heb dit een week gebruikt. Hier is mijn eerlijke oordeel. [pause]

Wat werkt: de interface is snel, de stem klinkt natuurlijk genoeg voor faceless content, en je kunt scripts in een keer klaarzetten.

Wat minder werkt: [pause]
zonder echte server-TTS blijf je afhankelijk van je browserstem.
Dat is prima voor drafts — minder ideaal voor finale ads.

Verdict: [pause]
<emphasis>Sterk voor creators die snel willen schrijven en previewen.</emphasis>
Koop het als je workflow script-first is. Skip het als je alleen studio-MP3's nodig hebt.`,
  },
  {
    id: 'storytime',
    title: 'Storytime',
    description: 'Persoonlijk, met een wending.',
    script: `Drie jaar geleden zette ik bijna mijn kanaal stop. [pause]

Elke video voelde als schreeuwen in een lege kamer.
Geen comments. Geen terugkerende kijkers. Alleen algoritme-stilte.

Toen gebeurde dit: [pause]
ik herschreef één hook. Geen nieuwe camera. Geen betere microfoon.
Alleen één zin die een belofte deed in plaats van een begroeting.

De video explodeerde niet. [pause]
Maar hij bleef doorlopen. En de volgende ook.

De wending? [pause]
<emphasis>Het probleem was nooit mijn stem. Het was mijn opening.</emphasis>

Als jij nu vastzit — begin daar.`,
  },
  {
    id: 'faceless-docu',
    title: 'Faceless docu',
    description: 'Kalme, cinematische voice-over.',
    script: `Ergens tussen middernacht en dageraad verandert een stad van gezicht. [pause]

Lichten dimmen. Straten ademen leegte.
En onder die stilte blijft één stem over — rustig, oud, bijna fluisterend.

Dit is geen schreeuwende thumbnail-video. [pause]
Dit is een documentaire voor mensen die willen blijven hangen.

We volgen drie nachten.
Drie mensen.
Drie keuzes die niemand ziet.

Luister goed. [pause]
<emphasis>Want de belangrijkste details zitten tussen de pauzes.</emphasis>`,
  },
]

export const SPEECH_CHIPS = [
  { id: 'pause', label: 'Pauze', insert: '[pause]' },
  { id: 'long-pause', label: 'Lange pauze', insert: '[long pause]' },
  { id: 'whisper', label: 'Fluister', insert: '<whisper></whisper>' },
  { id: 'emphasis', label: 'Nadruk', insert: '<emphasis></emphasis>' },
  { id: 'slow', label: 'Langzaam', insert: '<slow></slow>' },
  { id: 'fast', label: 'Snel', insert: '<fast></fast>' },
  { id: 'laugh', label: 'Lach', insert: '[laugh]' },
  { id: 'soft', label: 'Zacht', insert: '<soft></soft>' },
] as const

export const LUX_VOICE = {
  id: 'lux',
  badge: 'Oude slaapstem',
  name: 'Lux',
  subtitle: 'Old man, night',
  description:
    'Oude, kalme documentaire-stem. Laag en slaperig — alsof hij naast je bed een verhaal voorleest.',
  short: 'Oude, kalme documentaire-stem',
} as const
