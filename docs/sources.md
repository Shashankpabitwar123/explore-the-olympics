# Sources and credits

## Olympic results

The project uses a saved snapshot dated **28 September 2026**. [Olympedia](https://www.olympedia.org/) is the principal results source. The edition, event and award tables retain links to the relevant edition medal pages, such as [Paris 2024](https://www.olympedia.org/editions/63/medal).

Supplemental roster records retain their own source links, including the [Olympedia scraping dataset by Joseph Cheng](https://github.com/josephwccheng/olympedia_web_scraping). Follow the `source` and `roster_source` fields for record-level provenance.

The repository preserves the five supplied source CSVs without rewriting them. The published workbook and preview were downloaded from [Tableau Public](https://public.tableau.com/app/profile/shashank.pabitwar/viz/ExploretheOlympics/OlympicExplorer) on **1 October 2026**. File hashes are recorded in [the source manifest](../data/source_manifest.json).

## Artwork

- **Landmarks and decorative artwork:** project illustrations used as navigation and visual framing. Generated landmark illustrations are stylized representations, not photographs of Olympic venues.
- **Flags:** saved Olympedia flag assets, with delegation/NOC codes as filenames. [Flag source notes](credits/flags.txt) describe the PNG conversions. These are not an edition-specific historical flag reconstruction.
- **Sports pictograms:** Wikimedia Commons pictograms and supplementary icons, resized and recolored for the dashboard. [The full attribution file](credits/sport-icons.json) lists each source, author, license and modification, including icons under public-domain, CC0, CC BY and CC BY-SA terms.

Source data and third-party artwork retain their respective rights and attribution requirements.

## Coverage and limitations

- The snapshot contains **55 editions from 1896 to 2026**: 30 Summer and 25 Winter editions. This describes the saved dataset, not a live query. The 1906 Intercalated Games are not included.
- The project focuses on medal awards and recorded rosters. It does not include every participant or every performance result.
- Older editions can contain missing names or event details. Missing information is preserved rather than inferred.
- Historical delegations, art competitions, ties and team awards need their original context; treating every row as an individual athlete would misrepresent the data.
- The dataset contains 2026 records as supplied in the snapshot. The repository checks their consistency with the workbook; it does not independently re-audit every historical source fact.
- The visible country selector refers to **host countries**, not a filter for the country winning a medal.
- Validation checks data and package structure. The published opening view was visually reviewed; the repository release does not claim automated testing of every Tableau interaction.
