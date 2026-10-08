from project.problem import Problem
import argparse

class DFAProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments for DFA simulation.
        Megjegyzés: Az --input és --output argumentumokat a keretrendszer már létrehozta,
        így itt csak a saját --check argumentumunkat adjuk hozzá.
        """
        parser.add_argument('--check', type=str, help='Words to check, separated by commas (e.g. a,ab,abc)')
    
    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen (based on the presence of --check argument)
        """
        return bool(args.check)

    def run(self, args):
        """
        Run the DFA simulation
        """
        input_file = args.input
        output_file = args.output
        words_to_check = args.check

        # DFA adatok beolvasása a fájlból
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            
        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2]
        accept_states = set(lines[3].split())
        
        transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                from_state, symbol, to_state = parts
                transitions[(from_state, symbol)] = to_state
                
        # Szavak ellenőrzése
        words = words_to_check.split(",")
        results = []
        
        for word in words:
            current_state = start_state
            accepted = True
            for symbol in word:
                if (current_state, symbol) in transitions:
                    current_state = transitions[(current_state, symbol)]
                else:
                    accepted = False
                    break
            
            if accepted and current_state in accept_states:
                results.append("IGEN")
            else:
                results.append("NEM")
                
        # Eredmények kiírása a kimeneti fájlba, új soronként
        with open(output_file, 'w', encoding='utf-8') as f:
            for res in results:
                f.write(res + "\n")