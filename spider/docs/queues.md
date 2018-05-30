# Message Queues

This document records the message queues and their data structures used in the spider system.

## Review Crawl Order `review.order`

This queue is for the orders to crawl reviews from some app since some timestamp.

### Data Structure

```python
{
    "appid": 123,				# ID of app to crawl
    "last_updated": 1526609198,	# Start timestamp
    "language": "all"			# Language to filter
}
```

## Review Crawl Result `review.result`

This queue is to store the crawled reviews temporarily.

### Data Structure

```python
{
    "recommendationid": review["recommendationid"],
    "appid": self.appid,
    "steamid": review["author"]["steamid"],
    "playtime_forever": review["author"]["playtime_forever"],
    "playtime_last_two_weeks": review["author"]["playtime_last_two_weeks"],
    "last_played": review["author"]["last_played"],
    "language": review["language"],
    "content": review["review"],
    "steam_weight": review["weighted_vote_score"],
    "weight": review["weighted_vote_score"],    # as default value
    "type": "positive" if review["voted_up"] else "negative",
    "vote_up_count": review["votes_up"],
    "vote_funny_count": review["votes_funny"],
    "comment_count": review["comment_count"],
    "published_at": review["timestamp_created"],
    "edited_at": review["timestamp_updated"]
}
```

## User Crawl Order `user.order.pre`

This queue stores pre-orders from Review Spider. The orders should be checked before sending into `user.order`.

### Data Structure

```python
{
    "steamid": review["author"]["steamid"],
    "nickname": "",             # as default value
    "avatar": "",               # as default value
    "country": "",              # as default value
    "level": "",                # as default value
    "games": [],                # as default value
    "review_count": review["author"]["num_reviews"],
    "screenshot_count": 0,      # as default value
    "workshop_item_count": 0,   # as default value
    "badge_count": 0,           # as default value
    "group_count": 0,           # as default value
    "game_count": review["author"]["num_games_owned"],
    "friend_count": 0,          # as default value
    "registered_at": 0          # as default value
}
```

## User Crawl Order `user.order`

This queue stores orders to crawl user information.

### Data Structure

The same as `user.order.pre`.

## Game Crawl Order `game.order.pre`

This queue stores pre-orders from User Spider. The orders should be checked before sending into `game.order`.

### Data Structure

```python
{
    "appid": 123
}
```

## Game Crawl Order `game.order`

This queue stores orders to crawl game information.

### Data Structure

The same as `game.order.pre`.

