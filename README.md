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
 - [ ] add validation that `days_in_leap year` is greater than or equal `days_in_common_year`
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
- [ ] make `end` a proper `Column`

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
- [X] Refactor `is_leap_year`
- [X] Make ordinal conversions DRY with `is_leap_year`
- [X] Generic function to find `special_common_years` and `special_leap_years`
- [X] test special years functions
- [X] remove `_increment_by_one`
- [X] add `days_in_month` and use it
- [X] add `is_valid_month` and use it
- [X] make `days_in_year` use column properties on calendar
- [X] test `completed_cycles`
- [X] test `cycle_index`
- [X] test cycle properties with no leap years:
- [X] add `shift_ast_ymd`
    - [X] `shift_ast_year`
    - [X] `shift_ast_month`
- [ ] add `next_dateunit`
    - [X] check if `frequency` is an integer greater than zero
    - [ ] Should use human-readable years
- [ ] `next_week`(?)
- [ ] move `make_ordinal` out of `ConvertibleDate`, change name
- [X] remove `is_decending_era`
- [X] remove week stuff
- [X] `common_year_cycle_ordinals` generator is slowing the UI, refactor it so it's not generated everytime and change factories so tests to don't forever
- [ ] Test `__init__` properties
- [ ] Test `completed_cycles` with special years
#### ConvertibleTime
- [X] remove `convertible_clocks`
- [X] test error raised for `convert_hms`
- [X] add `next_hms`
    - [X] convert `hms` and `frequency` to `seconds` and find when modulo == 0
- [X] add `shift_hms`
    - [X] make it DRY
    - [X] test `day_diff` i.e. shift by 50 hours has a `day_diff` >= 2
- [ ] Test `__init__` properties
#### ConvertibleDateTime
- [ ] add `change_interval`
    - [X] pass `label_width` and `interval` and pick the smallest interval that's greater than the width
    - [X] make `change_XXX_interval` DRY
    - [ ] make proper year frequencies
- [X] add `extend_start_end` (by passed `interval`) to be used in `Timeline` and `Mark`
    - [X] use `shift_od`
- [X] shift days and weeks(?) in `shift_od`
- [ ] Test `__init__` properties
- [X] Optimize next_hms while loop
#### EventController
- [ ] `fields` in `make` are based on `Event` columns
- [ ] ensure negative `duraiton` raises error
- [ ] `get_events` adds `calendar.id` to where clause

### UI
- [ ] put logic in separate methods and call them in `on_###` methods
- [ ] Don't interact with the db at all. Rely entirely on business logic
- [ ] add keyboard equivalents for all mouse interactions
- [ ] Add Calendar from UI
- [X] Decouple focus and keyboard
- [ ] Break up Timeline into a `DateTimeView` and a layout containing `DateTimeController` and `CollapseBar`, and have collapse bar change size of `Timeline`
#### Timeline
- [ ] Sync timelines should set start and end ordinals of all timelines
- [ ] add scroll
  - [X] Gain focus when scrolling
  - [X] shift + scrollup/scrolldown
  - [X] left/right arrow scroll when in focus
  - [ ] allow shift scroll up when children are focused
  - [ ] up/down scroll when in focus
  - [ ] page up/down scroll when in focus
  - [ ] home/end scroll(?)
- [X] add zoom
  - [X] Gain focus when zooming
  - [X] ctrl + +/- to zoom
  - [X] pinch trackpad to zoom
- [X] Add `extended_start_ordinal` and `extended_end_ordinal` that's outside the visible `time_span`
    - [X] don't do the calculations in `Timeline`
- [ ] `TimelineScreen` should handle collapsing
- [ ] disable `focus` when `Timeline` is collapsed
- [ ] add proper reference to other timelines when scrolling/zooming while synced
- [ ] `ComboTimeline` should scroll/zoom its children instead of children manipulating their siblings
- [ ] Move event graphics to `EventView` class
  - [ ] test setting event height when two events ago is really long
  - [ ] test expand event_height and all other events shift y positions
- [ ] keep timeline behind collapse bar when collapsed and resizing
#### Mark
- [X] don't do shift calculations in `Mark`
- [ ] Test middle interval alignment
- [X] Fix Mark labels when zoomed in at 2 or 1 second intervals, they don't move
- [X] Fix Mark labels and stripes for BCE years
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
- [X] Fix `days_in_month` test for Julian Calendar for BCE years
- [ ] Probably more stuff...