from dis import disco
import logging
from logging import Formatter, StreamHandler
from operator import indexOf
import re
import sys
from bin.answers import get_answer,load_answers, _answers
from datetime import datetime, timedelta

SUCCESS_STRING = "GGGGG"

class Wordle:
    def __init__(self, path) -> None:
        self.lo = logging.getLogger("Wordle")

        t = get_answer(datetime.now())
        self.answer_text = t[0]
        self.answer_number = t[1]
        self.path = path
        self.list = self._loadDict(path)
        self.chars = ""
        self.pattern = ""
        self.feedback = []
        self.guesses = []
        self.lo.info("Loaded {} dictionary entries".format(len(self.list)))
        
        # self._saveDict(path, self.list)

    def guess(self, chars: str) -> str:
        """Takes the supplied string in `chars` and compares it against the stored answer, returning a string

        * `B` means the character is not in the answer  
        * `Y` means the character is in the answer, but not in the guessed location  
        * `G` means the guess is the correct character & location"""  
        pattern = "-----"
        chars = chars.upper()
        
        if len(chars) != len(self.answer_text):
            self.lo.error("Length of the answer and the guess don't match!")
            raise IndexError
        self.guesses.append(chars)
        chars_excl_greens = ""
        answer_excl_greens = "" 
        for index in range(len(chars)):
            if chars[index] == self.answer_text[index]:
                pattern = pattern[:index] + "G" + pattern[index+1:]
                chars_excl_greens += "-"
                answer_excl_greens += "="
            else:
                chars_excl_greens += chars[index]
                answer_excl_greens += self.answer_text[index]

        for index in range(len(chars)):
            if pattern[index] == "-":
                if chars_excl_greens[index] in answer_excl_greens:                
                    # how many matches there are in the string (e.g. 1)
                    max_match = self._instances_of(chars[index], answer_excl_greens)
                    
                    # how many matches are there in the guess SO FAR (e.g. 2)
                    cur_match = self._instances_of(chars[index], chars_excl_greens[0:index])
                    if cur_match < max_match:
                        
                        replace_char = "Y"
                        
                    # if we've matched yellow enough times already, this must be black
                    # but if we've not yet matched enough yellows, this must be yellow
                    #
                    else:
                        replace_char = "B"

                else:
                        replace_char = "B"
                pattern = pattern[:index] + replace_char + pattern[index+1:]
        logging.info("Response for guess %s is %s",chars,pattern )
        return pattern

    def _instances_of(self, char, string) -> int:
        "counts the number of times a character appears in an answer"
        filtered_string = list(filter(lambda x: x == char, string))
        count = len(filtered_string)
        return count 

    def _times_missed(self, char, chars,pattern) -> int:
        "counts the number of times a character is missed"
        ret_count = 0
        for i in range(len(chars)):
            if chars[i] == char and pattern[i] == "B": 
                ret_count += 1
        return ret_count

    def contains(self, chars: str, pattern: str) -> list:
        """Trims down the internal dictionary of guesses based on the feedback in the pattern. Pattern should be 5 characters, containing the following 

        * `B` means the character is not in the answer  
        * `Y` means the character is in the answer, but not in the guessed location  
        * `G` means the guess is the correct character & location"""  
        self.pattern = pattern
        self.chars = chars
        if len(chars) == 5 and len(pattern) == 5:
            
            self.process_greens()
            self.process_yellows()
            self.process_misses()
            
        else:
            outstr = "Didn't enter the right length of guesses/pattern, displaying opener [%s/%s]"
            self.lo.info(outstr % (len(chars), len(pattern)))
        if len(self.list) == 0:
            logging.warning("No options remain in the list! D:")
            return "00000"
        self.lo.info(" Guess:" + self.list[0].strip())
        return self.list[0].strip()

    def process_greens(self) -> list:
        chars = self.chars
        pattern = self.pattern
        if "G" not in pattern:
            return
        re_string = self._extract(chars, pattern, "G")
        self._trim(re.compile(re_string))

    def process_yellows(self):
        chars = self.chars
        pattern = self.pattern
        if "Y" not in pattern:
            return
        extracted_chars = self._extract(chars, pattern, "Y", other_char=".")
        for i in range(0, 5):
            char = extracted_chars[i]
            if char != ".":

                re_string = "%s[^%s]%s" % (("."*(i)), char, ("."*(4-i)))
                self._trim(re.compile(re_string))
                re_string = "(?=.*[%s].*)." % (char)
                self._trim(re.compile(re_string))

    def process_misses(self):
        chars = self.chars
        pattern = self.pattern
        if "B" not in pattern:
            return

        
        #re_string = self._extract(chars, pattern, "B", other_char="")
        #Aroma where A is a green or yellow


        re_strings = self._get_misses_regexes()
        for re_string in re_strings:
            self._trim(re.compile(re_string))
        


    def _get_misses_regexes(self) -> str: 
        chars = self.chars 
        pattern = self.pattern
        required_letters = {} 
        
        for i in range (0,5):
            
            misses = self._times_missed(chars[i], chars, pattern)
            times = self._instances_of(chars[i], chars)
            if pattern[i] == "B":
                if misses == times:
                    required_letters[chars[i]] = 0
                elif times > misses:
                    required_letters[chars[i]] = 1 if chars[i] not in required_letters else required_letters[chars[i]] + 1
                        #The letter was used more than once.
                        #if the letter was used more than once, then the regex must find words that contain that letter X times, where X is the number of Ys or Gs
                        #so for Aroma, we get
        
                


        return_regexes = []
        flat_excludes = ""
        for letter in required_letters:
            if required_letters[letter] == 1:
                return_regexes.append( ".*%s(?!.*%s.*)" % (letter, letter))
            flat_excludes += letter if required_letters[letter] == 0 else ""
        
        if flat_excludes != "":
            return_regexes.append("[^%s]{5}" % (flat_excludes))
        return return_regexes
                

    def _extract(self, chars, pattern, patternChar, other_char="."):
        return_str = ""
        
        if len(chars) == 5 and len(pattern) == 5 and patternChar in pattern:
            chars = chars.upper()
            for i in range(0, 5):
                return_str += chars[i] if pattern[i] == patternChar else other_char
        else:
            return ""
        return return_str

    def _trim(self, regex):
        self.lo.debug("Current entries [%s], about to trim with: %s" % (len(self.list), regex))
        newList = []
        
        for string in self.list:
            newstring = string.upper().strip().split(" ")
            word = newstring[0]
            if re.match(regex, word):
                # print(string)
                newList.append(string)
        self.list = newList
        self.lo.debug("new entries list [%s]" % len(self.list))

    def _loadDict(self, path) -> list:
        data_list = []
        with open(path, mode="r", encoding="UTF-8") as file:
            lines = file.readlines()
            regex = re.compile(r"^[A-Za-z]{5}( [0-9]*).\n")
            # lines = ["there 1234346\n"]
            data_list = [word if re.match(regex, word) is not None else "" for word in lines]
            # data_list = []
            # for word in lines:
            #    if re.match(regex,word):
            #        data_list.append(word)
        return data_list

    def _saveDict(self, path) -> None:
        with open(path, "w+") as file:
            for line in self.list:
                if line != "":
                    file.write("{}".format(line))

    def result_string(self, discord = False, overide_b = "⬛", overide_y = "🟦", overide_g = "🟧") -> str:
        total_guesses = "X" if self.feedback[len(self.feedback)-1] != SUCCESS_STRING else len(self.feedback)
        re_str = "Wordle {} {}/6\n\n".format(self.answer_number, total_guesses)
        for index  in range(len(self.feedback)):
            line = self.feedback[index]
            d = "||{}||".format(self.guesses[index]) if discord == True else ""
            line = line.replace("B",overide_b)
            line = line.replace("G",overide_g)
            line = line.replace("Y",overide_y)
            re_str += "{}{}\n".format(line,d)
        
        return re_str
    
    def solve(self, use_yesterdays_answer_as_opener = True, overide_opener = None):
        
        
        self._saveDict("wordle_dict.txt")

        if use_yesterdays_answer_as_opener:
            next_guess = get_answer(datetime.now() - timedelta(days=1))[0]
        else:
            next_guess = self.contains("","")
        if overide_opener is not None:
            next_guess = overide_opener
        
        for i in range(0,6):
            result_pattern = self.guess(next_guess[0:5])
            
            next_guess = self.contains(next_guess,result_pattern)[0:5]
            self.feedback.append(result_pattern)
            if result_pattern == SUCCESS_STRING:
                break
        

if __name__ == "__main__":
    format = "%(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(handlers=[StreamHandler()],
                        format=format,
                        level=logging.DEBUG)
    w = Wordle("wordle_dict_base_extract_weighted.txt")
    discord = True if "-d" in sys.argv else False 

    w.solve()
    if "UTF-8" in sys.stdout.encoding:
        print(w.result_string(discord=discord))
    else: 
        print(w.result_string(overide_b = "B", overide_y="Y", overide_g="G", discord = discord))
    