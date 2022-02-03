import json
import logging

VALID_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# import pandas
class weighter(): 
    def __init__(self, load_path, save_path) -> None:
        
        self.l = logging.getLogger("weighter")
        self.valued_words={}
        self._load_file(load_path)
        self._value_words(self.words)
        self._save_file(save_path)

    def _value_words(self,words):
        temp = {}
        for word in words:
            temp[word] = self._value_word(word)

        self.valued_words=dict(sorted(temp.items(),key= lambda x:-x[1]))
        



    def _value_word(self,word) -> int:
        length = len(self.letter_position_frequencies)
        if len(word) != length:
            self.l.warn("Couldn't value word %s, it's the wrong length" %(word))
            return 0
        word_value = 0 
        for i in range(length):
            
            letter = word[i]
            try:
                word_value += self.letter_position_frequencies[i][letter]

            except KeyError:
                self.l.error("Didn't recognise letter [%s] in the word [%s], does it conform?" % (letter,word))
            except IndexError:
                self.l.error("Tested word %s is too long" % (letter,word))
        return word_value

    def _save_file(self,path):
        with open(path,"w+") as file:
            
            for key in self.valued_words:
                file.write("%s %s\n"%(key,self.valued_words[key]))




    def _load_file(self, path):
        words = []
        new_words = []
        with open(path) as file:
            words = file.readlines()
        
        letterpos = [self._generate_blank_letters_obj(),
            self._generate_blank_letters_obj(),
            self._generate_blank_letters_obj(),
            self._generate_blank_letters_obj(),
            self._generate_blank_letters_obj()] 
        letters = self._generate_blank_letters_obj()
        for word in words:
            
            word = word.upper().strip()
            new_word = ""
            for i in range(len(word)):
                
                letter = word[i]
                if letter in VALID_LETTERS:
                    letters[letter] += 1
                    letterpos[i][letter] += 1
                    new_word += letter
            new_words.append(new_word)            


        self.words = new_words
        self.letter_frequencies = letters
        self.letter_position_frequencies = letterpos
                    
    def _generate_blank_letters_obj(self):
        letter_string = VALID_LETTERS
        return_obj = {}
        for letter in letter_string:
            return_obj[letter] = 0
        return return_obj

if __name__ == "__main__":
    w = weighter("wordle_list_extract.txt","wordle_dict.txt")
    