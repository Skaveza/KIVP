/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'kenya-green': '#006600',
        'kenya-red': '#BB0000',
        'kenya-black': '#000000',
      }
    },
  },
  plugins: [],
}
