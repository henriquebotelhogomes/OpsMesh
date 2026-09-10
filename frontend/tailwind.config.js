/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sand: {
          base: '#302A24',
          surface: '#241F1A',
          elevated: '#3C342C',
          terminal: '#1C1814',
          text: '#D9D0C5',
          muted: '#A39686',
        },
        brand: {
          bronze: '#8E7C5B',
          bronzeLight: '#B8A179',
          charcoal: '#2B2B2B',
          silver: '#BDBDBD',
          gold: '#CEB07E',
          ivory: '#FAF7F2',
          emerald: '#34D399',
          steel: '#82A1AA',
          crimson: '#E05A47',
          amber: '#D97706',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'glow-gold': '0 0 25px rgba(206, 176, 126, 0.25)',
        'glow-bronze': '0 0 30px rgba(142, 124, 91, 0.28)',
        'glow-crimson': '0 0 25px rgba(224, 90, 71, 0.35)',
        'card-depth': '0 20px 45px rgba(20, 16, 12, 0.65)',
      },
      animation: {
        'pulse-subtle': 'pulse 2.5s infinite',
        'pulse-hitl': 'pulse 1.8s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-4px)' },
        }
      }
    },
  },
  plugins: [],
}
