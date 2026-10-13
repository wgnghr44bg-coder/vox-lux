import { MyComposition } from "./Composition";
import { ImageComposition } from "./Images";
import { ThreeComposition } from "./ThreeD";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <ImageComposition />
      <ThreeComposition />
    </>
  );
};
