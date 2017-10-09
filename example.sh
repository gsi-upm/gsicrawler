curl -X POST "http://localhost:9200/reddit/comment,article/_search?pretty" -H 'Content-Type: application/json'  -d  @- <<EOF
{
            "aggs": {
             "type": {
               "terms": {
                 "field": "_type",
                 "order": {
                   "_count": "desc"
                 }
               }
             },
             "comments": {
               "filter": {"term": {"_type": "comment"}},
                "subreddit": {
                    "terms": {
                        "field": "subreddit",
                        "order": {
                            "_count": "desc"
                    }
                }
            }
            },
             "subreddit": {
                "terms": {
                    "field": "subreddit",
                    "order": {
                        "_count": "desc"
                    } 
                }
            }
    }
}
EOF

