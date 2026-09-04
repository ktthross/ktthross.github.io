#!/usr/bin/env python3
"""Turn a MIDI or MusicXML file into the score player's notation.

Written because transcribing from memory doesn't work. Given a real file the
conversion is mechanical: no ear, no guessing, no invented melodies.

    python3 score_from_midi.py song.mid  -o scores/song.score
    python3 score_from_midi.py song.mxl  -o scores/song.score --bars 8

Both formats land in the same intermediate form -- a flat list of
(start_beat, length_beats, midi_pitch, source_part) -- and everything after
that is shared, so the two front ends can't drift apart in how they emit.

Stdlib only: struct for MIDI, ElementTree for MusicXML, zipfile for .mxl.
"""

import argparse
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from fractions import Fraction

KEY_MIN, KEY_MAX = 1, 88          # A0 .. C8, and key = midi - 20
SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
LETTER_DUR = {Fraction(4): "w", Fraction(2): "h", Fraction(1): "q",
              Fraction(1, 2): "e", Fraction(1, 4): "s"}


def note_name(midi):
    return SHARP_NAMES[midi % 12] + str(midi // 12 - 1)


# --------------------------------------------------------------------------
# MIDI
# --------------------------------------------------------------------------

def _vlq(buf, i):
    """Variable-length quantity: 7 bits per byte, high bit means 'continues'."""
    n = 0
    while True:
        b = buf[i]
        i += 1
        n = (n << 7) | (b & 0x7F)
        if not b & 0x80:
            return n, i


def read_midi(path):
    data = open(path, "rb").read()
    if data[:4] != b"MThd":
        raise SystemExit(f"{path}: not a MIDI file (no MThd header)")
    (hdr_len,) = struct.unpack(">I", data[4:8])
    fmt, ntrk, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise SystemExit("SMPTE timecode MIDI isn't supported; re-export with "
                         "metrical (ticks-per-quarter) timing")
    pos = 8 + hdr_len

    notes = []            # (start_tick, length_ticks, midi, part)
    dangling = []         # note-ons we had to close ourselves
    tempos = []           # (tick, usec_per_quarter)
    sigs = []             # (tick, numerator, denominator)
    names = {}

    for trk in range(ntrk):
        if data[pos:pos + 4] != b"MTrk":
            break
        (length,) = struct.unpack(">I", data[pos + 4:pos + 8])
        end = pos + 8 + length
        i = pos + 8
        tick = 0
        running = None
        # note-on stacks per (channel, pitch); a repeated on before an off is
        # legal MIDI, so this has to be a stack rather than a single slot
        live = defaultdict(list)

        while i < end:
            delta, i = _vlq(data, i)
            tick += delta
            status = data[i]
            if status & 0x80:
                i += 1
                if status < 0xF0:
                    running = status
            else:
                if running is None:
                    raise SystemExit(f"{path}: running status with no prior event")
                status = running

            kind, chan = status & 0xF0, status & 0x0F

            if status == 0xFF:                              # meta
                mtype = data[i]
                i += 1
                mlen, i = _vlq(data, i)
                payload = data[i:i + mlen]
                i += mlen
                if mtype == 0x51 and mlen == 3:
                    tempos.append((tick, (payload[0] << 16) | (payload[1] << 8) | payload[2]))
                elif mtype == 0x58 and mlen >= 2:
                    sigs.append((tick, payload[0], 1 << payload[1]))
                elif mtype == 0x03 and mlen:
                    names[trk] = payload.decode("latin-1", "replace").strip()
                elif mtype == 0x2F:
                    break
            elif status in (0xF0, 0xF7):                    # sysex
                mlen, i = _vlq(data, i)
                i += mlen
            elif kind in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                d1, d2 = data[i], data[i + 1]
                i += 2
                if kind == 0x90 and d2 > 0:
                    live[(chan, d1)].append(tick)
                elif kind == 0x80 or (kind == 0x90 and d2 == 0):
                    stack = live.get((chan, d1))
                    if stack:
                        start = stack.pop(0)
                        if tick > start:
                            notes.append((start, tick - start, d1, (trk, chan)))
            elif kind in (0xC0, 0xD0):
                i += 1
            else:
                i += 1

        # A note-on with no matching note-off is common in the wild (a dropped
        # event, or a channel mismatch under running status). Close it at the end
        # of the track rather than losing the note silently.
        for (chan, pitch), stack in live.items():
            for start in stack:
                if tick > start:
                    notes.append((start, tick - start, pitch, (trk, chan)))
                    dangling.append(note_name(pitch))

        pos = end

    if not notes:
        raise SystemExit(f"{path}: no notes found")

    # ticks -> beats (quarter notes)
    out = [(Fraction(s, division), Fraction(l, division), m, p) for s, l, m, p in notes]
    tempo = 120.0
    if tempos:
        tempos.sort()
        tempo = 60_000_000.0 / tempos[0][1]
    meter = sigs[0][1] if sigs else 4
    if sigs and sigs[0][2] != 4:
        # the DSL's beat is always a quarter, so a x/8 or x/2 signature has to be
        # restated in quarters for the bar lines to land in the right place
        meter = Fraction(sigs[0][1] * 4, sigs[0][2])
    return out, tempo, meter, names, dangling


# --------------------------------------------------------------------------
# MusicXML
# --------------------------------------------------------------------------

STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _xml_root(path):
    if path.lower().endswith(".mxl"):
        with zipfile.ZipFile(path) as z:
            target = None
            try:                                    # the container names the root file
                container = ET.fromstring(z.read("META-INF/container.xml"))
                el = container.find(".//{*}rootfile")
                if el is not None:
                    target = el.get("full-path")
            except KeyError:
                pass
            if not target:
                target = next(n for n in z.namelist()
                              if n.lower().endswith((".xml", ".musicxml"))
                              and not n.startswith("META-INF"))
            return ET.fromstring(z.read(target))
    return ET.parse(path).getroot()


def read_musicxml(path):
    root = _xml_root(path)
    if root.tag.endswith("score-timewise"):
        raise SystemExit("timewise MusicXML isn't supported; export partwise")

    names = {}
    for sp in root.findall(".//{*}score-part"):
        nm = sp.find("{*}part-name")
        names[sp.get("id")] = (nm.text or "").strip() if nm is not None else ""

    notes, tempo, meter = [], None, None

    for part in root.findall("{*}part"):
        pid = part.get("id")
        divisions = Fraction(1)
        cursor = Fraction(0)                        # in quarter notes
        for measure in part.findall("{*}measure"):
            measure_start = cursor
            attrs = measure.find("{*}attributes")
            if attrs is not None:
                d = attrs.find("{*}divisions")
                if d is not None and d.text:
                    divisions = Fraction(int(d.text))
                t = attrs.find("{*}time")
                if t is not None and meter is None:
                    beats = int(t.findtext("{*}beats", "4"))
                    btype = int(t.findtext("{*}beat-type", "4"))
                    meter = Fraction(beats * 4, btype)
            # ElementTree's iter() takes a literal tag, so the {*} wildcard only
            # works through find/findall -- iter("{*}sound") silently matches nothing.
            for snd in measure.findall(".//{*}sound"):
                if snd.get("tempo") and tempo is None:
                    tempo = float(snd.get("tempo"))

            prev_start = cursor
            for el in measure:
                tag = el.tag.split("}")[-1]
                if tag == "note":
                    dur_el = el.find("{*}duration")
                    dur = Fraction(int(dur_el.text), 1) / divisions if dur_el is not None else Fraction(0)
                    is_chord = el.find("{*}chord") is not None
                    start = prev_start if is_chord else cursor
                    pitch = el.find("{*}pitch")
                    grace = el.find("{*}grace") is not None
                    if pitch is not None and not grace and dur > 0:
                        step = pitch.findtext("{*}step", "C")
                        octave = int(pitch.findtext("{*}octave", "4"))
                        alter = int(float(pitch.findtext("{*}alter", "0") or 0))
                        midi = (octave + 1) * 12 + STEP[step] + alter
                        voice = el.findtext("{*}voice", "1")
                        staff = el.findtext("{*}staff", "1")
                        notes.append((start, dur, midi, (pid, staff, voice)))
                    if not is_chord:
                        prev_start = cursor
                        cursor += dur
                elif tag == "backup":
                    cursor -= Fraction(int(el.findtext("{*}duration", "0"))) / divisions
                    prev_start = cursor
                elif tag == "forward":
                    cursor += Fraction(int(el.findtext("{*}duration", "0"))) / divisions
                    prev_start = cursor
            # measures are authoritative about where the next bar starts
            if meter:
                cursor = measure_start + meter

    if not notes:
        raise SystemExit(f"{path}: no pitched notes found")
    return notes, tempo or 100.0, meter or Fraction(4), names, []


# --------------------------------------------------------------------------
# quantize, split into playable voices, emit
# --------------------------------------------------------------------------

def part_table(notes, names):
    """One row per source part, in a stable order, so --parts can address them
    by number and --list-parts can show what's in the file."""
    rows = []
    for key in sorted({n[3] for n in notes}, key=str):
        group = [n for n in notes if n[3] == key]
        pitches = sorted(n[2] for n in group)
        label = ""
        if isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], int):
            label = names.get(key[0], "")
        elif isinstance(key, tuple):
            label = names.get(key[0], "")
        rows.append({
            "key": key, "name": label, "count": len(group),
            "lo": pitches[0], "hi": pitches[-1],
            "start": min(n[0] for n in group),
            "end": max(n[0] + n[1] for n in group),
        })
    return rows


def is_drum_part(key):
    """GM reserves channel 10 (index 9) for percussion. A kick drum arrives as a
    stream of one pitch, which is meaningless to a harmonic reconstruction."""
    return isinstance(key, tuple) and len(key) == 2 and key[1] == 9


def quantize(notes, grid):
    """Snap to a grid of `grid` subdivisions per beat. 12 covers both
    sixteenths (3/12) and triplet eighths (4/12), which is why it's default."""
    g = Fraction(1, grid)
    out = []
    dropped = 0
    for start, length, midi, part in notes:
        s = round(start / g) * g
        l = round(length / g) * g
        if l <= 0:
            l = g                                   # keep it, as the shortest legal note
        if not (KEY_MIN <= midi - 20 <= KEY_MAX):
            dropped += 1
            continue
        out.append((s, l, midi, part))
    out.sort(key=lambda n: (n[0], n[2]))
    return out, dropped


def snap_ends(notes, grid, units):
    """A played (rather than engraved) MIDI leaves notes a few ticks long or short,
    which turns into stray 1/12-beat rests and spurious extra voices. Pull a note's
    end onto the next onset in its own part when it's within `units` grid steps."""
    if units <= 0:
        return notes
    tol = Fraction(units, grid)
    by_part = defaultdict(list)
    for n in notes:
        by_part[n[3]].append(n)
    out = []
    for part, group in by_part.items():
        group.sort(key=lambda n: n[0])
        onsets = sorted({n[0] for n in group})
        for s, l, m, p in group:
            nxt = next((o for o in onsets if o > s), None)
            if nxt is not None and abs((s + l) - nxt) <= tol and nxt > s:
                l = nxt - s
            out.append((s, l, m, p))
    out.sort(key=lambda n: (n[0], n[2]))
    return out


def split_voices(notes, max_voices):
    """The DSL gives each track one note (or one chord) at a time, so real
    polyphony has to become several tracks. Notes that start together and last
    the same time collapse into a chord; anything still overlapping is pushed
    to the next free voice."""
    groups = defaultdict(list)
    for s, l, m, p in notes:
        groups[(s, l)].append(m)

    chords = sorted(((s, l, sorted(ms)) for (s, l), ms in groups.items()))
    voices = []                 # each: {events: [(start, len, [midi])], end, last}
    overflow = 0
    for s, l, ms in chords:
        centre = sum(ms) / len(ms)
        free = [i for i, v in enumerate(voices) if v["end"] <= s]
        if free:
            # Prefer the voice whose last note is nearest in pitch. Taking the
            # lowest free index instead scatters one melodic line across several
            # tracks and leaves voices holding a single stray note.
            vi = min(free, key=lambda i: (abs(voices[i]["last"] - centre), i))
        elif len(voices) < max_voices:
            vi = None
        else:
            # At the cap: clip whichever voice frees up soonest so this note still
            # fits. Only if even that is impossible do we exceed the cap -- losing
            # a note is never the right answer.
            vi = min(range(len(voices)), key=lambda i: voices[i]["end"])
            ps, pl, pms = voices[vi]["events"][-1]
            if ps < s:
                voices[vi]["events"][-1] = (ps, s - ps, pms)
            else:
                vi = None
                overflow += 1
        if vi is None:
            voices.append({"events": [], "end": Fraction(0), "last": centre})
            vi = len(voices) - 1
        voices[vi]["events"].append((s, l, ms))
        voices[vi]["end"] = s + l
        voices[vi]["last"] = centre
    return [v["events"] for v in voices], overflow


def fmt_dur(d):
    """Prefer the letter names, then dotted letters, then a fraction. The player
    reads all three, so this is only about the output being readable."""
    for base, letter in LETTER_DUR.items():
        if d == base:
            return letter
        for dots in (1, 2):
            if d == base * (Fraction(2) - Fraction(1, 2 ** dots)):
                return letter + "." * dots
    if d.denominator == 1:
        return str(d.numerator)
    return f"{d.numerator}/{d.denominator}"


def emit(voices, tempo, meter, header, track_names, bars=None):
    lines = list(header)
    lines.append("")
    lines.append(f"tempo {round(tempo)}")
    lines.append(f"meter {meter if meter.denominator != 1 else meter.numerator}")

    limit = meter * bars if bars else None
    clipped = []
    for events in voices:
        if limit:
            events = [(s, min(l, limit - s), ms) for s, l, ms in events if s < limit]
        clipped.append(events)

    # Every track is padded to the same whole bar, so the player's loop point and
    # the piano roll agree no matter which voice happens to be the longest.
    if limit:
        song_end = limit
    else:
        song_end = max((s + l for ev in clipped for s, l, _ in ev), default=Fraction(0))
        if song_end % meter:
            song_end += meter - (song_end % meter)

    for vi, events in enumerate(clipped):
        if not events:
            continue
        name = track_names[vi] if vi < len(track_names) else f"voice{vi + 1}"
        lines.append("")
        lines.append(f"track {name}")

        cursor = Fraction(0)
        last_dur = None
        row = []

        def flush():
            if row:
                lines.append("  " + "  ".join(row))
                row.clear()

        for s, l, ms in events:
            if s > cursor:                          # fill the gap with a rest
                gap = s - cursor
                tok = "-:" + fmt_dur(gap)
                row.append(tok)
                last_dur = gap
                cursor = s
            pitches = "+".join(note_name(m) for m in ms)
            tok = pitches if l == last_dur else f"{pitches}:{fmt_dur(l)}"
            row.append(tok)
            last_dur = l
            cursor = s + l
            # break at bar lines, but don't let a voice that never lands on one
            # run off into a single enormous line
            if cursor % meter == 0 or len(row) >= 16:
                flush()

        # trailing rest out to the shared end; rests carry length without events
        while cursor < song_end:
            step = min(song_end - cursor, meter - (cursor % meter) or meter)
            row.append("-:" + fmt_dur(step))
            cursor += step
            if cursor % meter == 0:
                flush()
        flush()

    n_events = sum(len(ev) for ev in clipped)
    n_notes = sum(len(ms) for ev in clipped for _, _, ms in ev)
    return "\n".join(lines) + "\n", n_events, n_notes, song_end


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help=".mid, .midi, .xml, .musicxml or .mxl")
    ap.add_argument("-o", "--out", help="write here instead of stdout")
    ap.add_argument("--grid", type=int, default=12,
                    help="quantize subdivisions per beat (12 = sixteenths and "
                         "triplets, 4 = sixteenths only, 24 = finer). default 12")
    ap.add_argument("--snap", type=int, default=0,
                    help="pull note ends onto the next onset when within this many "
                         "grid steps. 0 (default) for engraved files; try 2 with "
                         "--grid 4 for a recorded performance")
    ap.add_argument("--bars", type=int, help="keep only the first N bars")
    ap.add_argument("--skip-bars", type=int, default=0, help="drop the first N bars")
    ap.add_argument("--list-parts", action="store_true",
                    help="show the file's parts and exit, so you can pick with --parts")
    ap.add_argument("--parts", help="keep only these part numbers from --list-parts, "
                                    "e.g. 1,3,4")
    ap.add_argument("--keep-drums", action="store_true",
                    help="keep MIDI channel 10; by default percussion is dropped")
    ap.add_argument("--max-voices", type=int, default=4,
                    help="most .score tracks to split polyphony across (default 4)")
    ap.add_argument("--transpose", type=int, default=0, help="semitones")
    ap.add_argument("--tempo", type=float, help="override the file's tempo")
    ap.add_argument("--meter", type=int, help="override the file's beats per bar")
    ap.add_argument("--names", help="comma-separated track names, in order")
    ap.add_argument("--title", default="", help="first comment line of the output")
    args = ap.parse_args()

    lower = args.input.lower()
    if lower.endswith((".mid", ".midi")):
        notes, tempo, meter, part_names, dangling = read_midi(args.input)
        kind = "MIDI"
    elif lower.endswith((".xml", ".musicxml", ".mxl")):
        notes, tempo, meter, part_names, dangling = read_musicxml(args.input)
        kind = "MusicXML"
    else:
        raise SystemExit("unrecognized extension; expected .mid/.midi/.xml/.musicxml/.mxl")

    meter = Fraction(args.meter) if args.meter else Fraction(meter)
    tempo = args.tempo or tempo

    rows = part_table(notes, part_names)
    if args.list_parts:
        print(f"{kind}  tempo {round(tempo)}  meter {meter}  "
              f"{len(notes)} notes  ends at bar {float(max(r['end'] for r in rows) / meter):.1f}")
        for i, r in enumerate(rows, 1):
            drum = "  [drums]" if is_drum_part(r["key"]) else ""
            print(f"  {i}: {str(r['key']):<10} {str(r['name'])[:34]:<34} "
                  f"{r['count']:>5} notes  {note_name(r['lo'])}..{note_name(r['hi'])}"
                  f"  bars {float(r['start']/meter) + 1:.1f}-{float(r['end']/meter) + 1:.1f}{drum}")
        return

    if not args.keep_drums:
        drums = {r["key"] for r in rows if is_drum_part(r["key"])}
        if drums:
            before = len(notes)
            notes = [n for n in notes if n[3] not in drums]
            print(f"  dropped {before - len(notes)} percussion note(s) on channel 10 "
                  f"(--keep-drums to keep them)", file=sys.stderr)
    if args.parts:
        want = {int(x) for x in args.parts.replace(" ", "").split(",") if x}
        bad = want - set(range(1, len(rows) + 1))
        if bad:
            raise SystemExit(f"--parts: no part {sorted(bad)}; the file has "
                             f"{len(rows)} (see --list-parts)")
        keep = {rows[i - 1]["key"] for i in want}
        notes = [n for n in notes if n[3] in keep]
        if not notes:
            raise SystemExit("--parts selected nothing")

    if args.transpose:
        notes = [(s, l, m + args.transpose, p) for s, l, m, p in notes]
    if args.skip_bars:
        off = meter * args.skip_bars
        notes = [(s - off, l, m, p) for s, l, m, p in notes if s >= off]

    notes, dropped = quantize(notes, args.grid)
    notes = snap_ends(notes, args.grid, args.snap)
    if not notes:
        raise SystemExit("nothing left after quantizing / range filtering")

    origin = min(s for s, _, _, _ in notes)
    if origin > 0:                                  # don't emit a leading empty bar
        origin -= origin % meter
        notes = [(s - origin, l, m, p) for s, l, m, p in notes]

    # Voices are allocated within each source part, never across them. Pooling
    # everything would let a bass note and a piano note that happen to share a
    # start and length collapse into one chord -- it sounds the same, but it throws
    # away the part structure the track names refer to.
    # --names lines up with the file's parts, not with the tracks that come out of
    # them: a part that needs two voices becomes "bass" and "bass_2". Naming by
    # voice would silently shift every label as soon as one part split.
    given = [n.strip() for n in args.names.split(",")] if args.names else []
    rows = part_table(notes, part_names)
    if len(given) > len(rows):
        raise SystemExit(f"--names has {len(given)} entries but the selection has "
                         f"{len(rows)} part(s)")

    voices, names, overflow, mapping = [], [], 0, []
    for pi, r in enumerate(rows):
        part_notes = [n for n in notes if n[3] == r["key"]]
        vs, ov = split_voices(part_notes, args.max_voices)
        overflow += ov
        base = given[pi] if pi < len(given) else (r["name"] or "")
        base = re.sub(r"[^A-Za-z0-9_]", "", base.replace(" ", "_"))[:20] or f"part{pi + 1}"
        for j, v in enumerate(vs):
            voices.append(v)
            names.append(base if len(vs) == 1 else f"{base}_{j + 1}")
        mapping.append(f"{r['key']} {r['name'] or '(unnamed)'} -> "
                       + ", ".join(names[-len(vs):]))

    seen = {}
    for i, n in enumerate(names):
        seen[n] = seen.get(n, 0) + 1
        names[i] = n if seen[n] == 1 else f"{n}{seen[n]}"

    header = [f"# {args.title}"] if args.title else []
    header.append(f"# Converted from {kind} by score_from_midi.py -- not transcribed by ear.")
    text, n_events, n_notes, song_end = emit(
        voices, tempo, meter, header, names, args.bars)

    if args.out:
        open(args.out, "w").write(text)
    else:
        sys.stdout.write(text)

    limit = meter * args.bars if args.bars else None
    kept = [n for n in notes if limit is None or n[0] < limit]
    pitches = sorted(n[2] for n in kept)
    print(f"[{kind}] {args.input}", file=sys.stderr)
    print(f"  tempo {round(tempo)}  meter {meter}  grid 1/{args.grid} beat", file=sys.stderr)
    print(f"  {float(song_end / meter):.0f} bars, {n_events} events / {n_notes} notes "
          f"across {sum(1 for ev in voices if ev)} track(s), "
          f"range {note_name(pitches[0])}..{note_name(pitches[-1])}", file=sys.stderr)
    for line in mapping:
        print(f"  {line}", file=sys.stderr)
    if n_notes != len(kept):
        print(f"  WARNING: {len(kept)} notes went in but {n_notes} came out",
              file=sys.stderr)
    if overflow:
        print(f"  {overflow} chord(s) needed a track beyond --max-voices "
              f"{args.max_voices} rather than be dropped", file=sys.stderr)
    if dropped:
        print(f"  {dropped} note(s) outside A0..C8 dropped", file=sys.stderr)
    if dangling:
        shown = ", ".join(sorted(set(dangling))[:8])
        print(f"  {len(dangling)} note(s) had no note-off and were closed at the "
              f"end of their track ({shown})", file=sys.stderr)
    if args.snap:
        print(f"  snapped note ends within {args.snap}/{args.grid} beat "
              f"to the next onset", file=sys.stderr)


if __name__ == "__main__":
    main()
