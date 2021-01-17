# JulianBC
[![Maintainability](https://api.codeclimate.com/v1/badges/f8f0b0fd2b59791f4c87/maintainability)](https://codeclimate.com/github/xayhewalo/julianbc/maintainability)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

JulianBC will be a visual-timeline program in the near future

# Road Map to 0.1.0
- [X] Add convertible calendar
- [X] Add convertible date
- [X] Add convertible clock
- [X] Add convertible time
- [ ] Refactor `is_leap_year` for performance/DRY
- [ ] Add infinitely scrolling timeline
    - [X] Prevent scroll_x from approaching infinity
    - [ ] shift + scrolllup/scrolldown
    - [ ] left/right arrow scroll when in focus
    - [ ] up/down scroll when in focus
    - [ ] page up/down scroll when in focus
    - [ ] home/end scroll?
- [ ] Add zoom to timeline
    - [ ] ctrl + +/- to zoom
    - [X] limit zoom
    - [ ] Optimized zoom intervals
    - [ ] pinch trackpad to zoom
- [X] Label timeline
    - [X] with dates
    - [X] with time
    - [X] move dates and times dynamically with scroll and zoom
    - [X] widen interval labels based on label text width
    - [X] Set intervals by strings? I.e "week", "month", "year", etc.
    - [X] Convert Timeline days to label x position
    - [X] Add more precise formatting for human-readable dates
- [X] Add event containers to timeline
- [X] Link event container locations to dates and times
    - [X] Add event container detail window (inspect)
- [ ] Swap a calendar's timeline from the UI
- [ ] Show same events on two timelines with different calendars
- [ ] Make all calendar and clock calculations in datetime/date/time modules. UI should only call from methods from ConvertibleDateTime
- [ ] Add calendar from UI
- [ ] Probably more stuff...