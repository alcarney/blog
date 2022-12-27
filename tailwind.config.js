const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    "./styles.css",
    "./**/*.rst",
    "./landing.html",
    "./searchtools.patch",
    "./_templates/**/*.html",
    "./extensions/**/*.html",
    "./code/**/*.js"
  ],
  plugins: [
    require('@tailwindcss/typography')
  ],
  theme: {
    screens: {
      "md": "700px",
      "lg": "1100px"
    },
    extend: {
      colors: {
        gray: colors.zinc,
        green: colors.emerald,
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            h1: {
              fontWeight: '400',
              color: theme('colors.green.600')
            },
            h2: {
              fontWeight: '400',
              color: theme('colors.green.600')
            },
            h3: {
              fontWeight: '400',
              color: theme('colors.green.600')
            },
            h4: {
              fontWeight: '400',
              color: theme('colors.green.600')
            },
            pre: {
              color: 'inherit',
              backgroundColor: 'unset'
            },
            a: {
              textDecoration: 'none'
            },
            dd: {
              margin: '0 2rem'
            },
            dl: {
              lineHeight: '1'
            },
            ol: {
              listStyle: 'decimal'
            },
            'pre code::before': {
              display: 'none',
            },
            'pre code::after': {
              display: 'none',
            },
            'td > pre': {
              margin: 0,
              paddingLeft: '0',
              boxShadow: 'none'
            },
            'td:first-child': {
              userSelect: 'none',
            }
          }
        },
        sm: {
          css: {
            pre: {
              marginTop: 0,
              marginBottom: 0
            },
          }
        },
      })
    },
  },
}
