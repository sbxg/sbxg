SBXG Core
=========

1 Introduction
--------------

SBXG est  un  projet  visant �  produire des  3  composants  logiciels
fonctionnels diff�rents :

	- un boot de type UBOOT pour d�marrer une plateforme embarqu�e.
	- un noyau Linux s'ex�cutant sur la plateforme embarqu�e.
	- un rootfs  contenant le minimum de  composants logiciels de type
	Debian, � savoir un shell de login et un d�mon sshd.

A l'issue  de la production   logicielle, un  carte  SD ou  un  disque
bootable est pr�par� avec une configuration suivante:

	- un compte root initialis� sans mot de pass
	- un shell de login
	- un d�mon  sshd en attente   de connexion sur  le port  eth0 avec
	autorisation de login root
	- aucune autre application n'est install�e par choix.

En  effet, la sp�cialisation de l'�quipement  est assur�e par d'autres
outils indp�pendants de SBXG. Ce choix  vise � proposer un ensemble de
scripts  simples � maintenir dans le cadre  du projet  d�crit ici.  La
sp�cialisation   de  l'�quipement,  l'ajout   de  composants logiciels
compl�mentaires  permettant  de    configurer l'equipement  pour   une
activit� sp�cifique (serveur, gateway, point d'acc�s Wifi telecom) est
assur�e par d'autres composants de type Ansible.

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
crois�e, il convient  par cons�quent d'installer  un cross compilateur
GCC  (arm-gcc), les packages Debian �tant  disponibles  dans les repos
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

Enfin,   l'outil repo de   Google   est  utilis�, il  convient   de le
t�l�charger en lien avec la doc fournie � l'adresse suivante:

https://source.android.com/source/downloading.html#installing-repo.

3 Organisation des d�pots GIT
-----------------------------

Afin  de  maitriser la complexit�,  les �l�ments fonctionnels suivants
sont  install�s    dans   quatre  d�pots     git  ind�pendants.     La
synchronisation globale des  d�pots permettantr d'assurer la coh�rence
est effectu�e � travers l'outils 'repo' de Google.

3.1 El�ment   principal  (core)  

Cet �l�ment   est le  coeur  du   projet (system-builder-ng.git).   Il
contient l'ensemble des scripts permettant  d'assurer les fonctions de
production logicielle.


3.2 El�ment de board

Cet �l�ment   contient les r�f�rences de   toutes les cartes utilis�es
dans  le projet,  seula la description   des cartes est effectu�e � ce
niveau �  travers  la valorisation  de   variable de  type shell,  ces
derni�res �tant utilis�es par la  suite dans la production  logicielle
par les scripts et Makefiles.

3.3 El�ment noyau Linux

Cet �l�ment contient les  r�f�rences des noyaux   Linux mis en  oeuvre
pour les diff�rentes boards d�crites pr�c�dement.

3.4 El�ment de synchornisation (manifest)

Cet �l�ment est  l'�l�ment f�d�rateur,  il  assure la  lien entre  les
trois pr�c�dents.

4 Build 
-------

Build : phase 1
---------------

   L'organisation des d�pots git est telle  qu'il n'est pas n�cessaire
   de les  t�l�charger tous en premier lieu.   En effet,  une cible du
   Makefile   est en  charge  de   cette activit�, si    bien que pour
   initialiser la  premiere   fois     un  projet, seul    le    d�pot
   system-builder-ng doit �tre t�l�charg� comme le montre l'exemple ci
   dessous (sous r�serve de disposer des cl�s d'acc�s!)


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

Build : phase 3. Synchroniser les d�pots de SBXG [OPTIONNEL]
------------------------------------------------------------

   Cette �tape est faite automatiquement  par la commande `make init`,
   mais il peut �tre n�cessaire de le refaire � l'occasion

make sync

Build : phase 4. Lancement du build
-----------------------------------

make all

   Le   r�sultat  est une  image g�n�rique,    stock�e dans le dossier
   `images/`. Il peut �tre n�cessaire de la sp�cialiser (voir le d�pot
   ansible-specializer).

Build : phase 5 Etapes du build
--------------------------------

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



