from typing import List, Dict

def build_parking_carousel(parkings: List[Dict]) -> dict:
    if not parkings:
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "附近找不到停車場",
                        "weight": "bold",
                        "size": "md"
                    }
                ]
            }
        }

    bubbles = []
    for p in parkings:
        avail = p.get('available_spaces', -1)
        avail_text = str(avail) if avail >= 0 else "未知"
        avail_color = "#1DB446" # Green
        if avail == 0:
            avail_color = "#FF334B" # Red
        elif avail > 0 and avail <= 5:
            avail_color = "#FFC107" # Yellow
        elif avail == -1:
            avail_color = "#999999" # Gray

        dist = p.get('distance', 0)
        nav_url = f"https://www.google.com/maps/search/?api=1&query={p.get('lat')},{p.get('lon')}"

        bubble = {
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": p.get('name', '停車場'),
                        "weight": "bold",
                        "size": "sm",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "空位：",
                                "size": "sm",
                                "color": "#aaaaaa"
                            },
                            {
                                "type": "text",
                                "text": avail_text,
                                "size": "sm",
                                "color": avail_color,
                                "weight": "bold"
                            }
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "距離：",
                                "size": "sm",
                                "color": "#aaaaaa"
                            },
                            {
                                "type": "text",
                                "text": f"{dist}m",
                                "size": "sm",
                                "color": "#666666"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "導航",
                            "uri": nav_url
                        }
                    }
                ],
                "flex": 0
            }
        }
        bubbles.append(bubble)

    return {
        "type": "carousel",
        "contents": bubbles
    }
