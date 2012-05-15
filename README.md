Spur Distance Charts
====================
A GUI tool for frequency planning for broadband receivers. Start off by reading http://www.microwavejournal.com/articles/9084-the-distances-chart-a-new-approach-to-spurs-calculation where the idea was first presented.

The tool presents a frequency-distance vs. RF chart. The x-coordinate is the RF frequency a system is tuned to, and the y-coordinate is the delta from the respective RF. Coloured lines drawn on the chart delimit frequency bands that, if present at the RF-port of the mixer, will mix down to the same IF. The black parallelogram is a filter at the RF port; so long as no coloured lines cross inside the parallelogram, no intermodulation products will create trouble at the IF.

The app needs a fair bit of work. Many characteristics are hard-coded (eg `sdc.py:8` is where all the design settings are initialized), and there's still considerable functionality that I'd like to add, but here's a version 0.1.

Usage
-----
A short and rough tutorial can now be found at http://patrickyeon.github.com/spurdist/

The chart in the main window looks pretty much like the charts in the original article. You can set the IF using the slider below the chart, and the RF range is to the right. "dspan" is the height of the chart (ie: it shows `RF +/- (dspan/2)`). Click and drag the parallelogram sides (the vertical lines, that is) to change the width of the front-end filter.

By default, the chart shows any intermodulation products of the form `mRF +/- nLO; {m<=2, n<=4}`. For now, this is hard-coded, see `sdc.py:9`.

TODO Shortlist
--------------
* Better initial design entry
* Faster GUI (matplotlib may be the culprit here)
* More tests, of course!
