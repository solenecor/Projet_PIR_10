"""
excel_export.py
---------------
Script autonome : applique le STA/LTA sur une trace et remplit automatiquement
l'Excel comparatif
"""

import numpy as np
from datetime import timedelta
from openpyxl import load_workbook

# ── Constantes grille Excel ────────────────────────────────────────────────────

STA_VALUES      = [0.1, 0.25, 0.5, 1, 2]
LTA_VALUES      = [1, 5, 10, 20]
SEUIL_COL_START = {3: 3, 4: 10}   # colonne Excel (1-indexé) de LTA=1 par seuil
PIC_ROW_START   = 2               # ligne header du pic 1
PIC_ROW_STEP    = 7               # nb de lignes entre chaque pic


# ── STA/LTA ───────────────────────────────────────────────────────────────────

def _ratio(trace, i, ns, nl):
    sta = np.mean(np.square(trace[max(0, i - ns):i])) if i > 0 else 0.0
    lta = np.mean(np.square(trace[max(0, i - nl):i])) if i > 0 else 0.0
    return sta / lta if lta != 0 else 1.0


def _detect(trace, ns, nl, threshold, sample_rate, wait_time):
    """Retourne la liste des index de détection."""
    indexes = []
    for i in range(len(trace)):
        if _ratio(trace, i, ns, nl) > threshold:
            if not indexes or i > indexes[-1] + sample_rate * wait_time:
                indexes.append(i)
    return indexes


# ── Mapping paramètres → cellule Excel ────────────────────────────────────────

def _cell(pic_num, sta_s, lta_s, threshold):
    """Retourne (row, col) 1-indexé, ou None si paramètres hors grille."""
    if pic_num < 1 :
        return None
    if sta_s not in STA_VALUES or lta_s not in LTA_VALUES or threshold not in SEUIL_COL_START:
        return None
    row = PIC_ROW_START + (pic_num - 1) * PIC_ROW_STEP + STA_VALUES.index(sta_s) + 1
    col = SEUIL_COL_START[threshold] + LTA_VALUES.index(lta_s)
    return row, col


def _fmt(dt):
    """datetime → 'HH:MM:SS:cs'"""
    return dt.strftime("%H:%M:%S") + f":{dt.microsecond // 10000:02d}"


# ── Fonction principale ────────────────────────────────────────────────────────

def run_and_export(trace, sample_rate, sta_s, lta_s, threshold,
                   wait_time, start_time, filepath, sheet_name="EPS"):
    """
    Lance la détection STA/LTA et écrit la i-ème détection dans la cellule
    du "pic i" correspondant aux paramètres donnés.

    Paramètres
    ----------
    trace       : np.ndarray
    sample_rate : float — Hz
    sta_s       : float — parmi [0.1, 0.25, 0.5, 1, 2]
    lta_s       : float — parmi [1, 5, 10, 20]
    threshold   : int   — 3 ou 4
    wait_time   : float — secondes minimum entre deux détections
    start_time  : datetime — horodatage du premier échantillon
    filepath    : str — chemin vers le .xlsx
    sheet_name  : str — nom de la feuille (défaut "EPS")

    Retourne
    --------
    list[datetime] — horodatages des pics détectés
    """
    if sta_s not in STA_VALUES:
        raise ValueError(f"sta_s doit être dans {STA_VALUES}, reçu {sta_s}")
    if lta_s not in LTA_VALUES:
        raise ValueError(f"lta_s doit être dans {LTA_VALUES}, reçu {lta_s}")
    if threshold not in SEUIL_COL_START:
        raise ValueError(f"threshold doit être dans {list(SEUIL_COL_START)}, reçu {threshold}")

    ns = int(sta_s * sample_rate)
    nl = int(lta_s * sample_rate)

    indexes = _detect(trace, ns, nl, threshold, sample_rate, wait_time)
    times   = [start_time + timedelta(seconds=idx / sample_rate) for idx in indexes]

    if not times:
        print(f"[STA/LTA] Aucune détection  (STA={sta_s}s | LTA={lta_s}s | seuil={threshold})")
        return times

    wb = load_workbook(filepath)
    ws = wb[sheet_name]

    for pic_num, dt in enumerate(times, start=1):
        pos = _cell(pic_num, sta_s, lta_s, threshold)
        if pos is None:
            print(f"[export]  Pic {pic_num} ignoré (hors grille ou > 13 pics)")
            continue
        row, col = pos
        ws.cell(row=row, column=col, value=_fmt(dt))
        print(f"[export]  Pic {pic_num:2d} → {ws.cell(row=row, column=col).coordinate} = {_fmt(dt)}")

    wb.save(filepath)
    wb.close()
    print(f"[export]  Fichier sauvegardé : {filepath}")
    return times
