# How the dashboard works

The navigation follows a hierarchy: **host city → edition and season → sport → category → event**. Selecting an item updates the Tableau parameter **Explore selection**, which carries the selected IDs and paging state. Calculated fields use that selection to control the visible choices and podium.

The workbook contains 91 worksheets and 58 parameter actions. Many sheets are small interface elements: gallery hit areas, paging arrows, selected states, sport choices and medal labels. They support one dashboard rather than 91 separate analytical views.

## Navigation

- The landmark gallery shows six destinations at a time.
- The host-country selector narrows the gallery.
- Edition choices belong to the selected host city and season. Beijing has both Summer and Winter Games; unavailable seasons are disabled.
- Sport paging and the category choices reflect the selected Games.
- The event panel groups related events and supports scrolling.
- The podium shows the chosen event's awards and recorded team details. Ties and incomplete historical results should not be forced into exactly three individual names.

## Presentation model

The packaged extract combines factual and interface rows, distinguished by `RowType`. Awards have one row per award ID. Event controls use four geometry vertices each. Result lines hold wrapped names and roster text; other rows support edition, season and sport controls.

That structure makes the interface possible, but counting all rows would inflate the underlying data. The separate source CSVs provide a clearer relational model for analysis. [See the counting rules](data_dictionary.md).

## Editing

Open the packaged workbook, save a copy and inspect the underlying worksheets and dashboard actions. Results, labels, calculated fields and interaction logic remain editable in Tableau. Landmark and podium artwork are embedded images.

The repository preserves the published workbook as downloaded, including its embedded extract. The validation script reads it without changing its calculations, layout or source data.
