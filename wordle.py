import re

class Wordle:
    def __init__(self, path) -> None:
        self.path = path
        self.list = self._loadDict(path)
        print("Loaded {} dictionary entries".format(len(self.list)))
        #self._saveDict(path, self.list)
        pass


    def contains(self, chars:str, ignore_chars = "") -> list:
        chars = chars.lower()
        re_string = ""
        anything = "[a-z]" if ignore_chars == "" else "[^%s]" % (ignore_chars)
        for char in chars:
            re_string += anything if char == "." else char
        re.compile(re_string)
        print(re_string)
        counter = 0
        for string in self.list:
            string = string.lower().strip().split(" ")
            word = string[0]             
            if re.match(re_string,word):
                counter += 1
                print(string)
            if counter >= 20:
                break



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

    def _saveDict(self, path, list) -> None:
        with open(path, "w+") as file:
            for line in list:
                if line != "":
                    file.write("{}".format(line))

if __name__ == "__main__":
    w = Wordle(r"wordle_dict.txt")
    #w.contains(".ro..", "etuiasdfghjklcok")
    known=input("input your green characters with . as wildcard\n")
    excluded =  input("input your excluded characters\n")
    w.contains(known,excluded)
