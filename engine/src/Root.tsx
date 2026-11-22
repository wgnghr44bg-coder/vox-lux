import React from "react";
import { Composition } from "remotion";
import { Demo, demoDuur } from "./Demo";
import { FPS, W, H } from "./theme";

export const Root: React.FC = () => (
  <>
    <Composition id="Demo" component={Demo} durationInFrames={demoDuur} fps={FPS} width={W} height={H} />
  </>
);
