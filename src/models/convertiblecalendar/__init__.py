"""
The backbone of JulianBC's time-tracking.

Terminology
=============
Different libraries use different words for the same concept.
Below is a glossary for this project's date-related terms.

* `astronomical year` or `ast_year` is a year using astronomical year
  numbering, where year 0 is **not** skipped.
  In this project, astronomical years are only concerned with two eras.
  Moving forward from a calendar's epoch (Common Era in the Gregorian Calendar)
  , and moving backwards from the epoch (I.e Before Common Era).
  The first year of  calendar is always 1.
* `human-readable year` or `hr_year` is a year meant to be presented to
  the end-user. I.e the year before the Gregorian Calendar's epoch is year 0 in
  astronomical year numbering, but in human readable years, it is 1 BCE.
  Human-readable years **must** be non-negative.
* `ymd` is short for `Year, Month, Day`
* `hr_date` is a human-readable date including the era.
  I.e "2020/12/2/CE" is December 2nd, 2020 Common Era
* `leap year` is a year that contains the leap day(s) of a calendar system.
  I.e 2020 is a leap year for the Gregorian Calendar.
* `common year` is any year that is not a `leap year`. I.e 2019 is a common
  year for the Gregorian Calendar.
* `ordinal date` is a date in the following format: "Year/Day of Year".
  I.e the ordinal date for November 30th, 2020 is "2020/335" for the
  Gregorian Calendar. `ordinal date` defaults to an astronomical year
* `ordinal` is the number of days since the epoch of a calendar.
  This is consistent with :py:mod:`datetime`.
  This is **contrary** to :py:mod:`convertdate`, which calls the
  `ordinal date` an `ordinal`.
"""
