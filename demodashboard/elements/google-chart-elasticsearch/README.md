`<google-chart>` is a web component designed to visualize data with Google Charts but obtaining data from an elasticSearch index.

### Usage

This web component accepts the following parameters:

```html

<google-chart
    data="<!-- json with the ElasticSearch results -->"
    field="<! -- field to visualize -->"
    type='<!-- google chart type: column, pie, column, etc -->'
    filters="{{filters}}"
    icon='maps:my-location'
    param='{{param}}'
    options='{"title": "Places at different cities"}'
    cols='[{"label": "Place", "type": "string"},{"label": "Count", "type": "number"}]' '<!-- visalized data in case of connection error -->'
</google-chart>

```

data object is obtained from elasticsearch. The query is made in the dashboard.

For more information visit: https://developers.google.com/chart/

### Installation

This web component is available in bower. 

```bash

$ bower install google-chart-elasticsearch

```

This command will install it inside `bower_components` folder

Remember to edit your `elements.html` with this component.