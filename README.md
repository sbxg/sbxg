SBXG Core
=========

Dépendances
-----------

SBXG core a besoin :
- de `make` ;
- d'un compilateur natif (gcc) ;
- d'un cross-compilateur arm (arm-gcc) ;
- de `repo` : https://source.android.com/source/downloading.html#installing-repo.



Build
-----

1. Initialiser SBXG pour une board

      make BOARD=$myboard init

   où $myboard peut prendre une des valeurs parmi :
      - Cubieboard2
      - Cubietruck

2. Synchroniser les dépôts de SBXG [OPTIONNEL]

   Cette étape est faite automatiquement par le `make init`, mais il peut être nécessaire
   de le refaire à l'occasion

      make sync

3. Lancement du build

      make

   Le résultat est une image générique, stockée dans le dossier `images/`.
   Il peut être nécessaire de la spécialiser (voir le dépôt ansible-specializer).



Étapes du build
---------------

Le tableau ci-dessous résume les principales étapes du build,
qui peuvent ainsi être effectuées indépendemment.

+------------------------------+-----------------------+
|            Étape             |       Commande        |
+------------------------------+-----------------------+
| Génération de u-boot         | make u-boot           |
| Auto-configuration du kernel | make kernel_defconfig |
| Compilation du kernel        | make kernel_compile   |
| Deboostrap                   | make debootstrap      |
| Préparation de l'image flash | make prepare_sdcard   |
+------------------------------+-----------------------+



