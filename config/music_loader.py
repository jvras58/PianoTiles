import os
from pathlib import Path
from typing import List

import mido
from config.note_editor import (
    notes,
)


def load_music_notes(sounds_dir: str = "config/Sounds") -> List[str]:
    """
    Carrega notas de um arquivo MIDI ou usa fallback de notes.json.

    Prioridade:
    1. Procura por .mid mais recente em sounds_dir.
    2. Se não encontrar, usa notes.json (músicas hardcoded).

    Args:
        sounds_dir: Diretório de sons (padrão: config/Sounds).

    Returns:
        Lista de notas (ex.: ["c4", "g4"]).

    Raises:
        ValueError: Se MIDI inválido.
    """
    sounds_path = Path(sounds_dir)
    midi_files = list(sounds_path.glob("*.mid"))

    if midi_files:
        latest_midi = max(midi_files, key=os.path.getmtime)
        return parse_midi_to_notes(latest_midi)

    # Fallback: Usa notes.json
    print("Nenhum .mid encontrado. Usando músicas hardcoded de notes.json.")
    return load_fallback_notes()


def parse_midi_to_notes(midi_file: Path) -> List[str]:
    """
    Extrai notas da track principal de um arquivo MIDI.

    Foco: Melodia simples (notas de piano, duração ignorada por simplicidade).
    Converte para formato ['c4', 'g4'] (nota + oitava).

    Args:
        midi_file: Caminho para .mid.

    Returns:
        Lista de notas sequenciais.
    """
    try:
        mid = mido.MidiFile(str(midi_file))
        notes_list = []

        # Pega a primeira track (geralmente melodia)
        for msg in mid.tracks[
            0
        ]:  # Assumindo track 0 como principal; ajuste se necessário
            if msg.type == "note_on" and msg.velocity > 0:  # Nota ligada
                note_name = mido_note_to_string(msg.note)
                notes_list.append(note_name)

        if not notes_list:
            raise ValueError(f"Nenhuma nota válida encontrada em {midi_file}")

        print(f"Notas extraídas de {midi_file}: {len(notes_list)} notas.")
        return notes_list

    except Exception as e:
        raise ValueError(f"Erro ao processar MIDI {midi_file}: {e}")


def mido_note_to_string(note_num: int) -> str:
    """
    Converte número MIDI (0-127) para string como 'c4'.

    Ex.: 60 -> 'c4', 67 -> 'g4'.
    Usa notação flat (bemol) com hífen, ex: 'a-4' ao invés de 'g#4'.
    """
    # Mapeamento usando bemóis (flats) com hífen ao invés de sustenidos
    notes_map = ["c", "c-", "d", "d-", "e", "f", "f-", "g", "g-", "a", "a-", "b"]
    octave = (note_num // 12) - 1
    note_idx = note_num % 12
    note_name = notes_map[note_idx]

    return f"{note_name}{octave}"


def load_fallback_notes() -> List[str]:
    """Carrega uma música aleatória de notes.json como fallback."""
    import random

    key = random.choice(list(notes.keys()))
    return notes[key]
