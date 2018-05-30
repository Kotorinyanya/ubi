# Message Queues

This document records the message queues and their data structures used in the spider system.

## Review Crawl Order `review_order`

This queue is for the orders to crawl reviews from some app since some timestamp.

### Data Structure

```python
{
    "appid": 123,				# ID of app to crawl
    "last_updated": 1526609198,	# Start timestamp
    "language": "all"			# Language to filter
}
```

## Review Crawl Result `review_result`

This queue is to store the crawled reviews temporarily.

### Data Structure

```python

```

