/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html', './assets/js/**/*.js', './assets/site.js', './content/**/*.yaml'],
  theme: {
    extend: {
      colors: {
        ink:   'rgb(5 5 5 / <alpha-value>)',        // page background
        stage: 'rgb(11 11 11 / <alpha-value>)',     // raised panels
        paper: 'rgb(242 242 238 / <alpha-value>)',  // text / foreground
        line:  'rgb(242 242 238 / 0.12)',           // hairlines
        'line-strong': 'rgb(242 242 238 / 0.28)',
        signal:'rgb(215 255 58 / <alpha-value>)',   // ONLY: live dots, active marquee star, form success. Never body text.
      },
      fontFamily: {
        display: ['"Big Shoulders Display"', '"Arial Narrow"', 'sans-serif'],
        sans:    ['Geist', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
        mono:    ['"Geist Mono"', 'ui-monospace', 'SFMono-Regular', 'Consolas', 'monospace'],
      },
      transitionTimingFunction: {
        'out-expo': 'cubic-bezier(.16,1,.3,1)',
        'in-out-quint': 'cubic-bezier(.65,0,.35,1)',
        spring: 'cubic-bezier(.34,1.56,.64,1)',
      },
      keyframes: { marquee: { from: { transform: 'translate3d(0,0,0)' }, to: { transform: 'translate3d(-50%,0,0)' } } },
      animation: { marquee: 'marquee 48s linear infinite' },
      maxWidth: { shell: '1600px' },
    },
  },
  plugins: [],
};
