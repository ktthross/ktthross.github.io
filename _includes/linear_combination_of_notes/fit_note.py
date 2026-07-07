import numpy as np
from dataclasses import dataclass, field


@dataclass(frozen=True)
class NoteEntry:
    piano_key: int
    note_name: str
    midi_number: int
    frequency: float = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "frequency",
            440 * 2 ** ((self.midi_number - 69) / 12),
        )


PIANO_NOTES = [
    NoteEntry(1, "A0", 21),
    NoteEntry(2, "A#0/Bb0", 22),
    NoteEntry(3, "B0", 23),
    NoteEntry(4, "C1", 24),
    NoteEntry(5, "C#1/Db1", 25),
    NoteEntry(6, "D1", 26),
    NoteEntry(7, "D#1/Eb1", 27),
    NoteEntry(8, "E1", 28),
    NoteEntry(9, "F1", 29),
    NoteEntry(10, "F#1/Gb1", 30),
    NoteEntry(11, "G1", 31),
    NoteEntry(12, "G#1/Ab1", 32),
    NoteEntry(13, "A1", 33),
    NoteEntry(14, "A#1/Bb1", 34),
    NoteEntry(15, "B1", 35),
    NoteEntry(16, "C2", 36),
    NoteEntry(17, "C#2/Db2", 37),
    NoteEntry(18, "D2", 38),
    NoteEntry(19, "D#2/Eb2", 39),
    NoteEntry(20, "E2", 40),
    NoteEntry(21, "F2", 41),
    NoteEntry(22, "F#2/Gb2", 42),
    NoteEntry(23, "G2", 43),
    NoteEntry(24, "G#2/Ab2", 44),
    NoteEntry(25, "A2", 45),
    NoteEntry(26, "A#2/Bb2", 46),
    NoteEntry(27, "B2", 47),
    NoteEntry(28, "C3", 48),
    NoteEntry(29, "C#3/Db3", 49),
    NoteEntry(30, "D3", 50),
    NoteEntry(31, "D#3/Eb3", 51),
    NoteEntry(32, "E3", 52),
    NoteEntry(33, "F3", 53),
    NoteEntry(34, "F#3/Gb3", 54),
    NoteEntry(35, "G3", 55),
    NoteEntry(36, "G#3/Ab3", 56),
    NoteEntry(37, "A3", 57),
    NoteEntry(38, "A#3/Bb3", 58),
    NoteEntry(39, "B3", 59),
    NoteEntry(40, "C4", 60),
    NoteEntry(41, "C#4/Db4", 61),
    NoteEntry(42, "D4", 62),
    NoteEntry(43, "D#4/Eb4", 63),
    NoteEntry(44, "E4", 64),
    NoteEntry(45, "F4", 65),
    NoteEntry(46, "F#4/Gb4", 66),
    NoteEntry(47, "G4", 67),
    NoteEntry(48, "G#4/Ab4", 68),
    NoteEntry(49, "A4", 69),
    NoteEntry(50, "A#4/Bb4", 70),
    NoteEntry(51, "B4", 71),
    NoteEntry(52, "C5", 72),
    NoteEntry(53, "C#5/Db5", 73),
    NoteEntry(54, "D5", 74),
    NoteEntry(55, "D#5/Eb5", 75),
    NoteEntry(56, "E5", 76),
    NoteEntry(57, "F5", 77),
    NoteEntry(58, "F#5/Gb5", 78),
    NoteEntry(59, "G5", 79),
    NoteEntry(60, "G#5/Ab5", 80),
    NoteEntry(61, "A5", 81),
    NoteEntry(62, "A#5/Bb5", 82),
    NoteEntry(63, "B5", 83),
    NoteEntry(64, "C6", 84),
    NoteEntry(65, "C#6/Db6", 85),
    NoteEntry(66, "D6", 86),
    NoteEntry(67, "D#6/Eb6", 87),
    NoteEntry(68, "E6", 88),
    NoteEntry(69, "F6", 89),
    NoteEntry(70, "F#6/Gb6", 90),
    NoteEntry(71, "G6", 91),
    NoteEntry(72, "G#6/Ab6", 92),
    NoteEntry(73, "A6", 93),
    NoteEntry(74, "A#6/Bb6", 94),
    NoteEntry(75, "B6", 95),
    NoteEntry(76, "C7", 96),
    NoteEntry(77, "C#7/Db7", 97),
    NoteEntry(78, "D7", 98),
    NoteEntry(79, "D#7/Eb7", 99),
    NoteEntry(80, "E7", 100),
    NoteEntry(81, "F7", 101),
    NoteEntry(82, "F#7/Gb7", 102),
    NoteEntry(83, "G7", 103),
    NoteEntry(84, "G#7/Ab7", 104),
    NoteEntry(85, "A7", 105),
    NoteEntry(86, "A#7/Bb7", 106),
    NoteEntry(87, "B7", 107),
    NoteEntry(88, "C8", 108),
]


def diagonal_integral(frequency, upper_limit, lower_limit) -> float:
    return (upper_limit - lower_limit) / 2 - (
        np.sin(frequency * 2 * upper_limit) - np.sin(frequency * 2 * lower_limit)
    ) / (4 * frequency)


def off_diagonal_integral(frequency_0, frequency_1, upper_limit, lower_limit) -> float:
    frequency_diff = frequency_1 - frequency_0
    frequency_sum = frequency_0 + frequency_1
    term_0 = np.sin(frequency_diff * upper_limit)
    term_1 = np.sin(frequency_sum * upper_limit)
    term_2 = np.sin(frequency_diff * lower_limit)
    term_3 = np.sin(frequency_sum * lower_limit)
    return (term_0 - term_2) / (2 * frequency_diff) + (term_3 - term_1) / (
        2 * frequency_sum
    )


def diagonal_integral_with_lower_limit_zero(frequency, upper_limit) -> float:
    return upper_limit / 2 - np.sin(frequency * 2 * upper_limit) / (4 * frequency)


def off_diagonal_integral_with_lower_limit_zero(
    frequency_0, frequency_1, upper_limit
) -> float:
    frequency_diff = frequency_1 - frequency_0
    frequency_sum = frequency_0 + frequency_1
    term_0 = np.sin(frequency_diff * upper_limit)
    term_1 = np.sin(frequency_sum * upper_limit)
    return term_0 / (2 * frequency_diff) - term_1 / (2 * frequency_sum)


def generate_g_matrix_for_all_but_one(heldout_note: str, upper_limit) -> np.ndarray:
    active_notes = [note for note in PIANO_NOTES if note.note_name != heldout_note]
    total_notes = len(active_notes)
    g_matrix = np.zeros((total_notes, total_notes), dtype=float)
    for itr in range(total_notes):
        for jtr in range(itr, total_notes):
            if itr == jtr:
                g_matrix[itr, jtr] = diagonal_integral_with_lower_limit_zero(
                    active_notes[itr].frequency, upper_limit
                )
            else:
                g_matrix[itr, jtr] = off_diagonal_integral_with_lower_limit_zero(
                    active_notes[itr].frequency,
                    active_notes[jtr].frequency,
                    upper_limit,
                )
                g_matrix[jtr, itr] = g_matrix[itr, jtr]
    return g_matrix


def _get_fitted_note(fitted_note: str) -> NoteEntry | None:
    for note in PIANO_NOTES:
        if note.note_name == fitted_note:
            return note
    return None


def generate_b_vector_for_all_but_one(heldout_note: str, upper_limit) -> np.ndarray:
    fitted_note = _get_fitted_note(heldout_note)
    if fitted_note is None:
        raise ValueError("Missing the note that needs to be fitted!")

    active_notes = [note for note in PIANO_NOTES if note.note_name != heldout_note]
    total_notes = len(active_notes)
    b_vector = np.zeros((total_notes, 1), dtype=float)
    for itr in range(total_notes):
        b_vector[itr] = off_diagonal_integral_with_lower_limit_zero(
            fitted_note.frequency, active_notes[itr].frequency, upper_limit
        )
    return b_vector


def fit_note(note_name: str, upper_limit: float) -> np.ndarray:
    g_matrix = generate_g_matrix_for_all_but_one(note_name, upper_limit)
    b_vector = generate_b_vector_for_all_but_one(note_name, upper_limit)
    note_fit = np.linalg.solve(g_matrix, b_vector)
    return note_fit


def sweep_upper_limit_of_note(note_name: str):
    """
    For a note, find the period of the note we want to fit and calculate several fits as a multiple of the period for
    the upper bound.
    """
    note_to_fit = None
    for note in PIANO_NOTES:
        if note.note_name == note_name:
            note_to_fit = note

    if note_to_fit is None:
        raise ValueError(f"Could not find {note_name} in the list of Piano Notes")

    period = 2 * np.pi / note_to_fit.frequency

    for multiplier in (0.5, 0.75, 1, 1.25, 1.5, 2.0, 4.0):
        upper_limit = period * multiplier
        fitted_values = fit_note(note_name, upper_limit)
        print(fitted_values)


if __name__ == "__main__":
    sweep_upper_limit_of_note("C4")
