import { MyComposition } from "./Composition";
import { ImageComposition } from "./Images";
import { ThreeComposition } from "./ThreeD";
import { CityComposition } from "./City";
import { BuriedComposition } from "./whatif/Buried";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <ImageComposition />
      <ThreeComposition />
      <CityComposition />
      <BuriedComposition />
    </>
  );
};
