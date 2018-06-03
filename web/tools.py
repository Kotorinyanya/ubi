import argparse
import datetime
import json
import pymysql
import time

dolphin = None


def export(args):
    reviews = {
        "positive": dict(),
        "negative": dict()
    }
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
    # Get date slices.
    date_slices = list()
    date_slices.extend(get_date_slices(start_date, end_date, 3))
    date_slices.extend(get_date_slices(start_date, end_date, 7))
    date_slices.extend(get_date_slices(start_date, end_date, 15))
    # Get reviews.
    apps = list(map(lambda x: x["appid"], get_apps()))
    for app in apps:
        reviews["positive"][app] = {
            "3": dict(),
            "7": dict(),
            "15": dict()
        }
        reviews["negative"][app] = {
            "3": dict(),
            "7": dict(),
            "15": dict()
        }
        for s in date_slices:
            sql = """
                select 
                reviews.appid,
                reviews.recommendationid, 
                reviews.content, 
                reviews.`language`, 
                reviews.weight as review_weight, 
                users.weight as user_weight,
                (users.weight + reviews.weight * 2) as weight2,
                reviews.type
                from 
                reviews, 
                users 
                where 
                reviews.weight > 0 
                and users.weight > 0 
                and reviews.steamid = users.steamid 
                and reviews.edited_at > %s
                and reviews.edited_at < %s
                and reviews.appid = %s
                and reviews.type = %s
                order by weight2 desc 
                limit 100
                """
            with dolphin.cursor() as cursor:
                cursor.execute(sql, (
                    s["start_time"],
                    s["end_time"],
                    app,
                    'positive'
                ))
                results = cursor.fetchall()
                cursor.execute(sql, (
                    s["start_time"],
                    s["end_time"],
                    app,
                    'negative'
                ))
                results.extend(cursor.fetchall())
            for result in results:
                appid = app
                t = result["type"]
                window_length = s["window_length"]
                end_date = s["end_date"]
                language = result["language"]
                if appid not in reviews[t]:
                    reviews[t][appid] = dict()
                if window_length not in reviews[t][appid]:
                    reviews[t][appid][window_length] = dict()
                if end_date not in reviews[t][appid][window_length]:
                    reviews[t][appid][window_length][end_date] = dict()
                if language not in reviews[t][appid][window_length][end_date]:
                    reviews[t][appid][window_length][end_date][language] = list()
                reviews[t][appid][window_length][end_date][language].append(result)
            a = open("out", "w")
            a.write(json.dumps(reviews))
            a.close()


def main():
    global dolphin
    args = parse_arguments()
    dolphin = get_dolphin(args)
    if args.action == "export":
        export(args)


def get_date_slices(start_date, end_date, window_length):
    date_slices = []
    new_end = end_date
    while new_end - datetime.timedelta(days=window_length) >= start_date:
        new_start = new_end - datetime.timedelta(days=window_length)
        date_slices.append(
            {
                "start_time": int(time.mktime(new_start.timetuple())),
                "end_time": int(time.mktime(new_end.timetuple())),
                "window_length": window_length,
                "end_date": new_end.strftime('%Y-%m-%d'),
            }
        )
        new_end -= datetime.timedelta(days=1)
    return date_slices


def get_dolphin(args):
    """
    Get an instance of pymysql for MySQL.
    :return:
    """
    dolphin = pymysql.connect(
        host=args.db_host,
        port=args.db_port,
        user=args.db_user,
        password=args.db_password,
        db=args.db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    return dolphin


def get_apps():
    """
    Get apps with their "last_crawled".
    :param dolphin:
    :return:
    """
    query_sql = "SELECT `appid` FROM `apps` WHERE `is_concerned` = 1"
    with dolphin.cursor() as cursor:
        cursor.execute(query_sql)
        results = cursor.fetchall()
    return results


def parse_arguments():
    """
    Parse arguments from command line and return the results.
    :return: parsed args
    """
    parser = argparse.ArgumentParser(description="PB Tools.")
    parser.add_argument("--debug", action="store_true",
                        help="Use this option to enable debug mode.")
    parser.add_argument("--mysql-host", action="store", dest="db_host",
                        default="localhost", help="Specify MySQL host address.")
    parser.add_argument("--mysql-port", action="store", dest="db_port",
                        default=3306, type=int, help="Specify MySQL host port.")
    parser.add_argument("--mysql-user", action="store", dest="db_user",
                        default="root", help="Specify MySQL user.")
    parser.add_argument("--mysql-password", action="store", dest="db_password",
                        default="root", help="Specify MySQL password.")
    parser.add_argument("--mysql-db", action="store", dest="db_name",
                        default="ubi", help="Specify MySQL database.")
    parser.add_argument("-a", "--action", action="store",
                        dest="action", required=True,
                        help="Specify action.")
    parser.add_argument("-s", "--start-date", action="store", dest="start_date",
                        help="Start Date")
    parser.add_argument("-e", "--end-date", action="store", dest="end_date",
                        help="End Date")
    return parser.parse_args()


if __name__ == "__main__":
    main()
