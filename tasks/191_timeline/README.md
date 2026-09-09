---
title: bisect + rich comparisons — keep a composed timeline sorted
difficulty: medium
tier: core
minutes: 22
prereqs: [160, 178]
tags: [bisect, class-composition, rich-comparisons]
---
# bisect + rich comparisons — keep a composed timeline sorted

*Make events know their order, then let a timeline keep them in it.*

## Read first
- [Basic customization](https://devdocs.io/python~3.14/reference/datamodel#basic-customization) — `__lt__` defines `<`
- [bisect.insort](https://devdocs.io/python~3.14/library/bisect#bisect.insort) — insert without losing sorted order
- [bisect.bisect_left](https://devdocs.io/python~3.14/library/bisect#bisect.bisect_left) — find the first event at a time

## Why
A deployment timeline receives events out of order. Re-sorting the whole list after every arrival repeats work. A small `Event` value can own comparison, while a `Timeline` owns a sorted collection of those values.

## You get
No inputs to `solve`; return the class the grader will build.

## You return
A `Timeline` class. Each instance exposes its composed `Event` class as `event_type` and stores event objects in `events`.

## Rules
Inside `solve`, define:

- `Event(when, name)`, storing both values and implementing `__lt__` by `(when, name)`;
- `Timeline`, with an empty `events` list and `event_type = Event`;
- `Timeline.add(when, name)`, inserting an `Event` with `bisect.insort`;
- `Timeline.from_time(when)`, returning the events at or after `when`, found with `bisect_left` and an `Event(when, "")` probe.

Return `Timeline` from `solve`.

## Hints
### Hint 1
`bisect` asks the objects in the list which one is smaller. Put that rule on `Event.__lt__`, not in every timeline method.
### Hint 2
Compare `(self.when, self.name)` with the same pair from `other`. Tuple ordering gives time first and name as the tie-breaker.
### Hint 3
`insort(self.events, Event(when, name))` handles insertion. For the slice, compute `start = bisect_left(self.events, Event(when, ""))` and return `self.events[start:]`.
