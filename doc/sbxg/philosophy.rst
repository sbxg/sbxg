The Philosophy of SBXG
===============================================================================

To summarize the key-points of :doc:`the introduction </index>`, SBXG is
designed to offer a high level of reproductibility and tracability when it
comes to building the low-level components (Kernel, Bootloader) of a system.
Configuration should be trivial, easy to maintain and keep track of.

It only concentrates in **building from source** the low-level components,
eventually putting them together in a final image. In the later case, it
expects the rootfs to be provided: :doc:`it does not care about the roots
</sbxg/rootfs>`. Even for kernel modules. How you distribuate these components
is up to **you**.


Positions towards other tools
-------------------------------------------------------------------------------

SBXG is not a innovation. There (hopefully) exist many other tools able to
build a kernel. However, we think that SBXG fills a certain void when trying
to generate Linux-based embedded systems, for which other tools do not offer
a (subjectively judged) acceptable answer.


Why not Buildroot?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Buildroot <https://buildroot.org/>`_ allows to build root file systems, a
Linux kernel and the U-Boot bootloader. If you are interesed in creating a
self-contained, minimalistic and finely tailored to your needs, buildroot is
the way to go.  Don't bother with us! However, if your objective is to build
*only the low-level components*, or a whole bunch of them, you should consider
using SBXG. Furthermore compiling these components with an explicit
configuration (i.e. without fragments) is not handy with buildroot: if you
don't modify buildroot itself, you are obliged to add some kind of layer on top
of it to generate a meaningful buildroot configuration.


Why not a simple shell script?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your goal is just to build a couple of low-level components, a hand-crafted
shell script is surely enough, given you are familiar with their build systems.

However, if you need to build a lot of them, SBXG may come handy, as it knows
how to do. Also, if you want to create a full sdcard image, things may become
a bit more challenging. This is even more true when trying to put Xen in the
loop. SBXG knows how to do it. It should make things easier for you.


