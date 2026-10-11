:title: Migrating to Fossil
:date: 2026-10-11
:tags: blog, blogging, fossil
:identifier: 20261004T150218
:signature: 1=5

Migrating My Blog to Fossil
===========================

.. container:: post-teaser

   I've been `playing <https://github.com/swyddfa/awdur/pull/43>`__ with `fossil <https://fossil-scm.org/home/doc/trunk/www/index.wiki>`__ a lot `recently <https://github.com/swyddfa/awdur/pull/44>`__ and I'm really enjoying it.
   Also, with the recent issues surrounding GitHub I have been thinking about what an alternative might look like.
   Sure abandoning git entirely might be a bit drastic but fossil gives you *a lot* out of the box.

   So to try it out on a low risk project, I've moved this blog over to fossil... oh and I've redone the hosting while I'm at it 😅

.. _1-5-git-to-fossil:

Git to Fossil
-------------

.. highlight:: console

The first step is easy as it's `documented <https://fossil-scm.org/home/doc/trunk/www/inout.wiki>`__ on the fossil website

#. First I took a fresh clone of the repository in a ``/tmp`` folder::

          $ cd /tmp
     /tmp $ git clone https://github.com/alcarney/blog

#. Then imported the repository into fossil::

          /tmp $ cd blog
     /tmp/blog $ git fast-export --all | fossil import --git ../blog.fossil
     Rebuilding repository meta-data...
       100.0% complete...
     Vacuuming... ok
     project-id: 7a90b16344634602e62eba6997b2949da7295469
     server-id:  31df20e837efe775faa3a6a8567f65b75c931ce2
     admin-user: alex (password is "***")

   Which produced an 18Mb SQLite DB containing my blog's git history.

Unfortunately, it also contained all the commits on the ``gh-pages`` branch that were produced from deploying to GitHub Pages for years.

Fossil also took my user name as the author, whereas all the imported check-ins (i.e. commits) are linked to my Git committer email.

So I tweaked the command to be::

  $ git fast-export release | fossil import --git ../blog.fossil -A alcarneyme@gmail.com
  Rebuilding repository meta-data...
    100.0% complete...
  Vacuuming... ok
  project-id: 968d4558828a3458b1f85951ea0d2d62138521d7
  server-id:  752c338efbe7982a022e7f3d1262b8101ab6198c
  admin-user: alcarneyme@gmail.com (password is "***")

Which removed the history I didn't care about and reduced the size of DB to 6.5Mb.

.. _1-5-hosting-fossil:

Hosting Fossil
--------------

One of the many things you get out of the box with fossil is a server to host project repositories.
There are `many options <https://fossil-scm.org/home/doc/trunk/www/server/>`__ for hosting a server but I've gone for the "standalone HTTP server" approach, placing it behind a Caddy reverse proxy.

Server Setup
^^^^^^^^^^^^

I might look into doing something fancier in the future with containers etc. but for now, I've just set everything up direct on the host.

#. I created a ``fossil`` system user to run the fossil server under::

     $ sudo useradd --system --home-dir /srv/fossil --create-home --shell /usr/sbin/nologin fossil

#. I then copied in the repository and made the new ``fossil`` user the owner::

     $ sudo mv blog.fossil /srv/fossil/blog.fossil
     $ sudo chwon fossil:fossil /srv/fossil/blog.fossil

#. Next was to create a system service unit to manage running the server

   .. code-block:: ini
      :in-project: vps
      :in-file: fossil.service

      [Unit]
      Description=Fossil server
      After=network.target

      [Install]
      WantedBy=multi-user.target

      [Service]
      User=fossil
      Group=fossil
      ExecStart/usr/bin/fossil server --repolist /srv/fossil/ --localhost --port 8080 --https
      Restart=on-failure

   Passing ``--repolist`` tells fossil to serve all ``*.fossil`` files from a directory, so if I ever wanted to add new projects in the future, all I have to do is drop them into the ``/srv/fossil`` folder.

   .. code-block:: ini
      :in-project: vps
      :in-file: fossil.service

      NoNewPrivileges=yes
      PrivateTmp=yes
      ProtectSystem=strict
      ReadWritePaths=/srv/fossil

   Not sure how paranoid I need to be but these options lock down various settings to restrict what ``fossil`` has access to

   - ``NoNewPrivileges`` prevents ``fossil`` or any child process from elevating privileges.
   - ``PrivateTmp`` ensures that ``fossil`` receives an isolated ``/tmp`` dir that is automatically cleaned up when the process exits.
   - ``ProtectSystem=strict`` makes it so that ``fossil`` only has read access to the system's filesystem (minus a few exceptions).
   - ``ReadWritePaths`` grants an exception to ``/srv/fossil`` so that the server can update repository content as needed.

#. Finally Caddy needs to be configured to proxy the relevant requests to the ``fossil server`` process.

   .. code-block:: Caddyfile
      :in-project: vps
      :in-file: Caddyfile

      (logging) {
          log {
              output file /var/log/caddy/{args[0]}.log
              mode 0640
              roll_size 50MiB
              roll_keep 10
              roll_keep_for 720h
          }
      }

      scm.alcarney.me {
          import logging scm.alcarney.me
          encode zstd gzip
          reverse_proxy 127.0.0.1:8080
      }

Cloning and Pushing
^^^^^^^^^^^^^^^^^^^

With the server up and running it was time to try pushing some commits!

Cloning the repo was easy enough::

  $ fossil clone https://scm.alcarney.me/blog --no-open -A alcarneyme@gmail.com
  Round-trips: 3   Artifacts sent: 0  received: 1612
  Clone done, wire bytes sent: 794  received: 5954587  remote: <ipaddr>
  Rebuilding repository meta-data...
    100.0% complete...
  Extra delta compression... 2 deltas save 11,515 bytes
  Vacuuming the database...
  project-id: 6c060ac43a4c277c46c72ada7644349ed74cd4fc
  server-id:  8aa7fa5785c21465fe22f3cca0a1b3160a4d1385
  admin-user: alcarneyme@gmail.com (password is "***")

Now you will notice that the repository is a SQLite DB, to actually get a directory of files to work on, we need to open it::

  $ fossil open blog.fossil --workdir blog/
  Pull from https://scm.alcarney.me/blog
  Round-trips: 1   Artifacts sent: 0  received: 0
  Pull done, wire bytes sent: 310  received: 740  remote: <ipaddr>
  .devcontainer/Dockerfile
  .devcontainer/devcontainer.json
  .devcontainer/tools.mk
  .dir-locals.el
  ...
  theme/mytheme/theme.conf
  uv.lock
  project-name: alcarney.me
  repository:   /tmp/blog.fossil
  local-root:   /tmp/blog/
  config-db:    /home/alex/.config/fossil.db
  project-code: 6c060ac43a4c277c46c72ada7644349ed74cd4fc
  checkout:     207b1b11861f5708f8c2a4945428a0caf9bfb1f8 2026-10-04 10:11:56 UTC
  parent:       e67aa2ce0440b6fa8050a6a35c34c9bd40b66127 2026-10-04 09:59:22 UTC
  tags:         release, trunk
  comment:      emacs: drop unused gptel config (user: alcarneyme@gmail.com)
  check-ins:    433

Which I think is quite nice, it pushes you down a ``git worktree`` style workflow from the start.

Trying to commit my changes however, was a little surprising::

  $ ❯ fossil status
  repository:   /tmp/blog.fossil
  local-root:   /tmp/blog/
  config-db:    /home/alex/.config/fossil.db
  checkout:     207b1b11861f5708f8c2a4945428a0caf9bfb1f8 2026-10-04 10:11:56 UTC
  parent:       e67aa2ce0440b6fa8050a6a35c34c9bd40b66127 2026-10-04 09:59:22 UTC
  tags:         release, trunk
  comment:      emacs: drop unused gptel config (user: alcarneyme@gmail.com)
  EDITED     README.md

  $ fossil commit -m "a change"
  Cannot figure out who you are!  Consider using the --user
  command line option, setting your USER environment variable,
  or setting a default user with "fossil user default USER".
  cannot determine user

By using my email as my username I've deviated from the default and so need to tell ``fossil`` who I am::

  $ fossil user default alcarneyme@gmail.com

  $ fossil commit -m "a change"
  Pull from https://scm.alcarney.me/blog
  Round-trips: 1   Artifacts sent: 0  received: 0
  Pull done, wire bytes sent: 382  received: 740  remote: <ipaddr>
  New_Version: f992aa2d939246537020b4ca9541e604c5e2e0f0dd42ed313b69b4f1528e5019
  Sync with https://scm.alcarney.me/blog
  Round-trips: 1   Artifacts sent: 2  received: 0
  Sync done, wire bytes sent: 968  received: 741  remote: <ipaddr>
  Warning: The check-in was successful and is saved locally but you
           are not authorized to push the changes back to the server
           at https://scm.alcarney.me/blog

As you can see, fossil is very eager to push and pull changes from the remote and while I was able to commit my changes locally, I wasn't able to push them back upstream.

The trick, it seems, is to include your username in the url when you clone the repository and ask fossil to remember your credentials::

  $ fossil clone https://alcarneyme%40gmail.com@scm.alcarney.me/blog --no-open
  password for https://alcarneyme%40gmail.com@scm.alcarney.me/blog: ***
  remember password (Y/n)? y

After that any commits I make are auto-synced with the remote.

CI/CD
^^^^^

The only thing that I think I'm truly locked into GitHub for, is GitHub Actions.
For better or for worse it's now the de-facto standard and with extras like `trusted publishing <https://github.com/pypa/gh-action-pypi-publish>`__ it would be hard to move away from for a real project.

Thankfully for my blog, I don't have to deal with any of that.

It turns out fossil that provides `hooks <https://fossil-scm.org/home/doc/trunk/www/hooks.md>`__ and while the feature doesn't appear to have recevied a huge amount of attention, it gives me just enough to be able to roll my own CI/CD for my blog.

#. First we need to register an ``after-receive`` hook, instructing fossil to run the given command after it receives data from a push::

     $ sudo -u fossil fossil hook add -R /srv/fossil/blog.fossil --type after-receive --command 'touch /srv/fossil/blog-deploy.trigger'

#. Touching a file might not appear to be that useful, but we can use a systemd path trigger to start a build service.

   .. code-block:: ini
      :in-project: vps
      :in-file: blog-deploy.path

      [Unit]
      Description=Blog deployment trigger

      [Path]
      PathChanged=/srv/fossil/blog-deploy.trigger
      Unit=blog-deploy.service

      [Install]
      WantedBy=multi-user.target

#. And the build service is just configuration for a shell script

   .. code-block:: ini
      :in-project: vps
      :in-file: blog-deploy.service

      [Unit]
      Description=Blog deployment script

      [Service]
      Type=oneshot
      User=alex
      Environment=PATH=/home/alex/.local/bin:/home/alex/bin:/usr/local/bin:/usr/bin
      ExecStart=/home/alex/bin/blog-deploy.sh

#. Which does the real work of building and deploying the blog.

   .. code-block:: ini
      :in-project: vps
      :in-file: blog-deploy.sh

      #!/bin/sh
      set -euxo pipefail
      REPO=/home/alex/blog.fossil
      WORK=/home/alex/blog-build
      TMP=$(mktemp -d)
      OUT=/var/www/blog

      [ -f "$REPO" ] || fossil clone https://scm.alcarney.me/blog/ "$REPO"
      mkdir -p "$WORK" && cd "$WORK"
      [ -f .fslckout ] || fossil open "$REPO" trunk

      fossil update trunk

      BUILDDIR="${TMP}" make html

      rsync -av --delete "${TMP}/dirhtml/" "$OUT"/
      rm -r "${TMP}"

.. tip::

   Since everything is run under systemd, it's quite straightforward to monitor the build progress using ``journalctl``::

     $ journalctl -f -u blog-deploy.service

The only thing left to do was to configure Caddy to serve the newly built blog

.. code-block:: Caddyfile
   :in-project: vps
   :in-file: Caddyfile

   alcarney.me {
       redir https://www.alcarney.me{uri} permanent
   }

   www.alcarney.me {
           import logging www.alcarney.me
           root * /var/www/blog
           file_server
           encode zstd gzip
   }

Oh, and fix my DNS settings! 😅

Fossil to Git: In Theory
------------------------

Of course, I think it still makes sense to maintain a presence on GitHub so I need to be able to mirror the new fossil repo back to GitHub.

Once again, the fossil docs `have me covered <https://fossil-scm.org/home/doc/trunk/www/inout.wiki>`__ and shows how you can even do a bi-directional sync between the two sides using "marks" files. Note however, the instructions assume you're starting from a blank git repo whereas I want to maintain the existing Git history I already have on GitHub.

Thankfully after some searching I found `this forum post <https://fossil-scm.org/forum/forumpost/46c532e7356b8679>`__ which showed that as long as you export your marks during the initial import, it should be possible to maintain the existing history.
This does mean I need to recreate the fossil repo (again!), but I guess this is why you try it on a low stakes project first!

So without further ado, let's try syncing a fossil repo back to git.

#. Assuming an existing git repo, clone it::

     $ git clone https://github.com/alcarney/blog blog
     Cloning into 'blog'...
     remote: Enumerating objects: 23862, done.
     remote: Counting objects: 100% (344/344), done.
     remote: Compressing objects: 100% (236/236), done.
     remote: Total 23862 (delta 163), reused 178 (delta 91), pack-reused 23518 (from 1)
     Receiving objects: 100% (23862/23862), 15.48 MiB | 20.97 MiB/s, done.
     Resolving deltas: 100% (12354/12354), done.

#. Do the export to fossil :ref:`as before <1-5-git-to-fossil>`, but this time tell both sides to records their marks::

            $ cd blog/
      blog/ $ git fast-export release --export-marks="../blog.git-marks" | \
                fossil import --git --export-marks ../blog.fossil-marks ../blog.fossil --attribute "alcarneyme@gmail.com alex"
      Rebuilding repository meta-data...
        100.0% complete...
      Vacuuming... ok
      project-id: e93fd5cb678769f9e611d4c34e305770c259902e
      server-id:  c7977a1fb79e5ea5646076a5dab5d7d65275aadb
      admin-user: alex (password is "***")

   Rather than setting the admin user to be my committer email, I also figured out that the ``--attribute`` flag allows me to map my
   committer email to my fossil user name.

#. Have fossil keep track of *both* marks files.
   Interestingly, you don't have to open the repository to do this step!::

     $ fossil uv add blog.fossil-marks blog.git-marks -R blog.fossil

   Not to be confused with `uv <https://docs.astral.sh/uv/>`__, ``uv`` here stands for `unversioned files <https://fossil-scm.org/home/doc/trunk/www/unvers.wiki>`__ where fossil has the ability to store files in the repo but without tracking any version history - nice!

   Since this is a new repo, I of course had to replay some of the steps in :ref:`1-5-hosting-fossil` to redeploy the repo, reconfigure the deployment trigger and recommit the changes I had committed directly to fossil.

#. Then to sync changes back to GitHub the first step is to clone the git version of the repo (on the server this time)::

     $ git clone https://github.com/alcarney/blog blog-gh-mirror

#. Export the latest version of the marks files::

     $ fossil uv export blog.git-marks blog.git-marks -R blog.fossil
     $ fossil uv export blog.fossil-marks blog.fossil-marks -R blog.fossil

#. Do an incremental export from fossil to git based on the marks files::

     $ fossil export --git --import-marks ../blog.fossil-marks \
                           --export-marks ../blog.fossil-marks \
                           ../blog.fossil | \
         git fast-import --import-marks=../blog.git-marks \
                         --export-marks=../blog.git-marks

#. Finally, save the updated marks files::

     $ fossil uv add blog.fossil-marks blog.git-marks -R blog.fossil

Playing around in a ``/tmp`` folder this all appeared to be working fine, then I tried automating it...

Fossil to Git: In Practice
--------------------------

I started by updating the deploy script to include steps for syncing to GitHub.

.. code-block:: bash
   :in-file: blog-deploy.sh

   MIRROR=/home/alex/blog-gh-mirror

   fossil uv export blog.git-marks ../blog.git-marks
   fossil uv export blog.fossil-marks ../blog.fossil-marks

   cd $MIRROR
   fossil export --git \
         --import-marks ../blog.fossil-marks \
         --export-marks ../blog.fossil-marks ../blog.fossil | \
      git fast-import --import-marks=../blog.git-marks \
                      --export-matks=../blog.git-marks

   # Ensure the script continues to saving the marks, even if it failed.
   git push || echo "git push failed!"

   # Save the marks
   cd ../
   fossil uv add blog.git-marks blog.fossil-marks -R "$REPO"

Then I tried pushing some commits... ::

  Oct 10 16:12:59 blog-deploy.sh[13041]: + fossil export --git --import-marks ../blog.fossil-marks --export-marks ../blog.fossil-marks ../blog.fossil
  Oct 10 16:12:59 blog-deploy.sh[13042]: + git fast-import --import-marks=../blog.git-marks --export-marks=../blog.git-marks
  Oct 10 16:12:59 blog-deploy.sh[13041]: Non-existent SHA-1/SHA-3 in marks file: b2d5581c0b497c780b3ca0c61dee10237e3db30464f5fe93dafe037f8af60561
  Oct 10 16:12:59 blog-deploy.sh[13041]: error importing marks from file: ../blog.fossil-marks

Ok... this worked locally... and I was sure I had the right versions of the marks files... why wasn't it working?

Time to take a peek under the hood.
Let's try searching for this hash that apparently didn't exist::

  $ grep b2d558 blog.fossil-marks
  c524 :524 b2d5581c0b497c780b3ca0c61dee10237e3db30464f5fe93dafe037f8af60561

Yep, there it is, what about the git marks? ::

  $ grep :524 blog.git-marks
  :524 41336203795541f3b8de49e880fc60468d5b2e6a

So... it definitely exists and it maps to a hash on the git side too.
Well, it exists in the marks files, does it exist in the fossil repo itself? ::

  $ fossil sql -R blog.fossil
  sqlite> select rid from blob where uuid='b2d5581c0b497c780b3ca0c61dee10237e3db30464f5fe93dafe037f8af60561';
  ╭─────╮
  │ rid │
  ╞═════╡
  │ 524 │
  ╰─────╯

I guess that means the ``524`` in the marks files corresponds with the row id of the blob in the fossil repo - good to know.
So far everything appears to be in order, but then I've running this locally where the git export *did* work.

Time to try the same on the copy of the repo I have on the server::

  $ fossil sql -R blog.fossil
  sqlite> select rid from blob where uuid='b2d5581c0b497c780b3ca0c61dee10237e3db30464f5fe93dafe037f8af60561';
  ╭─────╮
  │ rid │
  ╞═════╡
  │ 563 │
  ╰─────╯

Ah, that's a problem...

If you've spent any time perusing the `fossil file format <https://fossil-scm.org/home/doc/trunk/www/fileformat.wiki>`__ documentation then you will see that the "global state of a fossil repository is an **unordered** set of artifacts".
You will also see that the page on the `databases used by Fossil <https://fossil-scm.org/home/doc/trunk/www/tech_overview.wiki>`__ stress that the database structure is merely an implementation detail, the true source of truth are the artifacts themselves.

I guess that means not even two clones of the same fossil repo are identical and by working off a clone of the repository I've instantly invalidated all the marks files!
The question now is... what to do about it?

``fossil git export``
^^^^^^^^^^^^^^^^^^^^^

Perhaps this inherent flakiness is why the ``fossil export --git`` command has been deprecated for some time::

  $  fossil export --git --help
  Usage: fossil export --git [REPOSITORY]

  This command is deprecated.  Use "fossil git export" instead.

The new way to do this is with the ``fossil git export`` command, which is much simpler to use::

  $ fossil git export /path/to/mirror --mainbranch release

Unfortunately, while the command supports incremental exports, I couldn't find a way to preserve the history of an existing git repository when setting up the mirror for the first time.

Also the corresponding import command has not yet been implemented, so no hope of a bi-directional sync with GitHub::

  $ fossil git --help
  Usage: fossil git SUBCOMMAND

  Do incremental import or export operations between Fossil and Git.
  Subcommands:

    fossil git export [MIRROR] [OPTIONS]

        <Details omitted...>

    fossil git import MIRROR

        TBD...

    fossil git status

        Show the status of the current Git mirror, if there is one.

          -q|--quiet         No output if there is nothing to report

And judging by `this comment <https://fossil-scm.org/forum/forumpost/6e4c1d6246ee8ff6>`__, it's likely to be "TBD" indefinitely...

The "Good Enough" Approach
--------------------------

I *could*, of course, stick to the original method.
I *could* carefully recreate ``blog.fossil`` again, in a way to make sure that the repo I do the mirroring from is the same one that was constructed by git, but to be honest I don't see the point, coming up with a robust solution is going to take more effort than I want to spend on this right now.

Being my personal blog, I also doubt anyone but me is going to care if my mirror to GitHub shares history with the existing repo.

So, I've just setup the mirror to export to a different branch name::

  $ fossil git export /path/to/mirror
  $ cd /path/to/mirror
  $ git push origin release:fossil   # Push local branch name to different remote branch name

The original history is still there, so I can try unifying them at some point in the future.
