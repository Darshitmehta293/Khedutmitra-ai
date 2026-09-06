/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "#059669", light: "#10b981", dark: "#047857" },
        emerald: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
          950: "#022c22",
        },
        accent: { DEFAULT: "#f59e0b", light: "#fbbf24" },
        surface: "#f6f8f6",
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "'Inter'", "'Noto Sans Gujarati'", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
}
