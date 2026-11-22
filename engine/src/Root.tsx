import React from "react";
import { Composition } from "remotion";
import { Demo, demoDuur } from "./Demo";
import { AIChips, AI_DUUR } from "./ai/AIChips";
import { AIChips2, AI2_DUUR } from "./ai/AIChips2";
import { FPS, W, H } from "./theme";

export const Root: React.FC = () => (
  <>
    <Composition id="Demo" component={Demo} durationInFrames={demoDuur} fps={FPS} width={W} height={H} />
    <Composition id="AIChips" component={AIChips} durationInFrames={AI_DUUR} fps={FPS} width={W} height={H} />
    <Composition id="AIChips2" component={AIChips2} durationInFrames={AI2_DUUR} fps={FPS} width={W} height={H} />
  </>
);
