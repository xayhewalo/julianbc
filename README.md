# JulianBC
[![Maintainability](https://api.codeclimate.com/v1/badges/f8f0b0fd2b59791f4c87/maintainability)](https://codeclimate.com/github/xayhewalo/julianbc/maintainability)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

JulianBC will be a visual-timeline program in the near future

# Road Map to 0.1.0
### Database
#### ConvertibleCalendar
 - [X] Change `outlaws` to `special_leap_years` and `special_common_years`
 - [X] Add `months_in_leap_year`
 - [X] Add `months_in_common_year`
 - [X] add `days_in_common_year`
 - [X] add `days_in_leap_year`
 - [X] add `leap_year_cycle_length`
 - [X] add `days_in_week`
 - [X] move validation methods out of this function
#### ConvertibleClock
- [X] add `convertible_clocks`
- [X] change table name to "convertible_clock"
#### Entity
- [ ] string validation on `aliases`
- [ ] add related `calendar`
- [ ] add related `clock`
- [ ] `CheckConstraint` that calendar and clock are `NOT NULL` when `creation_od` or `destruction_od` are `NOT NULL`
#### Event
- [ ] make `duration` a hybrid property based on `end`
- [ ] make `end` a proper `ColumnProperty`

### Business Logic
#### ConvertibleDate
- [X] recalculate calendar properties when it is set
- [X] Prevent common year cycle ordinals from slowing tests
- [X] refactor `ordinal_date_to_ordinal`
- [X] refactor `ordinal_to_ordinal_date`
    - [X] add `common_year_cycle_ordinals` property
        - [X] prevent setting `common_year_cycle_ordinals`
    - [X] add `common_years_in_normal_cycle` property
        - [X] prevent setting `common_years_in_normal_cycle`
    - [X] add `leap_years_in_normal_cycle` property
- [X] test cycle properties
- [ ] Refactor `is_leap_year`
- [ ] Make ordinal conversions DRY with `is_leap_year`
- [X] Generic function to find `special_common_years` and `special_leap_years`
- [X] test special years functions
- [X] remove `_increment_by_one`
- [X] add `days_in_month` and use it
- [X] add `is_valid_month` and use it
- [X] make `days_in_year` use column properties on calendar
- [ ] add `shift_ast_ymd`
    - [ ] `shift_ast_year`
    - [ ] `shift_ast_month`
    - [ ] `shift_ast_day`
    - [ ] check if `frequency` is an integer greater than zero
- [ ] add `next_dateunit`
- [ ] move `make_ordinal` out of `ConvertibleDate`, change name
- [X] remove week stuff
#### ConvertibleTime
- [X] remove `convertible_clocks`
- [X] test error raised for `convert_hms`
- [ ] add `next_hms`
    - [ ] different methods for `hour`, `minute`, and `second`
    - [ ] OR convert `hms` and `frequency` to `seconds` and find when modulo == 0(?)
    - [ ] refactor so `is_valid_hour` is checked twice
- [ ] add `shift_hms`
    - [ ] add `shift_hour`
    - [ ] add `shift_minute`
    - [ ] add `shift_second`
    - [ ] make it DRY
    - [ ] test every 24 hours returns 0
    - [ ] test `day_diff` i.e. shift by 50 hours has a `day_diff` >= 2
    - [ ] add rollover hour function
    - [ ] add rollover minute function
    - [ ] add rollover second function
    - [ ] add terminal hour function (?)
#### ConvertibleDateTime
- [ ] add `change_interval`
    - [ ] pass `label_width` and `interval` and pick the smallest interval that's greater than the width(?)
    - [ ] make `change_XXX_interval` DRY
- [ ] test `ast_ymd_to_od` for proleptic years
- [ ] add `extend_start_end` (by passed `interval`) to be used in `Timeline` `and Mark`
    - [ ] use `shift_od`
#### EventController
- [ ] `fields` in `make` are based on `Event` columns
- [ ] ensure negative `duraiton` raises error
- [ ] `get_events` adds `calendar.id` to where clause

### UI
- [ ] put logic in separate methods and call them in `on_###` methods
- [ ] Don't interact with the db at all. Rely entirely on business logic
- [ ] add keyboard equivalents for all mouse interactions
- [ ] Add Calendar from UI
#### Timeline
- [ ] Sync timelines should set start and end ordinals of all timelines
- [ ] add scroll
  - [ ] Gain focus when scrolling
  - [ ] shift + scrollup/scrolldown
  - [ ] left/right arrow scroll when in focus
  - [ ] up/down scroll when in focus
  - [ ] page up/down scroll when in focus
  - [ ] home/end scroll(?)
- [ ] add zoom
  - [ ] Gain focus when zooming
  - [ ] ctrl + +/- to zoom
  - [ ] pinch trackpad to zoom
- [ ] Add `extended_start_ordinal` and `extended_end_ordinal` that's outside the visible `time_span`
    - [ ] don't do the calculations in `Timeline`
- [ ] `TimelineScreen` should handle collapsing
- [ ] disable `focus` when `Timeline` is collapsed
- [ ] add proper reference to other timelines when scrolling/zooming while synced
- [ ] `ComboTimeline` should scroll/zoom its children instead of children manipulating their siblings
- [ ] Move event graphics to `EventContainer` class
  - [ ] test setting event height when two events ago is really long
  - [ ] test expand event_height and all other events shift y positions
#### Mark
- [ ] don't do shift calculations in `Mark`
#### EventEditor
- [ ] Properly locate `EventEditor`
- [ ] set widgets by constant align values created at parent level
- [ ] only allow numbers input
- [ ] redraw timelines on accept
- [ ] show/hide aliases button
- [ ] show/hide description button
- [ ] add `aliases` one by one, not by comma-separated values
- [ ] lose focus when after making the event
- [ ] put `TextInput`s into a collection and reset them in a loop
- [ ] put `hint_text_color` into a variable
#### CalendarChanger
- [ ] make readable references to timelines

### Misc.
- [ ] Probably more stuff...
- [ ] Fix `days_in_month` test for Julian Calendar for BCE years