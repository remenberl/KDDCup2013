from name import *
from precision_related import *
from custom_setting import *
import cPickle
from io import *

def claim(name_instance_A, name_instance_B, expected_result, strict_mode=True):
    if expected_result == name_comparable(name_instance_A,name_instance_B, name_statistics, strict_mode):
        print "Yes. Expected result: " + str(expected_result) + "; '" + name_instance_A.name + "' v.s. '" + name_instance_B.name + "' passed."
    else:
        print "No. Expected result: " + str(expected_result) + "; '" + name_instance_A.name + "' v.s. '" + name_instance_B.name + "' has not passed."

name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))


name_instance_A = Name('Yeong C. Kim')
name_instance_B = Name('Chonggun Kim')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Hong-Hu Zhu')
name_instance_B = Name('H. H. Zhu')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Paul M. Chen')
name_instance_B = Name('Peter M. Chen')
claim(name_instance_A, name_instance_B, False)

name_instance_A = Name('Xiang Li')
name_instance_B = Name('Xiang Lin')
claim(name_instance_A, name_instance_B, False)

name_instance_A = Name('Jun S. Liu')
name_instance_B = Name('Jundong Liu')
claim(name_instance_A, name_instance_B, False)

name_instance_A = Name('Ralph Mac Nally')
name_instance_B = Name('RalphMac Nally')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Jeremy J. Dahl')
name_instance_B = Name('Jeffrey Dahl')
claim(name_instance_A, name_instance_B, False)

name_instance_A = Name('Ken Wing Kuen Lee')
name_instance_B = Name('Kai-fu Lee')
claim(name_instance_A, name_instance_B, False)

name_instance_A = Name('Ruppert R. Koch')
name_instance_B = Name('Reinhard Koch')
claim(name_instance_A, name_instance_B, False)


name_instance_B = Name('V. P. Voloshin')
name_instance_A = Name('Vitaly I. Voloshin')
claim(name_instance_A, name_instance_B, False)

name_instance_B = Name('V. Scott Gordont')
name_instance_A = Name('V. Scott Gordon')
claim(name_instance_A, name_instance_B, True)

name_instance_B = Name('Ji-Hun Bae')
name_instance_A = Name('Jinsoo Bae')
claim(name_instance_A, name_instance_B, False)

name_instance_B = Name('Joao Coelho Garcia')
name_instance_A = Name('Juan Carlos Garcia Garcia')
claim(name_instance_A, name_instance_B, False)

name_instance_B = Name('Eric Vatikiotis-Bateson')
name_instance_A = Name('E. V-bateson')
claim(name_instance_A, name_instance_B, True)

name_instance_B = Name('V. P. Voloshin')
name_instance_A = Name('Vitaly I. Voloshin')
claim(name_instance_A, name_instance_B, False)

name_instance_B = Name('Joon S. Lim')
name_instance_A = Name('Joonhong Lim')
claim(name_instance_A, name_instance_B, False)

name_instance_B = Name('Jeffrey Naughton')
name_instance_A = Name('Jeffrey F. Naughton')
claim(name_instance_A, name_instance_B, True)

name_instance_B = Name('Jun-Hyuk Seo')
name_instance_A = Name('Jung-Hun Seo')
claim(name_instance_A, name_instance_B, False)

name_instance_A = Name('M. H. Kahae')
name_instance_B = Name('M. Hossein Kahaei')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('M. H. Kahae')
name_instance_B = Name('Mohammad Hossein Kahaei')
claim(name_instance_A, name_instance_B, True)


name_instance_A = Name('Ketan Mulmuley')
name_instance_B = Name('Ketan Mulmuley I')
claim(name_instance_A, name_instance_B, True)
# print my_string_match_score(name_instance_A.name, name_instance_B.name)

name_instance_A = Name('Jeff W. Hughes')
name_instance_B = Name('Jeffrey W. Hughes')
claim(name_instance_A, name_instance_B, True)


name_instance_A = Name('William Hughes')
name_instance_B = Name('Bill W. Hughes')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('William Hughes')
name_instance_B = Name('B Hughes')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('J. O. Daramola')
name_instance_B = Name('Olawande J. Daramola ')
claim(name_instance_A, name_instance_B, True, False)
# print name_comparable(name_instance_A,name_instance_B)
name_instance_A = Name('Giselle D. Carnaby')
name_instance_B = Name('Giselle Carnaby-Mann')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Gregory A. Margulis')
name_instance_B = Name('Gregori Aleksandrovich Margulis')
claim(name_instance_A, name_instance_B, True, False)

name_instance_A = Name('Martien Janssen')
name_instance_B = Name('Maarten C. W. Janssen')
claim(name_instance_A, name_instance_B, True, False)

name_instance_A = Name('Shankar Sundaresan')
name_instance_B = Name('Sankaran Sundaresan')
claim(name_instance_A, name_instance_B, False, False)

name_instance_A = Name('Yuriy Yu. Tarasevich')
name_instance_B = Name('Yuri Yu. Tarasevich')
claim(name_instance_A, name_instance_B, True, False)

name_instance_A = Name('Peter J. Funk')
name_instance_B = Name('Petra Funk')
claim(name_instance_A, name_instance_B, True, False)

name_instance_A = Name('Jie Chenl')
name_instance_B = Name('Jie Chen')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Jie Chenld')
name_instance_B = Name('Jie Chenla')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Hong-Jiang Zhangt')
name_instance_B = Name('Hongjiang Zhang')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Wen-Jye Yen')
name_instance_B = Name('Wen Jye Yen')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Anders Moeller')
name_instance_B = Name('Anders Moller')
claim(name_instance_A, name_instance_B, True)

name_instance_A = Name('Nasser Nemat-Bakhash')
name_instance_B = Name('Naser Nematbakhsh')
claim(name_instance_A, name_instance_B, True)


name_instance_A = Name('Valli Kumari Vatsavayi')
name_instance_B = Name('V. Valli Kumari')
claim(name_instance_A, name_instance_B, True)
# if single_name_comparable(name_instance_A, name_instance_B):
#     print True

# name_A = '- '.join([name_instance_A.last_name, name_instance_A.middle_name, name_instance_A.first_name]).strip()
# new_name_instance_A = Name(name_A)
# new_name_instance_A.is_asian = name_instance_A.is_asian
# if single_name_comparable(new_name_instance_A, name_instance_B):
#     print True

# name_A = '- '.join([name_instance_A.middle_name, name_instance_A.last_name, name_instance_A.first_name]).strip()
# new_name_instance_A = Name(name_A)
# new_name_instance_A.is_asian = name_instance_A.is_asian
# if single_name_comparable(new_name_instance_A, name_instance_B):
#     print True

# name_A = '- '.join([name_instance_A.last_name, name_instance_A.first_name, name_instance_A.middle_name]).strip()
# new_name_instance_A = Name(name_A)
# new_name_instance_A.is_asian = name_instance_A.is_asian
# if single_name_comparable(new_name_instance_A, name_instance_B):
#     print True

# name_A = '- '.join([name_instance_A.middle_name, name_instance_A.first_name, name_instance_A.last_name]).strip()
# new_name_instance_A = Name(name_A)
# new_name_instance_A.is_asian = name_instance_A.is_asian
# if single_name_comparable(new_name_instance_A, name_instance_B):
#     print True

# name_A = '- '.join([name_instance_A.first_name, name_instance_A.last_name, name_instance_A.middle_name]).strip()
# new_name_instance_A = Name(name_A)
# new_name_instance_A.is_asian = name_instance_A.is_asian
# if single_name_comparable(new_name_instance_A, name_instance_B):
#     print True





# name_A = name_instance_A.name
# name_B = name_instance_B.name

# if name_instance_A.is_asian and name_instance_B.is_asian:
#     # Han Liu and Huan Liu
#     if name_instance_A.middle_name == '' and name_instance_B.middle_name == '':
#         if len(name_instance_A.first_name) > 1 and len(name_instance_B.first_name) > 1:
#             if name_instance_A.first_name != name_instance_B.first_name:
#                 print "1" + "False"
#     # Han Liu  and H. L. Liu
#     if len(name_instance_A.first_name) == 1 and len(name_instance_A.middle_name) == 1:
#         if not is_substr(name_A.replace(' ', ''), name_B):
#              print "2" +  "False"
#     if len(name_instance_B.first_name) == 1 and len(name_instance_B.middle_name) == 1:
#         if not is_substr(name_A, name_B.replace(' ', '')):
#              print "3" +  "False"
#     # Lin Yu, Lin Yi
#     if name_instance_A.last_name != name_instance_B.last_name:
#          print "4" +  "False"

# if name_B.find(name_A.replace(' ', '')) >= 0 or name_A.find(name_B.replace(' ', '')) >= 0:
#      print "5" +  "True"

# if name_A.replace(' ', '') == name_B.replace(' ', ''):
#      print "6" +  "True"

# # if is_substr(name_A.replace(' ', ''), name_B.replace(' ', '')) and len(name_A) > 10 and len(name_B) > 10:
# #     return True
# if (name_instance_A.first_name, name_instance_B.first_name) not in nickname_set:
#     if not is_substr(name_instance_A.initials, name_instance_B.initials):
#          print "7" +  "False"
# else:
#     if not is_substr(name_instance_A.initials[1:], name_instance_B.initials[1:]):
#          print "8" +  "False"

# # Chris Ding and Cui Ding
# if len(name_instance_A.first_name) > 1 and len(name_instance_B.first_name) > 1:
#     if name_instance_A.first_name[0] == name_instance_B.first_name[0]:
#         if (name_instance_A.first_name, name_instance_B.first_name) not in nickname_set:
#             if (name_instance_A.first_name.find(name_instance_B.first_name) < 0 and name_instance_A.first_name.find(name_instance_B.first_name) < 0) \
#                     or (name_instance_A.middle_name == '' and name_instance_B.middle_name == ''):
#                 if not name_instance_A.bad_name_flag and not name_instance_B.bad_name_flag:
#                     if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.first_name[1:]).ratio() < 0.93:
#                          print "9" +  "False"
#                 else:
#                     if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.first_name[1:]).ratio() < 0.5:
#                          print "10" +  "False"

# # Michael Ia Jordan and Michael Ib jordan
# if len(name_instance_A.middle_name) > 1 and len(name_instance_B.middle_name) > 1:
#     if name_instance_A.middle_name[0] == name_instance_B.middle_name[0]:
#         if not is_substr(name_instance_A.middle_name.replace(' ', ''), name_instance_B.middle_name.replace(' ', '')):
#             if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.middle_name[1:]).ratio() <= 0.3:
#                  print "11" +  "False"

# if len(name_instance_A.last_name) > 1 and len(name_instance_B.last_name) > 1:
#     if name_instance_A.last_name[0] == name_instance_B.last_name[0]:
#         if not is_substr(name_instance_A.last_name.replace(' ', ''), name_instance_B.last_name.replace(' ', '')):
#             if SequenceMatcher(None, name_instance_A.last_name[1:], name_instance_B.last_name[1:]).ratio() < 0.5:
#                  print "12" +  "False"

#     # if len(name_instance_A.last_name) > 1 and len(name_instance_B.last_name) > 1:
#     #     if name_instance_A.last_name[0] == name_instance_B.last_name[0]:
#     #         if not is_substr(name_instance_A.last_name.replace(' ', ''), name_instance_B.last_name.replace(' ', '')):
#     #             if SequenceMatcher(None, name_instance_A.last_name[1:], name_instance_B.last_name[1:]).ratio() < 0.5:
#     #                 return False

# if name_instance_A.first_name[0] != name_instance_B.first_name[0]:
#     if len(name_instance_B.middle_name) > 0:
#         if name_instance_A.first_name[0] == name_instance_B.middle_name[0]:
#             if len(name_instance_A.first_name) > 1 and len(name_instance_B.middle_name) > 1:
#                 if my_string_match_score(name_instance_A.first_name, name_instance_B.middle_name) == 0:
#                     print "13" +  "False"
#                 # if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.middle_name[1:]).ratio() <= 0.9:
#                 #         return False
#     if len(name_instance_A.middle_name) > 0:
#         if name_instance_B.first_name[0] == name_instance_A.middle_name[0]:
#             if len(name_instance_B.first_name) > 1 and len(name_instance_A.middle_name) > 1:
#                 if my_string_match_score(name_instance_A.middle_name, name_instance_B.first_name) == 0:
#                     # if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.first_name[1:]).ratio() <= 0.9:
#                     print "14" +  "False"

# if name_instance_A.last_name != name_instance_B.last_name:
#     if SequenceMatcher(None, name_instance_A.last_name[1:], name_instance_B.last_name[1:]).ratio() <= 0.5:
#         print "15" +  "False"
#     if name_instance_A.middle_name != name_instance_B.middle_name and name_instance_A.first_name != name_instance_B.first_name:
#         print "16" +  "False"