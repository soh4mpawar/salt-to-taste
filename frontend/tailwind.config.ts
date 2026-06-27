import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        salt: {
          50: "#f8f9fa",
          100: "#f1f3f4",
          200: "#e8eaed",
          500: "#9aa0a6",
          900: "#202124",
        },
        umami: {
          50: "#fff8f1",
          100: "#ffe8cc",
          400: "#ff9500",
          500: "#e6851a",
          600: "#cc6600",
        },
        fresh: {
          400: "#34a853",
          500: "#1e8e3e",
        },
        danger: {
          400: "#ea4335",
          500: "#c5221f",
        }
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
      },
      minHeight: {
        touch: "44px",
      }
    },
  },
  plugins: [],
};

export default config;
