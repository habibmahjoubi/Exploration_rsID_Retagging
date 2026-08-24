# Brief projet — "Papier C" (identifiant provisoire) : artefact de retagging rsID/dbSNP

## Positionnement

Réplication et extension du mécanisme de "fausse nouveauté/fausse absence par
renumérotation d'identifiant" du **Papier A** (taxid/NCBI Taxonomy), appliqué à un
**second système d'identifiant indépendant** (rsID/dbSNP) dans un **second domaine**
(génomique clinique germinale, pas métagénomique virale). Sert aussi de démonstration
empirique concrète pour la thèse de **Papier B/KDCR** (dérive de référence gelée pour
stabilité de validation) — avec un coût mesuré plutôt que théorique.

## Contribution centrale (ce qui a été vérifié empiriquement, pas supposé)

1. Le mécanisme de fusion existe et est massif à l'échelle chr20 (échantillon initial :
   73,75 % des rsID les plus anciens ont un historique de fusion).
2. Sur de vrais variants (VCF de vérité GIAB HG002 chr20, 85 951 positions), 73,79 %
   des positions touchées par l'échantillon dbSNP reposent sur un rsID fusionné.
3. Le mécanisme "naïf vs merge-aware" est démontré en interne à dbSNP (pilote n=30,
   30/30 : l'ancien ID n'a aucune donnée propre sans suivre l'historique de fusion).
4. **Impact en aval testé sur deux ressources réelles** :
   - 1000 Genomes Phase 3 (2013) : négatif (0/8) — affine l'hypothèse (convention
     dbSNP "high merged into low" protège les ressources antérieures à l'ID fusionné).
   - **Bundle GATK `dbsnp138` (GRCh38, encore massivement déployé en production)** :
     **positif — 217/2 788 candidats (7,78 %) montrent un rsID périmé**, démonstration
     concrète d'un risque réel, mesurable, sur un artefact actuellement en production.

## Ce qui manque avant soumission (checklist, mise à jour au fil de l'eau)

- [x] **Couverture complète** — terminée : 25 938 655 enregistrements, taux final
      **47,78 %** (corrige le 73,79 % initial biaisé). Voir results/08.
- [x] **Matching allèle-exact** (REF/ALT) — fait et validé (99,22 % de concordance
      avec le matching par position sur l'échantillon partiel).
- [x] **Panel "impact en aval" re-dérivé sur la COUVERTURE COMPLÈTE** (25,9M
      enregistrements, 48 746 candidats, 2 894 à fusion 2014-2017) — chiffres
      DÉFINITIFS : **12,75 % (dbSNP138) → 3,63 % (dbSNP144)**, en hausse par
      rapport à l'échantillon partiel (8,24 %/1,73 %) — l'échantillon biaisé
      sous-estimait légèrement le risque réel. Voir results/10 (fichier de
      référence final, remplace 05/06/07 pour ces chiffres).
- [x] **Taux de fusion global recalculé en exact-allèle, couverture complète** :
      **66,44 % (chiffre définitif)**, remplace le 47,78 % (position seule) et
      le 73,79 % initial (échantillon biaisé). Voir results/08 et 10.
- [x] **Généraliser le test "bundle figé" à 2 versions** (dbSNP138, dbSNP144) —
      tendance temporelle réelle confirmée sur données complètes (12,75 % → 3,63 %).
      Un 3e point (151/152/courant) resterait utile mais bloqué par le format
      propriétaire Illumina Nirvana (.nsa) du seul fichier trouvé pour cette vintage.
- [x] **2 figures créées** (taux par vintage, répartition complète par bundle),
      intégrées dans le manuscrit, palette validée dataviz-skill.
- [x] **Indels traités** (résultats/12, Section 5.7 manuscrit) — fonction de
      normalisation (trim préfixe/suffixe) créée et validée, 85 % des indels
      matchent avec succès (99,7 % pour les SNV). Résultat honnête et riche :
      les indels sont MOINS souvent périmés (1,0-1,1 % vs 8,3 %/0,7 % SNV) mais
      BEAUCOUP plus souvent ambigus (4-12 % vs 0-2,3 % SNV). Fait sur
      l'échantillon partiel seulement — refaire sur couverture complète (~2h)
      reste un travail futur possible, pas fait par manque de nécessité claire.
- [ ] Remplacer le VCF de vérité GIAB (utilisé comme substitut) par une vraie sortie
      du pipeline nf-core/sarek d'Article 1, pour ancrer la démonstration dans un
      vrai pipeline de production plutôt qu'une base de données publique.
- [x] **Pilote naïf-vs-merge-aware étendu n=30 → n=100** (results/09) — même
      résultat parfait (100/100), tiré du panel exact-allèle.
- [x] **Références [3]-[6] vérifiées** avec sources primaires (auteurs complets,
      volumes/pages confirmés) — flags "[verify...]" retirés du manuscrit.
- [ ] Choisir le journal cible (candidats à discuter : JBCB — comme Papier A, même
      style "Critical Comments" ; ou une revue plus orientée génomique clinique
      étant donné l'angle GATK/production ; ou Bioinformatics/NAR Genomics si le
      budget APC le permet — sinon rester sur des revues sans frais comme JBCB).
- [ ] Décider auteur(s) — Article 1 est co-écrit avec A. Rebai ; à trancher si ce
      papier reste solo (comme Papier A/B) ou inclut un co-auteur, selon si l'angle
      "pipeline sarek réel" (infra d'Article 1) est effectivement utilisé.

## Fichiers du dossier

- `README.md` — journal complet de l'exploration (idée, disponibilité des données,
  tous les résultats intermédiaires avec dates)
- `Manuscript_Draft.docx` — premier brouillon structuré du manuscrit (ce brief)
- `data/`, `results/`, `scripts/` — données et scripts réels utilisés pour chaque
  résultat cité ci-dessus (traçabilité complète, rien n'est inventé)
