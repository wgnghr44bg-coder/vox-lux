import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";
import { HaaiShort, HAAI_FRAMES } from "./videos/haai/Haai";
import { RobotShort, ROBOT_FRAMES } from "./videos/robot/Robot";

export const Root: React.FC = () => (
  <>
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="HaaiShort" component={HaaiShort} durationInFrames={HAAI_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="RobotShort" component={RobotShort} durationInFrames={ROBOT_FRAMES} fps={30} width={1080} height={1920} />
  </>
);
