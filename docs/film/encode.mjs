// The rendered frames, as the looping WebP the README shows. `pnpm render` first.
import { execFileSync } from "node:child_process";

const [width = "1024", quality = "60", fps = "20"] = process.argv.slice(2);
execFileSync("ffmpeg", [
  "-loglevel", "error", "-y", "-framerate", "30", "-i", "out/frames/element-%04d.png",
  "-vf", `fps=${fps},scale=${width}:-1:flags=lanczos`,
  "-c:v", "libwebp_anim", "-lossless", "0", "-quality", quality, "-compression_level", "6", "-loop", "0",
  "../images/drillion-film.webp",
], { stdio: "inherit" });
