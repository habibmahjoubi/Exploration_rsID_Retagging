# Exploration — "Fausse nouveauté" par retagging de rsID (dbSNP)

Piste explorée pour un article original réutilisant l'infrastructure existante
(Article 1 = `llm-mr-discovery-genomics`, Papier A = artefact taxid, Papier B = KDCR).

## Idée

Le Papier A montre qu'un lookup taxid *courant* fabrique de la fausse nouveauté
quand l'identifiant a été renuméroté entre versions de la taxonomie NCBI
(39/56 candidats testés = fausse nouveauté par renumérotation).

dbSNP a un phénomène structurellement identique sur un système d'identifiants
totalement différent : un rsID peut être fusionné dans un autre rsID au fil des
builds (`RsMergeArch` historiquement, remplacé aujourd'hui par le champ
`dbsnp1_merges` de chaque enregistrement RefSNP JSON). Hypothèse : une
ré-annotation "historique" d'anciens appels de variants avec un build dbSNP
courant ferait apparaître comme "nouveaux" des variants qui avaient déjà un
rsID à l'époque, simplement fusionné depuis — exactement le mécanisme du
Papier A, mais en génomique clinique germinale (domaine du pipeline
nf-core/sarek d'Article 1) plutôt qu'en métagénomique virale.

## Disponibilité des données (vérifiée 2026-08-23)

- **Ancien fichier `RsMergeArch.bcp.gz`** (builds <=151) : chemin FTP legacy
  mort (404 confirmé), cohérent avec la dépréciation du système en 2018.
- **Mécanisme actuel (meilleur)** : chaque enregistrement RefSNP JSON expose
  un champ `dbsnp1_merges` — liste de `{merged_rsid, revision (build), merge_date}`.
  Plus riche que `merged.dmp` (Papier A) : chaque fusion est datée et versionnée
  individuellement. Vérifié en direct sur rs268 et sur l'échantillon chr20 ci-dessous.
- **Snapshots de builds historiques réels** : `ftp.ncbi.nlm.nih.gov/snp/archive/`
  contient des builds complets b152-b157 (oct. 2021 -> avr. 2025) ; `pre_build152/`
  étend la couverture jusqu'à ~2015-2020. Équivalent du `taxdump_archive` utilisé
  pour les 13 bases Kraken2 de Papier B.
- **Fichiers dbSNP par chromosome** : `refsnp-chr20.json.bz2` (~9,0 Go compressé),
  accessible par range-fetch HTTP (HTTP 206 confirmé), même technique que le
  byte-range partiel déjà utilisée pour PRJNA1026487 dans Papier B.

## Ce qui a été fait dans cette session

1. **Échantillon dbSNP chr20 brut** (`results/01_...txt`) : premier chunk de
   30 Mo compressé (~15 333 enregistrements) -> 73,75 % ont un historique de
   fusion. **Biaisé** : le fichier est trié par numéro de rsID, donc cet
   échantillon ne contient que les rsID les plus anciens (~2000-2001) —
   surreprésente les variants très étudiés, pas un taux représentatif.

2. **VCF de vérité GIAB HG002 (chr20)** téléchargé en entier depuis NIST
   (`HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz`, source publique, même
   échantillon HG002 que celui utilisé par Article 1) et filtré sur chr20 :
   **85 951 positions de variants réels** (`data/chr20_giab_HG002_v4.2.1_truth.vcf.gz`).
   Constat : la colonne ID du VCF GIAB est systématiquement "." (pas de rsID
   annoté nativement — normal, c'est un jeu de vérité terrain, pas une
   annotation dbSNP) : le croisement doit donc se faire par POSITION génomique
   (SPDI dbSNP, 0-based -> converti en 1-based pour matcher le VCF), pas par ID.

3. **Croisement position-par-position** (`scripts/cross_reference.py`) : chunk
   dbSNP chr20 élargi à 400 Mo compressé (~8 Go décompressés en streaming, sans
   écrire le fichier intermédiaire sur disque), positions chr20 (NC_000020.11)
   extraites de chaque enregistrement RefSNP et croisées avec les 85 951
   positions réelles GIAB.

   **Résultat (voir `results/02_...txt` pour le détail complet)** : ce chunk
   (315 939 enregistrements RefSNP) touche déjà 65 347 / 85 951 (76,0 %) des
   positions de variants réels HG002 chr20. Parmi ces variants réels touchés,
   **48 217 (73,79 %) reposent sur un rsID qui a historiquement absorbé un ou
   plusieurs anciens identifiants fusionnés** (dates de fusion réelles allant
   de 2001 à 2009 dans les exemples). C'est l'équivalent, à l'échelle chr20 et
   avec un système d'identifiant différent (rsID vs taxid), du ratio "39/56"
   du Papier A — première confirmation empirique, sur données réelles, que le
   pool de candidats pour cette piste est large et non anecdotique.

4. **Panel de candidats complet extrait** (`results/candidate_panel_full_48217.csv.gz`) : les 48 217 candidats
   (rsID courant, position chr20, rsID historiques fusionnés + dates) sont maintenant sauvegardés
   sous forme structurée (script : `scripts/build_candidate_panel.py`), pas seulement comptés.

5. **Vérification empirique naïf-vs-merge-aware, sur un panel pilote de 30 candidats**
   (`scripts/verify_naive_vs_mergeaware.py`, résultat : `results/03_naive_vs_mergeaware_verification.json`) :
   protocole calqué sur le Papier A. Pour 30 candidats tirés aléatoirement (seed=42) du panel de 48 217,
   requête live sur l'API RefSNP pour l'ANCIEN rsID (celui qui a été fusionné) :

   - **Verdict "naïf"** : 30/30 des anciens rsID n'ont **aucune donnée `primary_snapshot_data` propre**
     (pas de position, pas d'allèle) — un consommateur naïf (jointure simple par rsID, table statique
     de "rsID valides") les traiterait comme des identifiants inconnus/orphelins, alors que la variante
     qu'ils désignaient existe bel et bien aujourd'hui.
   - **Verdict "merge-aware"** : 30/30 résolvent correctement via `merged_snapshot_data.merged_into`
     vers le rsID courant attendu (validation croisée à 100 % entre deux champs indépendants du
     même enregistrement — `dbsnp1_merges` côté rsID courant et `merged_snapshot_data` côté ancien rsID).

   **C'est la première démonstration directe du mécanisme de "fausse absence/fausse nouveauté"**
   (pas seulement "il existe un historique de fusion quelque part") — équivalent du protocole
   naïf/merge-aware du Papier A §3.2-3.3, mais encore à l'échelle pilote (n=30, pas 48 217).

6. **Impact aval — deux tests, un négatif honnête et un positif confirmé** :

   - **Test A (négatif, `results/04_...1000G.txt`)** : recherche des rsID récemment
     fusionnés (2014-2016) dans 1000 Genomes Phase 3 (2013) — 0/8 trouvés. Affine
     l'hypothèse : par convention dbSNP ("high merged into low"), une ressource
     établie AVANT la création de l'identifiant fusionné n'a jamais pu l'utiliser —
     le risque n'est pas générique à "toute vieille ressource".

   - **Test B (POSITIF CONFIRMÉ, `results/05_...GATK_bundle_STALE_CONFIRMED.txt`)** :
     croisement des 2 788 candidats à fusion 2014-2017 contre le vrai bundle GATK
     `Homo_sapiens_assembly38.dbsnp138.vcf.gz` (référence "known-sites" standard,
     GRCh38, encore massivement déployée telle quelle en production aujourd'hui) :

     **217 / 2 788 (7,78 %) montrent que le bundle rapporte encore l'ANCIEN rsID**,
     alors que dbSNP l'a depuis officiellement fusionné dans un autre. C'est la
     démonstration concrète, sur un artefact réellement utilisé en production, du
     mécanisme de "fausse absence" (une jointure naïve entre un VCF annoté avec ce
     bundle et une ressource moderne comme ClinVar échouerait silencieusement).

     **C'est le chaînon manquant avec Papier B/KDCR** : ce bundle figé est un exemple
     concret et déjà déployé du phénomène de "référence gelée pour stabilité de
     validation" que KDCR théorise — avec un coût mesuré (~8 %) plutôt que supposé.

7. **Comparaison multi-version (`results/06_multiversion_bundle_trend.txt`)** : même
   panel de 2 788 candidats testé contre un 2e bundle réel indépendant, dbSNP144
   (utilisé par le NCI Genomic Data Commons, juin 2015) — taux d'IDs périmés :
   **7,78 % (138) → 0,68 % (144)**, une vraie tendance temporelle à deux points,
   dans le sens attendu. Renforce directement le lien avec Papier B/KDCR (dérive
   graduelle et mesurable, pas binaire figé/à jour).

8. **Couverture complète, chiffre définitif (`results/08_full_coverage_FINAL.txt`)** :
   25 938 655 enregistrements dbSNP chr20 traités en flux complet (~1h). **Taux de
   fusion réel : 47,78 %** (49 730/104 082 positions GIAB touchées) — nettement
   plus bas que l'estimation initiale biaisée (73,79 %), confirmant précisément
   le biais anticipé (tri par rsID surreprésente les variants anciens). La
   conclusion qualitative tient (près d'1 variante sur 2), le chiffre précis est
   corrigé. **Le panel "impact en aval" (05-07) est encore basé sur l'échantillon
   partiel, pas cette couverture complète — prochaine étape si on continue.**

9. **Matching exact-allèle (`results/07_allele_exact_validation.txt`)** : le
   panel de candidats et les tests bundles GATK138/dbSNP144 ont été refaits en
   matching POS+REF+ALT (pas juste position). Résultat : robuste (8,24 %/1,73 %
   au lieu de 7,78 %/0,68 %) ET résout le mystère des ~100 cas "identifiant
   différent" (tombent à 0 — c'étaient des faux positifs multi-alléliques du
   matching par position seule). Manuscrit et figures mis à jour en conséquence.

## Limites connues à ce stade (à traiter honnêtement si l'idée est poursuivie)

- Le fichier dbSNP est trié par rsID, pas par position : même le chunk de
  400 Mo ne couvre qu'une fraction (les rsID les plus anciens/bas) du spectre
  complet -> le taux de recoupement mesuré ici est une **borne / première
  estimation**, pas un taux exhaustif sur les 85 951 variants GIAB.
- Matching par position seule (pas par allèle exact) : suffisant pour la
  plupart des SNV, plus approximatif pour les indels (représentation SPDI vs
  VCF peut différer sur l'ancrage de base).
- Le test naïf-vs-merge-aware (point 5) vérifie le mécanisme *à l'intérieur même* de dbSNP
  (absence de `primary_snapshot_data` propre sur l'ancien ID) — c'est une preuve solide du
  mécanisme, mais pas encore une démonstration d'un échec *en aval*, dans un vrai pipeline ou
  un vrai croisement avec une autre ressource (ClinVar, gnomAD, un rapport clinique archivé).
  Un vrai papier voudrait montrer l'impact concret sur un cas d'usage réel, pas seulement la
  structure interne de dbSNP.
- Panel pilote n=30 seulement (sur 48 217 candidats déjà extraits) — à étendre avant de
  parler de "taux" définitif, mais le 30/30 est un signal déjà net.
- Pas encore de VCF réellement produit par le pipeline sarek d'Article 1
  (Nextflow/Docker non disponibles dans cet environnement) : le VCF utilisé
  ici est le jeu de vérité NIST/GIAB, pas une sortie sarek annotée dbSNP —
  substitution raisonnable pour un test de faisabilité, à remplacer par un
  vrai run sarek + annotation dbSNP si l'article est lancé pour de vrai.

## Plan de papier et manuscrit

- `brief_projet.md` — positionnement, contribution centrale, checklist avant soumission
  (dans le même style que les briefs des autres projets).
- `Manuscript_Draft.docx` — premier brouillon structuré (titre de travail : "When Frozen
  dbSNP Bundles Outlive Their Merges: A Reference-Identifier Retagging Artifact in
  Genomic Variant Annotation"), calqué sur la structure de Papier A (accepté JBCB) :
  Abstract, 1. Introduction, 2. Illustrative Examples (tableau à 3 cas réels),
  3. Background (mécanisme de fusion dbSNP), 4. Analysis Protocol (4.1-4.4),
  5. Results (5.1-5.5, avec les vrais tableaux de chiffres), 6. Impact and Implications
  (lien explicite avec Papier A et Papier B/KDCR), 7. Limitations, 8. Recommendations,
  Data/Code Availability, Acknowledgments, Conflict of Interest, References.
  Généré via `scripts/build_manuscript_docx.py` (à ré-exécuter après modif du script,
  jamais éditer le .docx à la main tant qu'on est à ce stade de brouillon).
  **Auteur/affiliation, titre définitif, journal cible et références [3]-[6] encore
  à vérifier/compléter** — placeholders explicitement marqués dans le document.

## Mise en forme et restructuration (dernière passe)

- **Mise en forme homogène** : police Times New Roman partout (corps de texte,
  titres, tableaux, légendes, références), texte en noir (plus de bleu théorique
  Word par défaut sur les titres), titres en gras, tableaux en style "Table Grid"
  (grille noire simple, sans remplissage coloré ni bandes alternées).
- **Restructuration** : les anciennes sections séparées "6. Impact and
  Implications" / "7. Limitations" / "8. Recommendations" ont été fusionnées en
  une seule **"6. Discussion"** avec 3 sous-sections (6.1 Generalizing Paper A's
  mechanism, 6.2 Limitations, 6.3 Implications for practice) — convention plus
  standard pour ce type d'article que des sections top-niveau séparées. Tous les
  renvois internes ("Section 7", "voir Limitations", etc.) ont été corrigés en
  conséquence. Vérifié visuellement (conversion PDF + rendu image des pages).

## Contenu du dossier

- `README.md` — ce fichier
- `data/chr20_giab_HG002_v4.2.1_truth.vcf.gz` — VCF de vérité GIAB HG002,
  filtré chr20 uniquement (85 951 variants), compressé
- `scripts/cross_reference.py` — script de croisement position dbSNP <-> GIAB
- `results/01_dbsnp_chr20_sample_merge_rate.txt` — stats sur l'échantillon brut
- `results/02_cross_reference_giab_dbsnp_chr20.txt` — résultat du croisement réel
