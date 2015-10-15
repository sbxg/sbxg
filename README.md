SBXG Core
=========

1 Introduction
--------------

SBXG est  un  projet  visant à  produire des  3  composants  logiciels
fonctionnels différents :

	- un boot de type UBOOT pour démarrer la plateforme embarquée.
	- un noyau Linux 
	- un  rootfs  contenant le  minimum de  composants  de type Debian
	Jessie, à  savoir un shell  de login  et un  démon sshd

A l'issue  de la production   logicielle, un  carte  SD ou  un  disque
bootable est préparé avec une configuration suivante:

	- un compte root initialisé sans mot de pass
	- un shell de login
	- un démon  sshd en attente   de connexion sur  le port  eth0 avec
	autorisation de login root
	- aucune autre application n'est installée par choix, la
	spécialisation de l'équipement étant assurée par d'autres outils
	indpépendants de SBXG. Ce  choix  vise à proposer un  ensemble  de
	scripts de type simple à maintenir.

2 Dépendances
-------------

Les composants logiciels suivants  doivent être installés  avant tout
lancement du makefile de production.

Toutes les   informations  suivantes  partent  d'une  hypothèse  d'une
plateforme de production logicielle  basée sur une distribution Debian
version Jessie,  architecture AMD64.  A ce   titre, le fichier suivant
doit contenir au minimum : 

# cat /etc/apt/sources.list

deb http://ftp.fr.debian.org/debian/ jessie main contrib non-free
deb http://security.debian.org/      jessie/updates main contrib non-free

La stratégie retenue utilise donc une plateforme de production de type
croisée, il convient par conséquent  d'installer un cross  compilateur
GCC (arm-gcc), les packages Debian  etant  disponibles dans les  repos
standards (definies ci-dessus). Pour cela, lancer la commande suivante
:

apt-get install  \
	binutils-arm-linux-gnueabihf  \
	cpp-4.7-arm-linux-gnueabihf \
	gcc-4.7-arm-linux-gnueabihf \
	g++-4.7-arm-linux-gnueabihf \
	g++-4.7-arm-linux-gnueabihf \
	libc-bin-armhf-cross

De plus, les   composants de developpement standards suivants  doivent
etre installés:

apt-get install  \
	autoconf \
	build-essential \
	make \
	automake 	

Enfin,  l'outil  repo de  Google  est  utilisé,   il convient  de  le
telecharger en lien avec la doc fournie à l'adresse suivante: 

https://source.android.com/source/downloading.html#installing-repo.

3 Organisation des dépots GIT
-----------------------------

Afin de  maitriser la  complexité, les éléments fonctionnels  suivants
sont installés   dans   quatre  dépots  git indépendants,    avec  une
synchronisation globale assurant  la  cohérence des  dépots à  travers
l'outils repo de Google.

Element   principal  (core)  

Cet élément   est le  coeur  du   projet (system-builder-ng.git).   Il
contient l'ensemble des scripts permettant  d'assurer les fonctions de
production logicielle.


Element de board

Cet élément contient les références de toutes les cartes utilisées dans
le projet, seul la description est effectuée à  ce niveau à travers la
valorisation de variable de  type shell, ces  dernières étant utilisées
par la suite dans la production logicielle.

Element noyau Linux

Cet élément contient les  références des noyaux   Linux mis en  oeuvre
pour les différentes boards décrites précédement.


Element de synchornisation (manifest)

Cet élément est  l'élément fédérateur,  il  assure la  lien entre  les
trois précédents.

4 Build 
-------

1. Initialiser SBXG pour une board

      make BOARD=$myboard init

   ou $myboard peut prendre une des valeurs parmi :
      - Cubieboard2
      - Cubietruck

2. Synchroniser les dépots de SBXG [OPTIONNEL]

   Cette étape est faite automatiquement par le `make init`, mais il
   peut être nécessaire de le refaire à  l'occasion

      make sync

3. Lancement du build

      make

   Le résultat est une image générique, stockée dans le dossier
   `images/`.
   Il     peut être  nécessaire de la      spécialiser  (voir le dépot
   ansible-specializer).



5 Etapes du build
-----------------

Le tableau ci-dessous résume les principales étapes du build,
qui peuvent ainsi être effectuées indépendemment.

+------------------------------+-----------------------+
|           étape              |       Commande        |
+------------------------------+-----------------------+
| Génération de u-boot         | make u-boot           |
| Auto-configuration du kernel | make kernel_defconfig |
| Compilation du kernel        | make kernel_compile   |
| Deboostrap                   | make debootstrap      |
| Préparation de l'image flash | make prepare_sdcard   |
+------------------------------+-----------------------+



