import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from Lecture_data.lecture_mseed import lecture_mseed
    MSEED_AVAILABLE = True
except ImportError as e:
    print(f"  Module pymseed non disponible: {e}")
    print("   Mode test avec données synthétiques activé.\n")
    MSEED_AVAILABLE = False

def eppf(data, window_size, degree):
    n = len(data)
    eppf_values = np.zeros(n)
    coeffs_dict = {}
    for center in range(n):
        indices = np.clip(
            np.arange(center - window_size // 2, center + window_size // 2 + 1),
            0, n - 1
        )
        x = np.arange(len(indices))
        y = data[indices]
        coeffs = np.polyfit(x, y, degree)
        coeffs_dict[center] = coeffs
    for i in range(n):
        coeffs = coeffs_dict[i]
        x_center = window_size // 2
        eppf_values[i] = np.polyval(coeffs, x_center)

    return eppf_values

if __name__ == "__main__":
    mseed_file = "event.mseed"
    window_size = 81
    degree = 2

    if MSEED_AVAILABLE:
        print(f"1. Lecture du fichier MSEED: {mseed_file}")
        print("-" * 70)
        try:
            trace_data = lecture_mseed(mseed_file)
            print(f"    {len(trace_data)} trace(s) lue(s)\n")
            
            print(f"2. Application du filtre EPPF (window_size={window_size}, degree={degree})")
            print("-" * 70)
            
            for idx, trace in enumerate(trace_data):
                nslc = trace["network_station_location_channel"]
                data_raw = trace["data_samples"]
                
                print(f"\nTrace {idx+1}: {nslc[0]}.{nslc[1]}.{nslc[2]}.{nslc[3]}")
                print(f"  Source ID: {trace['source_id']}")
                print(f"  Time: {trace['start_time']} to {trace['end_time']}")
                print(f"  Sample rate: {trace['sample_rate_hz']} Hz")
                print(f"  Num samples: {trace['num_samples']:,}")
                
                print(f"\n  [BRUTES]")
                print(f"    Range: {np.min(data_raw):.6f} à {np.max(data_raw):.6f}")
                print(f"    Mean:  {np.mean(data_raw):.6f}")
                print(f"    Std:   {np.std(data_raw):.6f}")
                
                data_filtered = eppf(data_raw, window_size, degree)
                
                print(f"\n  [FILTRÉES (EPPF)]")
                print(f"    Range: {np.min(data_filtered):.6f} à {np.max(data_filtered):.6f}")
                print(f"    Mean:  {np.mean(data_filtered):.6f}")
                print(f"    Std:   {np.std(data_filtered):.6f}")
                
                x = np.linspace(0, trace['num_samples'] / trace['sample_rate_hz'], 
                               num=trace['num_samples'])
                
                fig, axes = plt.subplots(2, 1, figsize=(14, 8))
                
                axes[0].plot(x, data_raw, 'b-', linewidth=1.5)
                axes[0].set_ylabel('Amplitude')
                axes[0].set_title(f'Signal brut - {nslc[0]}.{nslc[1]}.{nslc[2]}.{nslc[3]}')
                axes[0].grid(True, alpha=0.3)
                axes[0].set_xlim(x.min(), x.max())
                
                axes[1].plot(x, data_raw, 'lightblue', linewidth=1.5, alpha=0.7, label='Signal brut')
                axes[1].plot(x, data_filtered, 'r-', linewidth=2, label=f'Signal filtré EPPF (L={window_size}, degree={degree})')
                axes[1].set_xlabel('Temps (s)')
                axes[1].set_ylabel('Amplitude')
                axes[1].set_title(f'Comparaison - Brut vs Filtré')
                axes[1].grid(True, alpha=0.3)
                axes[1].legend()
                axes[1].set_xlim(x.min(), x.max())
                
                plt.tight_layout()
                plt.show()
        
        except FileNotFoundError:
            print(f"  Fichier '{mseed_file}' introuvable!")
            print("   Mode test avec données synthétiques activé.\n")
            MSEED_AVAILABLE = False

    if not MSEED_AVAILABLE:
        print("2. Génération de données synthétiques (MODE TEST)")
        print("-" * 70)
        
        np.random.seed(42)
        N = 60
        signal_reel = np.array([0.0]*30 + [1.0]*30)
        bruit = np.random.normal(0, 0.15, N)
        signal_bruite = signal_reel + bruit
        
        print(f"   Signal de test: {N} échantillons")
        print(f"   Type: Signal échelon + bruit gaussien")

        print(f"\n   Application du filtre EPPF (window_size={window_size}, degree={degree})...")
        resultat = eppf(signal_bruite, window_size=window_size, degree=degree)

        print(f"\n   [SIGNAL BRUTE]")
        print(f"    Range: {np.min(signal_bruite):.6f} à {np.max(signal_bruite):.6f}")
        print(f"    Mean:  {np.mean(signal_bruite):.6f}")
        print(f"    Std:   {np.std(signal_bruite):.6f}")
        
        print(f"\n   [SIGNAL FILTRÉ (EPPF)]")
        print(f"    Range: {np.min(resultat):.6f} à {np.max(resultat):.6f}")
        print(f"    Mean:  {np.mean(resultat):.6f}")
        print(f"    Std:   {np.std(resultat):.6f}\n")

        plt.figure(figsize=(12, 6))
        plt.plot(signal_bruite, color='lightgray', alpha=0.7, linewidth=1.5, label='Signal bruité')
        plt.plot(signal_reel, 'k--', alpha=0.6, linewidth=2, label='Signal réel (Échelon)')
        plt.plot(resultat, color='steelblue', linewidth=2.5, label=f'EPPF filtré (L={window_size}, degree={degree})')
        plt.title('Démonstration du filtre Edge-Preserving Smoothing', fontsize=14, fontweight='bold')
        plt.xlabel('Échantillons', fontsize=12)
        plt.ylabel('Amplitude', fontsize=12)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()