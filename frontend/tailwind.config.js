/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "#1a7a4a", light: "#22a05e", dark: "#145c38" },
        accent:  { DEFAULT: "#f59e0b", light: "#fbbf24" },
        surface: "#f7f8fa",
      },
      fontFamily: { sans: ["'Noto Sans Gujarati'", "system-ui", "sans-serif"] },
    },
  },
  plugins: [],
}
