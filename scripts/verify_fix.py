#!/usr/bin/env python3
"""
Script de vérification pour confirmer que tous les use_container_width ont été remplacés
"""

def verify_file(filepath):
    """Vérifie qu'un fichier ne contient plus use_container_width"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_param = content.count('use_container_width')
    new_param = content.count("width='stretch'")

    print(f"📊 Vérification de {filepath}")
    print(f"   ❌ Occurrences de 'use_container_width': {old_param}")
    print(f"   ✅ Occurrences de \"width='stretch'\": {new_param}")
    print()

    if old_param == 0 and new_param > 0:
        print("✅ SUCCÈS : Le fichier a été correctement corrigé !")
        print(f"   Tous les paramètres dépréciés ont été remplacés ({new_param} remplacements)")
        return True
    else:
        print("⚠️  ATTENTION : Des corrections sont encore nécessaires")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Vérification de la correction des warnings Streamlit")
    print("=" * 60)
    print()

    success = verify_file('app.py')

    print()
    print("=" * 60)
    if success:
        print("✅ Le code source est correct !")
        print()
        print("Si vous voyez encore des warnings :")
        print("1. Arrêtez complètement Streamlit (CTRL+C dans le terminal)")
        print("2. Nettoyez le cache : streamlit cache clear")
        print("3. Relancez : streamlit run app.py")
        print()
        print("Les warnings proviennent de l'ancienne version en mémoire,")
        print("pas du code sur le disque.")
    else:
        print("⚠️  Des corrections supplémentaires sont nécessaires")
    print("=" * 60)
