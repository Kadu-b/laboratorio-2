"""Laboratório 02: FCFS, Round Robin e conferência do SJF.
Sem dependências externas. Execute: python simulador_escalonador.py
"""
from dataclasses import dataclass
from collections import deque
from pathlib import Path
import copy

@dataclass
class Processo:
    pid: str
    chegada: int
    duracao: int
    restante: int = 0
    finalizacao: int = 0
    espera: int = 0
    retorno: int = 0

    def __post_init__(self):
        if self.chegada < 0 or self.duracao <= 0:
            raise ValueError('Chegada deve ser não negativa e duração positiva.')
        self.restante = self.duracao


def simular(processos, algoritmo, quantum=3):
    if algoritmo not in ('FCFS', 'RR', 'SJF'):
        raise ValueError('Algoritmo inválido.')
    if algoritmo == 'RR' and quantum <= 0:
        raise ValueError('Quantum deve ser positivo.')
    pendentes = sorted(copy.deepcopy(processos), key=lambda p: p.chegada)
    for p in pendentes:
        p.restante = p.duracao
    fila = deque()
    concluidos, linha = [], []
    tempo = 0
    while pendentes or fila:
        if not fila and pendentes and tempo < pendentes[0].chegada:
            linha.append(('Ocioso', tempo, pendentes[0].chegada))
            tempo = pendentes[0].chegada
        while pendentes and pendentes[0].chegada <= tempo:
            fila.append(pendentes.pop(0))
        if algoritmo == 'SJF':
            fila = deque(sorted(fila, key=lambda p: (p.duracao, p.chegada)))
        p = fila.popleft()
        fatia = min(p.restante, quantum) if algoritmo == 'RR' else p.restante
        linha.append((p.pid, tempo, tempo + fatia))
        tempo += fatia
        p.restante -= fatia
        while pendentes and pendentes[0].chegada <= tempo:
            fila.append(pendentes.pop(0))
        if p.restante:
            fila.append(p)
        else:
            p.finalizacao = tempo
            p.retorno = tempo - p.chegada
            p.espera = p.retorno - p.duracao
            concluidos.append(p)
    return sorted(concluidos, key=lambda p: p.pid), linha


def simular_fcfs(processos):
    return simular(processos, 'FCFS')


def simular_round_robin(processos, quantum=3):
    return simular(processos, 'RR', quantum)


def main():
    base = Path(__file__).resolve().parent
    workload = [Processo('P1', 0, 8), Processo('P2', 1, 4), Processo('P3', 2, 9), Processo('P4', 3, 5)]
    logs = []
    for nome, algoritmo, quantum, arquivo in [('FCFS', 'FCFS', 3, 'fcfs'), ('Round Robin q=3', 'RR', 3, 'rr_3'), ('Round Robin q=1', 'RR', 1, 'rr_1'), ('Round Robin q=50', 'RR', 50, 'rr_50'), ('SJF não preemptivo', 'SJF', 3, 'sjf')]:
        procs, linha = simular(workload, algoritmo, quantum)
        logs.append('\n--- ' + nome + ' ---')
        for p in procs:
            logs.append(f'{p.pid}: Fim={p.finalizacao} ms, Espera={p.espera} ms, Retorno={p.retorno} ms')
        logs.append(f'Espera média: {sum(p.espera for p in procs)/len(procs):.2f} ms')
        logs.append(f'Retorno médio: {sum(p.retorno for p in procs)/len(procs):.2f} ms')
        trocas = sum(a[0] != b[0] and 'Ocioso' not in (a[0], b[0]) for a, b in zip(linha, linha[1:]))
        logs.append(f'Trocas entre processos: {trocas}')
        logs.append('Linha do tempo: ' + '; '.join(f'{p} [{a},{b})' for p, a, b in linha))
    saida = '\n'.join(logs) + '\n'
    print(saida)
    (base / 'resultados.txt').write_text(saida, encoding='utf-8')

if __name__ == '__main__':
    main()
