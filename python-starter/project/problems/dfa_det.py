from project.problem import Problem
import argparse

class DFADeterminizatorProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--det', action='store_true', help='Determinizálja a megadott automatát')
    
    def is_chosen_problem(self, args):
        return args.det

    def run(self, args):
        input_file = args.input
        output_file = args.output

        # 1. Bemeneti fájl beolvasása
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            
        states = set(lines[0].split())
        alphabet = set(lines[1].split())
        start_state = lines[2]
        accept_states = set(lines[3].split())
        
        # Alapvető hibakezelés: ellenőrzések a bemeneti adatok helyességére
        if start_state not in states:
            raise ValueError(f"Hiba: A kezdőállapot ('{start_state}') nincs az érvényes állapotok között!")
        
        for acc in accept_states:
            if acc not in states:
                raise ValueError(f"Hiba: Az elfogadó állapot ('{acc}') nincs az érvényes állapotok között!")

        transitions = []
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                from_state, symbol, to_state = parts
                if from_state not in states:
                    raise ValueError(f"Hiba: Ismeretlen forrásállapot az átmenetben: '{from_state}'")
                if symbol not in alphabet:
                    raise ValueError(f"Hiba: Ismeretlen szimbólum az átmenetben: '{symbol}'")
                if to_state not in states:
                    raise ValueError(f"Hiba: Ismeretlen célállapot az átmenetben: '{to_state}'")
                transitions.append((from_state, symbol, to_state))
                
        # 2. NFA átmenetek ábrázolása szótárban: (állapot, szimbólum) -> {célállapotok halmaza}
        nfa_trans = {}
        for fs, sym, ts in transitions:
            if (fs, sym) not in nfa_trans:
                nfa_trans[(fs, sym)] = set()
            nfa_trans[(fs, sym)].add(ts)

        # 3. Determinizálás (Részhalmaz-szerkesztés / Powerset Construction)
        initial_set = frozenset([start_state])
        dfa_states_map = {initial_set: "s0"}  # Az új DFA állapotok elnevezései s0, s1, ...
        queue = [initial_set]
        dfa_transitions = []
        
        state_counter = 1
        
        while queue:
            current_set = queue.pop(0)
            current_dfa_name = dfa_states_map[current_set]
            
            for symbol in sorted(list(alphabet)):
                next_set = set()
                for state in current_set:
                    if (state, symbol) in nfa_trans:
                        next_set.update(nfa_trans[(state, symbol)])
                
                # Ha létezik hová lépni az adott szimbólummal
                if next_set:
                    frozen_next = frozenset(next_set)
                    if frozen_next not in dfa_states_map:
                        dfa_states_map[frozen_next] = f"s{state_counter}"
                        state_counter += 1
                        queue.append(frozen_next)
                    
                    target_dfa_name = dfa_states_map[frozen_next]
                    dfa_transitions.append((current_dfa_name, symbol, target_dfa_name))

        # 4. Új DFA állapotok és elfogadó állapotok meghatározása
        sorted_dfa_states = sorted(dfa_states_map.values(), key=lambda x: int(x[1:]))
        
        dfa_accept_states = []
        for f_set, name in dfa_states_map.items():
            # Ha a részhalmaz tartalmaz legalább egy eredeti elfogadó állapotot, akkor az új DFA-ban is elfogadó lesz
            if any(s in accept_states for s in f_set):
                dfa_accept_states.append(name)
        dfa_accept_states = sorted(dfa_accept_states, key=lambda x: int(x[1:]))

        # 5. Átmenetek rendezése a megadott szabály szerint:
        # (előbb csomópont szerint, majd él címkéje szerint, majd célállomás szerint)
        sorted_transitions = sorted(
            dfa_transitions,
            key=lambda t: (int(t[0][1:]), t[1], int(t[2][1:]))
        )

        # 6. Eredmények kiírása a kimeneti fájlba
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(" ".join(sorted_dfa_states) + "\n")
            f.write(" ".join(sorted(list(alphabet))) + "\n")
            f.write("s0\n")
            f.write(" ".join(dfa_accept_states) + "\n")
            for fs, sym, ts in sorted_transitions:
                f.write(f"{fs} {sym} {ts}\n")