module.exports = {
  purge: [
    "./**/*.html",
    "./**/*.rst",
    "./**/*.js"
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    screens: {
      "md": "700px",
      "lg": "1100px"
    },
    extend: {
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
              color: 'rgb(88, 110, 117)',
              backgroundColor: '#fdf6e3'
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
              listStyle: 'none'
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
        }
      })
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography')
  ],
}
