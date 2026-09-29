import path from "node:path";
import { Config } from "@remotion/cli/config";

// the app's own public folder: its fonts and track marks, not copies of them
Config.setPublicDir("../../web/public");

// the film draws with the app's design-system components; they import `react` from beside
// themselves, so both resolve to this package's single copy
const here = (m: string) => path.join(process.cwd(), "node_modules", m);
Config.overrideBundlerConfig((config) => ({
  ...config,
  resolve: {
    ...config.resolve,
    alias: {
      ...(config.resolve?.alias ?? {}),
      "@ds": path.join(process.cwd(), "..", "..", "web", "src", "ds"),
      "@app": path.join(process.cwd(), "..", "..", "web", "src"),
      react: here("react"),
      "react-dom": here("react-dom"),
    },
  },
}));
