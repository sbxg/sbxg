SBXG Core
=========

1 Introduction
--------------

SBXG (System Builder Next Generation) est un projet visant à produire 3
composants logiciels fonctionnels différents :

	- un bootloader (u-boot) pour démarrer une plateforme embarquée ;
	- un noyau Linux s'exécutant sur la plateforme embarquée ;
	- un rootfs  contenant le minimum de  composants logiciels de type
	Debian, à savoir un shell de login et un démon sshd ;

À l'issue  de la production   logicielle, une carte  SD ou  un  disque
bootable est préparé avec la configuration suivante :

	- un compte root initialisé avec le mot de  passe spécifié dans le
	  fichier config.template ;
    - un compte admin, sudoer  avec le mot de  passe spécifié dans  le
      fichier config.template ;
	- un shell de login ;
	- un démon  sshd en attente   de connexion sur  le port  eth0 avec
	  refus de login root ;
	- aucune autre application n'est installée par choix ;

En  effet, la spécialisation de l'équipement  est assurée par d'autres
outils indpépendants de SBXG. Ce choix  vise à proposer un ensemble de
scripts  simples à maintenir dans le cadre  du projet  décrit ici.  La
spécialisation   de  l'équipement,  l'ajout   de  composants logiciels
complémentaires  permettant  de    configurer l'équipement  pour   une
activité spécifique (serveur, gateway, point d'accès WiFi télécom) est
assurée par d'autres composants (cf Ansible).

2 Dépendances
-------------

Les composants logiciels suivants  doivent être installés  avant tout
lancement du Makefile de production logicielle.

2.1.1 Build via Docker
--------------------

Il est possible de générer une image en passant par une image Docker.
Cela permet de faire abstraction des spécificités de la distribution
Linux sous-jacente. Les outils de builds sont maîtrisés au sein d'un
conteneur. Le pré-requis est évidemment d'installer le paquet Docker.

Sous Debian/Ubuntu :
  |> apt-get install docker

Sous Arch Linux:
  |> pacman -S docker


2.1.2 Instructions pour Debian
----------------------------

Toutes  les   informations suivantes  partent   d'une hypothèse  d'une
plateforme de production logicielle basée  sur une distribution Debian
version Jessie (8.x), architecture  AMD64.   A  ce titre,  le  fichier
suivant doit contenir au minimum :

 |> cat /etc/apt/sources.list
 |
 | deb http://ftp.fr.debian.org/debian/ jessie main contrib non-free
 | deb http://security.debian.org/      jessie/updates main contrib non-free

La stratégie retenue utilise donc une plateforme de production de type
croisée (cible = arm), il convient par conséquent d'installer un cross
compilateur GCC (arm-gcc), les  packages Debian étant disponibles dans
les repos  standards  (definies   ci-dessus).  Pour  cela,   lancer la
commande suivante:

apt-get install  \
	binutils-arm-linux-gnueabihf  \
	cpp-4.7-arm-linux-gnueabihf \
	gcc-4.7-arm-linux-gnueabihf \
	g++-4.7-arm-linux-gnueabihf \
	g++-4.7-arm-linux-gnueabihf \
	libc-bin-armhf-cross


De plus, les composants de   développement standards suivants  doivent
être  installés,  l'utilisation de l'émulateur Qemu  est indispensable
pour   les dernières phases de construction   du rootfs (cf répertoire
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

Enfin,   l'outil repo de   Google   est  utilisé, il  convient   de le
télécharger en lien avec la doc fournie à l'adresse suivante:

https://source.android.com/source/downloading.html#installing-repo.

3 Organisation des dépots GIT
-----------------------------

Afin de   maîtriser la complexité, les éléments  fonctionnels suivants
sont   installés  dans   quatre      dépots git   indépendants.     La
synchronisation  globale  des  dépots GIT   permettant  d'assurer   la
cohérence est effectuée à travers l'outils 'repo' de Google.

3.1 Elément   principal  (core)
-------------------------------

Cet élément   est le  coeur   du  projet (system-builder-ng.git).   Il
contient l'ensemble des  scripts permettant d'assurer les fonctions de
production logicielle. Il s'agit du dépôt contenant ce fichier README.


3.2 Elément de board
--------------------

Cet élément   contient les références de   toutes les cartes utilisées
dans  le projet,  seule la description   des cartes est effectuée à ce
niveau à  travers  la valorisation  de  variables de  type shell,  ces
dernières étant utilisées par la  suite dans la production  logicielle
par les scripts et Makefiles.

3.3 Elément noyau Linux
-----------------------

Cet élément contient les  références des noyaux   Linux mis en  oeuvre
pour les différentes boards décrites précédement (i.e. .config).

3.4 Elément de synchronisation (manifest)
-----------------------------------------

Cet élément est  l'élément fédérateur,  il  assure la  lien entre  les
trois précédents.

4 Build
-------

4.1 Remarques
-------------

L'utilisation de repo peut poser un problème de  blocage si on utilise
des clés privés protégées par mot de passe. Dans ce cas, il semble que
repo demande les  clés associées aux dépots git  ..., et les shell tty
visiblement se mélangent se terminant finalement pas un shell de login
en mode ssh et forcément un échec de connexion puisque le mot de passe
du shell de login n'est pas celui de déverouillage de la clé privé.

Ce point est avéré sur distribution AMD64 Debian V 8.2 avec repo dans
la version suivante :

 repo version v1.12.32
       (from https://gerrit.googlesource.com/git-repo)
repo launcher version 1.22
       (from /local_home/local/bin/repo)
git version 1.9.1
Python 2.7.3 (default, Mar 13 2014, 11:03:55)
[GCC 4.7.2]

Pour   contourner ce  point,  dans   le shell   courant  de production
logiciel, lancer les commandes décrites à la section suivante.

Le  contournement proposé  consiste à   utiliser la  fonctionnalité de
sauvegarde du secret de déverrouillage de la clé privé ssh fournie par
ssh-agent,    si bien que l'opération    de  gestion des clés  devient
transparente.

Dans le  shell  de production (celui   hébergeant  la commande  repo),
lancer les commandes suivantes...

 |> eval $(ssh-agent -s)
 |> ssh-add /path/to/your/private/ssh/key


4.2 Build : phase 1. - Initialisation du projet
----------------------------------------------

L'organisation des dépots GIT est telle  qu'il n'est pas nécessaire de
les télécharger tous en premier lieu.  En effet, une cible du Makefile
est en charge   de cette activité, si  bien  que pour  initialiser  la
première fois   le projet, seul  le  dépot system-builder-ng doit être
téléchargé  comme le   montre l'exemple ci  dessous  (sous  réserve de
disposer des clés d'accès!)


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


4.3 Build : phase 2. - Initialiser SBXG pour une board
------------------------------------------------------

Merci de relire le §4.1 si difficultés

 |> cd /tmp/SBXG/system-builder-ng
 |> make BOARD=$myboard init

où $myboard peut prendre une des valeurs parmi :
   - Cubieboard2
   - Cubietruck
   - mx6qsabresd


4.4 Build : phase 3. - Synchroniser les dépots de SBXG [OPTIONNEL]
-------------------------------------------------------------------

   Cette étape est faite automatiquement  par la commande `make init`,
   mais il peut être nécessaire de le refaire à  l'occasion

 |> make sync



4.5 Build : phase 4. Lancement du build
----------------------------------------

|> make all

   Le   résultat  est une  image générique,    stockée dans le dossier
   `images/`. Il peut être nécessaire de la spécialiser (voir le dépot
   ansible-specializer).


4.6 Build : phase 5. Etapes du build
------------------------------------

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

4.7 Build avec Docker
---------------------

Le dossier docker/ contient trois fichiers :
  - Dockerfile, qui indique comment l'image Docker doit être construite
  - build, qui est un script permettant de créer une image Docker
    automatiquement à partir du Dockerfile
  - do, qui est un script éxécutant n'importe quelle commande passée en
    paramètre dans l'image Docker.

Ainsi, pour générer l'image complète, on procèdera comme suit :

  |> ./docker/build    # Afin de générer l'image Docker
  |> ./docker/do make  # Afin de lancer le build

Si l'image est déjà créée, lancer le script `build` n'est pas utile.


5. Annexe
---------

5.1 Support de Xemacs21 en mode UTF8
------------------------------------

Afin de supporter sous Xemacs21 le  mode UTF8, ajouter dans le fichier
~/.xemacs/init.el les lignes suivantes:

|> (require 'un-define)
(set-coding-priority-list '(utf-8))
(set-coding-category-system 'utf-8 'utf-8)


5.2 production logicielle (make debootstrap) dans un container LXC
------------------------------------------------------------------

Sous réserve que l'environnement de  production logiciel soit installé
dans un container de type LXC, bien que les précautions d'installation
telles que  définies au §2.1 soient  prise en compte,  il peut arriver
que l'erreur suivante se produise:


|> I: Extracting mount...
I: Extracting util-linux...
I: Extracting liblzma5...
I: Extracting zlib1g...
+ sudo cp /usr/bin/qemu-arm-static usr/bin
+ sudo LC_ALL=C LANGUAGE=C LANG=C chroot . /debootstrap/debootstrap --second-stage
chroot: failed to run command '/debootstrap/debootstrap': Exec format error
Makefile:191: recipe for target 'debootstrap' failed


Vérifiez que binfmt est correctement installé via la commande suivante :

|>  root@vm-jessie-x86-amd64-3:~# update-binfmts --display |grep arm
root@vm-jessie-x86-amd64-3:~# 


Dans ce cas (absence d'emulateur qemu, docn  cause de ce problème), il
est nécessaire d'ajouter la commande suivante :


|>  root@vm-jessie-x86-amd64-3:~# update-binfmts --install qemu-arm /usr/bin/qemu-arm-static --magic \x7fELF\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x28\x00


A l'issue de quoi, la commande précédente retourne bien la pésence de l'émulateur qemu correctemetn installé, car :

|> root@vm-jessie-x86-amd64-3:~# update-binfmts --display |grep arm
qemu-arm (enabled):
 interpreter = /usr/bin/qemu-arm-static

L'erreur précédente est  corrigée est la  cible 'make debootstrap' est
opérationnelle.
