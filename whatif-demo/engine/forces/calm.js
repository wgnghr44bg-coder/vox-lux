// CALM: no force at all – the world just goes on (use with TL.time for days and years passing,
// or for a quiet chapter). The counter is free (e.g. days or years); level 0..1 follows it.
import { baseForce } from './base.js';

export function create(E, TL) {
  return baseForce(E, TL, 'calm');
}
