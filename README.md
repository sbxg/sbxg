SBXG Core
=========

1 Introduction
--------------

SBXG est  un  projet  visant à  produire des  3  composants  logiciels
fonctionnels différents :

	- un boot de type UBOOT pour démarrer une plateforme embarquée.
	- un noyau Linux s'exécutant sur la plateforme embarquée.
	- un rootfs  contenant le minimum de  composants logiciels de type
	Debian, à savoir un shell de login et un démon sshd.

A l'issue  de la production   logicielle, un  carte  SD ou  un  disque
bootable est préparé avec une configuration suivante:

	- un compte root initialisé sans mot de pass
	- un shell de login
	- un démon  sshd en attente   de connexion sur  le port  eth0 avec
	autorisation de login root
	- aucune autre application n'est installée par choix.

En  effet, la spécialisation de l'équipement  est assurée par d'autres
outils indpépendants de SBXG. Ce choix  vise à proposer un ensemble de
scripts  simples à maintenir dans le cadre  du projet  décrit ici.  La
spécialisation   de  l'équipement,  l'ajout   de  composants logiciels
complémentaires  permettant  de    configurer l'equipement  pour   une
activité spécifique (serveur, gateway, point d'accès Wifi telecom) est
assurée par d'autres composants de type Ansible.

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
croisée, il convient  par conséquent d'installer  un cross compilateur
GCC  (arm-gcc), les packages Debian étant  disponibles  dans les repos
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

Enfin,   l'outil repo de   Google   est  utilisé, il  convient   de le
télécharger en lien avec la doc fournie à l'adresse suivante:

https://source.android.com/source/downloading.html#installing-repo.

3 Organisation des dépots GIT
-----------------------------

Afin  de  maitriser la complexité,  les éléments fonctionnels suivants
sont  installés    dans   quatre  dépots     git  indépendants.     La
synchronisation globale des  dépots permettantr d'assurer la cohérence
est effectuée à travers l'outils 'repo' de Google.

3.1 Elément   principal  (core)  

Cet élément   est le  coeur  du   projet (system-builder-ng.git).   Il
contient l'ensemble des scripts permettant  d'assurer les fonctions de
production logicielle.


3.2 Elément de board

Cet élément   contient les références de   toutes les cartes utilisées
dans  le projet,  seula la description   des cartes est effectuée à ce
niveau à  travers  la valorisation  de   variable de  type shell,  ces
dernières étant utilisées par la  suite dans la production  logicielle
par les scripts et Makefiles.

3.3 Elément noyau Linux

Cet élément contient les  références des noyaux   Linux mis en  oeuvre
pour les différentes boards décrites précédement.

3.4 Elément de synchornisation (manifest)

Cet élément est  l'élément fédérateur,  il  assure la  lien entre  les
trois précédents.

4 Build 
-------

Build : phase 1
---------------

   L'organisation des dépots git est telle  qu'il n'est pas nécessaire
   de les  télécharger tous en premier lieu.   En effet,  une cible du
   Makefile   est en  charge  de   cette activité, si    bien que pour
   initialiser la  premiere   fois     un  projet, seul    le    dépot
   system-builder-ng doit être téléchargé comme le montre l'exemple ci
   dessous (sous réserve de disposer des clés d'accès!)


mkdir /tmp/SBXG
cd /tmp/SBXG

lacroix@vm-jessie-x86-amd64-3:/tmp/SBXG$ git clone ssh://gitolite3@bie91-1-82-227-34-59.fbx.proxad.net:1024/public/system-builder-ng                 
Cloning into 'system-builder-ng'...
Enter passphrase for key '/home/lacroix/.ssh/id_dsa': 
remote: Counting objects: 185, done.
remote: Compressing objects: 100% (96/96), done.
remote: Total 185 (delta 111), reused 144 (delta 88)
Receiving objects: 100% (185/185), 47.24 KiB | 0 bytes/s, done.
Resolving deltas: 100% (111/111), done.
Checking connectivity... done.


Build : phase 2 Initialiser SBXG pour une board
-----------------------------------------------

cd /tmp/SBXG/system-builder-ng	
make BOARD=$myboard init

   ou $myboard peut prendre une des valeurs parmi :
      - Cubieboard2
      - Cubietruck

Build : phase 3. Synchroniser les dépots de SBXG [OPTIONNEL]
------------------------------------------------------------

   Cette étape est faite automatiquement  par la commande `make init`,
   mais il peut être nécessaire de le refaire à  l'occasion

make sync

Build : phase 4. Lancement du build
-----------------------------------

make all

   Le   résultat  est une  image générique,    stockée dans le dossier
   `images/`. Il peut être nécessaire de la spécialiser (voir le dépot
   ansible-specializer).

Build : phase 5 Etapes du build
--------------------------------

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



