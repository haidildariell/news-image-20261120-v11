# Friday 20 November 2026 — 36 stories, 7 regions, one front page

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/haidildariell/news-image-20261120-v11/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/haidildariell/news-image-20261120-v11/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![make.fun bounty](https://img.shields.io/badge/make.fun-news--image--20261120-red)](https://make.fun/bounty/news-image-20261120)
[![Prize pool $250](https://img.shields.io/badge/prize%20pool-%24250-gold)](https://make.fun/bounty/news-image-20261120)
[![Top 50 paid](https://img.shields.io/badge/paid%20places-top%2050-blue)](https://make.fun/bounty/news-image-20261120)

A program that draws one newspaper front page summing up the world's news
of Friday 20 November 2026: 36 dated stories across 7 regions — the Kyiv
bridge barrage, Cyclone Akvan's landfall in Odisha, the Asian AI sell-off,
COP31's deadlocked final day, BepiColombo's arrival at Mercury, and 31
more, plus a date-check box that keeps Thursday's news out of Friday's
page. Every number on the page is sourced per story in `SOURCES.md`.

## Run

```sh
python3 main.py            # writes entry.png next to main.py
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Deterministic: fixed seed, no clock, no network — two runs write
identical bytes. The image is 1024×1024 PNG, under 1 MiB.
