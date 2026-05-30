/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: "#090d16", // Rich space black
          800: "#0f1626", // Deep navy slate
          700: "#1e293b", // Slate 800
          600: "#334155"  // Slate 700
        },
        brand: {
          indigo: "#6366f1",
          violet: "#8b5cf6",
          fuchsia: "#d946ef",
          cyan: "#06b6d4",
          emerald: "#10b981",
          rose: "#f43f5e"
        }
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "system-ui", "sans-serif"]
      },
      animation: {
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" }
        }
      }
    },
  },
  plugins: [],
}
