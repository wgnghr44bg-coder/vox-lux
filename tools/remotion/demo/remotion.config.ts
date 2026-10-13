/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setJpegQuality(95);
Config.setCrf(16);
Config.setDefaultPremountInSeconds(2);

// Cloudsessie: gebruik de voorgeïnstalleerde Chromium (geen download nodig).
import fs from "fs";
const CLOUD_CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
if (fs.existsSync(CLOUD_CHROME)) {
  Config.setBrowserExecutable(CLOUD_CHROME);
  Config.setChromiumOpenGlRenderer("swangle"); // 3D (three.js) zonder GPU
}
