from django import template

register = template.Library()

def get_id(score, key):
    try:
        return score[key]
    except:
        return 0

register.filter('get_id', get_id)
