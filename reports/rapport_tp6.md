# CI6 : CI/CD pour systèmes ML + réentraînement automatisé + promotion MLflow
**Exercice 1 : Mise en place du rapport et vérifications de départ**

**Question 1.a**
**Question 1.b**
(capture/1.png)
Les logs confirment que l’API démarre sans erreur et que les services sont opérationnels.
(capture/2.png)

**Question 1.c**
(capture/3.png)
(capture/4.png)

**Question 1.d**
Un transcript terminal montrant docker compose up -d et docker compose ps : 

(capture/5.png)
(capture/1.png)

Une capture MLflow montrant la version
Production au début du TP:

(capture/4.png)

**Exercice 2 : Ajouter une logique de décision testable (unit test)**
**Question 2.a** 
fichier nano services/prefect/compare_utils.py crée :  
(capture/6.png)

**Question 2.b** 
fichier tests/unit/test_compare_utils.py crée 

**Question 2.c** 
(capture/7.png)

**Question 2.d** 
### 2. Tests unitaires de la logique de promotion

Les tests unitaires ont été exécutés localement à l’aide de pytest :

```
vboxuser@Linux:~/tp1-sysml-firiel$ pytest -q
..                                                                                                               [100%]
2 passed in 0.32s

```
(capture/7.png)

## pourquoi on extrait une fonction pure pour les tests unitaires : 

La logique de décision de promotion a été extraite dans une fonction pure afin de pouvoir être testée de manière simple et fiable.  
Tester directement Prefect ou MLflow introduirait des dépendances lourdes (services externes, état du registry, environnement Docker), ce qui rendrait les tests fragiles et difficiles à maintenir.

En isolant la règle métier dans une fonction indépendante, on garantit des tests rapides, déterministes et faciles à comprendre, tout en sécurisant un point critique du pipeline MLOps, la décision de promotion d’un modèle.

**Exercice 3 : Créer le flow Prefect train_and_compare_flow (train → eval → compare → promote)**

**Question 3.a.**
fichier services/prefect/train_and_compare_flow.py crée

**Question 3.b.**
commande lancée `$ docker compose exec prefect python train_and_compare_flow.py` 

résultat :

(capture/8.png)

**Question 3.c.**
(capture/9.png)
(capture/10.png)
(capture/11.png)

**Question 3.d.**
Extrait des logs :
```
11:32:21.123 | INFO    | Task run 'evaluate_production-cc7' - Finished in state Completed()
[COMPARE] candidate_auc=0.6424 vs prod_auc=0.9441 (delta=0.0100)
[DECISION] skipped
11:32:21.275 | INFO    | Task run 'compare_and_promote-857' - Finished in state Completed()
[SUMMARY] as_of=2024-02-29 cand_v=4 cand_auc=0.6424 prod_v=3 prod_auc=0.9441 -> skipped
11:32:21.412 | INFO    | Flow run 'tomato-bullfinch' - Finished in state Completed()

```
(capture/8.png)

Une capture de l'interface MLflow montre qu'une nouvelle version 4 a été crée, tandis que la version précédente a été automatiquement archivée. Cependant, la nouvelle version n'est pas déployée en production car ses performances sont moins bonnes que celles de l'ancien modèle. L'ancien modèle reste donc en production et le statut de la nouvelle version reste sur "None".
(capture/10.png)
(capture/11.png)

## Une phrase expliquant pourquoi on utilise un delta :
L’utilisation d’un delta permet d’éviter de promouvoir un modèle pour des gains de performance insignifiants.  
Dans un contexte réel, de petites variations d’AUC peuvent provenir du bruit statistique ou du split des données, et ne traduisent pas une amélioration réelle du modèle.

En imposant un seuil minimal d’amélioration, on garantit que la promotion en Production correspond à un gain mesurable et stable, ce qui limite les changements inutiles et renforce la fiabilité du pipeline MLOps.

**Exercice 4 : Connecter drift → retraining automatique (monitor_flow.py)**

**Question 4.a.**
fichier services/prefect/monitor_flow.py mis à jour.

**Question 4.b.**
(capture/12.png)
Décision : drift_share=0.06 >= 0.02 → Retraining déclenché !

**Question 4.c.**

Une capture (ou extrait) du rapport Evidently HTML (fichier reports/evidently/drift_*.html) :
(capture/13.png)

Un extrait de logs montrant le message RETRAINING_TRIGGERED ... et le résultat promoted/skipped : 
(capture/12.png)

Un drift de 6% a été détecté, dépassant le seuil de 2%. Un réentraînement a donc été déclenché, produisant un nouveau modèle. Cependant, ce modèle présente une performance dégradée (AUC=0.6424) comparée au modèle de production (AUC=0.9441). Conformément à la politique de déploiement, le modèle n'est pas promu (delta=0.01 non atteint). Ce comportement assure que seule une amélioration avérée des performances justifie le remplacement du modèle en production.

**Exercice 5 : Redémarrage API pour charger le nouveau modèle Production + test /predict**

**Question 5.a.** 

**Question 5.b.** 
Récupération d’un user_id réel : $ head -n 2 data/seeds/month_000/users.csv

Appel curl : 
```
curl -s -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"7590-VHVEG"}'
  
```
(capture/14.png)

**Question 5.c.** 
