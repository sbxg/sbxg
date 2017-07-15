#! /usr/bin/env python
#
# Copyright (c) 2017 Jean Guyomarc'h
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import jinja2
import os
import shutil
import subprocess
import sys
import yaml

def getopts(argv):
    """
    Parse command-line options and provide a structure that holds the values
    attributed for each option.

    :param argv: List of command-line arguments.
    """
    parser = argparse.ArgumentParser(description='SBXG Boostrapper')
    parser.add_argument(
        '--subcomponent-prog', '-S', type=str, default='subcomponent',
        help='Provide the path to the subcomponent program'
    )
    parser.add_argument(
        '--toolchain-prefix', '-T', type=str,
        help='Provide the prefix of a LOCAL toolchain'
    )
    parser.add_argument(
        '--toolchain', '-t', type=str,
        help='Path to the toolchain configuration'
    )
    parser.add_argument(
        '--kernel', '-k', type=str,
        help='Path to the kernel configuration'
    )
    parser.add_argument(
        '--kernel-config', '-K', type=str,
        help='Path to a configuration to be fed to the kernel'
    )
    parser.add_argument(
        '--uboot', '-u', type=str,
        help='Path to the u-boot configuration'
    )
    parser.add_argument(
        '--uboot-config', '-U', type=str,
        help='Path to a configuration to be fed to u-boot'
    )
    parser.add_argument(
        '--board', '-B', type=str,
        help='Name of a built-in SBXG board (default variant will be selected)'
    )
    parser.add_argument(
        '--board-variant', '-b', type=str,
        help='Name of a variant configuration for a selected board'
    )
    parser.add_argument(
        '--gen-image', '-I', type=str,
        help="Path to a genimage template configuration"
    )
    parser.add_argument(
        '--uboot-script', '-s', type=str,
        help="Path to the u-boot boot script"
    )
    parser.add_argument(
        '--no-download', '-n', action='store_true',
        help="Don't make subcomponent download the components"
    )
    return parser.parse_args(argv[1:])

def generate_subcomponent(build_dir, components):
    """
    Generate the subcomponent file structure to make possible the fetching of
    the required components.

    :param build_dir: The path to the top build directory
    :param components: A list of strings containing subcomponent configuration
                       per component.
    """
    # Create the directory structure if it does not already exist
    path_dir = os.path.join(build_dir, 'subcomponent')
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    # Generate the main subcomponent file by aggregating all different
    # configurations together.
    path = os.path.join(path_dir, 'components.sub')
    with open(path, 'w') as stream:
        stream.write(
            "/* This is a generated file. */\n"
            "\n"
            "subcomponents {"
        )

        for component in components:
            stream.write('\n' + component)

        stream.write("}\n")

def call_subcomponent(prog):
    """
    Run the subcomponent program to fetch the components requested either
    by the options passed to the bootstrap or by the configuration.

    :param prog: The subcomponent program to call
    """
    subprocess.check_call([prog, "fetch"])

def convert_compressions(compressions):
    converted = ""
    for compression in compressions:
        converted += '"{}", '.format(compression)
    return converted[:-2]

def forge_build_dir(path, name):
    return os.path.join(os.path.dirname(path), "build_" + name)

def db_common(name, path, data):
    return {
        "url": data["url"],
        "name": name,
        "path": path,
        "compressions": convert_compressions(data["compression"]),
        "sha256": data.get("sha256"),
        "pgp_signature": data.get("pgp-signature"),
        "pgp_pubkey": data.get("pgp-pubkey"),
    }

def db_toolchain(name, path, data):
    db = db_common(name, path, data)
    db["prefix"] = data["prefix"]
    db["arch"] = data["arch"]
    return {'toolchain': db}

def db_kernel(name, path, data):
    kernel_type = name.split('-')[0]
    db = db_common(name, path, data)
    db["type"] = kernel_type 
    build_dir = forge_build_dir(path, kernel_type)
    db["build_dir"] = build_dir

    return {'kernel': db}

def db_uboot(name, path, data):
    db = db_common(name, path, data)
    db["build_dir"] = forge_build_dir(path, "uboot" + name)
    return {'uboot': db}

def template_conf_file(build_dir, template_file, conf_file, j2_env, callback):
    # Load the yaml file into a string and parse it
    with open(conf_file, 'r') as stream:
        db_file = stream.read()
    conf = yaml.load(db_file)

    # The yaml file shall contain one key-value pair. The key shall be the
    # path where the toolchain will reside after extraction.
    assert len(conf.keys()) == 1
    path = conf.keys()[0]
    data = conf[path]
    path = os.path.join(build_dir, path)
    name = os.path.splitext(os.path.basename(conf_file))[0]

    database = callback(name, path, data)

    template = j2_env.get_template(template_file)
    return template.render(database), database

def build_genimage_db(build_dir):
    return {
        'path': os.path.join(build_dir, 'genimage-git'),
        'build_dir': os.path.join(build_dir, 'build_genimage'),
        'output_path': os.path.join(build_dir, 'images'),
        'input_path': os.path.join(build_dir, '.genimage-in'),
        'root_path': os.path.join(build_dir, '.genimage-root'),
        'tmp_path': os.path.join(build_dir, '.genimage-tmp'),
        'config': os.path.join(build_dir, 'genimage.cfg'),
    }

def template_genimage(database, j2_env):
    template = j2_env.get_template('genimage.j2')
    return template.render(database)

def template_file(template_name, database, j2_env, output):
    template = j2_env.get_template(template_name)
    contents = template.render(database)
    with open(output, 'w') as stream:
        stream.write(contents)


def generate_makefile(build_dir, database, j2_env):
    template = j2_env.get_template('Makefile.j2')
    data = template.render(database)

    with open(os.path.join(build_dir, 'Makefile'), 'w') as stream:
        stream.write(data)

def init_config(path, build_dir):
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    config = os.path.join(build_dir, ".config")
    shutil.copyfile(path, config)

def main(argv):
    args = getopts(argv)

    if args.board_variant and not args.board:
        print("error: --board-variant cannot be used without --board")
        sys.exit(1)

    if args.toolchain and args.toolchain_prefix:
        print("error: --toolchain and --toolchain-prefix are mutually "
              "exclusive options.")
        sys.exit(1)

    top_src_dir = os.path.dirname(os.path.realpath(__file__))
    top_build_dir = os.getcwd()

    if os.path.normpath(top_src_dir) == os.path.normpath(top_build_dir):
        print("error: Run bootstrap.py from a build directory that is "
              "distinct from the source directory.")
        sys.exit(1)

    configurations = []
    main_db = {
        "top_build_dir": top_build_dir,
    }

    if args.board:
        config = args.board_variant + '.yml' if args.board_variant else 'board.yml'
        board_dir = os.path.join(top_src_dir, "boards", args.board)
        filename = os.path.join(board_dir, config)
        assert os.path.exists(filename), "Invalid board name"
        with open(filename, 'r') as stream:
            board_file = stream.read()
        db = yaml.load(board_file)
        board_db = db["board"]
        board_db["boot_script"] = "boot.scr"
        if not args.toolchain:
            args.toolchain = os.path.join(
                top_src_dir, "toolchains", board_db["toolchain"] + ".yml"
            )
        if not args.kernel:
            args.kernel = os.path.join(
                top_src_dir, "kernels", board_db["kernel"] + ".yml"
            )
        if not args.kernel_config:
            args.kernel_config = os.path.join(
                top_src_dir, board_dir, "kernel", board_db["kernel-config"]
            )
        if not args.uboot:
            args.uboot = os.path.join(
                top_src_dir, "uboot", board_db["uboot"] + ".yml"
            )
        if not args.uboot_config:
            args.uboot_config = os.path.join(
                top_src_dir, board_dir, "uboot", board_db["uboot-config"]
            )
        if not args.gen_image:
            args.gen_image = os.path.join(
                top_src_dir, board_dir, 'images', board_db["image"]
            )
        if not args.uboot_script:
            args.uboot_script = os.path.join(
                top_src_dir, board_dir, 'uboot', board_db['uboot-script']
            )
        board_db["uboot_script"] = args.uboot_script
        main_db['board'] = board_db


    j2_loaders = [os.path.join(top_src_dir, "templates")]
    if args.gen_image:
        j2_loaders.append(os.path.dirname(args.gen_image))
    if args.uboot_script:
        j2_loaders.append(os.path.dirname(args.uboot_script))
    j2_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(j2_loaders),
        lstrip_blocks=True
    )


    if args.toolchain:
        toolchain_conf, db = template_conf_file(
            top_build_dir, 'toolchain.j2',
            args.toolchain, j2_env, db_toolchain
        )
        main_db.update(db)
        configurations.append(toolchain_conf)

    if args.kernel:
        kernel_conf, db = template_conf_file(
            top_build_dir, 'kernel.j2',
            args.kernel, j2_env, db_kernel
        )
        main_db.update(db)
        configurations.append(kernel_conf)

    if args.uboot:
        uboot_conf, db = template_conf_file(
            top_build_dir, 'uboot.j2',
            args.uboot, j2_env, db_uboot
        )
        main_db.update(db)
        configurations.append(uboot_conf)



    if args.kernel_config:
        init_config(args.kernel_config, main_db["kernel"]["build_dir"])
    if args.uboot_config:
        init_config(args.uboot_config, main_db["uboot"]["build_dir"])

    # Handle generation of image. Genimage is used to create an image, ready to
    # be flashed, without requiring the use of fancy, complex, priviledged
    # programs.
    if args.gen_image:
        # Collect data to form a DB for genimage's use
        main_db['genimage'] = build_genimage_db(top_build_dir)
        # Template the genimage subcomponent fragment
        genimage_conf = template_genimage(main_db, j2_env)
        configurations.append(genimage_conf)

        # Genimage requires some workering directories to exist.
        # Go through them one by one, and create hem if need be.
        for gen_dir in ["output_path", "input_path", "root_path", "tmp_path"]:
            directory = main_db['genimage'][gen_dir]
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Generate the final genimage configuration
        template_file(
            os.path.basename(args.gen_image), main_db, j2_env,
            os.path.join(top_build_dir, 'genimage.cfg')
        )

        # Generate the u-boot script from a template
        template_file(
            os.path.basename(main_db["board"]["uboot-script"]), main_db, j2_env,
            os.path.join(top_build_dir, 'boot.cmd')
        )


    # Aggregate all the configurations fragments into a valid subcomponent
    # file hierharchy.
    generate_subcomponent(top_build_dir, configurations)

    # Generate SBXG's Makefile
    generate_makefile(top_build_dir, main_db, j2_env)

    # Unless we explicitely provided --no-download, call subcomponent so we
    # can download the components.
    if not args.no_download:
        call_subcomponent(args.subcomponent_prog)

if __name__ == "__main__":
    main(sys.argv)
