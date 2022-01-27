import re
import sys
class Wordle:
    def __init__(self, path) -> None:
        self.path = path
        self.list = self._loadDict(path)
        self.chars = "" 
        self.pattern = ""
        print("Loaded {} dictionary entries".format(len(self.list)))
        #self._saveDict(path, self.list)
        
    def contains(self,chars:str, pattern:str) -> list:
        self.pattern = pattern
        self.chars = chars
        if len(chars) == 5 and len(pattern) == 5:
            self._edge_case_check()    
            self.contains_green()
            self.exclude_misses()
            self.contains_yellow()
        
        else:
            print ("Didn't enter the right length of guesses/pattern, displaying opener [%s/%s]" % (len(chars),len(pattern)))    
        for i in range(0,min(5,len(self.list))):
            print(self.list[i].strip())

    def contains_green(self) -> list:
        chars = self.chars
        pattern = self.pattern
        if "G" not in pattern:
            return
        re_string = self._extract(chars,pattern,"G")
        self._trim(re.compile(re_string))

    def contains_yellow(self):
        chars = self.chars
        pattern = self.pattern
        if "Y" not in pattern:
            return
        extracted_chars = self._extract(chars,pattern,"Y",other_char=".")
        for i in range(0,5):
            char = extracted_chars[i]
            if char != ".":
                
                re_string = "%s[^%s]%s" % (("."*(i)),char,("."*(4-i)))
                self._trim(re.compile(re_string))
                re_string = "(?=.*[%s].*)" % (char)
                
                self._trim(re.compile(re_string))
    def exclude_misses(self):
        chars = self.chars
        pattern = self.pattern
        if "B" not in pattern:
            return
        re_string = self._extract(chars,pattern,"B",other_char="")
        re_string = "[^%s]{5}" % (re_string)
        self._trim(re.compile(re_string))
        #[^abou]{5}


    def _edge_case_check(self):
        pass 

    def _extract(self,chars,pattern,patternChar,other_char = "."):
        return_str = ""
        if len(chars) == 5 and len(pattern) == 5 and patternChar in pattern: 
            chars = chars.lower()
            for i in range(0,5):
                return_str += chars[i] if pattern[i] == patternChar else other_char
        else:
            return ""
        return return_str

    def _trim(self,regex):
        print("Current entries [%s], about to trim with: %s" % (len(self.list),regex))
        newList = []
        for string in self.list:
            newstring = string.lower().strip().split(" ")
            word = newstring[0]             
            if re.match(regex,word):
                #print(string)
                newList.append(string)
        self.list = newList


    def _loadDict(self, path) -> list:
        data_list = []
        with open(path,mode="r",encoding="UTF-8") as file:
            lines = file.readlines()
            regex = re.compile(r"^[A-Za-z]{5}( [0-9]*).\n")
            #lines = ["there 1234346\n"]
            data_list = [word if re.match(regex,word) is not None else "" for word in lines]
            #data_list = []
            #for word in lines:
            #    if re.match(regex,word):
            #        data_list.append(word)
        return data_list

    def _saveDict(self, path) -> None:
        with open(path, "w+") as file:
            for line in self.list:
                if line != "":
                    file.write("{}".format(line))

if __name__ == "__main__":
    if "-r" in sys.argv:
        w = Wordle("wordle_dict_base.txt")
        w._saveDict("wordle_dict.txt")
    else:
        w = Wordle("wordle_dict.txt")
        known=input("input your guesses, leave empty for an opener\n")
        pattern = input ("input your guesses results as B, Y, or G\n")
        w.contains(known,pattern)
        w._saveDict(r"wordle_dict.txt")
