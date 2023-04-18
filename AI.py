import json

def get_input():
    return input("Enter input: ")

def add_rule(rules):
    new_if = input("Enter 'if' condition for the rule: ")
    new_then = input("Enter 'then' result for the rule: ")
    rule = {'if': new_if, 'then': new_then}
    rules.append(rule)
    return rules

def add_rule_con(rules):
    new_if = []
    new_if.append(input("Enter first fact for the 'if' condition: "))
    while True:
        operator = input("Enter logical operator (and/or) or press enter to finish: ")
        if operator == '':
            break
        new_if.append(operator)
        fact = input("Enter next fact: ")
        new_if.append(fact)
    new_then = input("Enter 'then' result for the rule: ")
    rule = {'if': new_if,'then': new_then}
    rules.append(rule)
    return rules

def save_rules(rules):
    with open('rules.json', 'w') as f:
        json.dump(rules, f)

def load_rules():
    try:
        with open('rules.json', 'r') as f:
            rules = json.load(f)
            return rules
    except:
        return []

def infer(rules, input_data, max_iterations=1000):
    inferred_facts = set(input_data.split())
    iterations = 0

    while iterations < max_iterations:
        new_inferred_facts = set()
        for rule in rules:
            rule_conditions = rule['if']
            if isinstance(rule_conditions, list):
                # rule has multiple conditions
                condition_values = []
                for cond in rule_conditions:
                    if cond == 'and' or cond == 'or' or cond == 'not':
                        condition_values.append(cond)
                    else:
                        if cond in inferred_facts:
                            condition_values.append(True)
                        else:
                            condition_values.append(False)
                if 'and' in condition_values and False not in condition_values:
                    # If there's an "and" condition and all conditions are True, infer the conclusion
                    new_inferred_facts.add(rule['then'])
                elif 'or' in condition_values and True in condition_values:
                    # If there's an "or" condition and at least one condition is True, infer the conclusion
                    new_inferred_facts.add(rule['then'])
                elif all(condition_values):
                    # If there's no "and" or "or" condition and all conditions are True, infer the conclusion
                    new_inferred_facts.add(rule['then'])
            else:
                # rule has a single condition
                if rule_conditions in inferred_facts:
                    new_inferred_facts.add(rule['then'])
        
        if not new_inferred_facts:
            # no new facts were inferred
            break
        inferred_facts.update(new_inferred_facts)
        iterations += 1
    
    # Subtract the initial input facts from the inferred facts before returning
    return inferred_facts - set(input_data.split())

def add_starter_nodes(input_data):
    rules = load_rules()
    unmatched_conditions = find_unmatched_conditions(rules)
    
    # Ask the user for each starter node one by one
    for node in unmatched_conditions:
        user_input = input(f"Do you want to add more starting node  '{node}'? [y/n]: ")
        
        if user_input.lower() == "y":
            input_data += " " + node
            print(f"Added {node} to input_data.")
    
    # Return the updated input_data list
    return input_data

#function to get starting node
def find_unmatched_conditions(rules):
    # Extract all the unique conditions from the rules
    conditions = set()
    for rule in rules:
        if isinstance(rule["if"], list):
            for cond in rule["if"]:
                if isinstance(cond, str):
                    conditions.add(cond)
        else:
            conditions.add(rule["if"])

    # Find all conditions that don't have a matching outcome
    unmatched_conditions = []
    for cond in conditions:
        if cond not in ['and', 'or']:  # exclude logical operators
            matched = False
            for rule in rules:
                if rule["then"] == cond:
                    matched = True
                    break
            if not matched:
                unmatched_conditions.append(cond)

    return unmatched_conditions

#function to find end node
def find_mismatched_outcomes(rules):
    if_conditions = set()
    then_outcomes = set()

    # Collect all conditions mentioned in 'if' and 'then' parts of the rules
    for rule in rules:
        if isinstance(rule['if'], list):
            # Filter out 'and' and 'or' from the conditions
            if_conditions.update(set([condition for condition in rule['if'] if condition not in ['and', 'or']]))
        else:
            if_conditions.add(rule['if'])

        then_outcomes.add(rule['then'])

    # Find all outcomes that were mentioned in 'then' but not in 'if'
    mismatched_outcomes = then_outcomes.difference(if_conditions)

    return mismatched_outcomes

#function find unique
def find_unique_conditions(rules):
    all_conditions = set()

    # Collect all conditions mentioned in the rules
    for rule in rules:
        if isinstance(rule['if'], list):
            # Filter out 'and' and 'or' from the conditions
            all_conditions.update(set([condition for condition in rule['if'] if condition not in ['and', 'or']]))
        else:
            all_conditions.add(rule['if'])

        all_conditions.add(rule['then'])

    # Remove duplicate conditions
    unique_conditions = list(set(all_conditions))

    return unique_conditions

def main():
    rules = load_rules()

    while True:
        print("Enter 1 to add a rule, 2 to make an inference, or 3 to quit.")
        option = int(input("Enter option: "))

        if option == 1:
            print("Enter 1 to add a normal rule, 2 to make a operational rule")
            select = int(input("Enter option: "))
            if select == 1:
                rules = add_rule(rules)
                save_rules(rules)
            elif select == 2:
                rules = add_rule_con(rules)
                save_rules(rules)
            else:
                print("Invalid option. Please enter 1 or 2")
        elif option == 2:
            while True:
                allcon = find_unmatched_conditions(rules)
                unique = find_unique_conditions(rules)
                endnode = find_mismatched_outcomes(rules)
                
                attributefun = set(unique) - set(allcon)
                input_data = input(f"Enter starting node: ")
                result = infer(rules, input_data)
                if result:
                        if set(attributefun).issubset(set(result)):
                            result = endnode
                            print("Final Result:", result)
                            break
                        else:
                            print("Result:", result)  
                            break
                else:
                    while True:
                        x = add_starter_nodes(input_data)
                        input_data += " " + x
                        get_result = input_data
                        result = infer(rules, get_result)
                        
                        if set(attributefun).issubset(set(result)):
                            result= endnode
                            print("Final Result:", result)
                            break
                        elif result:
                            print(f"Partial match found for input: ",result)
                            user_exists= input("Do you want to continue(y/n)?")
                            if user_exists =='y':
                                continue
                            else:
                                print("This is Final Result:", result)
                                break
                        else:
                            print(f"No match found for input '{input_data}'.")
                            break

                break    
        elif option == 3:
            break
        else:
            print("Invalid option. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()


