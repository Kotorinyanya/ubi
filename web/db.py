import heapq
import json
import pymysql

dolphin = None

DB_PARAMS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "ubi"
}


def init_dolphin():
    """
    Get an instance of pymysql for MySQL.
    :return: None
    """
    global dolphin
    if dolphin:
        dolphin.close()
    dolphin = pymysql.connect(
        host=DB_PARAMS["host"],
        port=DB_PARAMS["port"],
        user=DB_PARAMS["user"],
        password=DB_PARAMS["password"],
        db=DB_PARAMS["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def get_detail(appid):
    """
    Get details of an game.
    :param appid: ID of app
    :return: dict or None
    """
    detail = dict()
    query_sql = """ SELECT 
                    `apps`.`appid`, `apps`.`name`, `apps`.`image`, 
                    (SELECT COUNT(*) FROM `reviews` WHERE `appid` = `apps`.`appid`) AS review_count, 
                    (SELECT COUNT(*) FROM `reviews` WHERE `appid` = `apps`.`appid` AND `type` = 'positive') AS positive_count, 
                    (SELECT COUNT(*) FROM `reviews` WHERE `appid` = `apps`.`appid` AND `type` = 'negative') AS negative_count, 
                    (SELECT sum(`new_up` + `down_to_up`) FROM `review_changes` WHERE `appid` = `apps`.`appid` GROUP BY `id` ORDER BY `date` DESC LIMIT 1 OFFSET 1) as new_up, 
                    (SELECT sum(`new_down` + `up_to_down`) FROM `review_changes` WHERE `appid` = `apps`.`appid` GROUP BY `id` ORDER BY `date` DESC LIMIT 1 OFFSET 1) as new_down
                    FROM `apps` WHERE `appid` = %s AND `is_concerned` = 1 """
    # Fetch from DB.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql, (appid,))
        result = cursor.fetchone()
    # Check if exists.
    if not result:
        return None
    detail["app"] = result

    return detail


def get_apps():
    """
    Get all apps that are concerned.
    :return: dict
    """
    query_sql = """ SELECT 
                    `apps`.`appid`, `apps`.`name`, `apps`.`image`, 
                    (SELECT COUNT(*) FROM `reviews` WHERE `appid` = `apps`.`appid`) AS review_count, 
                    (SELECT COUNT(*) FROM `reviews` WHERE `appid` = `apps`.`appid` AND `type` = 'positive') AS positive_count, 
                    (SELECT COUNT(*) FROM `reviews` WHERE `appid` = `apps`.`appid` AND `type` = 'negative') AS negative_count, 
                    (SELECT `new_up` FROM `review_changes` WHERE `appid` = `apps`.`appid` GROUP BY `id` ORDER BY `date` DESC LIMIT 1 OFFSET 1) as `new_up`, 
                    (SELECT `new_down` FROM `review_changes` WHERE `appid` = `apps`.`appid` GROUP BY `id` ORDER BY `date` DESC LIMIT 1 OFFSET 1) as `new_down`, 
                    (SELECT `up_to_down` FROM `review_changes` WHERE `appid` = `apps`.`appid` GROUP BY `id` ORDER BY `date` DESC LIMIT 1 OFFSET 1) as `up_to_down`, 
                    (SELECT `down_to_up` FROM `review_changes` WHERE `appid` = `apps`.`appid` GROUP BY `id` ORDER BY `date` DESC LIMIT 1 OFFSET 1) as `down_to_up`
                    FROM `apps` WHERE `is_concerned` = 1 ORDER BY `name` """
    # Fetch from DB.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    return results


def get_review_changes(appid, start_date, end_date):
    """
    Get the review changes between "start_date" and "end_date"
    (both included) of "appid".
    :param appid: int, ID of app
    :param start_date: yyyy-MM-dd
    :param end_date: yyyy-MM-dd
    :return: list of dicts
    """
    query_sql = "SELECT " \
                "`date`, " \
                "`new_up`, " \
                "`new_down`, " \
                "`up_to_down`, " \
                "`down_to_up` " \
                "FROM " \
                "`review_changes` " \
                "WHERE " \
                "`appid` = %s AND " \
                "`date` >= %s AND " \
                "`date` <= %s"
    # Fetch from DB.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql, (appid, start_date, end_date))
        results = cursor.fetchall()
    # Format the dates.
    for result in results:
        result["date"] = result["date"].strftime("%Y-%m-%d")
    return results


def get_review_result(appid, window_length, end_date):
    """
    Get the review result of a given app of some window.
    :param appid: int, ID of app
    :param window_length: int, length of window
    :param end_date: yyyy-MM-dd, ending date of window
    :return: a dict or None
    """
    query_sql = "SELECT " \
                "`top_up_tags`, " \
                "`top_up_sentences`, " \
                "`top_up_reviews`, " \
                "`top_down_tags`, " \
                "`top_down_sentences`, " \
                "`top_down_reviews`, " \
                "`emotion` " \
                "FROM `results` " \
                "WHERE `appid` = %s " \
                "AND `window_length` = %s " \
                "AND `window_end_date` = %s"
    # Fetch from DB.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql, (appid, window_length, end_date))
        result = cursor.fetchone()
    # Decode the JSON texts.
    if result:
        for x in result.keys():
            result2 = json.loads(result[x])
            result[x] = dict()
            # Get top 8.
            largest = heapq.nlargest(8, result2, key=result2.get)
            for k in largest:
                result[x][k] = result2[k]
        # Get reviews.
        ups = []
        downs = []
        for rid in result["top_up_reviews"]:
            ups.append(get_review(rid))
        for rid in result["top_down_reviews"]:
            downs.append(get_review(rid))
        result["top_up_reviews"] = ups
        result["top_down_reviews"] = downs
    return result


def get_review(recommendationid):
    """
    Get a review by its ID.
    :param recommendationid:
    :return: dict or None
    """
    query_sql = "SELECT " \
                "`reviews`.`appid`, " \
                "`reviews`.`steamid`, " \
                "`users`.`nickname`, " \
                "`users`.`avatar`, " \
                "`users`.`country`, " \
                "`users`.`level`, " \
                "`users`.`review_count`, " \
                "`users`.`screenshot_count`, " \
                "`users`.`workshop_item_count`, " \
                "`users`.`badge_count`, " \
                "`users`.`group_count`, " \
                "`users`.`game_count`, " \
                "`users`.`dlc_count`, " \
                "`users`.`friend_count`, " \
                "`reviews`.`playtime_forever`, " \
                "`reviews`.`playtime_last_two_weeks`, " \
                "`reviews`.`last_played`, " \
                "`reviews`.`language`, " \
                "`reviews`.`content`, " \
                "`reviews`.`type`, " \
                "`reviews`.`vote_up_count`, " \
                "`reviews`.`vote_funny_count`, " \
                "`reviews`.`comment_count`, " \
                "`users`.`registered_at`, " \
                "`reviews`.`published_at`, " \
                "`reviews`.`edited_at` " \
                "FROM " \
                "`reviews`, " \
                "`users`" \
                "WHERE " \
                "`reviews`.`steamid` = `users`.`steamid`" \
                "AND `reviews`.`recommendationid` = %s"
    # Fetch from DB.
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql, (recommendationid,))
        result = cursor.fetchone()
    return result
