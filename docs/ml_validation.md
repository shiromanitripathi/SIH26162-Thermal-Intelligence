\# ML Validation and OSM Enrichment Experiment



\## Purpose



This document records the ML validation work performed on the FIRMS spatial dataset and the controlled experiment evaluating whether real OpenStreetMap (OSM) context improves classification performance.



The experiment is intended for pipeline development and model benchmarking. The current target labels are heuristic FIRMS-derived labels, not independently verified industrial-fire ground truth.



\## Data



\- Source: NASA FIRMS VIIRS 375 m S-NPP standard archive

\- Raw FIRMS observations: 1,739,550

\- Spatial grid cells: 644,550

\- OSM-covered FIRMS grid cells used for the controlled experiment: 67,273

\- OSM coverage was derived from 468 persisted real OSM tile context files.

\- Each OSM-covered `grid\_id` was unique and matched exactly to one FIRMS spatial cell.



\## Target Labels



The multiclass target is heuristic and is derived from FIRMS behavioral features:



\- `0` = vegetation/agricultural fire

\- `1` = industrial fire candidate

\- `2` = persistent thermal source

\- `3` = other/ephemeral hotspot



These categories should not be interpreted as independently validated ground truth. In particular, a FIRMS hotspot does not by itself establish that an industrial fire occurred.



\## Leakage Audit



Several features are directly or indirectly involved in the heuristic target construction and can therefore make model scores overly optimistic.



\### Direct dependencies



\- `active\_days`

\- `persistence\_days`

\- `night\_ratio`

\- `type\_2\_count`

\- `mean\_frp`



\### Derived dependencies



\- `recurrence\_ratio`

\- `obs\_per\_active\_day`

\- `type\_2\_ratio`



The controlled leakage-reduced experiment removes these eight features. However, the remaining `observation\_count`, `day\_observations`, and `night\_observations` features still contain mathematical information related to `night\_ratio`. Therefore, the reduced experiment should be treated as a diagnostic leakage reduction, not proof of independent ground-truth validation.



\## Controlled OSM Comparison



The FIRMS-only and FIRMS+OSM experiments use:



\- the same 67,273 OSM-covered cells

\- the same target labels

\- the same spatial train/validation/test split

\- the same five models

\- the same evaluation metrics



The spatial split uses 0.10-degree spatial blocks and prevents the same spatial block from appearing across train, validation, and test sets.



\### Full FIRMS vs FIRMS + OSM



| Model | FIRMS Macro F1 | FIRMS Balanced Accuracy | FIRMS + OSM Macro F1 | FIRMS + OSM Balanced Accuracy |

|---|---:|---:|---:|---:|

| Logistic Regression | 0.7471 | 0.9486 | 0.7573 | 0.9619 |

| Decision Tree | 0.9858 | 0.9966 | 0.9858 | 0.9966 |

| Random Forest | 0.9965 | 0.9933 | 0.9862 | 0.9735 |

| HistGradientBoosting | 0.9799 | 0.9966 | 0.9799 | 0.9966 |

| XGBoost | 0.9774 | 0.9948 | 0.9774 | 0.9948 |



\### Interpretation



Adding real OSM context did \*\*not produce a consistent improvement\*\* in classification performance under this controlled spatial evaluation.



\- Logistic Regression improved modestly.

\- Random Forest performance decreased.

\- Decision Tree, HistGradientBoosting, and XGBoost produced unchanged classification metrics in this comparison.



Therefore, the experiment does not support the claim that OSM improves the classifier in its current form.



\## Untouched Test Evaluation



A separate evaluation trained on the development data (training + validation) and evaluated once on the untouched spatial test set was also performed for the leakage-reduced feature sets.



\### Leakage-reduced FIRMS vs FIRMS + OSM



| Model | FIRMS Macro F1 | FIRMS Balanced Accuracy | FIRMS + OSM Macro F1 | FIRMS + OSM Balanced Accuracy |

|---|---:|---:|---:|---:|

| Logistic Regression | 0.6847 | 0.8694 | 0.6819 | 0.8617 |

| Decision Tree | 0.7915 | 0.7750 | 0.7796 | 0.7582 |

| Random Forest | 0.8250 | 0.7867 | 0.8127 | 0.7704 |

| HistGradientBoosting | 0.8300 | 0.9156 | 0.8236 | 0.9063 |

| XGBoost | 0.8408 | 0.8928 | 0.8346 | 0.8873 |



On this untouched test evaluation, adding OSM again did not improve any of the five models.



\## Feature Importance



For the leakage-reduced XGBoost comparison, the five OSM features together contributed approximately 2.34% of the model's built-in feature importance in the FIRMS+OSM experiment.



The largest individual contributors remained FIRMS-derived features, particularly `observation\_count`, `night\_observations`, and `std\_frp`.



Feature importance indicates model usage, not causal importance, and should not be interpreted as proof that OSM is or is not scientifically relevant.



\## Recommended Role of OSM



Based on the current controlled results, OSM should be treated primarily as \*\*geospatial context and investigation evidence\*\* rather than as a required primary classifier input.



Examples of contextual use include:



\- proximity to mapped industrial features

\- nearby power infrastructure

\- nearby man-made features

\- spatial investigation and analyst prioritization

\- supporting evidence alongside persistence and thermal behavior



OSM proximity alone should not be treated as proof of an industrial fire.



\## Scientific and Evaluation Limitations



1\. FIRMS detections are observations of thermal anomalies, not confirmed industrial-fire events.

2\. The current multiclass target is heuristic and FIRMS-derived rather than independently validated ground truth.

3\. The leakage-reduced feature set still retains mathematically related observation-count features.

4\. Repeated observations from the same physical source can create dependence between samples.

5\. Spatial proximity and temporal recurrence can introduce evaluation leakage if row-level random splitting is used.

6\. The current metrics measure agreement with the heuristic labeling scheme; they should not be presented as real-world industrial-fire classification accuracy.

7\. OSM coverage is incomplete relative to all 644,550 FIRMS spatial cells, so the controlled OSM comparison is restricted to the verified 67,273-cell overlap.



\## Final Conclusion



> Adding real OSM context did not produce a consistent improvement in classification performance under the controlled spatial evaluation.



> The current labels are heuristic/weak labels, not independently verified ground truth; therefore the reported metrics measure agreement with the current labeling scheme rather than real-world industrial-fire accuracy.



> OSM is currently better positioned as contextual geospatial evidence for investigation and prioritization than as a demonstrated classifier-performance enhancement.



\## Reproducibility



The experiment scripts are stored in `scripts/`:



\- `compare\_firms\_osm.py` — controlled FIRMS-only vs FIRMS+OSM comparison

\- `evaluate\_test.py` — untouched spatial test evaluation

\- `feature\_importance.py` — leakage-reduced XGBoost feature-importance analysis



The ML configuration and spatial splitting logic remain under `src/ml/`.

