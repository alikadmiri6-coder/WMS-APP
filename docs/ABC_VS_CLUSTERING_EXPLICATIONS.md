# 📊 Différence entre Classification ABC et Clustering

## 🎯 Vue d'Ensemble

La **Classification ABC** et le **Clustering** sont deux méthodes d'analyse complémentaires mais fondamentalement différentes pour segmenter vos produits. Voici une explication détaillée.

---

## 📐 CLASSIFICATION ABC (Analyse de Pareto)

### 🧮 Principe de Calcul

La classification ABC est une méthode **univariée** (1 seule dimension) basée sur le **principe de Pareto** (80/20).

#### Étapes de calcul :

1. **Agrégation** : Somme du volume total par article
   ```
   Article A → 10,000 unités
   Article B → 5,000 unités
   Article C → 1,000 unités
   ```

2. **Tri décroissant** : Classement par volume
   ```
   1. Article A (10,000)
   2. Article B (5,000)
   3. Article C (1,000)
   Total : 16,000 unités
   ```

3. **Calcul du pourcentage cumulé** :
   ```
   Article A → 10,000 / 16,000 = 62.5% cumulé
   Article B → 15,000 / 16,000 = 93.8% cumulé
   Article C → 16,000 / 16,000 = 100% cumulé
   ```

4. **Classification par seuils fixes** :
   - **Classe A** : 0% → 80% du volume cumulé (produits critiques)
   - **Classe B** : 80% → 95% du volume cumulé (produits intermédiaires)
   - **Classe C** : 95% → 100% du volume cumulé (produits à faible rotation)

#### Résultat pour cet exemple :
```
Article A → Classe A (car 62.5% < 80%)
Article B → Classe B (car 93.8% entre 80% et 95%)
Article C → Classe B (car 93.8% < 100%)
```

### 📊 Code dans votre application (app.py:492)

```python
def compute_abc(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    # 1. Agrégation par article
    agg = df.groupby('Article')[metric].sum().reset_index()

    # 2. Tri décroissant
    agg = agg.sort_values(metric, ascending=False)

    # 3. Calcul pourcentage et cumulé
    agg['Pct'] = (agg[metric] / agg[metric].sum()) * 100
    agg['Cumul'] = agg['Pct'].cumsum()

    # 4. Classification avec seuils FIXES
    def classify_abc(cumul):
        if cumul <= 80:
            return 'A'  # Top 80% du volume
        elif cumul <= 95:
            return 'B'  # 80-95% du volume
        else:
            return 'C'  # 95-100% du volume

    agg['Classe'] = agg['Cumul'].apply(classify_abc)
    return agg
```

### 🎯 Objectif de l'ABC

- **Identifier les 20% de produits qui génèrent 80% du volume**
- **Hiérarchiser les efforts** : concentrer les ressources sur les produits A
- **Optimiser le stockage** : Produits A = zones chaudes, Produits C = zones froides
- **Méthode simple et universelle** : Même classification dans tous les entrepôts

### ✅ Avantages

- Simple à comprendre et à expliquer
- Classification standardisée (A/B/C universel)
- Focus sur l'impact business
- Comparaison facile entre périodes

### ❌ Limites

- **Une seule dimension** : Ignore la fréquence de commande
- **Seuils arbitraires** : 80/95% sont des conventions
- Deux produits de même volume → même classe (pas de nuance)

---

## 🤖 CLUSTERING (K-Means)

### 🧮 Principe de Calcul

Le clustering est une méthode **multivariée** (plusieurs dimensions) basée sur l'**apprentissage automatique** (Machine Learning).

#### Étapes de calcul :

1. **Sélection de 2 dimensions** :
   ```
   Dimension 1 : Volume total par article
   Dimension 2 : Fréquence (nombre de commandes)
   ```

2. **Préparation des données** :
   ```
   Article A → Volume: 10,000 | Fréquence: 50 commandes
   Article B → Volume: 5,000  | Fréquence: 100 commandes
   Article C → Volume: 1,000  | Fréquence: 10 commandes
   ```

3. **Transformation logarithmique** (pour normaliser) :
   ```
   Article A → log(10,000) = 4.0 | log(50) = 1.7
   Article B → log(5,000) = 3.7  | log(100) = 2.0
   Article C → log(1,000) = 3.0  | log(10) = 1.0
   ```

4. **Algorithme K-Means** :
   - Place 3 "centres" (centroids) aléatoirement dans l'espace 2D
   - Attribue chaque produit au centre le plus proche (distance euclidienne)
   - Recalcule les centres en fonction des produits assignés
   - Répète jusqu'à convergence

5. **Classification dynamique** :
   - **Zone Or** (Hot) : Fréquence ÉLEVÉE + Volume ÉLEVÉ
   - **Zone Argent** (Warm) : Fréquence MOYENNE ou Volume MOYEN
   - **Zone Bronze** (Cold) : Fréquence FAIBLE + Volume FAIBLE

#### Résultat pour cet exemple :
```
Article A → Zone Or (volume élevé, fréquence moyenne)
Article B → Zone Or (fréquence très élevée malgré volume moyen)
Article C → Zone Bronze (volume et fréquence faibles)
```

### 📊 Code dans votre application (app.py:543)

```python
def compute_clustering(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Agrégation sur 2 dimensions
    prod = df.groupby('Article').agg({
        'Nbre Unités': 'sum',      # Dimension 1: Volume
        'No Op': 'nunique'          # Dimension 2: Fréquence
    }).reset_index()

    prod.columns = ['Article', 'Volume', 'Frequence']

    # 2. Transformation logarithmique (normalisation)
    prod['LogVolume'] = np.log1p(prod['Volume'])
    prod['LogFreq'] = np.log1p(prod['Frequence'])

    # 3. Machine Learning : K-Means avec 3 clusters
    kmeans = KMeans(n_clusters=3, random_state=42)
    X = prod[['LogFreq', 'LogVolume']].values
    prod['Cluster'] = kmeans.fit_predict(X)

    # 4. Classification DYNAMIQUE basée sur les moyennes
    # Calcul de la moyenne de chaque cluster
    cluster_centers = prod.groupby('Cluster')[['Frequence', 'Volume']].mean()

    # Le cluster avec la plus haute fréquence ET volume = Zone Or
    # Le cluster avec la plus basse fréquence ET volume = Zone Bronze
    # Le reste = Zone Argent

    def label_cluster(cluster_id):
        center = cluster_centers.loc[cluster_id]
        score = center['Frequence'] * center['Volume']

        if score > threshold_hot:
            return '🥇 Zone Or (Hot)'
        elif score > threshold_warm:
            return '🥈 Zone Argent (Warm)'
        else:
            return '🥉 Zone Bronze (Cold)'

    prod['Cluster_Label'] = prod['Cluster'].apply(label_cluster)
    return prod
```

### 🎯 Objectif du Clustering

- **Identifier des profils de produits** basés sur plusieurs critères
- **Détecter des patterns cachés** : Produit peu volumineux mais très fréquent
- **Optimisation fine du picking** : Distance vs Fréquence
- **Classification adaptative** : S'adapte automatiquement aux données

### ✅ Avantages

- **Multi-dimensionnel** : Prend en compte volume ET fréquence
- **Plus nuancé** : Distingue "gros volume rare" vs "petit volume fréquent"
- **Adaptatif** : Classification unique à chaque jeu de données
- **Détection de patterns** : Révèle des groupes non évidents

### ❌ Limites

- Plus complexe à expliquer aux opérationnels
- Classification non standardisée (varie selon les données)
- Nécessite suffisamment de données pour être pertinent
- Résultats peuvent varier légèrement à chaque exécution

---

## 📊 COMPARAISON DIRECTE

### Exemple concret avec 3 produits :

| Produit | Volume Total | Fréquence Commandes | Classe ABC | Cluster |
|---------|-------------|-------------------|-----------|---------|
| **Produit X** | 10,000 unités | 5 commandes | **A** | Zone Bronze |
| **Produit Y** | 1,000 unités | 200 commandes | **C** | Zone Or |
| **Produit Z** | 5,000 unités | 50 commandes | **B** | Zone Argent |

#### Analyse :

**Produit X** :
- ABC dit : Classe A (80% du volume) → Stocker en zone chaude
- Clustering dit : Zone Bronze (peu fréquent) → Stocker en zone froide
- **Conclusion** : Le clustering est plus pertinent ! Grande commande rare ne nécessite pas zone chaude.

**Produit Y** :
- ABC dit : Classe C (faible volume) → Stocker en zone froide
- Clustering dit : Zone Or (très fréquent) → Stocker en zone chaude
- **Conclusion** : Le clustering détecte un produit critique ignoré par ABC !

**Produit Z** :
- ABC dit : Classe B (intermédiaire)
- Clustering dit : Zone Argent (équilibré)
- **Conclusion** : Les deux méthodes s'accordent.

---

## 🎯 QUAND UTILISER CHAQUE MÉTHODE ?

### Classification ABC - Utilisez pour :

1. **Communication management** : Simple à présenter en comité
2. **Stratégie commerciale** : Identifier les produits stars
3. **Gestion des stocks** : Niveau de service différencié (A=99%, B=95%, C=90%)
4. **Approvisionnement** : Priorité commandes fournisseurs
5. **Comparaison périodes** : "La classe A représente maintenant 85% du CA"

### Clustering - Utilisez pour :

1. **Optimisation du picking** : Placement physique dans l'entrepôt
2. **Dimensionnement des zones** : Combien d'emplacements chauds/froids ?
3. **Stratégie de préparation** : Picking par vagues vs unitaire
4. **Analyse fine** : Détecter les produits à fréquence anormale
5. **Prévision de charge** : Anticiper les pics d'activité

---

## 💡 RECOMMANDATION

**Utilisez LES DEUX en complément !**

```
┌─────────────────────────────────────────────────────┐
│  WORKFLOW OPTIMAL                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1️⃣  ABC Analysis                                   │
│      → Identifier les produits critiques (A)       │
│      → Communication business                       │
│                                                     │
│  2️⃣  Clustering                                     │
│      → Affiner le placement physique               │
│      → Optimiser les flux de picking              │
│                                                     │
│  3️⃣  Croisement des résultats                       │
│      → Classe A + Zone Or = PRIORITÉ MAX          │
│      → Classe C + Zone Or = Alerte (très fréquent)│
│      → Classe A + Zone Bronze = Opportunité       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 EN RÉSUMÉ

| Critère | ABC | Clustering |
|---------|-----|-----------|
| **Dimensions** | 1 (volume) | 2 (volume + fréquence) |
| **Méthode** | Statistique simple | Machine Learning |
| **Seuils** | Fixes (80/95%) | Dynamiques |
| **Complexité** | ⭐ Simple | ⭐⭐⭐ Avancé |
| **Stabilité** | ✅ Toujours pareil | ⚠️ Varie selon données |
| **Universel** | ✅ Oui | ❌ Spécifique |
| **Nuance** | ❌ Limitée | ✅ Élevée |
| **Usage** | Stratégie business | Opérations terrain |

---

## 📚 Pour aller plus loin

- **ABC** : Principe de Pareto (Vilfredo Pareto, 1896)
- **Clustering** : K-Means (Stuart Lloyd, 1957)
- **Livre recommandé** : "Warehouse Management" by Gwynne Richards

---

**Date** : 2025-01-07
**Application** : WMS Analytics Pro v6.0
