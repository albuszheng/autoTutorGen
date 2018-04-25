from yattag import Doc, indent
import os

def create_brd_file(brd_content: str, problem_name: str):
    path = "temp_file/brd/"
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = problem_name + "_%Y_%m_%d.brd"
    with open(path+file_name, "w+") as text_file:
        text_file.write(brd_content)

    return path+file_name


def build_behavior_graph(cognitive_model, problem_name:str, var_lists: list):
    stage_changes = len(cognitive_model)
    node_count = stage_changes + 1
    var_pos = {'line': 0}

    for i in range(0, len(var_lists)):
        var_pos[var_lists[i]] = i + 1

    doc, tag, text, line = Doc().ttl()

    doc.asis('<?xml version="1.0" standalone="yes"?>')

    with tag('stateGraph', firstCheckAllStates="true", caseInsensitive="true", unordered="false", lockWidget="true", hintPolicy="Use Both Kinds of Bias", version="4.0", suppressStudentFeedback="Show All Feedback", highlightRightSelection="true", startStateNodeName="%(startStateNodeName)%", tutorType="Example-tracing Tutor"):
        # startNodeMessage
        with tag('startNodeMessage'):

            doc.asis(message_section({'verb': 'SendNoteProperty', 'properties': {'MessageType': 'StartProblem', 'ProblemName': problem_name}}))

            doc.asis(message_section({'verb': 'SendNoteProperty', 'properties': {'MessageType': 'StartStateEnd'}}))

        # nodes -> states
        for i in range(1, node_count + 2):
            if i == 1:
                doc.asis(stage_node({'end': False, 'text': problem_name, 'id': str(i), 'x': str(181), 'y': str( 30 + 110 * ( i -1 ) )}))
            elif i == node_count + 1:
                doc.asis(stage_node(
                    {'end': True, 'text': 'Done', 'id': str(i), 'x': str(181), 'y': str(30 + 110 * (i - 1))}))
            else:
                doc.asis(stage_node(
                    {'end': False, 'text': 'state' + str(i), 'id': str(i), 'x': str(181), 'y': str(30 + 110 * (i - 1))}))

        # edges -> state changes
        R_value = 1
        current_line = 1
        for i in range(1, stage_changes + 1):
            # print(cognitive_model[i-1])
            if current_line != cognitive_model[i-1]['line']:
                current_line = cognitive_model[i-1]['line']
                R_value += 1
            prop = {'id': i,
                    'step_value': cognitive_model[i-1]['value'],
                    'step_var_name': cognitive_model[i-1]['changed'],
                    'line_num': R_value,
                    'target': 'MyTable.R'+str(R_value)+'C'+str(var_pos[cognitive_model[i-1]['changed']]),
                    'action': 'UpdateTextArea'
                    }
            print(prop)
            doc.asis(edge(prop, var_pos))

        prop_done = {'id': stage_changes+1,
                     'step_value': -1,
                     'step_var_name': 'Button',
                     'target': 'done',
                     'action': 'ButtonPressed'}
        doc.asis(edge(prop_done, var_pos))
        # other tags
        with tag('EdgesGroups', ordered="true"):
            pass

    return indent(doc.getvalue())


# create message tags
def message_section(msg: dict):
    doc, tag, text, line = Doc().ttl()

    with tag('message'):
        line('verb', msg['verb'])

        with tag('properties'):
            for key in msg['properties']:
                if type(msg['properties'][key]) != dict:
                    line(key, msg['properties'][key])
                else:
                    with tag(key):
                        for in_key in msg['properties'][key]:
                            line(in_key, msg['properties'][key][in_key])

    return doc.getvalue()


# create node tags
def stage_node(prop: dict):
    doc, tag, text, line = Doc().ttl()

    with tag('node', locked='false'):
        if prop['end']:
            doc.attr(doneState='true')
        else:
            doc.attr(doneState='false')

        line('text', prop['text'])

        line('uniqueID', prop['id'])

        with tag('dimension'):
            line('x', prop['x'])

            line('y', prop['y'])

    return doc.getvalue()


# create edge tags
def edge(prop: dict, var_pos: dict):
    doc, tag, text, line = Doc().ttl()

    with tag('edge'):
        with tag('actionLabel', preferPathMark="true", minTraversals="1", maxTraversals="1"):
            with tag('studentHintRequest'):
                pass

            with tag('stepSuccessfulCompletion'):
                pass

            with tag('stepStudentError'):
                pass

            line('uniqueID', str(prop['id']))

            doc.asis(message_section(get_edge_action_msg(prop['step_value'], prop['target']) if prop['target'] != 'done' else get_edge_ending_action_msg()))

            line('buggyMessage', 'No, this is not correct.')

            with tag('successMessage'):
                pass

            if prop['target'] != 'done':
                line('hintMessage', "Please enter '" + str(prop['step_value']) + "' in the highlighted field.")
            else:
                line('hintMessage', "Please click on the highlighted button.")

            with tag('callbackFn'):
                pass

            line("actionType", "Correct Action")
            line("oldActionType", "Correct Action")
            line("checkedStatus", "Never Checked")

            with tag('matchers', Concatenation="true"):
                with tag('Selection'):
                    with tag('matcher'):
                        line('matcherType', 'ExactMatcher')
                        line('matcherParameter', prop['target'], name="single")

                with tag('Action'):
                    with tag('matcher'):
                        line('matcherType', 'ExactMatcher')
                        line('matcherParameter', prop['action'], name='single')

                with tag('Input'):
                    with tag('matcher'):
                        line('matcherType', 'ExactMatcher')
                        line('matcherParameter', str(prop['step_value']), name='single')

                line('Actor', 'Student', linkTriggered="false")

        line("preCheckedStatus", "No-Applicable")

        with tag('rule'):
            line('text', 'unnamed')
            line('indicator', '-1')

        line('sourceID', str(prop['id']))
        line('destID', str(prop['id'] + 1))
        line('traversalCount', '0')


    return doc.getvalue()


def get_edge_action_msg(var, pos):
    properties = {'MessageType': "InterfaceAction",
                  'Selection': {'value': pos},
                  'Action': {'value': 'UpdateTextArea'},
                  'Input': {'value': var}
                  }
    msg = {'verb': "NotePropertySet", "properties": properties}

    return msg


def get_edge_ending_action_msg():
    properties = {'MessageType': "InterfaceAction",
                  'Selection': {'value': 'done'},
                  'Action': {'value': 'ButtonPressed'},
                  'Input': {'value': -1}
                  }
    msg = {'verb': "NotePropertySet", "properties": properties}

    return  msg
