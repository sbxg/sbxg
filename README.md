SBXG Core
=========

1 Introduction
--------------

SBXG (System Builder Next Generation) est un projet visant � produire 3
composants logiciels fonctionnels diff�rents :

	- un bootloader (u-boot) pour d�marrer une plateforme embarqu�e ;
	- un noyau Linux s'ex�cutant sur la plateforme embarqu�e ;
	- un rootfs  contenant le minimum de  composants logiciels de type
	Debian, � savoir un shell de login et un d�mon sshd ;

� l'issue  de la production   logicielle, une carte  SD ou  un  disque
bootable est pr�par� avec la configuration suivante :

	- un compte root initialis� avec le mot de passe sp�cifi� dans
          le fichier config.template ;
        - un compte admin, sudoer avec le mot de passe sp�cifi� dans
          le fichier config.template ;
	- un shell de login ;
	- un d�mon  sshd en attente   de connexion sur  le port  eth0 avec
 	  refus de login root ;
	- aucune autre application n'est install�e par choix ;

En  effet, la sp�cialisation de l'�quipement  est assur�e par d'autres
outils indp�pendants de SBXG. Ce choix  vise � proposer un ensemble de
scripts  simples � maintenir dans le cadre  du projet  d�crit ici.  La
sp�cialisation   de  l'�quipement,  l'ajout   de  composants logiciels
compl�mentaires  permettant  de    configurer l'�quipement  pour   une
activit� sp�cifique (serveur, gateway, point d'acc�s WiFi t�l�com) est
assur�e par d'autres composants (Ansible).

2 D�pendances
-------------

Les composants logiciels suivants  doivent �tre install�s  avant tout
lancement du Makefile de production.

2.1 Instructions pour Debian
----------------------------

Toutes les   informations  suivantes  partent  d'une  hypoth�se  d'une
plateforme de production logicielle  bas�e sur une distribution Debian
version Jessie,  architecture AMD64.  A ce   titre, le fichier suivant
doit contenir au minimum :

 |> cat /etc/apt/sources.list
 |
 | deb http://ftp.fr.debian.org/debian/ jessie main contrib non-free
 | deb http://security.debian.org/      jessie/updates main contrib non-free

La strat�gie retenue utilise donc une plateforme de production de type
crois�e, il convient  par cons�quent d'installer  un cross compilateur
GCC  (arm-gcc), les packages Debian �tant  disponibles  dans les repos
standards (definies ci-dessus). Pour cela, lancer la commande suivante:

apt-get install  \
	binutils-arm-linux-gnueabihf  \
	cpp-4.7-arm-linux-gnueabihf \
	gcc-4.7-arm-linux-gnueabihf \
	g++-4.7-arm-linux-gnueabihf \
	g++-4.7-arm-linux-gnueabihf \
	libc-bin-armhf-cross

 
De plus, les composants  de  d�veloppement standards suivants  doivent
�tre  install�s, l'utilisation  de l'�mulateur  Qemu est indispensable
pour les derni�res  phase de  construction  du  rootfs (cf  r�pertoire
scripts)

apt-get install  \
	autoconf \
	build-essential \
	make \
	automake \
	debootstrap \
	qemu-user-static \
	qemu \
	binfmt-support


2.2 Repo
--------

Enfin,   l'outil repo de   Google   est  utilis�, il  convient   de le
t�l�charger en lien avec la doc fournie � l'adresse suivante:

https://source.android.com/source/downloading.html#installing-repo.

3 Organisation des d�pots GIT
-----------------------------

Afin  de  ma�triser la complexit�,  les �l�ments fonctionnels suivants
sont  install�s    dans   quatre  d�pots     git  ind�pendants.     La
synchronisation globale des  d�pots permettantr d'assurer la coh�rence
est effectu�e � travers l'outils 'repo' de Google.

3.1 El�ment   principal  (core)
-------------------------------

Cet �l�ment   est le  coeur  du   projet (system-builder-ng.git).   Il
contient l'ensemble des scripts permettant  d'assurer les fonctions de
production logicielle. Il s'agit du d�p�t contenant ce README.


3.2 El�ment de board
--------------------

Cet �l�ment   contient les r�f�rences de   toutes les cartes utilis�es
dans  le projet,  seule la description   des cartes est effectu�e � ce
niveau �  travers  la valorisation  de  variables de  type shell,  ces
derni�res �tant utilis�es par la  suite dans la production  logicielle
par les scripts et Makefiles.

3.3 El�ment noyau Linux
-----------------------

Cet �l�ment contient les  r�f�rences des noyaux   Linux mis en  oeuvre
pour les diff�rentes boards d�crites pr�c�dement (i.e. .config).

3.4 El�ment de synchronisation (manifest)
-----------------------------------------

Cet �l�ment est  l'�l�ment f�d�rateur,  il  assure la  lien entre  les
trois pr�c�dents.

Pour   contourner   ce point, dans  le    shell  courant de production
logicile, lancer les commandes d�crites � la section suivante.


4 Build
-------

4.1 Remarques
-------------

L'utilisation de repo peut poser un probl�me de  blocage si on utilise
des cl�s priv�s prot�g�es par mot de passe. Dans ce cas, il semble que
repo demande les  cl�s associ�es aux d�pots git  ..., et les shell tty
visiblement se m�langent se terminant finalement pas un shell de login
en mode ssh et forc�ment un �chec de connexion puisque le mot de passe
du shell de login n'est pas celui de d�verouillage de la cl� priv�.

Ce point est av�r� sur distribution AMD64 Debian V 8.2 avec repo dans
la version suivante :

 repo version v1.12.32
       (from https://gerrit.googlesource.com/git-repo)
repo launcher version 1.22
       (from /local_home/local/bin/repo)
git version 1.9.1
Python 2.7.3 (default, Mar 13 2014, 11:03:55)
[GCC 4.7.2]

Le contournement propos�   consiste  a utiliser la  fonctionnalit�  de
sauvegarde du secret de d�verrouillage de la cl� priv� ssh fournie par
ssh-agent.

Dans le  shell  de production (celui   h�bergeant  la commande  repo),
lancer les commandes suivantes...

 |> eval $(ssh-agent -s)
 |> ssh-add /path/to/your/private/ssh/key


4.2 Build : phase 1
-------------------

   L'organisation des d�pots git est telle  qu'il n'est pas n�cessaire
   de les  t�l�charger tous en premier lieu.   En effet,  une cible du
   Makefile   est en  charge  de   cette activit�, si    bien que pour
   initialiser la  premiere   fois     un  projet, seul    le    d�pot
   system-builder-ng doit �tre t�l�charg� comme le montre l'exemple ci
   dessous (sous r�serve de disposer des cl�s d'acc�s!)


 |> mkdir /tmp/SBXG
 |> cd /tmp/SBXG
 |> git clone ssh://gitolite3@bie91-1-82-227-34-59.fbx.proxad.net:1024/public/system-builder-ng
 | Cloning into 'system-builder-ng'...
 | Enter passphrase for key '/path/to/your/private/ssh/key':
 | remote: Counting objects: 185, done.
 | remote: Compressing objects: 100% (96/96), done.
 | remote: Total 185 (delta 111), reused 144 (delta 88)
 | Receiving objects: 100% (185/185), 47.24 KiB | 0 bytes/s, done.
 | Resolving deltas: 100% (111/111), done.
 | Checking connectivity... done.


4.3 Build : phase 2 - Initialiser SBXG pour une board
------------------------------------------------------

Merci de relire le �4.1

 |> cd /tmp/SBXG/system-builder-ng
 |> make BOARD=$myboard init

o� $myboard peut prendre une des valeurs parmi :
   - Cubieboard2
   - Cubietruck
   - mx6qsabresd


4.4 Build : phase 2.1 - Synchroniser les d�pots de SBXG [OPTIONNEL]
-------------------------------------------------------------------

   Cette �tape est faite automatiquement  par la commande `make init`,
   mais il peut �tre n�cessaire de le refaire � l'occasion

 |> make sync



4.5 Build : phase 4. Lancement du build
----------------------------------------

|> make all

   Le   r�sultat  est une  image g�n�rique,    stock�e dans le dossier
   `images/`. Il peut �tre n�cessaire de la sp�cialiser (voir le d�pot
   ansible-specializer).


4.6 Build : phase 5 Etapes du build
-----------------------------------

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

