from project.problem import Problem
import argparse
import re

class DFAMinimizerProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--mini', action='store_true', help='Minimalizálja a megadott determinisztikus automatát')
    
    def is_chosen_problem(self, args):
        return args.mini

    def run(self, args):
        input_file = args.input
        output_file = args.output

        # 1. Bemeneti fájl beolvasása
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            
        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2]
        accept_states = set(lines[3].split())
        
        # Alapvető hibakezelés
        if start_state not in states:
            raise ValueError(f"Hiba: A kezdőállapot ('{start_state}') nincs az érvényes állapotok között!")
        
        for acc in accept_states:
            if acc not in states:
                raise ValueError(f"Hiba: Az elfogadó állapot ('{acc}') nincs az érvényes állapotok között!")

        transitions = {}
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
                transitions[(from_state, symbol)] = to_state

        # 1.5. Elérhető állapotok szűrése (Breadth-First Search a kezdőállapotból)
        reachable_states = set([start_state])
        queue = [start_state]
        while queue:
            curr = queue.pop(0)
            for sym in alphabet:
                nxt = transitions.get((curr, sym))
                if nxt and nxt not in reachable_states:
                    reachable_states.add(nxt)
                    queue.append(nxt)

        # Csak az elérhető állapotokat tartjuk meg
        states = [s for s in states if s in reachable_states]
        transitions = {k: v for k, v in transitions.items() if k[0] in reachable_states and v in reachable_states}
        accept_states = set(s for s in accept_states if s in reachable_states)

        # 2. Minimalizálás (Moore-algoritmus)
        accept_set = set(accept_states)
        non_accept_set = set(states) - accept_set
        
        partitions = []
        if non_accept_set:
            partitions.append(non_accept_set)
        if accept_set:
            partitions.append(accept_set)

        def get_partition_index(state, current_partitions):
            for i, p in enumerate(current_partitions):
                if state in p:
                    return i
            return -1

        while True:
            new_partitions = []
            for group in partitions:
                split_groups = {}
                for state in group:
                    signature = []
                    for sym in sorted(alphabet):
                        next_state = transitions.get((state, sym))
                        if next_state is not None:
                            target_idx = get_partition_index(next_state, partitions)
                        else:
                            target_idx = -1
                        signature.append((sym, target_idx))
                    
                    sig_tuple = tuple(signature)
                    if sig_tuple not in split_groups:
                        split_groups[sig_tuple] = set()
                    split_groups[sig_tuple].add(state)
                
                for sg in split_groups.values():
                    new_partitions.append(sg)
            
            if len(new_partitions) == len(partitions):
                break
            partitions = new_partitions

        def state_to_int(s):
            numbers = re.findall(r'\d+', s)
            return int(numbers[0]) if numbers else 0

        # Csoportosítás és reprezentánsok kiválasztása
        group_representatives = []
        canonical_map = {}
        for group in partitions:
            sorted_group = sorted(list(group), key=state_to_int)
            rep = sorted_group[0]
            group_representatives.append((rep, sorted_group))
            for st in sorted_group:
                canonical_map[st] = rep

        # Rendezzük a csoportokat az eredeti reprezentánsok számai szerint, hogy s0, s1... sorrend helyes legyen
        group_representatives.sort(key=lambda x: state_to_int(x[0]))

        final_state_names = {}
        sorted_final_states = []
        for i, (rep, _) in enumerate(group_representatives):
            new_name = f"s{i}"
            sorted_final_states.append(new_name)
            final_state_names[rep] = new_name

        def get_new_name(st):
            rep = canonical_map[st]
            return final_state_names[rep]

        new_start_state = get_new_name(start_state)
        
        new_accept_states = set()
        for acc in accept_states:
            new_accept_states.add(get_new_name(acc))
        sorted_new_accept_states = sorted(list(new_accept_states), key=lambda x: int(x[1:]))

        # Átmenetek generálása
        new_transitions = set()
        for (fs, sym), ts in transitions.items():
            new_fs = get_new_name(fs)
            new_ts = get_new_name(ts)
            new_transitions.add((new_fs, sym, new_ts))

        sorted_transitions = sorted(
            list(new_transitions),
            key=lambda t: (int(t[0][1:]), t[1], int(t[2][1:]))
        )

        # 3. Kiírás a kimeneti fájlba
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(" ".join(sorted_final_states) + "\n")
            f.write(" ".join(sorted(alphabet)) + "\n")
            f.write(new_start_state + "\n")
            f.write(" ".join(sorted_new_accept_states) + "\n")
            for fs, sym, ts in sorted_transitions:
                f.write(f"{fs} {sym} {ts}\n")