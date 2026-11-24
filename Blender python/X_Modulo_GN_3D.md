# X Modulo 3D — Geometry Nodes

Le script [X_Modulo_GN_3D.py](./X_Modulo_GN_3D.py) crée, dans Blender 5.3,
une sphère de points reliés par une multiplication modulo. Les positions et
les connexions sont calculées par Geometry Nodes ; les réglages se trouvent
dans le modificateur du cube.

## Utilisation

1. Ouvrir Blender 5.3 avec une scène contenant un objet maillage nommé `Cube`
   et une caméra active. La scène par défaut convient.
2. Dans l'espace **Scripting**, ouvrir le fichier Python et exécuter le script.
3. Sélectionner le cube, puis ouvrir l'onglet **Modificateurs**.
4. Choisir une valeur de **Repartition** et ajuster les autres paramètres.
5. Enregistrer le fichier `.blend` pour conserver la scène.

À chaque exécution, le modificateur X Modulo créé par le script est remplacé :
**ses réglages reviennent aux valeurs par défaut**. Les autres modificateurs
sont conservés ; un ancien groupe encore utilisé par un autre objet n'est pas
supprimé.

Le script configure aussi la scène :

- une lumière ponctuelle est placée au centre du cube, avec une puissance de
  10 000 ;
- le World utilise un fond de puissance 0 ;
- la caméra regarde le centre et tourne autour sur 720 images à 24 images par
  seconde. La plage de rendu est de 1 à 720 ; une clé à l'image 721 et un
  cycle prolongent le mouvement.

La caméra doit être active et ne pas avoir d'animation, de parent ou de
contraintes externes incompatibles. Le script signale une erreur si ce n'est
pas le cas. La lumière réutilisée ne doit pas non plus avoir de parent, de
contraintes ou d'animation.

## Principe du modulo

Le modulo est le **reste d'une division entière** :

- `7 modulo 10 = 7` ;
- `12 modulo 10 = 2`, car `12 = 1 × 10 + 2` ;
- `27 modulo 10 = 7`, car `27 = 2 × 10 + 7`.

On peut l'imaginer comme une horloge : après 9, on revient à 0.

Les points possèdent des indices commençant à 0. Pour chaque point émetteur,
le script calcule :

```text
point d'arrivée = (indice de départ × Table) modulo nombre de points
```

Le modulo ramène l'indice d'arrivée dans l'intervalle disponible. Le point de
rang 0 **n'émet pas de lien**, mais d'autres points peuvent pointer vers lui.
Chaque lien est un segment entre deux positions sur la sphère, généralement
à travers son intérieur ; ce n'est pas une courbe plaquée sur la surface.

### Exemple : 10 points, table 2

| Départ | Calcul | Arrivée |
|---:|---|---:|
| 1 | 1 × 2 modulo 10 | 2 |
| 2 | 2 × 2 modulo 10 | 4 |
| 3 | 3 × 2 modulo 10 | 6 |
| 4 | 4 × 2 modulo 10 | 8 |
| 5 | 5 × 2 modulo 10 | 0 |
| 6 | 6 × 2 modulo 10 | 2 |
| 7 | 7 × 2 modulo 10 | 4 |
| 8 | 8 × 2 modulo 10 | 6 |
| 9 | 9 × 2 modulo 10 | 8 |

La **répartition** détermine les positions des points ; le **modulo** détermine
leurs connexions. Ainsi, modifier la répartition peut changer le dessin sans
changer les paires d'indices reliées.

Quelques valeurs de la table :

- **0** : chaque point émetteur pointe vers le rang 0.
- **1** : chaque point pointe vers lui-même ; ces segments sont de longueur
  nulle et ne forment pas de lignes visibles.
- **2, 3, 4…** : produisent d'autres connexions et d'autres motifs.

Des liens de sens opposés, par exemple `1 → 9` et `9 → 1`, se superposent
visuellement. La table est entière : les valeurs disponibles vont de 0 à
10 000.

## Filtrer les nombres

Le réglage **Filtre des nombres** s'applique à toutes les répartitions :

| Valeur | Points retenus |
|---:|---|
| 0 | Tous les indices |
| 1 | Les indices non premiers, y compris 0 et 1 |
| 2 | Les indices premiers : 2, 3, 5, 7… |

Un nombre premier est un entier supérieur à 1 divisible seulement par 1 et
par lui-même. Les nombres 0 et 1 ne sont pas premiers.

Le filtre ne déplace pas les points : il sélectionne les indices après leur
répartition. Les numéros affichés restent toujours leurs **indices d'origine**.
Si le filtre ne retient aucun point, ou seulement un point, il ne produit
aucun lien entre deux points distincts.

### Modulo sur sélection décoché

Le calcul utilise les indices et le nombre de points **avant filtrage**. Un
lien n'est conservé que si ses deux extrémités sont sélectionnées.

Exemple avec les indices de 0 à 9, le filtre premiers et la table 2. Les points
retenus sont `2, 3, 5, 7`, mais les liens d'origine sont :

| Départ | Arrivée | Résultat |
|---:|---:|---|
| 2 | 4 | Masqué : 4 n'est pas premier |
| 3 | 6 | Masqué : 6 n'est pas premier |
| 5 | 0 | Masqué : 0 n'est pas premier |
| 7 | 4 | Masqué : 4 n'est pas premier |

Aucun de ces liens ne reste visible. Ce comportement est normal : pour une
autre table ou un autre nombre de points, certains liens peuvent rester.

### Modulo sur sélection coché

Le script calcule le modulo **uniquement sur les points sélectionnés**, en
utilisant leur rang temporaire dans la sélection et leur nombre réel.

Pour les points premiers `2, 3, 5, 7` :

| Rang temporaire | Numéro d'origine affiché |
|---:|---:|
| 0 | 2 |
| 1 | 3 |
| 2 | 5 |
| 3 | 7 |

Le modulo vaut 4, car il y a quatre points sélectionnés :

| Rang de départ | Calcul avec la table 2 | Rang d'arrivée | Lien entre numéros affichés |
|---:|---|---:|---|
| 1 | 1 × 2 modulo 4 | 2 | 3 → 5 |
| 2 | 2 × 2 modulo 4 | 0 | 5 → 2 |
| 3 | 3 × 2 modulo 4 | 2 | 7 → 5 |

Le rang temporaire 0, correspondant ici au point 2, n'émet pas de lien. Il peut
néanmoins être une destination. Avec le filtre « tous », les deux modes de
calcul donnent les mêmes connexions.

## Répartitions disponibles

Choisir le numéro indiqué dans le premier paramètre du modificateur,
**Repartition**. Les modes 0 à 2 utilisent l'axe Y comme axe polaire ; les
modes suivants utilisent l'axe Z, à l'exception de l'icosphère et des grands
cercles, dont les sommets ne suivent pas un unique axe polaire.

### 0 — Fibonacci

Les points suivent une spirale utilisant l'angle d'or, avec des hauteurs
régulièrement espacées. Cela produit généralement une répartition assez
homogène sur la surface, sans anneaux apparents.

**Graine** modifie le décalage utilisé pour calculer les angles. La répartition
est déterministe pour des réglages identiques.

### 1 — Aléatoire uniforme

Chaque point reçoit une hauteur et un angle aléatoires. Le choix de la hauteur
permet une distribution statistiquement uniforme sur la surface, mais des
amas et des zones vides restent possibles.

**Graine** permet de produire une autre disposition reproductible.

### 2 — Anneaux

Les points sont répartis sur des anneaux de latitude, de l'axe +Y vers −Y.
Chaque anneau contient au maximum **Points par anneau** points. Le dernier
peut être incomplet ; ses points restent répartis sur tout l'anneau.

### 3 — Colimaçon

Les points suivent une spirale du pôle Nord `+Z` au pôle Sud `−Z` : l'indice
0 est au Nord et le dernier indice au Sud.

- **Tours du colimacon** règle le nombre de tours.
- **Colimacon surface uniforme** activé espace régulièrement les hauteurs,
  ce qui correspond à des bandes de surface égale ; cela ne garantit pas une
  distance identique entre points voisins.
- Décoché, le réglage espace régulièrement les latitudes.

### 4 — Anneaux décalés

Les points sont disposés par anneaux autour de l'axe Z, mais chaque anneau
est tourné par rapport au précédent.

**Points par anneau** fixe leur capacité maximale. **Decalage des anneaux**
ajoute, à chaque anneau, une fraction de l'intervalle angulaire entre points.
Une valeur de 0 supprime ce décalage.

### 5 — Méridiens

Les points suivent des lignes de longitude allant du Nord vers le Sud. Ils
sont regroupés par méridien et placés entre les pôles, sans point
exactement sur ceux-ci.

**Points par meridien** fixe le maximum par ligne. Le dernier méridien peut
contenir moins de points ; ils sont alors répartis sur sa longueur.

Avec **Points par meridien = 1**, tous les points se trouvent sur l'équateur,
dans le plan XY : on retrouve ainsi la disposition circulaire et les liens
modulo de [X_Modulo_2D.py](./X_Modulo_2D.py). Pour retrouver ses réglages
initiaux, utiliser **Nombre de points = 200**, **Table = 2**,
**Rayon sphere = 2** et **Filtre des nombres = 0**. Le rayon des liens du
script 2D est de 0,005.

### 6 — Grille perturbée

La base est une grille d'anneaux autour de l'axe Z. Chaque point est ensuite
décalé aléatoirement en latitude et en longitude.

- **Points par anneau** fixe la structure de départ.
- **Perturbation de la grille** règle l'amplitude des décalages ; 0 laisse
  la grille régulière.
- **Graine** modifie les décalages aléatoires.

### 7 — Icosphère

Les points sont les sommets d'une icosphère subdivisée. Leur ordre est celui
des sommets générés par Blender. Le réglage **Nombre de points** n'est pas
utilisé pour ce mode : le nombre dépend des **Subdivisions icosphere**.

| Subdivisions | Nombre de sommets |
|---:|---:|
| 1 | 12 |
| 2 | 42 |
| 3 | 162 |
| 4 | 642 |
| 5 | 2 562 |
| 6 | 10 242 |

Le modulo utilise ce nombre réel de sommets, ou le nombre retenu après
filtrage si **Modulo sur selection** est coché.

### 8 — Paires antipodales

Les points sont créés par paires : chaque point est accompagné d'un point
opposé sur la sphère, de l'autre côté du centre. Les indices alternent entre
les deux points de chaque paire.

Si **Nombre de points** est impair, le dernier point n'a pas de partenaire.

### 9 — Bande équatoriale

Les points sont placés dans une bande autour de l'équateur, avec une
progression angulaire de type Fibonacci.

**Demi-largeur bande** est un angle en degrés : 0 place les points sur
l'équateur ; 90 autorise des hauteurs sur l'ensemble de la sphère. **Graine**
modifie leur décalage angulaire.

### 10 — Double spirale

Deux bras de spirale parcourent la sphère autour de l'axe Z. Les indices
alternent entre les deux bras, qui sont opposés à chaque hauteur.

**Tours du colimacon** règle aussi le nombre de tours de ce mode. Les points
sont placés entre les pôles. Si leur nombre est impair, le dernier point n'a
pas de partenaire sur l'autre bras.

### 11 — Trois grands cercles

Les points alternent entre trois grands cercles situés dans les plans
orthogonaux XY, XZ et YZ. Chaque cercle est centré sur la sphère et utilise
son rayon.

Le nombre total de points est réparti entre les trois cercles ; il n'est pas
nécessaire qu'il soit divisible par trois.

## Autres réglages du modificateur

| Paramètre | Rôle | Valeur initiale |
|---|---|---:|
| **Nombre de points** | Nombre de points avant filtrage, sauf pour l'icosphère | 1 000 |
| **Table** | Multiplicateur utilisé pour les liens | 2 |
| **Rayon sphere** | Rayon de la sphère de répartition | 1 |
| **Afficher les liens** | Affiche ou masque les segments | Activé |
| **Rayon des liens** | Épaisseur des segments | 0,002 |
| **Afficher les points** | Affiche ou masque les points sélectionnés | Désactivé |
| **Rayon des points** | Taille des points visibles | 0,01 |
| **Afficher les numeros** | Affiche les indices d'origine des points sélectionnés | Désactivé |
| **Taille des numeros** | Taille des étiquettes | 0,1 |

Les numéros sont orientés vers la caméra utilisée lors de la création du
groupe. Leur génération peut être lente lorsque beaucoup de points sont
affichés. Les réglages propres aux répartitions sont décrits dans les
sections correspondantes ci-dessus.

## Si aucune ligne n'apparaît

1. Vérifier que **Afficher les liens** est activé et que **Rayon des liens**
   est suffisamment grand.
2. Si un filtre est actif, essayer **Modulo sur selection** : sinon, tous les
   liens peuvent être masqués lorsque leurs extrémités ne passent pas le filtre.
3. Essayer une autre **Table** : avec la valeur 1, tous les liens sont de
   longueur nulle.
4. Vérifier que le filtre retient au moins deux points.
