Skip to content
matplotlib
mplfinance
Repository navigation
Code
Issues
154
 (154)
Pull requests
20
 (20)
Actions
Projects
Wiki
Security
Insights
Owner avatar
mplfinance
Public
matplotlib/mplfinance
Go to file
t
Name		
DanielGoldfarb
DanielGoldfarb
Merge pull request #666 from DanielGoldfarb/master
493811d
 · 
2 years ago
.github
this should fix 3.10 being interpreted as 3.1
3 years ago
doc
DOC: Add example and update documentation
9 years ago
examples
re-generate price-movement_plots notebook
2 years ago
markdown
mention documentation is in the code examples.
4 years ago
readme_files
tweak types; fix readme_5_1.png
6 years ago
scripts
add workflow and update version
5 years ago
src/mplfinance
Merge branch 'master' into master
3 years ago
tests
fix regression tests and bump version
4 years ago
.gitignore
tweak .gitignore
5 years ago
CODE_OF_CONDUCT.md
Create CODE_OF_CONDUCT.md
4 years ago
CONTRIBUTING.md
Update CONTRIBUTING.md
2 years ago
LICENSE
Update LICENSE
6 years ago
MANIFEST.in
Add MANIFEST.in to include license file in source distribution
6 years ago
README.md
add fill_between to Tutorials Table of Contents
4 years ago
RELEASE_NOTES.md
Update RELEASE_NOTES.md
5 years ago
TODO.md
Added description fields in remaining kwarg dicts
5 years ago
archive.tox.ini
archive tox.ini (not needed with Github Actions)
5 years ago
archive.travis.yml
archive travis.yml file (not needed; using github actions instead)
5 years ago
pytest.ini
add workflow and update version
5 years ago
readme.ipynb
tweak types; fix readme_5_1.png
6 years ago
setup.py
fix error in 'Development Status' classifier
5 years ago
Repository files navigation
README
Code of conduct
Contributing
License
mplfinance Checks

mplfinance
matplotlib utilities for the visualization, and visual analysis, of financial data

Installation
pip install --upgrade mplfinance
mplfinance requires matplotlib and pandas
⇾ Latest Release Information ⇽
⇾ Older Release Information
Contents and Tutorials
The New API
Tutorials
Basic Usage
Customizing the Appearance of Plots
Adding Your Own Technical Studies to Plots
Subplots: Multiple Plots on a Single Figure
Fill Between: Filling Plots with Color
Price-Movement Plots (Renko, P&F, etc)
Trends, Support, Resistance, and Trading Lines
Coloring Individual Candlesticks (New: December 2021)
Saving the Plot to a File
Animation/Updating your plots in realtime
⇾ Latest Release Info ⇽
Older Release Info
Some Background History About This Package
Old API Availability
The New API
This repository, matplotlib/mplfinance, contains a new matplotlib finance API that makes it easier to create financial plots. It interfaces nicely with Pandas DataFrames.

More importantly, the new API automatically does the extra matplotlib work that the user previously had to do "manually" with the old API. (The old API is still available within this package; see below).

The conventional way to import the new API is as follows:

    import mplfinance as mpf
The most common usage is then to call

    mpf.plot(data)
where data is a Pandas DataFrame object containing Open, High, Low and Close data, with a Pandas DatetimeIndex.

Details on how to call the new API can be found below under Basic Usage, as well as in the jupyter notebooks in the examples folder.

I am very interested to hear from you regarding what you think of the new mplfinance, plus any suggestions you may have for improvement. You can reach me at dgoldfarb.github@gmail.com or, if you prefer, provide feedback or a ask question on our issues page.

Basic Usage
Start with a Pandas DataFrame containing OHLC data. For example,

import pandas as pd
daily = pd.read_csv('examples/data/SP500_NOV2019_Hist.csv',index_col=0,parse_dates=True)
daily.index.name = 'Date'
daily.shape
daily.head(3)
daily.tail(3)
(20, 5)
Open	High	Low	Close	Volume
Date					
2019-11-01	3050.72	3066.95	3050.72	3066.91	510301237
2019-11-04	3078.96	3085.20	3074.87	3078.27	524848878
2019-11-05	3080.80	3083.95	3072.15	3074.62	585634570
...

Open	High	Low	Close	Volume
Date					
2019-11-26	3134.85	3142.69	3131.00	3140.52	986041660
2019-11-27	3145.49	3154.26	3143.41	3153.63	421853938
2019-11-29	3147.18	3150.30	3139.34	3140.98	286602291

After importing mplfinance, plotting OHLC data is as simple as calling mpf.plot() on the dataframe

import mplfinance as mpf
mpf.plot(daily)
png


The default plot type, as you can see above, is 'ohlc'. Other plot types can be specified with the keyword argument type, for example, type='candle', type='line', type='renko', or type='pnf'

mpf.plot(daily,type='candle')
png

mpf.plot(daily,type='line')
png

year = pd.read_csv('examples/data/SPY_20110701_20120630_Bollinger.csv',index_col=0,parse_dates=True)
year.index.name = 'Date'
mpf.plot(year,type='renko')
png

mpf.plot(year,type='pnf')
png


We can also plot moving averages with the mav keyword

use a scalar for a single moving average
use a tuple or list of integers for multiple moving averages
mpf.plot(daily,type='ohlc',mav=4)
png

mpf.plot(daily,type='candle',mav=(3,6,9))
png

We can also display Volume

mpf.plot(daily,type='candle',mav=(3,6,9),volume=True)
png

Notice, in the above chart, there are no gaps along the x-coordinate, even though there are days on which there was no trading. Non-trading days are simply not shown (since there are no prices for those days).

However, sometimes people like to see these gaps, so that they can tell, with a quick glance, where the weekends and holidays fall.

Non-trading days can be displayed with the show_nontrading keyword.

Note that for these purposes non-trading intervals are those that are not represented in the data at all. (There are simply no rows for those dates or datetimes). This is because, when data is retrieved from an exchange or other market data source, that data typically will not include rows for non-trading days (weekends and holidays for example). Thus ...
show_nontrading=True will display all dates (all time intervals) between the first time stamp and the last time stamp in the data (regardless of whether rows exist for those dates or datetimes).
show_nontrading=False (the default value) will show only dates (or datetimes) that have actual rows in the data. (This means that if there are rows in your DataFrame that exist but contain only NaN values, these rows will still appear on the plot even if show_nontrading=False)
For example, in the chart below, you can easily see weekends, as well as a gap at Thursday, November 28th for the U.S. Thanksgiving holiday.

mpf.plot(daily,type='candle',mav=(3,6,9),volume=True,show_nontrading=True)
png

We can also plot intraday data:

intraday = pd.read_csv('examples/data/SP500_NOV2019_IDay.csv',index_col=0,parse_dates=True)
intraday = intraday.drop('Volume',axis=1) # Volume is zero anyway for this intraday data set
intraday.index.name = 'Date'
intraday.shape
intraday.head(3)
intraday.tail(3)
(1563, 4)
Open	Close	High	Low
Date				
2019-11-05 09:30:00	3080.80	3080.49	3081.47	3080.30
2019-11-05 09:31:00	3080.33	3079.36	3080.33	3079.15
2019-11-05 09:32:00	3079.43	3079.68	3080.46	3079.43
...

Open	Close	High	Low
Date				
2019-11-08 15:57:00	3090.73	3090.70	3091.02	3090.52
2019-11-08 15:58:00	3090.73	3091.04	3091.13	3090.58
2019-11-08 15:59:00	3091.16	3092.91	3092.91	3090.96
The above dataframe contains Open,High,Low,Close data at 1 minute intervals for the S&P 500 stock index for November 5, 6, 7 and 8, 2019. Let's look at the last hour of trading on November 6th, with a 7 minute and 12 minute moving average.

iday = intraday.loc['2019-11-06 15:00':'2019-11-06 16:00',:]
mpf.plot(iday,type='candle',mav=(7,12))
png

The "time-interpretation" of the mav integers depends on the frequency of the data, because the mav integers are the number of data points used in the Moving Average (not the number of days or minutes, etc). Notice above that for intraday data the x-axis automatically displays TIME instead of date. Below we see that if the intraday data spans into two (or more) trading days the x-axis automatically displays BOTH TIME and DATE

iday = intraday.loc['2019-11-05':'2019-11-06',:]
mpf.plot(iday,type='candle')
png

In the plot below, we see what an intraday plot looks like when we display non-trading time periods with show_nontrading=True for intraday data spanning into two or more days.

mpf.plot(iday,type='candle',show_nontrading=True)
png

Below: 4 days of intraday data with show_nontrading=True

mpf.plot(intraday,type='ohlc',show_nontrading=True)
png

Below: the same 4 days of intraday data with show_nontrading defaulted to False.

mpf.plot(intraday,type='line') 
png

Below: Daily data spanning across a year boundary automatically adds the YEAR to the DATE format

df = pd.read_csv('examples/data/yahoofinance-SPY-20080101-20180101.csv',index_col=0,parse_dates=True)
df.shape
df.head(3)
df.tail(3)
(2519, 6)
Open	High	Low	Close	Adj Close	Volume
Date						
2007-12-31	147.100006	147.610001	146.059998	146.210007	118.624741	108126800
2008-01-02	146.529999	146.990005	143.880005	144.929993	117.586205	204935600
2008-01-03	144.910004	145.490005	144.070007	144.860001	117.529449	125133300
...

Open	High	Low	Close	Adj Close	Volume
Date						
2017-12-27	267.380005	267.730011	267.010010	267.320007	267.320007	57751000
2017-12-28	267.890015	267.920013	267.450012	267.869995	267.869995	45116100
2017-12-29	268.529999	268.549988	266.640015	266.859985	266.859985	96007400
mpf.plot(df[700:850],type='bars',volume=True,mav=(20,40))
png

For more examples of using mplfinance, please see the jupyter notebooks in the examples directory.

Some History
My name is Daniel Goldfarb. In November 2019, I became the maintainer of matplotlib/mpl-finance. That module is being deprecated in favor of the current matplotlib/mplfinance. The old mpl-finance consisted of code extracted from the deprecated matplotlib.finance module along with a few examples of usage. It has been mostly un-maintained for the past three years.

It is my intention to archive the matplotlib/mpl-finance repository soon, and direct everyone to matplotlib/mplfinance. The main reason for the rename is to avoid confusion with the hyphen and the underscore: As it was, mpl-finance was installed with the hyphen, but imported with an underscore mpl_finance. Going forward it will be a simple matter of both installing and importing mplfinance.

Old API availability
With this new mplfinance package installed, in addition to the new API, users can still access the old API.
The old API may be removed someday, but for the foreseeable future we will keep it ... at least until we are very confident that users of the old API can accomplish the same things with the new API.

To access the old API with the new mplfinance package installed, change the old import statements

from:

    from mpl_finance import <method>
to:

    from mplfinance.original_flavor import <method>
where <method> indicates the method you want to import, for example:

    from mplfinance.original_flavor import candlestick_ohlc
About
Financial Markets Data Visualization using Matplotlib

pypi.org/project/mplfinance/
Topics
finance market-data matplotlib candlestick candlestick-chart ohlc intraday-data ohlcv ohlc-chart ohlc-plot mplfinance trading-days ohlc-data candlestickchart
Resources
 Readme
License
 View license
Code of conduct
 Code of conduct
Contributing
 Contributing
 Activity
 Custom properties
Stars
 4.3k stars
Watchers
 97 watching
Forks
 669 forks
Report repository
Releases 11
v0.12.10b0
Latest
on Aug 2, 2023
+ 10 releases
Packages
No packages published
Used by 7.9k
@so1761
@xanthein
@AA-Turner
@nguemechieu
@javadebadi
@Fincept-Corporation
+ 7,843
Contributors
42
@DanielGoldfarb
@coffincw
@DrChandrakant
@tacaswell
@KenanHArik
@jenshnielsen
@anbarief
@andrewrgarcia
@alexpvpmindustry
@AurumnPegasus
@mattsta
@donbing
@soellingeraj
@wsyxbcl
+ 28 contributors
Languages
Python
99.7%
 
Shell
0.3%
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information
 