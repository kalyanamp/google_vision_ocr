import io
import json
import re
import os
import datetime
import cv2
import numpy as np
import requests
from google.cloud import vision
from google.cloud.vision import types
import sys
import difflib
from PIL import Image, ExifTags
import xml.etree.ElementTree as ElementTree

"""
Changelog
## [5.0] - 2018-03-20
### Added
- Function to identify paystub type based on lookups texts which are added in 
    structure files.

### Changed
- Get structure moved into class, class name and invocation method also changed
    so as to make it easier for integration.

## [4.4] - 2018-03-20
### Added
- Added new rule of Is TaxType header defined, would be used for deductions tables
 which has Pre / Post or B/A defined in values itself.
- Method to determine Gross Pay, if gross pay is not provided, instead total of earnings
 is provided.

### Changed
- Updated entire method of create blocks to work as per new method of pre/post deduction
    identification.
- Updated Identify pay component method to resolve bugs

## [4.3.3] - 2018-03-14
### Added
- Method to convert all amount values to final float type as required
- Method to determine text compression and search words from lines based on compression 
    level.
- Added 'Federal Taxable Wages' and 'Total Gross Earnings' in other and gross columns rspectively

### Changed
- Logic of Net Pay and Gross Pay in final output, if more than one rows found in these
    types, we shall finalize only one (preferably having Current and YTD both values)
    and display it in final output.

## [4.3.2] - 2018-03-13
### Added
- Method to read vertical data value pair
- Added method to read values of rules.
- Logic to identify tables which has headers, in this case no old columns of blocking
    blocks are inherited in new block
- Logic to ignore values if block is deactivated
- Method to read values as per data dictionary definitions

### Changed
- Logic of block identification in find_col_sequence method,
    now we use block end-x instead of mean-x
- Paystub struct file, changes in data_val and data_dict

### Removed
- Method to read 'is star pre tax', now any rule can be read using check_rule method
- Delete col sequence logic

## [4.3.1] - 2018-03-12
### Added
- Method to determine paystub type based on filename
- Added '=' and '>' in ignore characters list
- Added ':' character as end of word, useful to read data in data_val pairs

### Changed 
- Method to make space_width zero in rectify_data, now if next word is also part of 
    previous word which is a column header we must include that
- Changed method to define end of horizontal table, now we shall look at values line
    to define end of table. [tab_width method failed in few cases]

## [4.3] - 2018-03-09
### Added
- Method to finalise block based on given block name in col sequence function,
    if seq_found is having confidence > 75, then only we refer block name
- 'Your federal taxable....' text in ignore words
- Data Dictionary which can be used to fetch data of summary or other general data

### Changed
- Logic to identify total of some block.
- Now column header can also be payment component
- Logic to delete columns based on blocking words, now any string containing 
    digits cannot delete column.

## [4.2] - 2018-03-07
### Added
- Function to identify values from horizontal table and add them to data blocks
- Function to identify key-value pair of data as given in structure.
- Function to create all_headers from structure based on given type

### Changed
- Paytype identifying block, it is now used just for general paytype identification
- Logic of structure reading, now for every paystub by default generic structure
    will be loaded, and if specific structure is provided, it will update all_headers
    as per specific structure.
- Data blocks output for empty value changed from None to ''

## [4.1] - 2018-03-05
### Added
- Rules in paystub structures. for e.g. we can define whether star is used 
    for pre-tax or not
- If a pay component name is equal to its block name we consider that as Total of that block
- Function to identify whether paystub has got star value as pre-tax deductions

### Changed 
- Improved log comments to understand execution flow in a better way
- Resolved bug of check_flag in find_sequence function

## [4.0] - 2018-03-01
### Added
- Method to read pasytub based on given structure as per XML
- Method to calculate Total of Earnings, Deductions (Pre & Post), Taxes
- Method to read 'Rate' and 'Hour' from paystub
- Signs '-' and '–' is added to ignore signs list

### Changed
- Create final data method has been changed to accomodate 'rate' and 'hour' values in it
- Column end in column headers are now calculated so as to check if next word is a part of respective
    column or if it is a new column header

## [3.3.1] - 2018-02-26
### Added
- Added few values in tax headers and current, ytd col headers
- Block name now to be identified as per block header values


## [3.3] - 2018-02-23
### Added
- Logic to delete column if it is being blocked by any text apart from header flags.
- Logic to stop word, when word belonging to column column headers are found in line algorithm. 
    [Current and YTD column detection is very important for this algorithm]
- Curent column flags added in initialisation function.
- Added 'voluntary deductions','other deductions' as types of deduction headers
- Added 'taxable earnings', 'earnings period' as types of earnings headers
- Added 'pay distribution' in types of other headers
- Added new Block Names in final output 'Pre Tax Deductions','Post Tax Deductions'
- Logic to identify deduction type such as 'Pre' or 'Post' based on given block header or if word / value contains * in it.

### Changed
- space width distance between two words increased from 2.5X to 2.75X
- Delete column-block mapping logic is updated, where first number of columns are counted,
    If there are 1+ columns:
    First preference will be given to columns that are placed below block headers. 
    [Note: y-distance should be greater than block's start-y plus half of block header height]
    If no such column found, find the nearest column column but not the overlapping column
- Block blocking logic is changed, now it works on following idea:
    First try to search for a block that is near to its mean and block it
    If no such block found, for the nearest block check if new block is in between mean of block and its respective current column mean
    If any of above is true, change all columns from previous block to new block
- Categorized deduction headers into three parts: Normal, Pre and Post

### Removed
- Block Name 'Deductions' from final outputs

## [3.2.1] - 2018-02-21
### Changed
- number of words to be considered for first general space width from 9 to 5
- space width distance between two words increased from 2.25X to 2.5X
- Delete column-block mapping logic is updated, such as there can be multiple columns of same type to 
    same block, if and only if columns names are similar. (To resolve issue of Blocks having data in 1+ parts)

### Added
- Now storing column name as well, at 5th index of variable holding all column details

## [3.2] - 2018-02-21
### Added
- Changelog to note down version-wise changes and to make my life easy
- Logic to rotate image when camera orientation is incorrect
- Function to identify payment component
- Added a special character in float value identification method, new character added is '–', which is used
    as a subtraction symbol in few paystubs
- Added 'associate taxes' in tax headers
- New global variable 'other_headers' to store all other headers
- Added 'rate this period' in current col flags
- Added 'year to' in YTD col flags
- Added 'amount earned' in other col flags
- Added 'chck1' in other columns in create blocks method
- Added 'gross earnings' in gross columns in create blocks method

### Changed
- Column-block mapping algortihm is changed, it works on following idea:
    For upto 3 lines above this column look for:
    1. Closest block on left of this column where block start-x is less than column start-x
    2. If not found, find closest block on right of this column where block start-x is greater than or equal 
        to column start-x
- Delete column-block mapping logic is changed (for multiple columns of same type to same block),
    it works on following idea:
    1. For a block having multiple columns to its bottom-right, keep the one closest on its right side.
    2. If no such column found, for columns on its same line or above it, keep the one farthest to it on right side.
- Logic to joint float values, now two integers with a space between them will be considered as a float. 
(Missing decimal issue resolved)
- Logic for payment component identification, now it uses a new method which is added in this version.
(Solves issue of incorrect pay component detection)

### Removed
- Extra init parameters that were carried along from the start of this project
- Draw bounding box and get data in box code, as it was not relevant to this project.

"""

class paystub_gcv:
    def __init__(self):
        self.result={}
        self.text_val=[]
        self.keys=[]
        self.values=[]
        self.description = []

    def init_structure(self,all_headers):
        self.earning_headers = all_headers['block_headers']['earnings']
        self.normal_deduction_headers = all_headers['block_headers']['normal_deductions']
        self.pre_deduction_headers = all_headers['block_headers']['pre_deductions']
        self.post_deduction_headers = all_headers['block_headers']['post_deductions']
        self.deduction_headers = self.normal_deduction_headers + self.pre_deduction_headers + self.post_deduction_headers
        
        self.tax_headers = all_headers['block_headers']['taxes']
        self.other_headers = all_headers['block_headers']['other']
        
        #define column headers
        self.current_col_flags = all_headers['col_headers']['current']
        self.ytd_col_flags = all_headers['col_headers']['ytd']
        self.other_col_flags = all_headers['col_headers']['other_earnings']
        self.rate_col_flags = all_headers['col_headers']['rate']
        self.hour_col_flags = all_headers['col_headers']['hours']
        self.column_header_flags = self.current_col_flags+self.ytd_col_flags+self.other_col_flags+self.rate_col_flags+self.hour_col_flags

        self.column_sequences = all_headers['col_sequence']
        self.rules = all_headers['rules']
        self.vertical_column_sequences = all_headers['vertical_col_sequence']

        self.data_val = all_headers['data_val']
        self.data_dict = all_headers['data_dict']

    def is_float(self,s):
        try:
            if s[-3] == ',':
                k = s.rfind(",")
                s = s[:k] + "." + s[k+1:]
        except:
            pass
        s = s.replace('B','8')
        s = s.replace('S','5')
        s = s.replace(',','')
        #s = s.replace('$','')
        s = s.replace('-','')
        s = s.replace('–','')
        s = s.replace(' ','.')
        s = s.replace('.','',s.count('.')-1)
        try:
            int(s)
            return False
        except:
            try:
                float(s)
                return s
            except ValueError:
                return False

    def is_float_or_int(self,s):
        try:
            if s[-3] == ',':
                k = s.rfind(",")
                s = s[:k] + "." + s[k+1:]
        except:
            pass
        s = s.replace('B','8')
        s = s.replace('S','5')
        s = s.replace(',','')
        #s = s.replace('$','')
        #s = s.replace('s','')
        s = s.replace('-','')
        s = s.replace('–','')
        s = s.replace(' ','.')
        s = s.replace('.','',s.count('.')-1)
        try:
            int(s)
            return True
        except:
            try:
                float(s)
                return True
            except ValueError:
                return False

    def final_float(self,s,c_type='General'):
        s = s.replace('B','8')
        s = s.replace('S','5')
        s = s.replace('s','')
        s = s.replace(',','')
        #s = s.replace('$','')
        s = s.replace('-','')
        s = s.replace('–','')
        s = s.replace(' ','')
        if c_type != 'Rate':
            s = s.replace('.','')
            s = s[:-2]+'.'+s[-2:]
        return s
    
    def is_pay_component(self,s):
        if s.lower() in ['yes','no']:
            return False
        s = s.replace(',','')
        s = s.replace(':','')
        s = s.replace('/','')
        s = s.replace('-','')
        s = s.replace('–','')
        s = s.replace(' ','')
        s = s.replace('.','')
        s = s.replace('*','')
        try:
            int(s)
            return False
        except:
            if len(s) < 2:
                return False
            else:
                return True

    def rectify_data(self):
        line_list = []
        line_heights = []
        desc = self.description.description
        print(desc)

        #sort all words as per y-axis of its first element
        res = sorted(self.result, key=lambda x: x[1][0][1])
        #initialise all values for reading first word of document
        prev_y_start = -100
        prev_y_end = -100
        prev_y_mid = -100
        mod_ht = abs(res[0][1][0][1] - res[0][1][2][1])
        """
        Algorithm to bring all words in one line if it belongs to same line
        It works best on documents which are not slanted.
        1. For each word check if word falls on a new line, 
            i.e. its start-y is at a distance more than 3/4th of current line's start-y
            1A: If YES, start a new line with new start point, end point and 3/4th point
            1B: If NO, add the word to current line
        """
        for key, values in enumerate(res):
            if values[1][0][1] < prev_y_mid and abs(prev_y_start-values[1][0][1]) <= mod_ht:
                line_list[-1].append([values[0],values[1]])
            else:
                line_list.append([[values[0],values[1]]])
                prev_y_start = values[1][0][1]
                prev_y_end = values[1][2][1]
                prev_y_mid = int(((prev_y_start + prev_y_end) / 2 + prev_y_end)/2)
                line_heights.append(abs(prev_y_start-prev_y_end))
                mod_ht = max(line_heights,key=line_heights.count)
        """
        ALgorithm to sort each line as per its x-axis co-ordinate and also to merge words as per document
        1. For each line do steps 2 to 6:
        2. Sort the line w.r.to start-x of each word on line
        3. For each word on line do steps 4 to 5:
        4. Check if word falls under specific word such as $,|,USD
            4A: If YES, add the word to pop-elements list and continue to next word. (To discard them later)
        5. Check if new word is very close to the previous word,
            i.e. distance between two words is less than max space width
            5A: If YES, check if both word are float or both are characters
                5AA: If No, then add new word as a seperate word
                5AB: If YES, then check if combined word with or without spaces 
                    is present in description given by Google API, and merge the word accordingly.
                5AC: If word doesn't fall in any of above category, add it as a separate word.
            5B: If NO, add the new word a separate word.
        6. For each element in pop-elements list traversed in reverse:
            Remove the element from line. 
            (These words are either merged with some other words or are specific words to be discarded)
        """
        space_lists = []
        decimal_value = False
        compression_level = self.check_rule('Text Compression Level')
        if compression_level == 'Compressed':
            height_wise_multiplier = 1.25
            space_wise_multiplier = 2
        else:
            height_wise_multiplier = 1.5
            space_wise_multiplier = 2.75
        
        for k,line in enumerate(line_list):
            line_list[k] = sorted(line, key=lambda x: x[1][0][0])
            line = line_list[k]
            pop_elements = []
            word_end = 0
            space_width = 0
            if len(space_lists) > 5:
                general_space_width = int(sum(space_lists[-5:])/5)
            else:
                general_space_width = 100

            for w_index,word in enumerate(line):
                print(word)
                if word[0] in ('$','|','USD','(',')','=','>',':'):
                    pop_elements.append(w_index)
                    continue
                #if new word is very close to the previous word
                if abs(word_end - word[1][0][0]) <= space_width:
                    #check word without space
                    d = word_val + word[0]
                    d1 = word_val + ' ' + word[0]
                    if self.is_float_or_int(word_val):
                        if not self.is_float_or_int(word[0]) and word[0] not in (',','.','/','-','–','%'):
                            line_list[k][w_index] = word
                            if general_space_width < (abs(word[1][0][1] - word[1][2][1]) * height_wise_multiplier):
                                space_width = general_space_width
                            else:
                                space_width = abs(word[1][0][1] - word[1][2][1]) * height_wise_multiplier
                            word_end = word[1][2][0]
                            word_val = word[0]
                            prev_index = w_index
                            check_word = word
                            continue
                        if word_val[-1] == '.' and len(word[0]) == 2:
                            space_width = 0
                        #if there is a flost value without any decimal point in between
                        if '.' not in word_val and word[0] not in (',','.','/','-','–','%') and len(word[0]) == 2:
                            d = word_val+'.'+word[0]
                            decimal_value = True
                    if d in desc or decimal_value:
                        decimal_value = False
                        line_list[k][prev_index][0] = d
                        line_list[k][prev_index][1] = [check_word[1][0],word[1][1],word[1][2],check_word[1][3]]
                        #remove current word from line list
                        pop_elements.append(w_index)

                        #if word belongs to column header, no further word should be added in it.
                        col_word = difflib.get_close_matches(d.lower(),self.column_header_flags,cutoff=0.85)
                        if col_word:
                            #if its next word is not a part of this entire word
                            try:
                                if not difflib.get_close_matches(d.lower()+line[w_index+1][0].lower(),self.column_header_flags,cutoff=0.85):
                                    space_width = 0
                            except:
                                space_width = 0
                        """
                        if d[-1] == ':':
                            space_width = 0
                        """

                        word_val = d
                        word_end = word[1][2][0]
                        continue
                    if d1 in desc:
                        line_list[k][prev_index][0] = d1
                        line_list[k][prev_index][1] = [check_word[1][0],word[1][1],word[1][2],check_word[1][3]]
                        #remove current word from line list
                        pop_elements.append(w_index)
                        #if this word is a column header word we should stop adding further words
                        col_word = difflib.get_close_matches(d1.lower(),self.column_header_flags,cutoff=0.85)
                        if col_word:
                            try:
                                #if its next word is not a part of this entire word
                                if not difflib.get_close_matches(d1.lower()+line[w_index+1][0].lower(),self.column_header_flags,cutoff=0.85):
                                    space_width = 0
                                else:
                                    space_width = abs(word_end - word[1][0][0]) * space_wise_multiplier
                                    space_lists.append(space_width)
                            except:
                                space_width = abs(word_end - word[1][0][0]) * space_wise_multiplier
                                space_lists.append(space_width)
                        else:
                            space_width = abs(word_end - word[1][0][0]) * space_wise_multiplier
                            space_lists.append(space_width)
                        word_val = d1
                        word_end = word[1][2][0]
                        continue
                    line_list[k][w_index] = word
                    if general_space_width < (abs(word[1][0][1] - word[1][2][1]) * height_wise_multiplier):
                        space_width = general_space_width
                    else:
                        space_width = abs(word[1][0][1] - word[1][2][1]) * height_wise_multiplier
                    word_end = word[1][2][0]
                    word_val = word[0]
                    prev_index = w_index
                    check_word = word
                else:            
                    line_list[k][w_index] = word
                    if general_space_width < (abs(word[1][0][1] - word[1][2][1]) * height_wise_multiplier):
                        space_width = general_space_width
                    else:
                        space_width = abs(word[1][0][1] - word[1][2][1]) * height_wise_multiplier
                    word_end = word[1][2][0]
                    word_val = word[0]
                    prev_index = w_index
                    check_word = word
            for i in reversed(pop_elements):
                line_list[k].pop(i)
        return line_list

    """
    We assume that horizontal tables would be of three lines, first line for payment components
    second and third line for current and YTD or vice-versa
    """
    def read_horizontal_table(self,lines,l_index,word,probable_list,columns,data_blocks):
        line = lines[l_index]
        w_index = line.index(word)
        final_seq = ''
        for seq in probable_list:
            print(seq)
            col_headers = []
            col_headers.append([word,w_index])
            word_mean = (word[1][0][0] + word[1][1][0])/2
            print(word_mean)
            try:
                temp_l_index = l_index
                temp_l_index = temp_l_index+1
                temp_line = lines[temp_l_index]
                print(temp_line)
                match_found = match_not_found = 0
                for s in range(1,len(seq)):
                    mean_diff = min(enumerate(temp_line),key=lambda x: abs(word_mean - x[1][1][0][0]))
                    try:
                        if self.is_float_or_int(mean_diff[1][0]):
                            temp_w_index = temp_line.index(mean_diff[1])
                            print(temp_line[temp_w_index-1][0])
                            if difflib.get_close_matches(temp_line[temp_w_index-1][0].lower(),[seq[s][0]],cutoff=0.80):
                                col_headers.append([temp_line[temp_w_index-1],temp_w_index-1])
                        else:
                            if difflib.get_close_matches(mean_diff[1][0].lower(),[seq[s][0]],cutoff=0.80):
                                col_headers.append([mean_diff[1],temp_w_index])
                        temp_l_index = temp_l_index+1
                        temp_line = lines[temp_l_index]
                    except:
                        pass
                if len(col_headers) == len(seq):
                    print('We found a sequence',seq)
                    final_seq = seq
                    break
            except Exception as e:
                print(e)
        #If sequence is found look for values and their respective component
        if final_seq:
            paytype_line = lines[l_index]
            print(paytype_line)
            #find current and YTD line based on given types, 
            #   default is 1st Current, 2nd YTD
            try:
                if final_seq[1][1]['col_type'] == 'Current':
                    curr_line = lines[l_index+1]
                    ytd_line = lines[l_index+2]
                elif final_seq[1][1]['col_type'] == 'YTD':
                    ytd_line = lines[l_index+1]
                    curr_line = lines[l_index+2]
            except Exception as e:
                print('first try',e)
                curr_line = lines[l_index+1]
                ytd_line = lines[l_index+2]
            
            #assign block name based on given block name,
            #   default is 'Summary_table'
            try:
                block_name = final_seq[0][1]['block_name']
            except Exception as e:
                print('second try',e)
                block_name = 'Summary_table'

            temp_data_blocks = []
            l2_index = col_headers[1][1]
            l3_index = col_headers[2][1]
            tab_width = (paytype_line[w_index+1][1][0][0] - paytype_line[w_index][1][1][0]) * 1.5
            #for each word in paytype line, look for its respective values
            paytype_end = False
            try:
                for p_index in range(w_index,len(paytype_line)):
                    p_word = paytype_line[p_index]
                    print(p_word)
                    try:
                        if abs(last_word[1][1][0] - p_word[1][0][0]) > tab_width:
                            paytype_end = True
                        last_word = p_word
                    except:
                        last_word = p_word
                    mean_diff = min(enumerate(curr_line),key=lambda x: p_word[1][1][0] - x[1][1][0][0] if p_word[1][1][0] - x[1][1][0][0] >= 0 else float('inf'))
                    if self.is_float_or_int(mean_diff[1][0]) and p_word[1][0][0] < mean_diff[1][1][1][0]:
                        temp_data_blocks.append([p_word[0],self.final_float(mean_diff[1][0]),'Current',block_name])
                    elif paytype_end:
                        print('We need to end this table')
                        break
                    mean_diff = min(enumerate(ytd_line),key=lambda x: p_word[1][1][0] - x[1][1][0][0] if p_word[1][1][0] - x[1][1][0][0] >= 0 else float('inf'))
                    if self.is_float_or_int(mean_diff[1][0]) and p_word[1][0][0] < mean_diff[1][1][1][0]:
                        temp_data_blocks.append([p_word[0],self.final_float(mean_diff[1][0]),'YTD',block_name])
            except Exception as e:
                print(e)

            try:
                #nullify all pay components in first line, also current and ytd col
                update_lines = [lines[l_index],lines[l_index+1],lines[l_index+2]]
                for p_index in range(w_index,len(paytype_line)):
                    if paytype_line[p_index] == last_word:
                        update_lines[0][p_index][0] = 'None'
                        table_end_x = update_lines[0][p_index][1][1][0]
                        break
                    update_lines[0][p_index][0] = 'None'
                
                update_lines[1][l2_index][0] = 'None'
                update_lines[2][l3_index][0] = 'None'
                table_start_x = paytype_line[w_index][1][0][0]
            except Exception as e:
                print('third try',e)
            

            #delete all columns that comes in range of this horizontal table
            #   i.e whose mean is between table start-x and table end-x
            try: 
                pop_cols = []
                for i,x in enumerate(columns):
                    if x[3] > table_start_x and x[3] < table_end_x:
                        print('deleting',x)
                        pop_cols.append(i)
                for i in reversed(pop_cols):
                    columns.pop(i)
            except Exception as e:
                print('Fourth try',e)
            print(temp_data_blocks)
            data_blocks.extend(temp_data_blocks)
            return True, columns, data_blocks, update_lines
        
        return False, columns, data_blocks, None

    def find_column_sequence(self,line,word,probable_list,columns,blocks):
        w_index = line.index(word)
        final_seq = ''
        #for each sequence in probable sequence list, look for matching sequence
        for seq in probable_list:
            print(seq)
            seq_word = difflib.get_close_matches(word[0],[s[0].lower() for s in seq],cutoff=0.80)
            s_index = [s[0] for s in seq].index(seq_word[0])
            print(seq_word,s_index)
            try:
                temp_w_index = w_index
                match_found = match_not_found = 0
                temp_columns = []
                #for each word in sequence, check if it matches word in line
                for s in range(s_index,len(seq)):
                    temp_word = line[temp_w_index]
                    if difflib.get_close_matches(seq[s][0],[temp_word[0].lower()],cutoff=0.75):
                        match_found = match_found + 1
                        try:
                            if line[temp_w_index+1][1][0][0] > temp_word[1][1][0]:
                                if not difflib.get_close_matches(temp_word[0].lower()+line[temp_w_index+1][0].lower(),[t[0] for t in seq[s]],cutoff=0.80):
                                    end_x = line[temp_w_index+1][1][0][0]
                                    temp_w_index = temp_w_index + 1
                                else:
                                    end_x = 0
                            else:
                                end_x = 0
                        except:
                            end_x = 0
                        try:
                            temp_columns.append([temp_word[1][0][0],temp_word[1][0][1],end_x,(temp_word[1][0][0]+temp_word[1][1][0])/2,None,temp_word[0],seq[s][1]['col_type'],abs(temp_word[1][0][1]-temp_word[1][3][1])])
                        except:
                            temp_columns.append([temp_word[1][0][0],temp_word[1][0][1],end_x,(temp_word[1][0][0]+temp_word[1][1][0])/2,None,temp_word[0],None,abs(temp_word[1][0][1]-temp_word[1][3][1])])
                    else:
                        match_not_found = match_not_found + 1
                    temp_w_index = temp_w_index + 1
                seq_confidence = match_found/len(seq)
                if seq_confidence > 0.65:
                    final_seq = seq
                    print('Yes we have found a sequence in this line')
                    break
            except:
                pass
        if final_seq:
            b_index = False
            
            #check for block name in sequence if sequence confidence is above 75
            if seq_confidence > 75:
                for i in final_seq:
                    try:
                        block_name = i[1]['block_name']
                        print(block_name,blocks)
                        #if block name is provided in structure, search for block with this name
                        block_found = difflib.get_close_matches(block_name,[x[0] for x in blocks if x[5] == True],cutoff=0.85)
                        if block_found:
                            print('Found block by name ',block_found[0])
                            block_id = [x for x in blocks if x[5] == True and x[0] == block_found[0]]
                            b_index = blocks.index(block_id[0])
                        #if no such block found, create a new block
                        else:
                            blocks.append([block_name,temp_columns[0][0],temp_columns[0][1],temp_columns[0][3],temp_columns[0][7],True])
                            b_index = len(blocks) - 1
                        break
                    except Exception as e:
                        print(e)

            #if block is not finalised, look for block w.r.to mean distance
            if not b_index:
                #find closest block
                seq_mean = (temp_columns[0][0] + temp_columns[-1][0])/2
                seq_y = temp_columns[0][1]
                try:
                    y_diff = enumerate([x for x in blocks if x[5] == True and abs(x[2] - seq_y) < (3 * x[4])])
                    mean_diff = min(y_diff,key=lambda x: abs(seq_mean - ((x[1][3] * 2) - x[1][1])))
                    print('Block for this sequence is',mean_diff)
                    b_index = blocks.index(mean_diff[1])
                except Exception as e:
                    print(e)

            #delete previous columns, blocking columns and assign b_index to 
            try:
                #delete all columns which belonged to this block
                pop_cols = []
                for i,x in enumerate(columns):
                    if x[4] == b_index:
                        print('deleting',x)
                        pop_cols.append(i)
                for i in reversed(pop_cols):
                    columns.pop(i)

                #delete columns which are being blocked by these new columns
                for i,t in enumerate(temp_columns):
                    temp_columns[i][4] = b_index
                    try:
                        mean_diff = min(enumerate(columns), key=lambda x:abs(x[1][3] - t[3]))
                        mean_width = mean_diff[1][7] * 1.5
                        if abs(mean_diff[1][3]-t[3]) < mean_width or abs(mean_diff[1][0]-word[1][0][0]) < mean_width:
                            print('we are blocking this column',mean_diff[0])
                            columns.pop(mean_diff[0])                            
                    except:
                        pass
                print('Adding new columns in column list',temp_columns)
                columns.extend(temp_columns)
                return True, columns, blocks, final_seq
            except Exception as e:
                print(e)
        return False, columns, blocks, final_seq

    def check_rule(self,rule_name):
        try:
            for sublist in self.rules:
                if sublist[0] == rule_name:
                    return sublist[1]['val']
            return False
        except:
            return False
    
    def get_payslip_amounts(self,lines):
        block_header_flags = self.earning_headers + self.deduction_headers + self.tax_headers + self.other_headers
        
        #define general paytype headers
        general_paytype_headers = ['type','description','pay type']

        extra_paytype_headers = ['rate','hours','hours/units','pay rate','hours/days']
        
        blocks = []
        columns = []

        data_blocks = []
        block_with_headers = self.check_rule('All Blocks With Headers')


        is_star_pre = self.check_rule('Is Star Pre-Tax')
        is_pre_header_defined = self.check_rule('Is TaxType Header Defined')
        prev_component = ''

        #block list = [word,start-x,start-y,mean-x,word_height,status]
        #column_list = [start-x,start-y,end-x,mean-x,block_id,None,Type,Word Height]

        """
        Algorithm to identify blocks of data
        1. For each line do steps from 2 to 3
        2. Deactivate General Paytype header and current flags
        3. For each word in this line do steps from 4 to 7
        4. Check if word belongs to block headers, if yes do steps 4A to 4C
            4A. Add the block with its details.
            4B: Check if block belongs to any of the column above this block.
                (Column should not be associated to any block and column start-x should be greater than block start-x)
                4B(a): If yes, assign this block to all such columns as describe above and goto step 5
            4C: Check if this block is blocking y-axis of any other block which is active
                4C(a): If yes, assign all columns belonging to that block to this block and de-activate that block
        5. Check if word belongs to paytype headers:
            5A: Check if it blongs to general paytype headers:
                5A(a): If yes, activate general paytype header
        6. Check if word belongs to column header, if yes do steps 6A to 6C
            6A: Determine if it belongs to current or YTD based on current flag
            (When current flag is false, column belongs to Current else YTD)
            6B: if column is blocking some other column, de-activate that column
            6C: check if this column belongs to any block by following steps:
                (a): Get all blocks upto 3 lines above this column
                (b): First, find nearest block on left of this column, if found assign column to this block
                (c): If not found, find nearest block on right side.
                6C(a): Delete all previous columns belonging to that block and having type(current/ytd) same as new column
                6C(b): Assign column to this block.
        7. If any column is created already, do following steps:
            7A: Check if word is a float value, If yes, look for the column where it may belong and assign it
            7B: Else, store the word as prev word value.
        8. Return data blocks.
        """
        for l_index,line in enumerate(lines):
            g_pt_header = False
            current_flag = False
            for w_index,word in enumerate(line):                
                mean_x = (word[1][0][0]+word[1][1][0])/2

                #check if word belongs to a horizontal data value pair
                try:
                    seq_word = difflib.get_close_matches(word[0].lower(),[j[0] for j in self.data_val['Horizontal']],cutoff=0.75)
                    if seq_word:
                        print(word[0],line[w_index+1][0])
                        data_blocks.append([word[0],line[w_index+1][0],'Current','General'])
                except:
                    pass

                #check if word belongs to a vertical data value pair
                try:
                    seq_word = difflib.get_close_matches(word[0].lower(),[j[0] for j in self.data_val['Vertical']],cutoff=0.75)
                    if seq_word:
                        possible_word = min(enumerate(lines[l_index+1]), key=lambda x: word[1][1][0] - x[1][1][0][0] if word[1][1][0] - x[1][1][0][0] >= 0 else float('inf'))
                        if possible_word[1][1][1][0] > word[1][0][0]:
                            val = self.is_float(possible_word[1][0])
                            if val:
                                data_blocks.append([word[0],self.final_float(val),'Current','General'])
                except Exception as e:
                    pass

                #check if word belongs to a horizontal table
                try:
                    seq_word = difflib.get_close_matches(word[0].lower(),[j[0] for i in self.vertical_column_sequences for j in i],cutoff=0.80)
                    if seq_word:
                        print('We have got a start of some horizontal table',seq_word)
                        probable_list = []
                        for s in seq_word:
                            print(self.vertical_column_sequences)
                            for i in self.vertical_column_sequences:
                                if s in [j[0] for j in i]:
                                    if i not in probable_list:
                                        probable_list.append(i)
                        status, columns, data_blocks, update_lines = self.read_horizontal_table(lines,l_index,word,probable_list,columns,data_blocks)
                        if status:
                            print('Horizontal Table has been read properly')
                            lines[l_index] = update_lines[0]
                            lines[l_index+1] = update_lines[1]
                            lines[l_index+2] = update_lines[2]
                            continue
                        else:
                            print('No Sequence found, we will continue looking for normal columns')
                except:
                    pass

                #check if word belongs to block headers
                b = difflib.get_close_matches(word[0].lower(),block_header_flags,cutoff=0.90)
                if b:
                    print('\nI am in B',word[0])
                    blocks.append([word[0],word[1][0][0],word[1][0][1],mean_x,abs(word[1][0][1]-word[1][3][1]),True])
                    print(blocks[-1])
                    block_flag = True
                    #check if there is any column upto 3 lines above which this block can be a part of
                    #that column should have its mean-x after block's mean-x
                    try:
                        for i in range(len(columns)):
                            if columns[i][4] == None:
                                if abs(columns[i][1] - word[1][0][1]) < (3 * columns[i][7]) and (columns[i][3] - mean_x) > 0:
                                    columns[i][4] = len(blocks) - 1
                                    block_flag = False
                    except:
                        pass

                    if block_flag:
                        print('It might block someone')
                        #check if block is blocking some other block by using its mean and start x co-ordinates
                        try:
                            mean_diff = min(enumerate([x for x in blocks[0:-1] if x[5] == True]), key=lambda x:abs(x[1][3] - mean_x))
                            mean_width = mean_diff[1][4] * 1.5
                            print(mean_diff)
                            b_index = blocks.index(mean_diff[1])
                            change_block = False
                            #b_index is index of closest block
                            #check if its mean difference or start-x difference is less than certain value
                            if abs(mean_diff[1][3]-mean_x) < mean_width or abs(mean_diff[1][1]-word[1][0][0]) < mean_width:
                                change_block = True
                            #else check if block  mean-x is coming between 
                            # closest block' mean and its respective 'Current' type column's start-x
                            else:
                                for i,x in enumerate(columns):
                                    if x[4] == b_index and x[6] == 'Current' and blocks[-1][3] > blocks[b_index][3] and blocks[-1][3] < x[0]:
                                        change_block = True
                            if change_block:
                                print('we are changing blocks')
                                #assign previous block's columns to new block iff
                                #all blocks doesnt have headers
                                if not block_with_headers:
                                    for i in range(len(columns)):
                                        if columns[i][4] == b_index:
                                            columns[i][4] = len(blocks) - 1
                                blocks[b_index][5] = False
                                print(blocks,columns)
                        except:
                            pass

                #check if word belongs to general paytypes header    
                g = difflib.get_close_matches(word[0].lower(),general_paytype_headers,cutoff=0.80)
                if g:
                    g_pt_header = True
                
                #check if word belongs to column headers
                c = difflib.get_close_matches(word[0].lower(),self.column_header_flags,cutoff=0.80)
                if c:
                    mw_factor = 1
                    print('\nI am in C',word,c)
                    
                    #check if this column is already added in column list, if yes go to next word
                    goto_next_word = False
                    for i in columns:
                        if i[0] == word[1][0][0] and i[1] == word[1][0][1]:
                            goto_next_word = True
                            break
                    if goto_next_word:
                        print('This column is already added by sequence')
                        continue
                    
                    #check if it belongs to any pre-defined sequence
                    try:
                        seq_word = difflib.get_close_matches(word[0],[j[0] for i in self.column_sequences for j in i],cutoff=0.80)
                        if seq_word:
                            print('We have got a start of some sequence(s)',seq_word)
                            probable_list = []
                            for s in seq_word:
                                for i in self.column_sequences:
                                    if s in [j[0] for j in i]:
                                        if i not in probable_list:
                                            probable_list.append(i)
                            status, columns, blocks, final_seq = self.find_column_sequence(line,word,probable_list,columns,blocks)
                            if status:
                                # comment this for a while
                                #self.column_sequences.remove(final_seq)
                                #print('we have deleted col seq')
                                continue
                            else:
                                print('No Sequence found, we will continue looking for normal columns')
                    except Exception as e:
                        print(e)

                    #check if is of type current or ytd
                    if c[0] in self.current_col_flags:
                        col_type = 'Current'
                        check_flag = self.current_col_flags
                    elif c[0] in self.ytd_col_flags:
                        col_type = 'YTD'
                        check_flag = self.ytd_col_flags
                    elif c[0] in self.rate_col_flags:
                        col_type = 'Rate'
                        check_flag = self.rate_col_flags
                    elif c[0] in self.hour_col_flags:
                        col_type = 'Hour'
                        check_flag = self.hour_col_flags
                    else:
                        check_flag = self.other_col_flags
                        if not current_flag:
                            current_flag = True
                            g_pt_header = False
                            col_type = 'Current'
                        else:
                            if g_pt_header:
                                col_type = 'Current'
                                g_pt_header = False
                            else:
                                col_type = 'YTD'
                        #must deactivate Current or YTD column just above this, increase mw_factor
                        mw_factor = 6


                    try:
                        if line[w_index+1][1][0][0] > word[1][1][0]:
                            if not difflib.get_close_matches(word[0]+line[w_index+1][0],check_flag,cutoff=0.80):
                                 end_x = line[w_index+1][1][0][0]
                            else:
                                end_x = 0
                        else:
                            end_x = 0
                    except:
                        end_x = 0
                    columns.append([word[1][0][0],word[1][0][1],end_x,mean_x,None,word[0],col_type,abs(word[1][0][1]-word[1][3][1])])
                    
                    
                    #check if it is blocking some other column headers, if yes deactivate that column
                    try:
                        mean_diff = min(enumerate(columns[0:-1]), key=lambda x:abs(x[1][3] - mean_x))
                        mean_width = mean_diff[1][7] * 1.5 * mw_factor
                        if abs(mean_diff[1][3]-mean_x) < mean_width or abs(mean_diff[1][0]-word[1][0][0]) < mean_width:
                            #columns[mean_diff[0]][6] = False
                            columns.pop(mean_diff[0])
                            print('We are blocking this column',mean_diff[0])
                    except:
                        pass
                    
                    #check the block where this column belongs to, 
                    #look for upto 3 lines of document above this column as per column height
                    try:
                        y_diff = enumerate([x for x in blocks if x[5] == True and abs(x[2] - word[1][0][1]) < (3 * x[4])])
                        try:
                            mean_diff = min(y_diff,key=lambda x: word[1][0][0] - x[1][1] if word[1][0][0] - x[1][1] > 0 else float('inf'))
                        except:
                            mean_diff = min(y_diff,key=lambda x: x[1][1] - word[1][0][0] if x[1][1] - word[1][0][0] >= 0 else float('inf'))
                        print('Block where this column belongs to is', mean_diff)
                        b_index = blocks.index(mean_diff[1])
                        columns[-1][4] = b_index
                        print(blocks,columns)
                        
                        #DELETE COLUMNS IF THERE ARE MORE THAN ONE FOR SAME BLOCK SAME TYPE
                        del_columns = []
                        num_cols = sum(1 for x in columns if x[4] == b_index and x[6] == columns[-1][6])
                        if num_cols > 1:
                            print('We might have to delete some column')
                            c_block = enumerate([x for x in columns if x[4] == b_index and x[6] == columns[-1][6]])
                            try:
                                mean_diff = min(c_block,key=lambda x: x[1][0] - blocks[b_index][1] if x[1][1] > blocks[b_index][2] else float('inf'))
                                if not mean_diff[1][1] > (blocks[b_index][2] + blocks[b_index][4]/2):
                                    raise Exception('Go to exception')
                            except:
                                print('we are in except')
                                c_block = enumerate([x for x in columns if x[4] == b_index and x[6] == columns[-1][6]])
                                mean_diff = min(c_block,key=lambda x: x[1][0] - blocks[b_index][1] if x[1][0] != blocks[b_index][1] else float('inf'))
                            print(mean_diff,mean_diff[1][0],mean_diff[1][1],b_index,columns[-1][6])
                            pop_cols = []
                            for i,x in enumerate(columns):
                                if x[4] == mean_diff[1][4] and x[6] == mean_diff[1][6] and (x[0] != mean_diff[1][0] or x[1] != mean_diff[1][1]) and x[5] != mean_diff[1][5]:
                                    print('deleting',x)
                                    pop_cols.append(i)
                            for i in reversed(pop_cols):
                                columns.pop(i)
                            print(blocks,columns)
                    except Exception as e:
                        print(e)
                        #No blocks have been created yet.
                        #pass
                    prev_word = c[0]
                    prev_word_details = word
                    continue
                    #check the paytype where this column belongs to

                #if columns are created, start looking for float values
                if columns:
                    val = self.is_float(word[0])
                    if val:
                        try:
                            next_word = line[w_index+1][0]
                            if next_word == '*':
                                val = '*'+str(val)
                        except:
                            pass
                        for i, e in reversed(list(enumerate(columns))):
                            if word[1][1][0] > columns[i][3] and (word[1][1][0] <= columns[i][2] or columns[i][2] == 0):
                                #if block of this column is deactivated, no need to read values
                                try:
                                    if not blocks[columns[i][4]][5]:
                                        break
                                except:
                                    pass
                                if columns[i][2] == 0:
                                    if abs(columns[i][3] - word[1][0][0]) <= (3 * columns[i][7] * 1.5):
                                        columns[i][2] = word[1][1][0] + (3 * columns[i][7] * 1.5)
                                    try:
                                        print('-----**-----',prev_word,val,columns[i][6],blocks[columns[i][4]])
                                        data_blocks.append([prev_word,self.final_float(val,columns[i][6]),columns[i][6],blocks[columns[i][4]][0]])
                                    except:
                                        print('-----**-----',prev_word,val,columns[i][6])
                                        data_blocks.append([prev_word,self.final_float(val,columns[i][6]),columns[i][6],'Undefined'])
                                else:
                                    try:
                                        print('-----**-----',prev_word,val,columns[i][6],blocks[columns[i][4]])
                                        data_blocks.append([prev_word,self.final_float(val,columns[i][6]),columns[i][6],blocks[columns[i][4]][0]])
                                    except:
                                        print('-----**-----',prev_word,val,columns[i][6])
                                        data_blocks.append([prev_word,self.final_float(val,columns[i][6]),columns[i][6],'Undefined'])

                                #identify type of deduction if there is any defined
                                if prev_word == prev_component:
                                    if identified_block:
                                        #assign identified block to this data block
                                        data_blocks[-1][3] = identified_block
                                    break
                                else:
                                    prev_component = prev_word
                                    identified_block = False
                                    dh = difflib.get_close_matches(data_blocks[-1][3].lower(),self.deduction_headers,cutoff=0.90)
                                    if dh:
                                        nh = difflib.get_close_matches(data_blocks[-1][3].lower(),self.normal_deduction_headers,cutoff=0.90)
                                        if nh:
                                            #code to find 'Total' pay component
                                            if difflib.get_close_matches(data_blocks[-1][0].lower(),['total','total '+data_blocks[-1][3].lower(),data_blocks[-1][3].lower()],cutoff=0.80):
                                                data_blocks[-1][0] = 'Total'
                                                prev_component = 'Total'
                                            elif "total" in data_blocks[-1][0].lower():
                                                data_blocks[-1][0] = 'Total'
                                                prev_component = 'Total'

                                            #code for identifying pre and post based on star or header
                                            if is_star_pre:
                                                #if star pre tax apply this rule
                                                if data_blocks[-1][0].find('*') != -1 or data_blocks[-1][1].find('*') != -1:
                                                    identified_block = 'Pre Tax Deductions'
                                                    data_blocks[-1][0] = data_blocks[-1][0].replace('*','')
                                                    data_blocks[-1][1] = data_blocks[-1][0].replace('*','')
                                                else:
                                                    identified_block = 'Post Tax Deductions'
                                                data_blocks[-1][3] = identified_block
                                                break
                                            elif is_pre_header_defined:
                                                try:
                                                    pc_index = line.index(prev_word_details)
                                                    for i in range(pc_index+1,len(line)):
                                                        if line[i][0].lower() in ['yes','b','pre']:
                                                            identified_block = 'Pre Tax Deductions'
                                                            break
                                                        elif line[i][0].lower() in ['no','a','post']:
                                                            identified_block = 'Post Tax Deductions'
                                                            break
                                                    if identified_block:
                                                        data_blocks[-1][3] = identified_block
                                                        break
                                                except:
                                                    pass
                                        else:
                                            if difflib.get_close_matches(data_blocks[-1][3].lower(),self.pre_deduction_headers,cutoff=0.90):
                                                identified_block = 'Pre Tax Deductions'
                                            else:
                                                identified_block = 'Post Tax Deductions'
                                            data_blocks[-1][3] = identified_block
                                            break
                                        #code for identifying pre and post based on name if found
                                        if data_blocks[-1][0].lower().find('pre') != -1:
                                            identified_block = 'Pre Tax Deductions'
                                        else:
                                            identified_block = 'Post Tax Deductions'
                                        data_blocks[-1][3] = identified_block
                                        break
                                    break
                    else:
                        if self.is_pay_component(word[0]):
                            prev_word = word[0]
                            prev_word_details = word
                            #check if it is blocking some column headers, if yes deactivate that column
                            try:
                                #if component contains any digit, do not block columns
                                if bool(re.search(r'\d', prev_word)):
                                    #continue to next word
                                    continue
                                pop_cols = []
                                for i,x in enumerate(columns):
                                    if x[3] > word[1][0][0] and x[3] < word[1][1][0]:
                                        pop_cols.append(i)
                                for i in reversed(pop_cols):
                                    print('word ',word[0],' is blocking this column ',columns[i])
                                    columns.pop(i)
                            except:
                                pass
        print(blocks)
        print(columns)
        return data_blocks

    def read_data_dict(self,val_name):
        print(val_name)
        data_def = {
            'post_deduction_total_auto':['Post Tax Deductions','Total'],
            'pre_deduction_total_auto':['Pre Tax Deductions','Total'],
            'tax_total_auto':['Taxes','Total']
            }
        try:
            return data_def[val_name]
        except:
            return False

    def create_blocks(self,data_blocks):
        print(data_blocks)

        net_columns = ['net pay','total net','net earnings']
        gross_columns = ['gross pay','total gross','gross earnings','gross','total gross earnings']
        other_columns = ['checking ','net check','checkng','Chck1',
                        'savings','direct deposit','dir dip check',
                        'your federal taxable wages this period','federal taxable wages']
        final_data = {'Net Pay':[],'Gross Pay':[],'Earnings':[],'Pre Tax Deductions':[],'Post Tax Deductions':[],'Taxes':[],'Others':[]}
        
        prev_word = ''
        prev_block = ''
        temp_rate = temp_hour = ''
        temp_rate_val = temp_hour_val = 0.00
        
        for i,db in enumerate(data_blocks):
            #finalize block name based on column name or block name
            pc = difflib.get_close_matches(db[0].lower(),net_columns+gross_columns+other_columns,cutoff=0.85)
            if pc:
                if pc[0] in net_columns:
                    block_name = 'Net Pay'
                elif pc[0] in gross_columns:
                    block_name = 'Gross Pay'
                else:
                    block_name = 'Others'
            else:
                bn = difflib.get_close_matches(db[3].lower(),self.earning_headers+self.tax_headers+['pre tax deductions','post tax deductions'],cutoff=0.80)
                if bn:
                    if bn[0] in ['pre tax deductions','post tax deductions']:
                        block_name = db[3]
                    elif bn[0] in self.earning_headers:
                        block_name = 'Earnings'
                    elif bn[0] in self.tax_headers:
                        block_name = 'Taxes'
                else:
                    block_name = 'Others'
            
            if block_name == 'Others':
                summary_word = difflib.get_close_matches(db[0].lower(),[s[0].lower() for s in self.data_dict],cutoff=0.85)
                if summary_word:
                    s_index = [s[0] for s in self.data_dict].index(summary_word[0])
                    [bn, cn] = self.read_data_dict(self.data_dict[s_index][1]['col'])
                    db[0] = cn
                    block_name = bn
                else:
                    block_name = 'Others'

            #finalize column name based on column name and block name
            if difflib.get_close_matches(db[0].lower(),['total','total '+db[3].lower(),db[3].lower()],cutoff=0.80):
                db[0] = 'Total'
            elif "total" in db[0].lower():
                db[0] = 'Total'
            
            if db[2] == 'Rate':
                temp_rate = db[0]
                temp_rate_val = db[1]
            elif db[2] == 'Hour':
                temp_hour = db[0]
                temp_hour_val = db[1]
            elif db[2] == 'Current':
                final_data[block_name].append([db[0],db[1],'','',''])
                prev_word = db[0]
                prev_block = block_name
                if prev_word == temp_rate:
                    final_data[block_name][-1][3] = temp_rate_val
                    temp_rate = ''
                if prev_word == temp_hour:
                    final_data[block_name][-1][4] = temp_hour_val
                    temp_hour = ''
            elif db[2] == 'YTD':
                if db[0] == prev_word and block_name == prev_block:
                    final_data[block_name][-1][2] = db[1]
                    prev_word = ''
                    prev_block = ''
                else:
                    final_data[block_name].append([db[0],'',db[1],'',''])
        for x in final_data:
            if x in ['Pre Tax Deductions','Post Tax Deductions','Taxes','Earnings']:
                cal_cur = 0
                cal_ytd = 0
                for dt in final_data[x]:
                    if dt[0] != 'Total':
                        try:
                            if dt[1].find('+') != -1:
                                cal_cur = cal_cur - float(dt[1])
                            else:
                                cal_cur = cal_cur + float(dt[1])
                        except:
                            pass
                        try:
                            cal_ytd = cal_ytd + float(dt[2])
                        except:
                            pass
                final_data[x].append(['Total_Calculated',"{:.2f}".format(cal_cur),"{:.2f}".format(cal_ytd),'','']) 
        if len(final_data['Net Pay']) > 1:
            pop_elements = []
            for i in final_data['Net Pay']:
                if i[1] != '' and i[2] != '':
                    final_data['Net Pay'] = [i]
                    break
        if len(final_data['Net Pay']) == 1:
            final_data['Net Pay'][0][0] = 'Net Pay'
            final_data['Net Pay'][0][1] = self.final_float(final_data['Net Pay'][0][1])
            final_data['Net Pay'][0][2] = self.final_float(final_data['Net Pay'][0][2])
        if len(final_data['Gross Pay']) > 1:
            pop_elements = []
            for i in final_data['Gross Pay']:
                if i[1] != '' and i[2] != '':
                    final_data['Gross Pay'] = [i]
                    break
        if len(final_data['Gross Pay']) == 1:
            final_data['Gross Pay'][0][0] = 'Gross Pay'
            final_data['Gross Pay'][0][1] = self.final_float(final_data['Gross Pay'][0][1])
            final_data['Gross Pay'][0][2] = self.final_float(final_data['Gross Pay'][0][2])
        elif len(final_data['Gross Pay']) == 0:
            try:
                for lt in final_data['Earnings']:
                    print(lt,lt[0])
                    if lt[0] == 'Total':
                        print('here')
                        final_data['Gross Pay'] = [['Gross Pay',lt[1],lt[2],'','']]
                        break
            except:
                pass
        return final_data

    def get_text(self,path,img=False):
        client = vision.ImageAnnotatorClient()
        ext = path.split('.')[-1]
        if not img:
            img = Image.open(path)
        try:
            if hasattr(img, '_getexif'): # only present in JPEGs
                for orientation in ExifTags.TAGS.keys(): 
                    if ExifTags.TAGS[orientation]=='Orientation':
                        break 
                e = img._getexif()       # returns None if no EXIF data
                if e is not None:
                    exif=dict(e.items())
                    orientation = exif[orientation] 

                    if orientation == 3:
                        print('transpose 3')
                        img = img.transpose(Image.ROTATE_180)
                    elif orientation == 6:
                        print('transpose 6')
                        img = img.transpose(Image.ROTATE_270)
                    elif orientation == 8:
                        print('transpose 8')
                        img = img.transpose(Image.ROTATE_90)
        except:
            print('we are here')
            pass
        b = io.BytesIO()
        if ext.lower() in ('png'):
            save_ext = 'PNG'
        elif ext.lower() in ('jpg','jpeg'):
            save_ext = 'JPEG'
        img.save(b, save_ext)
        content = b.getvalue()

        image = types.Image(content=content)
        
        #if 'Pay Stub' in doc_type:
        #response = client.text_detection(image=image)
        #else:
        response = client.document_text_detection(image=image)
        #texts = response.full_text_annotation
        # response = client.text_detection(image=image)
        texts = response.text_annotations
        self.description = texts[0]
        for text in texts[1:]:

            self.text_val.append(text.description)
            vertices = [(vertex.x, vertex.y)
                        for vertex in text.bounding_poly.vertices]
            self.keys.append(text.description)
            self.values.append(vertices)
        self.result=zip(self.keys, self.values)
        data = " ".join(map(str, self.text_val))
        return data

    def get_paystub_type(self,paystub_types):
        lookups = [j for x in paystub_types for j in paystub_types[x]]
        if not lookups:
            return 'Generic'
        lookup_string = lookups[0]
        for i in range(1,len(lookups)):
            lookup_string = lookup_string+'|'+lookups[i]
        val = re.compile(r'\b(!?'+lookup_string+r')\b', re.IGNORECASE)
        lookup_found = val.findall(self.description.description)
        if lookup_found:
            for pt in paystub_types:
                if lookup_found[0] in paystub_types[pt]:
                    print('Paystub Type Found',pt)
                    return pt
        return 'Generic'

    def get_structure(self,root,all_headers,paystub_type):
        for item in root.findall('./paystub'):
            if item.attrib.get('id') == paystub_type:
                paystub_structure = item
                break
        for table in paystub_structure.findall('./'):
            if table.tag in ['block_headers','col_headers']:
                all_headers[table.tag] = {}
                for val_type in table.findall('./'):
                    type_id = val_type.attrib.get('id')
                    all_headers[table.tag][type_id] = []
                    for vals in val_type.findall('./'):
                        all_headers[table.tag][type_id].append(vals.text)
            elif table.tag in ['col_sequence','vertical_col_sequence']:
                all_headers[table.tag] = []
                for val_type in table.findall('./'):
                    all_headers[table.tag].append([])
                    for vals in val_type.findall('./'):
                        try:
                            all_headers[table.tag][-1].append([vals.text,vals.attrib])
                        except:
                            all_headers[table.tag][-1].append([vals.text,None])
            elif table.tag in ['data_val']:
                all_headers[table.tag] = {}
                for val_type in table.findall('./'):
                    type_id = val_type.attrib.get('id')
                    all_headers[table.tag][type_id] = []
                    for vals in val_type.findall('./'):
                        try:
                            all_headers[table.tag][type_id].append([vals.text,vals.attrib])
                        except:
                            all_headers[table.tag][type_id].append([vals.text,None])
            elif table.tag in ['data_dict']:
                all_headers[table.tag] = []
                for val_type in table.findall('./'):
                    all_headers[table.tag].append([val_type.text,val_type.attrib])
            else:
                all_headers['rules'] = []
                for val_type in table.findall('./'):
                    all_headers['rules'].append([val_type.text,val_type.attrib])
        return all_headers

    def remove_dotted_band(self,path):
        img = cv2.imread(sys.argv[1], 0)
        _, blackAndWhite = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, 4, cv2.CV_32S)
        sizes = stats[1:, -1] #get CC_STAT_AREA component
        img2 = np.zeros((labels.shape), np.uint8)

        for i in range(0, nlabels - 1):
            if sizes[i] >= 8:   #filter small dotted regions
                img2[labels == i + 1] = 255

        res = cv2.bitwise_not(img2)
        cv2.imwrite('res.jpg', res)
        pilImage = Image.fromarray(res)
        return pilImage

    def paystub_details(self,path):
        #get text data from GCV
        text_output_data = self.get_text(path)

        #parse tree and get root element
        tree = ElementTree.parse('struct.xml')
        root = tree.getroot()
        paystub_structs = []
        for item in root.findall('./paystub'):
            paystub_structs.append(item.attrib.get('id'))

        #get all headers from Generic structure
        all_headers = {}
        all_headers = self.get_structure(root,all_headers,'Generic')

        #read all structure types and their lookup texts
        paystub_types = {}
        for item in root.findall('./paystub_types/'):
            type_id = item.attrib.get('id')
            paystub_types[type_id] = []
            for lookups in item.findall('./'):
                paystub_types[type_id].append(lookups.text)

        #get paystub type based on text
        paystub_type = self.get_paystub_type(paystub_types)
        if paystub_type != 'Generic':
            all_headers = self.get_structure(root,all_headers,paystub_type)

        """
        if paystub_type == 'ADP':
            clear_image = self.remove_dotted_band(path)
            self.result={}
            self.text_val=[]
            self.keys=[]
            self.values=[]
            self.description = []
            text_output_data = self.get_text(path,clear_image)
        """

        #initilize structure to read paystub
        self.init_structure(all_headers)

        #convert raw data into line-wise structured data
        lines = self.rectify_data()
        for line in lines:
            print(line)

        #get data blocks
        data_blocks = self.get_payslip_amounts(lines)

        #get output data from data blocks
        final_data = self.create_blocks(data_blocks)
        print(final_data)
        return final_data,text_output_data

"""
To run this program manually.
"""
pt = paystub_gcv()
x,y = pt.paystub_details(sys.argv[1])
print(x,y)