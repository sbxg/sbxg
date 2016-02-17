SBXG Core
=========

1 Introduction
--------------

SBXG est  un  projet  visant �  produire des  3  composants  logiciels
fonctionnels diff�rents :

	- un boot de type UBOOT pour d�marrer la plateforme embarqu�e.
	- un noyau Linux 
	- un  rootfs  contenant le  minimum de  composants  de type Debian
	Jessie, �  savoir un shell  de login  et un  d�mon sshd

A l'issue  de la production   logicielle, un  carte  SD ou  un  disque
bootable est pr�par� avec une configuration suivante:

	- un compte root initialis� sans mot de pass
	- un shell de login
	- un d�mon  sshd en attente   de connexion sur  le port  eth0 avec
	autorisation de login root
	- aucune autre application n'est install�e par choix, la
	sp�cialisation de l'�quipement �tant assur�e par d'autres outils
	indp�pendants de SBXG. Ce  choix  vise � proposer un  ensemble  de
	scripts de type simple � maintenir.

2 D�pendances
-------------

Les composants logiciels suivants  doivent �tre install�s  avant tout
lancement du makefile de production.

Toutes les   informations  suivantes  partent  d'une  hypoth�se  d'une
plateforme de production logicielle  bas�e sur une distribution Debian
version Jessie,  architecture AMD64.  A ce   titre, le fichier suivant
doit contenir au minimum : 

# cat /etc/apt/sources.list

deb http://ftp.fr.debian.org/debian/ jessie main contrib non-free
deb http://security.debian.org/      jessie/updates main contrib non-free

La strat�gie retenue utilise donc une plateforme de production de type
crois�e, il convient par cons�quent  d'installer un cross  compilateur
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
etre install�s:

apt-get install  \
	autoconf \
	build-essential \
	make \
	automake 	

Enfin,  l'outil  repo de  Google  est  utilis�,   il convient  de  le
telecharger en lien avec la doc fournie � l'adresse suivante: 

https://source.android.com/source/downloading.html#installing-repo.

3 Organisation des d�pots GIT
-----------------------------

Afin de  maitriser la  complexit�, les �l�ments fonctionnels  suivants
sont install�s   dans   quatre  d�pots  git ind�pendants,    avec  une
synchronisation globale assurant  la  coh�rence des  d�pots �  travers
l'outils repo de Google.

Element   principal  (core)  

Cet �l�ment   est le  coeur  du   projet (system-builder-ng.git).   Il
contient l'ensemble des scripts permettant  d'assurer les fonctions de
production logicielle.


Element de board

Cet �l�ment contient les r�f�rences de toutes les cartes utilis�es dans
le projet, seul la description est effectu�e �  ce niveau � travers la
valorisation de variable de  type shell, ces  derni�res �tant utilis�es
par la suite dans la production logicielle.

Element noyau Linux

Cet �l�ment contient les  r�f�rences des noyaux   Linux mis en  oeuvre
pour les diff�rentes boards d�crites pr�c�dement.


Element de synchornisation (manifest)

Cet �l�ment est  l'�l�ment f�d�rateur,  il  assure la  lien entre  les
trois pr�c�dents.

4 Build 
-------

1. Initialiser SBXG pour une board

      make BOARD=$myboard init

   ou $myboard peut prendre une des valeurs parmi :
      - Cubieboard2
      - Cubietruck

2. Synchroniser les d�pots de SBXG [OPTIONNEL]

   Cette �tape est faite automatiquement par le `make init`, mais il
   peut �tre n�cessaire de le refaire � l'occasion

      make sync

3. Lancement du build

      make

   Le r�sultat est une image g�n�rique, stock�e dans le dossier
   `images/`.
   Il     peut �tre  n�cessaire de la      sp�cialiser  (voir le d�pot
   ansible-specializer).



5 Etapes du build
-----------------

Le tableau ci-dessous r�sume les principales �tapes du build,
qui peuvent ainsi �tre effectu�es ind�pendemment.

+------------------------------+-----------------------+
|           �tape              |       Commande        |
+------------------------------+-----------------------+
| G�n�ration de u-boot         | make u-boot           |
| Auto-configuration du kernel | make kernel_defconfig |
| Compilation du kernel        | make kernel_compile   |
| Deboostrap                   | make debootstrap      |
| Pr�paration de l'image flash | make prepare_sdcard   |
+------------------------------+-----------------------+



