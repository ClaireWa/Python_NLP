#!/usr/bin/env python

import os
import simpleaudio as sa
import argparse
from nltk.corpus import cmudict
import re
import string
import sys
import numpy as np
import time
import datetime
import calendar

### NOTE: DO NOT CHANGE ANY OF THE EXISTING ARGUMENTS
parser = argparse.ArgumentParser(
    description='A basic text-to-speech app that synthesises an input phrase using diphone unit selection.')
parser.add_argument('--diphones', default="./diphones", help="Folder containing diphone wavs")
parser.add_argument('--play', '-p', action="store_true", default=False, help="Play the output audio")
parser.add_argument('--outfile', '-o', action="store", dest="outfile", type=str, help="Save the output audio to a file",
                    default=None)
parser.add_argument('phrase', nargs=1, help="The phrase to be synthesised")

# Arguments for extensions
parser.add_argument('--spell', '-s', action="store_true", default=False,
                    help="Spell the phrase instead of pronouncing it")
parser.add_argument('--crossfade', '-c', action="store_true", default=False,
					help="Enable slightly smoother concatenation by cross-fading between diphone units")
parser.add_argument('--volume', '-v', default=None, type=int,
                    help="An int between 0 and 100 representing the desired volume")

args = parser.parse_args()

print(args.diphones)

class Synth:
    def __init__(self, wav_folder):
        self.diphones = []
        self.get_wavs(wav_folder)


    def get_wavs(self, wav_folder):
        ''' This function produces the full wave for the phrase, by concatenating the diphone files together'''

        # list the entire collection of available diphone sounds from the diphone folder in self.diphones
        for root, dirs, files in os.walk(wav_folder, topdown=False):
            for file in files:
                self.diphones.append(file)

        # the diphone sounds for the phrase will be added to this list in numpy array format, dtype = int16
        diphone_sounds = []

        if args.spell:
            # loop through the letters in the word(s) in the normalised phrase,
            # load the corresponding diphones from the diphone folder,
            # access the numpy array of this diphone and append it to diphone sounds
            for word in norm_phrase.split():
                for letter in word:
                    for diphone in diphone_seq[letter]:
                            d = sa.Audio()
                            d.load("diphones/{}".format(diphone))
                            num_array = d.data
                            diphone_sounds.append(num_array)

        else:
            # loop through the list objects in phrase_punc (these are words and allowed punctuation),
            # load the corresponding diphones for the words from the diphone folder, and
            # access the numpy array of this diphone and append it to diphone sounds
            for i in range(len(phrase_punc)):
                if phrase_punc[i] in diphone_seq.keys():
                    for diphone in diphone_seq[phrase_punc[i]]:
                        d = sa.Audio()
                        d.load("diphones/{}".format(diphone))
                        num_array = d.data
                        diphone_sounds.append(num_array)

                # for the punctuation list objects
                else:
                    try:
                        # insert a pause from the end of the previous word before the silence
                        d = sa.Audio()
                        d.load("diphones/{}-pau.wav".format(phone_seq[phrase_punc[i - 1]][-1]))
                        num_array = d.data
                        diphone_sounds.append(num_array)

                        if phrase_punc[i] == ',':
                            # insert 200ms of silence in place of the punctuation
                            silence = np.zeros(2000, dtype=np.int16)
                            diphone_sounds.append(silence)

                        if phrase_punc[i] == '.' or phrase_punc[i] == ':' or phrase_punc[i] == '!' or phrase_punc[i] == '?':
                            # insert 400ms of silence in place of the punctuation
                            silence = np.zeros(4000, dtype=np.int16)
                            diphone_sounds.append(silence)

                        if i <= range(len(phrase_punc))[-2]:
                            # insert a pause after the silence to the beginning of the next word, only if
                            # there is a next word
                            d.load("diphones/pau-{}.wav".format(phone_seq[phrase_punc[i + 1]][0]))
                            num_array = d.data
                            diphone_sounds.append(num_array)

                    except KeyError:
                        print("Ignoring consecutive punctuation:{}".format(phrase_punc[i]))

        # concatenate the diphone sounds to produce the phrase sound
        phrase_sound = np.concatenate(diphone_sounds)

        # create the instance of the phrase wave file
        x = sa.Audio(rate=16000)
        x.data = phrase_sound

        if args.play:
            if args.volume:
                # scale the volume integer entered by the user so that it can be understood
                # by rescale in SimpleAudio
                volume = int(args.volume) * 0.01
                x.rescale(volume)
            x.play()

        if args.outfile:
            x.save(args.outfile)



class Utterance:
    def __init__(self, phrase):
        self.phrase_date = self.dates_to_word(phrase)
        self.phrase_norm = self.normalise_text()
        self.phone_seq = self.get_phone_seq()


    def dates_to_word(self, phrase):
        ''' This function will replace dates in digit format to dates in word format
        and remove all other digits'''

        new_phrase = phrase
        days = ['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
                'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth',
                'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth',
                'nineteenth', 'twentieth', 'twenty-first', 'twenty-second', 'twenty-third',
                'twenty-fourth', 'twenty-fifth', 'twenty-sixth', 'twenty-seventh', 'twenty-eighth',
                'twenty-ninth', 'thirtieth', 'thirty-first']

        year_unit = ["", "one", "two", "three", "four", "five", "six", "seven", "eight",
                     "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                     "sixteen", "seventeen", "eighteen", "nineteen"]
        year_dec = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        # used to search the phrase for a date in dd/mm, dd/mm/yy or dd/mm/yyyy format
        # group 3 is optional and will be the decade of the year and the year unit,
        # ignoring the century if it is there
        r = re.search(r'(\d{2})/(\d{2})/*(\d\d)*', phrase)

        # check if there is a date in the phrase in the specified format
        if bool(re.search(r'(\d{2})/(\d{2})/*(\d\d)*', phrase)) == True:
            # define the day number, month and year from the date in the phrase
            day_num = int(r.group(1))
            month_num = int(r.group(2))
            year_num = r.group(3)

            # convert the day and month numbers to their corresponding names
            day_name = days[day_num]
            month_name = calendar.month_name[month_num]

            # check if there is a year specified in the date
            if bool(year_num) == True:
                # this will account for the year 1900 or 00
                if int(year_num[0]) == 0 and int(year_num[1]) == 0:
                    year_name = 'nineteen hundred'

                # this will account for years from 1901-1919 (inclusive)
                elif int(year_num[0]) == 0 or int(year_num[0]) == 1:
                    year_name = 'nineteen hundred and ' + year_unit[int(year_num)]

                # this will account for decade years from 1920 to 1990 (inclusive)
                elif int(year_num[1]) == 0:
                    year_name = 'nineteen ' + year_dec[int(year_num[0])]

                # this will account for all other years not already specified in range 1900-1999
                else:
                    year_name = 'nineteen ' + year_dec[int(year_num[0])] + ' ' + year_unit[int(year_num[1])]
                new_phrase = re.sub(r'(\d{2})/(\d{2})/*(\d\d)*', month_name + ' ' + day_name + ' ' + year_name, phrase)

            # if a year is not specified in the date
            else:
                new_phrase = re.sub(r'(\d{2})/(\d{2})/*(\d\d)*', month_name + ' ' + day_name, phrase)

        # remove other digits from the phrase and then lowercase all of the text in it
        new_phrase = ''.join([i for i in new_phrase if not i.isdigit()])
        new_phrase = new_phrase.lower()

        return new_phrase


    def normalise_text(self):
        ''' This function will normalise phrase_date to remove everything but letters and spaces,
        the phone sequence function will then use the output from this function as its input
        to search the cmudict for pronunciations'''

        # define ascii letters and spaces as the only allowed characters
        allowed = string.ascii_letters + ' '
        norm_text = self.phrase_date

        # loops through the string of text and removes any character not included in 'allowed'
        for i in range(len(self.phrase_date)):
            if self.phrase_date[i] not in allowed:
                norm_text = norm_text.replace(self.phrase_date[i], '')

        return norm_text


    def text_for_punc(self):
        ''' This function will create a version of phrase_date (as a list) which keeps specified punctuation in it.
        The output from this function will be used to determine where silence should be inserted in
        place of the punctuation, when creating the numpy array of concatenated diphones '''

        phrase = self.phrase_date
        phrase = re.findall(r"[\w']+|[,.:!?]", phrase)
        phrase_punc = list(phrase)

        return phrase_punc


    def get_phone_seq(self):
        ''' Loop through the words (or letters if user chooses spell option) in norm_phrase,
        find the corresponding pronunciation for the word/letter in the nltk corpus 'cmudict' and
        add it to a dictionary as the value, with the key as the word/letter '''

        # create dictionary of all pronunciations for words/letters in cmudict
        all_phones = cmudict.dict() # www.nlyk.org/howto/corpus.html

        # empty dictionary where the word/letter phones will be added to
        phone_seq = {}

        # append the pronunciations of the letters/words to phone_seq
        for word in self.phrase_norm.split():
            if args.spell:
                for i in word:
                    try:
                        # only including the first pronunciation per letter if there are more than one
                        phone_seq[i] = all_phones[i][0]
                    except KeyError:
                        # if the letter is not in cmudict, let the user know and exit program
                        print("Exiting program as failed to find the pronunciation for: {}.".format(i))
                        sys.exit()
            else:
                try:
                    # including only first pronunication for word, if more than one
                    phone_seq[word] = all_phones[word][0]
                except KeyError:
                    print("Exiting program as failed to find the pronunciation for: {}.".format(word))
                    sys.exit()

        if args.spell:
            # add pause phone before and after every letter for spelling words
            for word in phone_seq.keys():
                phone_seq[word].insert(0, 'pau')
                phone_seq[word].insert(len(phone_seq[word]), 'pau')

        else:
            # add pause phone at the beginning of the first word and at the end of the last word in the phrase
            first_word = list(phone_seq)[0]
            phone_seq[first_word].insert(0, 'pau')
            last_word = list(phone_seq)[len(phone_seq)-1]
            phone_seq[last_word].insert(len(phone_seq[last_word]), 'pau')

        # lower case the phones in phone_seq so that they will match lowercase names of diphones in diphone folder
        phone_seq = {k.lower(): [i.lower() for i in v] for k, v in phone_seq.items()}

        word_regex = re.compile(r'\W*([a-z]+)(\d*)')
        # removing numbers from phones in phone_seq by appending only the matched lowercase words/letters
        for value in phone_seq.values():
            for i in range(len(value)):
                word_match = word_regex.match(value[i])
                w = word_match.group(1)
                value[i] = w

        return phone_seq


    def get_diphone_seq(self):
        ''' This function will concatenate the phones to create the diphones for the phrase,
        matching the format of the diphone names in the diphone folder'''

        diphone_seq = {}

        # loop through phones for each word and create diphones by concatenating adjacent phones,
        # adding '-' in between them and '.wav' at the end to match the format of the diphone names
        # in the diphone folder
        for word in self.phone_seq.keys():
            # account for one letter words
            if len(self.phone_seq[word]) == 1:
                diphone_seq[word] = [self.phone_seq[word][0] + '-' + self.phone_seq[word][0] + ".wav"]

            else:
            # set the range to be the from the first phone to the second last phone so that it doesn't try to
            # create a diphone with the last phone and nothing
                for i in range(len(self.phone_seq[word]) - 1):
                    try:
                        diphone_seq[word].append(self.phone_seq[word][i] + '-' + self.phone_seq[word][i + 1] + ".wav")
                    except KeyError:
                        diphone_seq[word] = [self.phone_seq[word][i] + '-' + self.phone_seq[word][i + 1] + ".wav"]

        return diphone_seq


if __name__ == "__main__":
    utt = Utterance(args.phrase[0])
    norm_phrase = utt.normalise_text()
    phrase_punc = utt.text_for_punc()
    phone_seq = utt.get_phone_seq()
    diphone_seq = utt.get_diphone_seq()
    diphone_synth = Synth(wav_folder=args.diphones)
    sound = Synth.get_wavs(wav_folder=args.diphones)



