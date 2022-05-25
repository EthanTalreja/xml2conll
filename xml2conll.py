from xml.dom import minidom
import argparse
import nltk


#! Create file
def bio_formatting(word,tags,entities):
    if word in entities:
        for value in tags.values():
            if type(value[1]) == str and value[1] == word:
                return [word + ' I-' + value[0] + '\n', False]
            elif type(value[1]) == list:
                if word == value[1][0]:
                    line = ''
                    counter = 0
                    category = value[0]
                    for item in value[1]:
                        if counter == 0:
                            line += item + ' B-' + category + '\n'
                            counter += 1
                        else:
                            line += item + ' I-' + category + '\n'
                    return [line, len(value[1])]
        return [(word + ' 0' + '\n'), False]
    else:
        return [(word + ' 0' + '\n'), False]



def write_line(output,line):
    output.write(line)


def create_lines(words,tags,entities):
    lines = []
    counter = 0
    
    for token in words:
        if token == '_____________________________________________':
            continue
        elif counter != 0:
            counter -= 1
            continue
        else:
            line,skip = bio_formatting(token,tags,entities)[0], bio_formatting(token,tags,entities)[1]
            if skip != False:
                counter = skip 
                lines.append(line)
                counter -= 1
            else:
                lines.append(line)
    return lines



def write_to_file(doc_text,tags,entities,output_path,filename):
    new_file = output_path + '/' + filename.split('/')[-1]
    new_file = new_file[0:-3] + 'conll'

    with open(new_file, 'a') as output:
        word_list = nltk.word_tokenize(doc_text)
        lines = create_lines(word_list, tags,entities)
        for line in lines:
            write_line(output, line)


def convert_xml_to_conll(file, output_path):
    parser = argparse.ArgumentParser(description='XML to Conll converter')
    parser.add_argument('--input', type=str, default=file,
                        help='The XML file to convert')
    parser.add_argument('--output', type=str,
                        help='The output CONLL file name')
    parser.add_argument('--csv', action='store_true', 
                        help='Convert to CSV instead of CONLL')
    args = parser.parse_args()
    # Read XML input file 
    xmldoc = minidom.parse(args.input)
    docs = xmldoc.getElementsByTagName('TAGS')

    tags_element = False # TAGS element
    doc_element = False # DOC element
    for item in xmldoc.childNodes[0].childNodes:
        if item.nodeType == 1:
            if item.tagName == 'TAGS':
                tags_element = item
            elif item.tagName == 'TEXT' or item.tagName == 'DOC':
                doc_element = item

    #! TAGS Tag
    tags_elements = [] # list w/ all tags inside TAGS tag

    # filter out text tags
    for element in tags_element.childNodes:
        if element.nodeType == 1:
            if element.tagName != 'TEXT':
                tags_elements.append(element)


    tags = {}

    for tag in tags_elements:
        attributes = tag._attrs
        _id, text, _type = attributes['id'].value, attributes['text'].value, attributes['TYPE'].value
        if len(text.split()) > 1:
            text = text.split(' ')
            text = [i for i in text if i]
            for i in range(len(text)):
                if text[i] == '':
                    text.pop(i)
                    continue
                if len(text[i]) > 1 and text[i][-1] == ',':
                    text[i] = text[i][0:-1]
                    text.insert(i+1,',')
        tags[_id] = [_type, text]


    #! Text from DOC Tag
    doc_text = doc_element.childNodes[0].data


    #! Create list of entities
    entities_list_with_lists = []

    for tag_attributes in tags.values():
        text = tag_attributes[1]
        entities_list_with_lists.append(text)

    entities = []
    for value in entities_list_with_lists:
        if type(value) == list:
            for entity in value:
                entities.append(entity)
        else:
            entities.append(value)


    entities = list(set(entities))

    write_to_file(doc_text,tags,entities,output_path, file)

