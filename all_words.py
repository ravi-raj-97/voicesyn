all_w = "the you and it a 's to of that in we is do they er was yeah have but for on this know well so oh got if with " \
        "she at there think just can would mm them up now about me very out my mean right which people like really other" \
        " something actually take those only into us quite hundred again used mhm ah never point eight new big after " \
        "today even ooh aye job children area obviously idea aha eh saw around situation change boy usually changed wish" \
        " oil garage ee oi zero oops"

s_list = ['aha eh ee oi ah ooh mm er mhm aye',
          'oh there are around a hundred children in the area',
          'oops you never saw me even if it was mean',
          'something has obviously changed with us',
          'people usually change job very often and quit',
          'she was really quite today only',
          'he used zero of my idea but gave credit',
          'at this point we have to take the right decision',
          'do they know which out of those is new',
          'so think about the situation after that',
          'yeah just wish them again at the end',
          'actually the other eight got up on time',
          'for now the homeless boy would like us',
          'we put big can of garage oil into the well']


all_w_set = set(all_w.split(' '))
s_list_set = set()


file = open('split.txt', "r")
word_dicts = []
diphone_dict = {}
for line in file:
    line = line.strip()
    if diphone_dict.get(line.split(" ")[0], None):
        print('repeated', line.split(" ")[0])
    diphone_dict[line.split(" ")[0]] = line.split(" ")[2:]

all_possible_diphones = set()
all_generated = set()

for key in diphone_dict.keys():
    for sound in diphone_dict[key]:
        all_possible_diphones.add(sound)

print(len(all_possible_diphones))

for word in all_w_set:
    for sound in diphone_dict[word]:
        all_generated.add(sound)
print(len(all_generated))

print(all_possible_diphones-all_generated)