from datetime import datetime, timedelta
import logging
import json
_start_date = datetime(2021, 6, 19)
_answers = []
_lo = logging.getLogger("answers")
def load_answers(path = "bin/answers.json"):
    global _answers
    global _start_date
    try:
        j = json.load(open(path,"r"))
        _start_date  = datetime.strptime(j["START_DATE"],r"%Y-%m-%d")
        _answers = j["ANSWERS"]
    except Exception as e:
        _lo.error("Couldn't load answers.json %s",e)
    return _answers

def get_answer(date: datetime):
    global _answers
    global _start_date
    if len(_answers) == 0:
        load_answers()
    diff = date - _start_date 
    offset = diff.days
    _lo.debug(datetime.now() - timedelta(days=241))
    _lo.debug(offset)
    try:
        _lo.debug(_answers[offset])
        return (_answers[offset].upper(),offset)
    except KeyError as e:
        _lo.warn("Couldn't get an answer, KeyError - %s - %s", offset, e)
        return ("ERROR",-1)
    except IndexError as e:
        _lo.error("Didn't find an answer for that date. Looked for %s",diff)
        return ("ERROR",-1)