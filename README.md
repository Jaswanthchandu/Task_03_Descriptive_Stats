# Task_03_Descriptive_Stats

> Note: The statistics scripts were developed with AI assistance; the analysis, validation, and findings are my own.

A generalized descriptive-statistics system that runs unchanged on three different
2024 U.S. election social-media datasets, Facebook ads, Facebook posts, and
Twitter/X posts, computed three independent ways (pure standard-library Python,
pandas, and Polars), plus a cross-platform comparison of the columns they share.

## Datasets

Source: [2024 Election Social Media Data, Milestone B (Google Drive)](https://drive.google.com/file/d/1Jq0fPb-tq76Ee_RtM58fT0_M3o-JDBwe/view?usp=sharing)

The bundle contains three CSVs:
- `2024_fb_ads_president_scored_anon.csv` (246,745 rows x 41 cols), Facebook ads.
  This is the same ads dataset used in Task 2 / Milestone A, reused here per the
  assignment's statement that Milestone B's ads data is the same file.
- `2024_fb_posts_president_scored_anon.csv` (19,009 rows x 56 cols), Facebook posts.
- `2024_tw_posts_president_scored_anon.csv` (27,304 rows x 47 cols), Twitter/X posts.

The datasets are **not** included in this repository. Download the bundle from the
link above, place the CSVs locally, and pass their paths to the scripts.

## How to run

```bash
pip install -r requirements.txt
```

Each script takes a CSV path and an optional group-by column. The grouping column
differs by dataset (this is intentional, see Generalization below):

```bash
# Facebook Ads  (group by page_id)
python pure_python_stats.py 2024_fb_ads_president_scored_anon.csv page_id
python pandas_stats.py      2024_fb_ads_president_scored_anon.csv page_id
python polars_stats.py      2024_fb_ads_president_scored_anon.csv page_id

# Facebook Posts  (group by Facebook_Id)
python pure_python_stats.py 2024_fb_posts_president_scored_anon.csv Facebook_Id
python pandas_stats.py      2024_fb_posts_president_scored_anon.csv Facebook_Id
python polars_stats.py      2024_fb_posts_president_scored_anon.csv Facebook_Id

# Twitter/X Posts  (group by source)
python pure_python_stats.py 2024_tw_posts_president_scored_anon.csv source
python pandas_stats.py      2024_tw_posts_president_scored_anon.csv source
python polars_stats.py      2024_tw_posts_president_scored_anon.csv source
```

Cross-dataset comparison (all three files at once):

```bash
python cross_dataset.py 2024_fb_ads_president_scored_anon.csv 2024_fb_posts_president_scored_anon.csv 2024_tw_posts_president_scored_anon.csv
```

Redirect any command to a file with `> output.txt` to save its results.

## What each script does

- `pure_python_stats.py`, `pandas_stats.py`, `polars_stats.py`, the same generalized
  analysis three ways. Dataset level: per column count, mean, min, max, sample std,
  median (numeric); count, unique, mode + frequency, top 5 (categorical); plus
  row/column counts, missing values, and inferred type per column. Grouped (when a
  group-by column is given): rows per group and the mean of every numeric column for
  the top groups by size. Nothing about the schema is hardcoded, column types are
  detected dynamically and the grouping column is a command-line argument.
- `cross_dataset.py`, loads all three files, reports which columns are shared by all
  three vs unique to each, and compares the mean of every shared numeric column across
  the three platforms.

All three stats scripts use sample standard deviation (n − 1).

## Findings

The most interesting result from comparing the three datasets is that each platform is used differently. Advertisements are mainly designed to encourage people to take action, tweets contain the most attack messaging, and Facebook posts focus more on discussing issues. Even though all three datasets are related to the 2024 U.S. presidential election, the messaging changes depending on the platform.

The three datasets also have different structures. The Ads dataset contains 246,745 rows and 41 columns, the Facebook Posts dataset contains 19,009 rows and 56 columns, and the Tweets dataset contains 27,304 rows and 47 columns. Although each dataset has many platform-specific columns, they all share 27 illuminating_ content flags. These shared columns describe message types, political topics, incivility, scam-like content, and other communication characteristics. Everything else depends on the platform. The Ads dataset contains spending, impressions, audience size, and campaign bylines. The Facebook Posts dataset includes engagement measures such as Likes, Shares, Comments, Love, Wow, Haha, Sad, Angry, and Care reactions, along with sponsor information. The Tweets dataset contains metrics such as retweets, replies, likes, quotes, bookmarks, views, language, and tweet source.

While examining the Facebook Posts dataset, I found a data quality issue in the header row. The columns illuminating_scored_message and election_integrity_Truth_illuminating were accidentally merged into a single column named illuminating_scored_messageelection_integrity_Truth_illuminating. This appears to be caused by a missing comma in the original CSV file. Because of this, Facebook Posts does not contain a separate election integrity flag like the other datasets, which is why only 27 illuminating_ columns are shared across all three datasets instead of 28.

Comparing the shared content flags shows clear differences between the platforms. Call-to-action messaging appears much more often in advertisements (57.3%) than in Facebook posts (13.3%) or tweets (11.0%). This makes sense because paid advertisements are usually designed to encourage people to donate, vote, or visit a website. The same pattern appears in fundraising messages, which account for 22.9% of advertisements but only 1.8% of Facebook posts and 0.8% of tweets.

Attack messaging follows a different pattern. It appears in 27.2% of advertisements, 21.7% of Facebook posts, and 30.8% of tweets, making Twitter the most attack-oriented platform in this dataset. On the other hand, issue-based messaging is more common in organic content. It appears in 38.2% of advertisements, 46.0% of Facebook posts, and 50.8% of tweets. This suggests that advertisements are more focused on encouraging action, while posts and tweets spend more time discussing political issues.

There are also noticeable differences in the topics being discussed. The economy is the most common topic on Twitter (16.0%), followed by advertisements (12.2%) and Facebook posts (9.0%). Immigration also appears more often on Twitter (6.5%) than in advertisements (3.4%). Health-related content is most common in advertisements (10.9%). Scam-related content is also highest in advertisements (7.2%) compared to only about 1–2% in the other two datasets. One pattern that remained surprisingly consistent across all three datasets is advocacy messaging, which appears in about 55–56% of the records regardless of platform.

I also looked at the grouped summaries for each dataset. Grouping the Ads dataset by page_id identified 4,475 unique pages, which matches the results from Task 2. Grouping Facebook Posts by Facebook_Id showed that pages varied widely in the amount of engagement they received, with some pages generating far more reactions than others. For the Tweets dataset, grouping by source produced 14 different Twitter clients, and one source accounted for most of the tweets in the dataset.

## Generalization

One goal of this task was to make the programs work on different datasets without rewriting the code each time. I was able to use the same three scripts on all three datasets without making any dataset-specific changes. Instead of hardcoding column names, the programs detect column types automatically using the same 80% numeric parsing rule from the previous tasks. The filename and grouping column are both provided as command-line arguments, so the same program can be run on different datasets simply by changing the input file and the grouping column. For example, I grouped the Ads dataset by page_id, the Facebook Posts dataset by Facebook_Id, and the Tweets dataset by source.

This approach worked well because the programs automatically recognized columns such as Likes, Shares, retweetCount, and other engagement metrics as numerical data, while correctly treating text and dictionary-like columns as categorical. No changes to the analysis logic were needed when switching between datasets.

However, working with different datasets also exposed a few problems that needed to be handled. The Facebook Posts dataset contains column names with spaces, such as Post Views and Total Views, which caused problems with pandas' named aggregation syntax. I had to rewrite the grouping code so that it no longer depended on keyword arguments. In the Tweets dataset, some groups contained no valid values for certain numerical columns. Polars returned None for the mean of these groups, which caused formatting errors until I added a check for missing values. The merged header in the Facebook Posts dataset also affected the shared-column comparison by reducing the number of common illuminating_ columns from 28 to 27. This showed that automated analysis still depends on having clean and consistent input data.

The main advantage of generalizing the programs is that they are no longer tied to a single dataset. If someone wanted to analyze a completely different CSV file, such as a healthcare survey or a transaction log, they would only need to specify a different grouping column. The type detection, descriptive statistics, and grouping logic would remain the same. In other words, the programs now work more like reusable tools than one-time scripts. The same command format can be used for any compatible dataset:

```bash
python pandas_stats.py <file> <group_column>
```

## Comparison of the three approaches

The three implementations produced the same results across all three datasets. The descriptive statistics and grouped summaries matched regardless of whether the analysis was performed using pure Python, pandas, or Polars. The pandas and Polars output files matched exactly, while the pure Python version differed only in formatting. This consistency gives confidence that all three implementations are performing the same calculations correctly.

The pure Python version still required the most work because every step had to be implemented manually. Missing values, type detection, descriptive statistics, and grouping all had to be written from scratch. Although this required more code, it also gave me a much better understanding of how these operations work internally.

Pandas remained the easiest library to use. Its syntax is familiar, and functions such as .groupby() and .describe() make the code much shorter than the pure Python implementation. Most of the analysis could be completed with relatively little code, although I still needed to handle missing values and make small adjustments for the Facebook Posts dataset.

Using Polars taught me the most because it behaves differently from pandas. Its expression-based syntax took some time to get used to, and its stricter type checking meant I had to be more careful when reading and converting data. During this task, I also noticed that Polars reported problems that pandas handled more quietly. For example, Polars returned None when calculating the mean of groups with no valid values, while pandas returned NaN, which could still be formatted without causing an error. These differences initially caused extra work, but they also made data quality issues much easier to notice instead of silently continuing with potentially misleading results.

After using all three approaches across three different datasets, I think each one has its own strengths. Pure Python provides the greatest control and helps build a deeper understanding of the underlying algorithms, but it requires much more code. Pandas is the easiest and most practical library for everyday data analysis because of its simple syntax and large ecosystem. Polars has a steeper learning curve because of its strict typing and expression-based style, but it performs very well and encourages writing more robust code. Overall, completing all three tasks showed that the same core analysis can be reused across multiple datasets, turning the programs into reusable analysis tools instead of scripts written for a single assignment.

## Reproducibility

Clone the repo, install `requirements.txt`, download the Milestone B bundle to a
local path, and run the commands above with your own file paths. Each script prints
to stdout; redirect to a file to save the output.
