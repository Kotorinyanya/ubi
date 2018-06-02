from flask import jsonify


def succeed(data=None):
    """
    Generate a succeeded JSON with "success" field.
    :param data:
    :return:
    """
    return jsonify({
        "success": 1,
        "data": data
    })


def fail(message=""):
    """
    Generate a failed JSON with optional message.
    :param message:
    :return:
    """
    return jsonify({
        "success": 0,
        "message": str(message)
    })
