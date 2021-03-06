Visual Editors
==============

.. _visualEditors:

This chapter is about maintaining Cheetah templates with visual
editors, and the tradeoffs between making it friendly to both text
editors and visual editors.

Cheetah's main developers do not use visual editors. Tavis uses
{emacs}; Mike uses {vim}. So our first priority is to make
templates easy to maintain in text editors. In particular, we don't
want to add features like Zope Page Template's
placeholder-value-with-mock-text-for-visual-editors-all-in-an-XML-tag.
The syntax is so verbose it makes for a whole lotta typing just to
insert a simple placeholder, for the benefit of editors we never
use. However, as users identify features which would help their
visual editing without making it harder to maintain templates in a
text editor, we're all for it.

As it said in the introduction, Cheetah purposely does not use
HTML/XML tags for $placeholders or #directives. That way, when you
preview the template in an editor that interprets HTML tags, you'll
still see the placeholder and directive source definitions, which
provides some "mock text" even if it's not the size the final
values will be, and allows you to use your imagination to translate
how the directive output will look visually in the final.

If your editor has syntax highlighting, turn it on. That makes a
big difference in terms of making the template easier to edit.
Since no "Cheetah mode" has been invented yet, set your
highlighting to Perl mode, and at least the directives/placeholders
will show up in different colors, although the editor won't
reliably guess where the directive/placeholder ends and normal text
begins.


