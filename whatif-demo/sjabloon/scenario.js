// =====================================================================================================
//  SJABLOON: zo werkt de IfScape3D-engine (een video = één scenario.js)
// =====================================================================================================
//
//  HOE EEN VIDEO ONTSTAAT
//  1. Kopieer deze map naar  whatif-demo/topics/<slug>/   (slug = korte naam, bv. 'moon-closer')
//     en geef `number` hieronder een nieuw nummer (uit onderwerpen.md).
//  2. Schrijf `lines` (de tekst die de stem zegt) en `default(at)` (wat er in beeld gebeurt).
//  3. Testbeelden (6 shots + overzicht, nog geen stem):
//        python3 whatif-demo/make_whatif.py <number> --stills
//     -> topics/<slug>/stills/overzicht.jpg      (eerst laten goedkeuren, regels/standaard-video.md)
//  4. Hele video:
//        python3 whatif-demo/make_whatif.py <number>
//     Stappen (STAGES): voice -> render -> audio -> final
//        voice   script.txt + voice.mp3 (xAI Atlas) + timing.json (echte zinstijden)
//        render  silent.mp4 (engine/render.mjs, Chromium, 720x1280, 30 fps)
//        audio   mix.wav (stem + achtergrond + effecten, -14 LUFS)
//        final   <slug>.mp4 (1080x1920) + upload.json
//     Opnieuw vanaf een stap:  --from render   /  --from audio
//
//  Los renderen kan ook (handig bij testen):
//        node whatif-demo/engine/render.mjs <slug> stills 5 12 30      # beelden op 5, 12 en 30 s
//        TO=10 node whatif-demo/engine/render.mjs <slug> video uit.mp4 3   # eerste 10 s, 3 workers
//        LOOK=blender ...                                                # Blender-look forceren
//
//  TIJD: alles in `default(at)` rekent met at('<id>') = { s: start, e: einde } van een zin, in
//  video-seconden. Zonder voice.mp3 schat de engine de tijden (2,55 woorden/s); na de stem
//  worden het de echte tijden, en schuift alles vanzelf mee. Gebruik dus altijd at(), nooit vaste seconden.
//
//  ASSEN: x = links/rechts, y = omhoog (meters), z = naar de camera toe / ervan af.
//  Posities zijn [x, y, z]; paden over de grond zijn [t, x, z].
// =====================================================================================================

export const topic = {
  number: 999,                 // nummer uit onderwerpen.md (make_whatif.py zoekt de map hierop)
  slug: 'sjabloon',            // = mapnaam onder topics/
  place: 'suburb',             // DE PLEK (engine/places/):
                               //   street (stadsstraat aan zee) · suburb (woonwijk + park + supermarkt) · boulevard (strand)
                               //   harbor (haven, nacht) · river-city (rivier + hangbrug) · airport · nature-park (meer/vulkaan)
                               //   mountain-village (sneeuw) · prehistoric (dino-vallei) · colosseum (Rome) · indoors (huiskamer/tv)
  force: 'calm',               // WAT ER GEBEURT (engine/forces/):
                               //   calm (niets) · day (tijd van de dag) · gravity · wind · water (stijgt/zakt) · tide (getij)
                               //   heat (zon dichterbij) · cold (donker/bevriezen) · quake · sinkhole · eruption · alien (ufo)
  question: 'What if ...?',    // de vraag (YouTube-titel zonder #shorts)
  title: 'What if<br>...?',    // titel in beeld bij de start (<br> = nieuwe regel)
  voOffset: 1.0,               // seconden stilte vóór de stem begint
};

// DE TEKST: [id, zin, pauze erna]
//   pauze: 'none' · '' (0,3 s) · 'pause' (0,5 s) · 'long' (1 s) · een getal = zoveel seconden stilte (climax, ± 3-4 s)
//   Regels (regels/standaard-video.md): Engels, "you", eerste zin "Imagine…", 130-200 woorden (± 60-90 s),
//   Europese eenheden. Geen [pause] binnen een zin: splits dan de regel.
export const lines = [
  ['imagine', 'Imagine…', 'pause'],
  ['intro', 'in a single minute, something changes everywhere at once.', 'pause'],
  ['place', 'You are walking your dog through a quiet park.', 'long'],
  ['normal', 'Normally, the number on the screen is zero.', 'long'],
  ['climax', 'Then, everything changes.', 3.5],
  ['q', 'What would you do?', 'none'],
];

// WAT ER IN BEELD GEBEURT. `at(id)` geeft { s, e } van een zin. Geeft één object terug (TL = timeline).
export default function (at) {
  const T_END = at('q').e + 2.4;                       // lengte van de video
  const dogX = t => -42 + 1.15 * t;                    // waar de hond is (loopt 1,15 m/s langs x): de camera loopt mee
  const cs = at('climax').s;
  return {
    T_END,

    // ---- LOOK -------------------------------------------------------------------------------------
    look: 'blender',       // Blender-look: AgX-kleuren, lage warme zon, zachte schaduwen, ronde mensen/dieren.
                           // Weglaten = de oude look. Alleen overdag; 's nachts schakelt hij zichzelf uit.
    // post: true,         // (zonder Blender-look) filmlook: ambient occlusion, gloed, vignet

    // ---- TITEL EN TELLER (HUD linksboven) ---------------------------------------------------------
    titleOut: at('place').e + .4,                      // titel verdwijnt
    hudIn: at('place').e + .7,                         // teller verschijnt (1e9 = nooit)
    hud: { label: 'LEVEL', unit: ' m', decimals: 0,    // of fmt: v => ... voor eigen opmaak
           second: { label: 'TIME', fn: (v, t) => t, unit: ' s', decimals: 0, showAt: at('normal').s } },   // optionele 2e regel
    counter: [[0, 0], [cs, 0], [cs + 2.5, 100], [T_END, 100]],   // [t, waarde]: de teller loopt lineair tussen de punten
    range: [0, 100],                                   // waarde -> 0..1 "sterkte" van de kracht (en het geluid)

    // ---- DE KRACHT ---------------------------------------------------------------------------------
    // Elke force leest zijn eigen forceParams (zie de kop van engine/forces/<force>.js). Voorbeelden:
    //   sinkhole: { radius: [[t, m], ...], center: [x, z] }       tide: { tide: [[t, y], ...], calm: 1, top: 6 }
    //   gravity/wind/water/heat: volgen `counter` + `range`        eruption: { ash, lava, ... } per onderdeel
    forceParams: {},

    // ---- ONDERTITELS IN BEELD (korte kernzinnen, cursief) ------------------------------------------
    captions: [[at('normal').s, at('normal').e + .6, 'Zero. As always.']],          // [van, tot, tekst]

    // ---- CAMERA ------------------------------------------------------------------------------------
    // Standaard: één doorlopende beweging. camPath = [t, [camera x,y,z], [kijkt naar x,y,z]], vloeiend ertussen.
    // Met camPath zet de engine ook vanzelf: titel aan, geen logo, geen eindkaart, laatste beeld blijft staan.
    camPath: [
      [0, [dogX(0) + 2.4, 1.3, 24.4], [dogX(0) - .3, .95, 20.1]],        // naast de hond, ooghoogte
      [cs, [dogX(cs) + 2.4, 1.4, 24.4], [dogX(cs) - .3, 1.0, 20.1]],     // loopt mee
      [T_END, [dogX(T_END) + 6, 12, 36], [dogX(T_END), 1, 18]],          // climax: omhoog en achteruit, overzicht
    ],
    fov: 58,               // kijkhoek in graden (kleiner = meer ingezoomd)
    // Alternatief zonder camPath: vaste shots van de plek (zie kop van places/<plek>.js) en eigen standpunten:
    //   shots: [[0, 'wide'], [at('place').s, 'park']],
    //   extraShots: { naam: { pos: [x,y,z], look: [x,y,z], drift: [dx,dy,dz] /* per 10 s */, fov: 45 } },

    // ---- MENSEN EN DIEREN --------------------------------------------------------------------------
    // Groepjes mensen (engine/crowd.js): staan, kijken omhoog bij beats.lookUp, lopen weg bij beats.shelter.
    groups: [
      { at: [-30, 30], n: 4, spread: 2, face: 0, coats: [0x2f5d8a, 0x8a3b2f], lamp: false },
    ],
    // Dieren (engine/animals.js): dog · fox · deer · horse · lion · birds (+ grote dieren: dino's, olifanten).
    //   path: [[t, x, z], ...] waypoints; twee gelijke punten = stilstaan en `act` doen (sniff, graze, sit, look)
    //   walker: een baasje loopt mee en houdt de riem vast  { side: -.45 (welke kant), behind: 1.3, coat, pants }
    animals: [
      { kind: 'dog', path: [[0, dogX(0), 20.3], [T_END, dogX(T_END), 20.3]], color: 0xb08a5a,
        walker: { side: -.45, coat: 0xb8322a, pants: 0x27324f } },
      { kind: 'birds', n: 10, center: [-30, 12, 15], radius: 10 },
    ],
    // Meer bouwstenen (zie de kop van elk bestand): traffic/bikes/crashes/smoke (small.js), wave (wave.js),
    // fences/towers/gates (fences.js), time (time.js: dagen/jaren verstrijken), moon (moon.js), space (space.js),
    // ufo (ufo.js), army (army.js), meteors (meteors.js), seabed (seabed.js), tv (tv.js).

    // ---- BEATS: momenten waarop de plek reageert ---------------------------------------------------
    beats: {
      stop: T_END,               // vanaf hier staat de simulatie stil
      climax: at('climax').s,    // het grote moment (o.a. geluid)
      lookUp: at('normal').s,    // mensen kijken omhoog / reageren
      shelter: 1e9,              // mensen lopen weg (1e9 = nooit)
      carsStop: 1e9,             // rijdende auto's stoppen
    },
  };
}

// UPLOADTEKST (make_whatif.py zet dit in upload.json). Feiten met bronnen in `sources`.
export const upload = {
  title: 'What if ...?',
  description: '...\n\n#whatif #science #shorts',
  tags: ['what if', 'science', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: 'What if ...? #whatif #science #fyp',
  sources: [],
};
